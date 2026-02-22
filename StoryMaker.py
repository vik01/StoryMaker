from dotenv import dotenv_values
from openai import OpenAI

config = dotenv_values(".env")
open_ai_key = config["OPENROUTER_API"]

class StoryMaker:
    """
    An AI-powered story generation class that interfaces with language models via OpenRouter.

    Manages conversation history, model configuration, and HTTP connection lifecycle.
    Supports both standard and streaming responses, and can be used as a context manager
    to ensure the HTTP client is properly closed after use.

    Attributes:
        url (str): The OpenRouter API base URL.
        main_model (str): The primary model used for generation.
        fallback_models (list[str]): Fallback models if the primary is unavailable.
        basic_prompt (str): Default user prompt when none is provided.
        init_sys_prompt (str): Default system prompt applied when no custom prompt is given.
    """

    # Base URL
    url = "https://openrouter.ai/api/v1"
    
    # Models to use and fallbacks
    main_model = "arcee-ai/trinity-large-preview:free"
    __fallback_models = ["deepseek/deepseek-r1-0528:free", "meta-llama/llama-3.3-70b-instruct:free"]

    # system and prompts
    basic_prompt = "Write a one paragraph story about a hero who goes on a journey, meets alies, gets stronger, finds weapons and treasure, and defeats the demon king."
    init_sys_prompt = "You are a master storyteller known for bestselling and critically acclaimed novels. Your writing is cinematic, emotionally immersive, and rich with atmosphere. \
                       Show, don’t tell. Use sensory detail, internal monologue, and layered description. Build tension naturally. Characters should feel psychologically real and complex. \
                        Avoid generic phrasing, shallow description, and mechanical structure."
    
    # All conversations
    __all_convo = {}

    def __init__(self, system_prompt:str=""):
        """
        Initializes the StoryMaker with default settings.

        The HTTP client is not created here. It is created lazily the first time
        generate() is called.

        Args:
            system_prompt (str): A custom system prompt to guide the model's behavior.
                If left empty, the default storytelling prompt is used.
        """

        # make sure some values are set.
        self.temp = 1
        self.max_tokens = 10000
        self.stream_result = False
        self.__preserve_convo = []

        if system_prompt == "":
            self.__preserve_convo.append({
                    "role": "system", 
                    "content": self.init_sys_prompt
                }
            )
        else:
            self.__preserve_convo.append({
                    "role": "system", 
                    "content": system_prompt
                }
            )


    def __create_client(self):
        """Creates and assigns the OpenAI HTTP client. Called lazily by generate()."""
        self.client = OpenAI(base_url=self.url, api_key=open_ai_key)


    def __chat(self):
        """
        Sends the current conversation to the model and appends the response to history.

        Handles the non-streaming mode.

        Returns:
            str: The complete response text from the model.
        """
        response = self.client.chat.completions.create(
            model=self.main_model, 
            messages=self.__preserve_convo,
            extra_body={
                "models": self.__fallback_models
            },
            max_tokens=self.max_tokens,
            stream=self.stream_result,
            temperature=self.temp
        )

        self.__preserve_convo.append({
                "role": "assistant", 
                "content": response.choices[0].message.content,
            }
        )
        return response.choices[0].message.content

        
    def __stream_chat(self):
        """
        Generator version of __chat() for streaming output.

        Makes the same API call as __chat() but always streams, yielding each
        text chunk as it arrives instead of printing it. After all chunks have
        been yielded, the complete response is appended to conversation history
        exactly like __chat() does, keeping the history consistent.

        Yields:
            str: Individual text chunks from the model as they arrive.
        """
        response = self.client.chat.completions.create(
            model=self.main_model,
            messages=self.__preserve_convo,
            extra_body={
                "models": self.__fallback_models
            },
            max_tokens=self.max_tokens,
            stream=True,                 # always stream in this path
            temperature=self.temp
        )

        complete_response = ""
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                complete_response += content
                yield content            # send chunk to the caller

        # Append the full assembled response to history once streaming is done
        self.__preserve_convo.append({
            "role": "assistant",
            "content": complete_response,
        })


    def stream_generate(self, prompt: str = ""):
        """
        Generator version of generate() that yields text chunks for streaming.

        Intended for use with Streamlit's st.write_stream() or any other caller
        that consumes a generator. Creates the HTTP client on first call if it
        does not already exist.

        Args:
            prompt (str): The story prompt to send to the model. If empty, the
                default basic_prompt is used.

        Yields:
            str: Individual text chunks from the model as they arrive.
        """
        if not hasattr(self, 'client'):
            self.__create_client()

        message = {"role": "user", "content": prompt if prompt else self.basic_prompt}
        self.__preserve_convo.append(message)

        # Delegate to __stream_chat() which handles the streaming loop
        yield from self.__stream_chat()


    def generate(self, prompt:str=""):
        """
        Generates a story from the model using a user-provided or default prompt.

        Creates the HTTP client on first call if it does not already exist.

        Args:
            prompt (str): The story prompt to send to the model. If empty, the
                default basic_prompt is used.

        Returns:
            str: The generated story text.
        """
        
        if not hasattr(self, 'client'):
            self.__create_client()
        
        # Initialize the prompt.
        message = {"role": "user", "content": prompt if prompt else self.basic_prompt}
        self.__preserve_convo.append(message)
        
        # chat with the model.
        model_response = self.__chat()

        return model_response


    def update(self, **kwargs):
        """
        Sends a follow-up request to update the previously generated story.

        Must be called after generate(). Accepts keyword arguments that are formatted
        into an update instruction for the model.

        Args:
            **kwargs: Arbitrary keyword arguments describing the desired updates
                (e.g., tone="darker", length="longer").

        Returns:
            str: The updated story text from the model.

        Raises:
            Exception: If generate() has not been called first.
        """
        if len(self.__preserve_convo) == 1:
            raise ValueError("Error: You need to run `generate()` first to get a basic story. Then run `update()` again to make updates to it.")

        # Make the message
        message = {"role":"user", "content": "Update the story you have created with the following parameters:\n"}
        for key, value in kwargs.items():
            message["content"] += f"{key}: {value}\n"
        self.__preserve_convo.append(message)
        
        # chat with the model.
        model_response = self.__chat()

        return model_response


    def get_convo_history(self, pretty:bool=False):
        """
        Returns the current conversation history.

        Args:
            pretty (bool): If False, returns a copy of the raw list of message
                dictionaries. If True, returns a human-readable formatted string
                with each message separated by a divider line.

        Returns:
            list[dict] | str: The conversation history as a list of dicts when
                pretty=False, or a formatted string when pretty=True.
        """
        if not pretty:
            return list(self.__preserve_convo)

        divider = "------------------------------------------"
        result = ""
        for message in self.__preserve_convo:
            result += f"{divider}\n"
            result += f"role: {message['role']}\n"
            result += f"content: {message['content']}\n"
        result += divider
        return result


    def turn_off_streaming(self):
        """Disables streaming mode. Model responses will be returned all at once."""
        self.stream_result = False
    

    def turn_on_streaming(self):
        """Enables streaming mode. Model responses will be printed to stdout in real time."""
        self.stream_result = True


    def change_temperature(self, temperature):
        """
        Sets the model's temperature for response generation.

        Args:
            temperature (float): Controls randomness. Higher values produce more varied
                output; lower values produce more focused output.
        """
        self.temp = temperature
    

    def change_max_tokens(self, new_max_tokens):
        """
        Sets the maximum number of tokens the model can generate per response.

        Args:
            new_max_tokens (int): The new token limit for model responses.
        """
        self.max_tokens = new_max_tokens


    def close(self):
        """Explicitly closes the underlying HTTP client and releases its connections.
        Clears preserved conversation with model to clear unused space.

        Does nothing if the client was never created.
        """
        if hasattr(self, 'client'):
            self.client.close()
        self.__preserve_convo.clear()
    

    def __del__(self):
        """Safety net to close the HTTP client when the object is garbage collected.
        Clears preserved conversation with model to clear unused space."""
        if hasattr(self, 'client'):
            self.client.close()
        self.__preserve_convo.clear()


    def __enter__(self):
        """Enables use as a context manager. Returns the StoryMaker instance."""
        return self


    def __exit__(self, _exc_type, _exc_val, _exc_tb):
        """Closes the HTTP client when exiting a context manager block. 
        Clears preserved conversation with model to clear unused space.

        Does nothing if the client was never created.
        """
        if hasattr(self, 'client'):
            self.client.close()
        self.__preserve_convo.clear()


    @classmethod
    def get_api_url(cls):
        """Returns the OpenRouter API base URL as a formatted string."""
        return f"Base url: {cls.url}"
    

    @classmethod
    def get_main_model(cls):
        """Returns the primary model name as a formatted string."""
        return f"Main model: {cls.main_model}"
    

    @classmethod
    def get_basic_prompt(cls):
        """Returns the default story prompt as a formatted string."""
        return f"If you do not specify a story prompt, you will get the following prompt:\n {cls.basic_prompt}"
    

    @classmethod
    def get_fallback_model(cls):
        """Returns a numbered list of fallback models as a formatted string."""
        fallback_str = "The following are fallback models in case the main model doesn't work:\n"
        for index, model in enumerate(cls.__fallback_models):
            fallback_str += f"({index}) {model}, \n"
        return fallback_str
