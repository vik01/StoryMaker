from StoryMaker import StoryMaker
from collections import namedtuple
from PIL import Image
import json
from pathlib import Path

# A lightweight, immutable record for a single story archetype.
# Being a namedtuple makes StoryRecord hashable, so instances can be used
# as dictionary keys or stored in sets — see app.py's generated_stories dict.
StoryRecord = namedtuple(
    'StoryRecord',
    ['id', 'protagonist', 'description', 'setting', 'plot', 'conflict', 'theme', 'point_of_view']
)

class StoryHelper(StoryMaker):

    def __init__(self):
        self.__story_path = Path("story_inputs")
        self.__image_path = self.__story_path / "posters"


    def __load_helpers(self):
        """Load story types from story_types.json into self.helpers as StoryRecord instances."""
        with open(self.__story_path / "story_types.json") as file:
            raw = json.load(file)
        self.helpers = [
            StoryRecord(
                id=story['id'],
                protagonist=story['characters']['protagonist'],
                description=story['characters']['description'],
                setting=story['setting'],
                plot=story['plot'],
                conflict=story['conflict'],
                theme=story['theme'],
                point_of_view=story['point_of_view'],
            )
            for story in raw
        ]


    def __load_system_prompts(self):
        """Load system prompts from story_system_prompts.json into self.system_prompt."""
        with open(self.__story_path / "story_system_prompts.json") as file:
            self.system_prompt = json.load(file)


    def __check_attr(self, attribute):
        """
        Lazily load data only when it is first accessed.

        Args:
            attribute (str): Either "helpers" or "system_prompt". If the
                corresponding instance attribute does not yet exist, the
                matching private loader method is called to populate it.
        """
        if attribute == "helpers":
            if not hasattr(self, 'helpers'):
                self.__load_helpers()
        elif attribute == "system_prompt":
            if not hasattr(self, 'system_prompt'):
                self.__load_system_prompts()


    def get_helper_story(self, story_id: int) -> dict:
        """
        Return a single story type dict by its 1-based ID.

        Args:
            story_id (int): The 1-based ID of the story (matches the "id" field
                in story_types.json).

        Returns:
            dict: The story type entry for the given ID.
        """
        self.__check_attr("helpers")
        return self.helpers[story_id - 1]


    def get_helper_prompts(self, prompt_id: int) -> dict:
        """
        Return a single system prompt dict by its 1-based ID.

        Args:
            prompt_id (int): The 1-based ID of the system prompt (matches the
                "prompt_id" field in story_system_prompts.json).

        Returns:
            dict: The system prompt entry for the given ID.
        """
        self.__check_attr("system_prompt")
        return self.system_prompt[prompt_id - 1]


    def get_helper_image(self, story_id: int, hero_type: str):
        """
        Load and return the poster image for a given story.

        Builds the file path from the zero-padded story ID and the protagonist
        name (spaces replaced with underscores), then attempts to open it with
        Pillow.

        Args:
            story_id (int): The numeric story ID. Values below 10 are
                zero-padded automatically (e.g. 3 → "03").
            hero_type (str): The protagonist name as it appears in the JSON
                (e.g. "The Reluctant Hero"). Spaces are converted to underscores
                to match the filename convention.

        Returns:
            PIL.Image.Image: The opened image on success.
            str: An error message ("File not found." or "Cannot open the image.")
                if the file is missing or cannot be read.
        """
        id = f"0{story_id}" if story_id < 10 else str(story_id)
        image = self.__image_path / f"{id}_{hero_type.replace(' ', '_')}.jpg"
        try:
            helper_img = Image.open(image)
            return helper_img
        except FileNotFoundError:
            return "File not found."
        except IOError:
            return "Cannot open the image."


    def get_all_helpers(self, ids: list) -> list:
        """
        Return story type dicts for a list of 0-based indices.

        Args:
            ids (list): A list of 0-based indices into the story types list.

        Returns:
            list: The matching story type dicts.
        """
        self.__check_attr("helpers")
        return [self.helpers[i] for i in ids]


    def get_all_system_prompts(self) -> list:
        """
        Return all system prompt dicts.

        Returns:
            list: Every entry from story_system_prompts.json.
        """
        self.__check_attr("system_prompt")
        return self.system_prompt


    def generate_story(self, system_prompt: str, *args):
        """
        Initialize StoryMaker with a system prompt and generate a story.

        Calling super().__init__() here (rather than in StoryHelper.__init__)
        lets us inject the user-selected system prompt at generation time.
        Each call starts a fresh StoryMaker conversation, so successive calls
        are independent of one another.

        Args:
            system_prompt (str): The full system prompt text to pass to
                StoryMaker (e.g. the "system_prompt" field from a prompt dict).
            *args: Story detail strings passed in from the Streamlit app,
                expected in this order:
                    protagonist, description, setting, plot,
                    conflict, theme, point_of_view
                These are assembled into a structured prompt for the model.

        Returns:
            str: The generated story text from StoryMaker.
        """
        # Re-initialize StoryMaker fresh with the chosen system prompt.
        # stream_generate() handles streaming internally, so turn_on_streaming()
        # is not needed here.
        super().__init__(system_prompt)

        # Assemble the story fields into a structured prompt for the model.
        # The labels match the order the Streamlit app passes the args.
        labels = [
            "Protagonist", "Description", "Setting",
            "Plot", "Conflict", "Theme", "Point of View"
        ]
        prompt_lines = ["Write a story with the following details:"]
        for label, value in zip(labels, args):
            prompt_lines.append(f"- {label}: {value}")
        prompt = "\n".join(prompt_lines)

        # yield from turns generate_story() into a generator, so the caller
        # (e.g. st.write_stream) receives chunks as they arrive from the model.
        yield from self.stream_generate(prompt)


    def close_instance(self):
        """Calls the close function to close the HTTP client and delete loaded JSON data from memory to free unused space."""
        self.close()
        if hasattr(self, 'helpers'):
            del self.helpers
            
        if hasattr(self, 'system_prompt'):
            del self.system_prompt