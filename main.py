from StoryMaker import StoryMaker
from StoryHelper import StoryHelper
import argparse
import functools
from pathlib import Path

# Global variable parser.
parser = argparse.ArgumentParser()

def ensure_files(files):
    story_path   = Path(files[0]) / files[1]
    history_path = Path(files[2]) / files[3]

    if not story_path.exists():
        raise FileNotFoundError("Story file not found. Please check the path or create the story.")

    if not history_path.exists():
        raise FileNotFoundError("History file not found. Please check the path or create the story.")

    return story_path, history_path

# Depending on the argument, we do specific things.
parser.add_argument("--files", nargs=4, type=str, help = "story_folder story_file  history_folder history_file", required=True)

# Create the list of arguments. 
args = parser.parse_args()

def get_conversation_storyMaker(func):
    @functools.wraps(func)
    def wrapper(story:StoryMaker, pretty:bool=True):
        history = story.get_convo_history(pretty)
        func(story)
        return history
    return wrapper

def generate_storyMaker(story:StoryMaker, prompt:str=""):
    return story.generate(prompt)

def update_storyMaker(story:StoryMaker, **updates):
    return story.update(**updates)

@get_conversation_storyMaker
def close_storyMaker(story:StoryMaker):
    story.close()

def check_correct(question, answer):
    if question == "System Prompt" or question == "Generate":
        if answer == 'd':
            return True
        
        if len(answer) < 50 and answer != "d":
            return False
        else:
            return True 
    if question == "Question" or question == "New_Story":
        if answer not in ["1", "2"]:
            return False
        else:
            return True


def ask(qn:str, err:str, err_check_type:str):
    ans = input(qn + "\n Answer:")
    while not check_correct(err_check_type, ans):
        print(err)
        ans = input(qn + "\n Answer:")
    return ans


def main():
    story_path, history_path = ensure_files(args.files)

    # Initial prints
    print(f"Welcome to StoryMaker!")
    print("Lets help you build your story!")
    print("--------------------------------------------------------------------------------")

    # set break condition for while loop
    # 0 means keep going.
    # 1 is break from the next loop
    condition_num = 0

    while condition_num != 1:
        # Initialize system prompt and make sure it follows order.
        sys_prompt = ask(
            qn="Do you have your own system prompt or do you want to use the default (d for default else type your answer).",
            err="Please enter 'd' or a system prompt that is descriptive!",
            err_check_type="System Prompt"
        )            
        print("Perfect! You have chosen the system prompt:") 
        if sys_prompt == "d":
            print(StoryMaker.get_default_system_prompt())
            story_maker = StoryMaker()
        else:
            print(sys_prompt)
            story_maker = StoryMaker(sys_prompt)
        print("---------------------")
        
        # Build out generator prompt
        print("Now here is a menu, please select from the options!")
        ask_to_do = ask(
            qn="1. Generate new prompt.\n2. Close.",
            err="Please only input either a 1, or 2. Thank you!",
            err_check_type="Question"
        )

        if ask_to_do == "2":
            condition_num = 1
            print("Thank you! Enjoy your day!")
            print("---------------------")

        elif ask_to_do == "1":
            print("You have selected to generate a new prompt!")
            print("---------------------")
            
            prompt = ask(
                qn="Do you want to select the default prompt or wrote your own (d for default else type your answer).",
                err="Please enter 'd' or a prompt that is descriptive!",
                err_check_type="Generate"
            )

            if prompt == "d":
                print("Your prompt is:")
                print(StoryMaker.get_basic_prompt())  
                prompt = ""           
            else:
                print("Your prompt is:")
                print(prompt)
            
            print("---------------------")
            print("Please wait, your prompt is being created.")
            initial_story = generate_storyMaker(story_maker, prompt)    
            print("You story is here:")
            print(initial_story)  
            print("---------------------")
            print("Now we will save your files and conversation history to the drive.")
            conversation = close_storyMaker(story_maker, pretty=True)
            
            # story file
            with story_path.open("a") as f:
                f.write(initial_story)
                f.write("")

            # history file
            with history_path.open("a") as f:
                f.write(conversation)
                f.write("")

            save_it = ask(
                qn="You have now created the story, and saved it. Would you like to continue to make a new story or exit:\n1. Make new story.\n2. Exit.",
                err="Please select only 1 or 2.",
                err_check_type="New_Story"
            ) 

            if save_it == "2":
                condition_num = 1
                print("Thank you! Enjoy your day!")
                print("---------------------")
            else:
                print("You have selected to continue. Lets go forward!")
                print("--------------------------------------------------------------------------------")


if __name__ == "__main__":
    main()
