from create_world.creator import generate_chain
from create_world.utils import save_json

from tutle_game_prompt import sys_prompt, game_prompt

from langchain_upstage import ChatUpstage

import ast

from dotenv import load_dotenv
load_dotenv()


def create_tutle_game_scenario(llm=ChatUpstage()):
    prompt = sys_prompt
    while(True):
        try:
            storyline = generate_chain(prompt, prompt_variable={}, llm=llm)
            storyline_dict= ast.literal_eval(storyline)
            return storyline_dict
        except:
            continue
    

def tutle_game_qa(question, storyline_dict, llm):
    prompt = game_prompt
    prompt_variable = {'question': question,
                        'game_story' :storyline_dict['game_story'],
                        'game_answer':storyline_dict['game_answer']}
    
    return generate_chain(prompt, prompt_variable, llm =llm)


if __name__ == '__main__':
    story_dict = create_tutle_game_scenario()
    print(story_dict)
    chance = 1

    for i in range(chance):
        question = input('질문을 입력하세요 :')
        tutle_game_qa(question, story_dict)
