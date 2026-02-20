from dotenv import dotenv_values
from openai import OpenAI

class StoryMaker:

    url = "https://openrouter.ai/api/v1"
    __config = dotenv_values(".env")
    __open_ai_key = __config["OPENROUTER_API"]

    def __init__(self):
        self.client = OpenAI(base_url=self.url, api_key=self.__open_ai_key)
        self.main_model = "arcee-ai/trinity-large-preview:free"
        self.fallback_models = ["deepseek/deepseek-r1-0528:free", "meta-llama/llama-3.3-70b-instruct:free"]
        self.basic_prompt = "Write a paragraph length story about a hero who goes on a journey, meets alies, gets stronger, finds weapons and treasure, and defeats the demon king."

    def generate(self, prompt="", temp=1, stream_result=False, max_tokens=5000):
        if prompt == "":
            self.first_prompt = self.basic_prompt
        else:
            self.first_prompt = prompt

        pass

    def update(self):
        pass
