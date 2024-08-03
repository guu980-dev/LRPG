from create_world.creator import create_scenario, create_storyline
from create_world.utils import load_txt, load_yaml
from create_character.personal_profile import generate_character_creation_questions, create_character_profile, parse_character_data_to_json
from play_game.main import play_game

def main():
  print("LRPG 게임에 오신것을 환영합니다. 이곳에서 당신만의 세계 속, 당신만의 캐릭터로, 당신만의 선택을 통해 당신만의 이야기를 만들어가세요.")
  print('-----------------------------')
  
  # Prepare world information
  print("세게관 로딩중입니다... (해리포터)")
  world_summary_path = 'harrypotter_scenario/world_summary.txt'
  topic = 'harry potter'
  world_summary = load_txt(world_summary_path)
  config = load_yaml(path='create_world/prompt.yaml')
  scenario = create_scenario(topic, world_summary, config['create_scenario_prompt'], output_count=1)
  round_stories = create_storyline(topic, scenario[0], config['create_storyline_prompt'])
  print("세계가 만들어졌습니다!")
  print('-----------------------------')
  
  # Create Character
  print("다음은 게임에서 플레이할 당신의 캐릭터를 만들겠습니다")
  with open(world_summary_path, "r", encoding="utf-8") as file:
    world_summary = file.read()
  questions = generate_character_creation_questions(world_summary)
  character_description = create_character_profile(questions)
  character_profile = parse_character_data_to_json(character_description)
  print("캐릭터 생성이 완료되었습니다!")
  print("당신 캐릭터의 정보는 다음과 같습니다: ", character_profile)
  print('-----------------------------')
  
  # Play Game
  play_game(round_stories, world_summary, character_profile)


if __name__ == "__main__":
  main()