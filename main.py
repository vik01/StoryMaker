from StoryMaker import StoryMaker
from StoryHelper import StoryHelper
import argparse

# Global variable parser.
parser = argparse.ArgumentParser()

# Depending on the argument, we do specific things.
parser.add_argument("--outline", action= "store_true", help= "Default will be for Exercise 2. But if you specify this argument, it will be Exercise 3.")

# Create the list of arguments. 
args = parser.parse_args()

def main():
    print(StoryMaker.get_api_url())
    print(StoryMaker.get_basic_prompt())
    print(StoryMaker.get_main_model())
    print(StoryMaker.get_fallback_model())
    pass


if __name__ == "__main__":
    main()
