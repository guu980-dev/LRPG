from .generator import generate_chain
from .utils import load_yaml, load_txt
import ast

from langchain_core.output_parsers import JsonOutputParser, StrOutputParser


# def create_custom_world():
#     topic = input("세계의 이름을 알려 주세요: ")
#     world_story = input("""구현할 세계관과 룰을 소개하세요. ex)마법사의 세계:""")
#     world_summary =  generate_chain(prompt,
#                                     prompt_variable)
#     return topic, world_summary


def create_scenario(topic, context, prompt, output_count=5,language='한국어'):
    '''
    주어진 world_summary를 바탕으로 {output_count} 개의 scenario를 생성합니다.
    '''
    prompt_variable = {'topic':topic,
                       'output_count': output_count,
                       'context':context,
                       'language':language,}
    
    scenario = generate_chain(prompt,
                              prompt_variable)
    return scenario


def create_storyline(topic, context, prompt, output_count=5,language='한국어'):
    '''
    주어진 scenario를 바탕으로 세부적인 게임 storyline을 {output_count} 개의 원소로 가지는 파이썬 리스트로 생성합니다.
    '''
    prompt_variable = {'topic':topic,
                       'output_count': output_count,
                       'context':context,
                       'language':language,}

    while(True):
        try:
            storyline = generate_chain(prompt,
                                    prompt_variable,
                                    parser=StrOutputParser())
            storyline_list = ast.literal_eval(storyline)
            return storyline_list
        except:
            continue


if __name__ == '__main__':
    config = load_yaml(path='prompt.yaml')
    topic = 'harry potter'
    world_path = 'dummy/world_summary.txt'
    world_summary = load_txt(world_path)

    scenario = create_scenario(topic, world_summary, config['create_scenario_prompt'], output_count=10)
    print(scenario)
    print(create_storyline(topic, scenario, config['create_storyline_prompt']))

    

