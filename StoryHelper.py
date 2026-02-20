from StoryMaker import StoryMaker

class StoryHelper(StoryMaker):
    
    def __init__(self):
        super().__init__()
    
    def get_main_model(self):
        return self.main_model


if __name__ == "__main__":
    test = StoryHelper()
    print(test.get_main_model())