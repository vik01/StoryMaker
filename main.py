from StoryMaker import StoryMaker
from StoryHelper import StoryHelper
import argparse
import functools
import json
import os

# Global variable parser.
parser = argparse.ArgumentParser()

def ensure_story(story):
    if story not in ["StoryMaker", "StoryHelper"]:
        raise argparse.ArgumentTypeError("The value for --build should be either StoryHelper or StoryMaker. If no value is specified, default will be StoryMaker.")
    return story

def ensure_history(history):
    if history not in ["true", "false"]:
        raise argparse.ArgumentTypeError("The value for --history should be either true or false. If no value is specified, default will be true.")
    return history

# Depending on the argument, we do specific things.
parser.add_argument("--build", default="StoryMaker", help= "Build a story either using the StoryHelper or StoryMaker.", type=ensure_story)
parser.add_argument("--history", 
                    default="true", 
                    help="""Specified only when you want to output the history of your conversation with the model. 
                            Only accepts 2 values, true and false. Default is true.""", 
                    type=ensure_history
) 

# Create the list of arguments. 
args = parser.parse_args()

def get_conversation_storyMaker(func):
    @functools.wraps(func)
    def wrapper(story:StoryMaker, pretty:bool=True):
        history = story.get_convo_history(pretty)
        func(story)
        return history
    return wrapper

def generate_storyMaker(story:StoryMaker):
    return story.generate()

def update_storyMaker(story:StoryMaker, **updates):
    return story.update(**updates)

@get_conversation_storyMaker
def close_storyMaker(story:StoryMaker):
    story.close()


def main():
    if args.build == "StoryMaker":
        story_maker = StoryMaker()

        initial_story = generate_storyMaker(story_maker)
        print(initial_story)

        updated_story = update_storyMaker(
            story_maker,
            new_format="short story format with multiple paragraphs",
            characters="provide more information on each character; their age, their motives, a bit of backstory, their combat specialty, etc.",
            pov="narrator third person",
            structure="freytag's pyramid",
            enemy="Give the demon king strength, explain the fight between the hero party and the demon king (with his minions)"
        )
        with open("outputs/updated_story.txt", "w") as st:
            st.write(updated_story)

        conversation = close_storyMaker(story_maker, pretty=False)

        if args.history == "true":
            os.makedirs("outputs", exist_ok=True)
            with open("outputs/first_convo.json", "w", encoding="utf-8") as f:
                json.dump(conversation, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
