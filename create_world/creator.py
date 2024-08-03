from .generator import generate_chain
from .utils import load_yaml, load_txt, save_json
import ast

from langchain_core.output_parsers import StrOutputParser


def create_custom_world(prompt, language='한국어', save=False):
    '''
    config: prompt.yaml
    prompt = config['create_custom_world_prompt']

    User가 직접 topic을 정하고, world_story를 입력합니다. 게임의 전반적인 세계관과 게임의 룰을 정합니다.
    
    ex) 
    topic: 해리 포터
    world_story: 해리 포터 세계는 마법사들의 세계입니다. 
    빗자루를 타고 날아다니며, 신기한 마법 생물 그리핀, 피닉스 등이 있습니다. 
    어둠의 세력과 맞서 싸우세요.
    '''
    topic = input("세계관 주제를 알려 주세요 ex)마법사 세계, 우주 전쟁: ")
    world_story = input("구체적인 세계관 설명과 룰을 소개하세요: ")
    prompt_variable = {'topic':topic,
                       'context':world_story,
                       'language':language,}
    
    world_summary =  generate_chain(prompt, prompt_variable)

    if save == True:
        save_json(topic + '_world.json', {'topic':topic, 'world_summary':world_summary})

    return topic, world_summary


def create_scenario(topic, context, prompt, output_count=5, language='한국어', save=False):
    '''
    config: prompt.yaml
    prompt = config['create_scenario_prompt']

    주어진 world_summary를 바탕으로 {output_count} 개의 scenario를 생성합니다.
    '''
    prompt_variable = {'topic':topic,
                       'output_count':output_count,
                       'context':context,
                       'language':language,}
    
    scenario = generate_chain(prompt,
                              prompt_variable)

    while(True):
        try:
            storyline = generate_chain(prompt,
                                    prompt_variable,
                                    parser=StrOutputParser())
            scenario = ast.literal_eval(storyline)

            if save == True:
                prompt_variable['scenario'] = scenario
                save_json(str(topic) + '_scenario.json', prompt_variable)

            return scenario
        except:
            continue


def create_storyline(topic, context, prompt, output_count=5, language='한국어', save=False):
    '''
    config: prompt.yaml
    prompt = config['create_storyline_prompt']
    
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
            if save== True:
                prompt_variable['scenario'] = context
                prompt_variable['story_line'] = storyline_list
                save_json(str(topic) + str('story_line') +'.json', prompt_variable)

            return storyline_list
        except:
            continue
            

if __name__ == '__main__':
    config = load_yaml(path='prompt.yaml')
    create_new_world = True
    save = True

    if create_new_world:
        topic, world_summary = create_custom_world(config['create_custom_world_prompt'], save=save)

    else:
        topic = 'harry potter'
        world_summary = load_txt('dummy/world_summary.txt')

    print(world_summary)
    scenario = create_scenario(topic, world_summary, config['create_scenario_prompt'], output_count=1, save=save)
    print(scenario)
    print(create_storyline(topic, scenario[0], config['create_storyline_prompt'], save=save))

    

