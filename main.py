from create_world.creator import create_scenario, create_storyline
from create_world.utils import load_txt, load_yaml
from create_character.personal_profile import generate_character_creation_questions, create_character_profile, parse_character_data_to_json
from play_game.main import play_game

def main():
  # Prepare world information
  world_summary_path = 'harrypotter_scenario/world_summary.txt'
  topic = 'harry potter'
  world_summary = load_txt(world_summary_path)
  config = load_yaml(path='create_world/prompt.yaml')
  scenario = create_scenario(topic, world_summary, config['create_scenario_prompt'], output_count=10)
  round_stories  = create_storyline(topic, scenario, config['create_storyline_prompt'])
  
  # Create Character
  with open(world_summary_path, "r", encoding="utf-8") as file:
    world_summary = file.read()
  questions = generate_character_creation_questions(world_summary)
  character_description = create_character_profile(questions)
  character_profile = parse_character_data_to_json(character_description)
  
  # Play Game
  play_game(round_stories, world_summary, character_profile)


if __name__ == "__main__":
  main()