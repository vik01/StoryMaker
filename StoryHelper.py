from StoryMaker import StoryMaker
from PIL import Image
import json

class StoryHelper(StoryMaker):

    # paths
    __story_path = "story_inputs"
    __image_path = f"{__story_path}/posters"
    
    def __init__(self):
        super().__init__()


    def __load_helpers(self):
        with open(f"{self.__story_path}/story_types.json") as file:
            self.helpers = json.load(file)

    
    def __load_system_prompts(self):
        with open(f"{self.__story_path}/story_system_prompts.json") as file:
            self.system_prompt = json.load(file)


    def __check_attr(self, attribute):
        if attribute == "helpers":
            if not hasattr(self, 'helpers'):
                self.__load_helpers()
        elif attribute == "system_prompt":
            if not hasattr(self, 'system_prompt'):
                self.__load_system_prompts()


    def get_helper_story(self, story_id:int):
        self.__check_attr("helpers")
        return self.helpers[story_id-1]


    def get_helper_prompts(self, prompt_id:int):
        self.__check_attr("system_prompt")
        return self.system_prompt[prompt_id-1]
        

    def get_helper_image(self, story_id:int, hero_type:str):
        id = f"0{story_id}" if story_id < 10 else str(story_id)
        image = f"{self.__image_path}/{id}_{hero_type.replace(" ", "_")}.jpg"
        try:
            helper_img = Image.open(image)
            return helper_img
        except FileNotFoundError:
            return "File not found."
        except IOError:
            return "Cannot open the image."


    def get_all_helpers(self, ids:list=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]):
        self.__check_attr("helpers")
        if len(ids) == 10:
            return self.helpers
        else:
            return self.helpers[ids]
    
    def get_all_system_prompts(self):
        self.__check_attr("system_prompt")
        return self.system_prompt


    def close(self):
        del self.helpers, self.system_prompt



if __name__ == "__main__":
    test = StoryHelper()
    test.get_all_helpers()