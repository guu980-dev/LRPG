import conversation as cs

def test_user_person_creation(topic, language):
  user_persona_answer = None
  previous_conversation = None
  
  for i in range(2):
    question = cs.make_user_persona(topic, user_persona_answer, previous_conversation, language)
    if i == 0:
      previous_conversation = f"Host: {question['response']}"
    else:
      previous_conversation = f"{previous_conversation}\nHost: {question['response']}\n"

    print(question["response"])
    user_persona_answer = input("Enter your answer: ")
    previous_conversation =  f"{previous_conversation}\nUser: {user_persona_answer}\nHost: "

    # if i == 4:
    if i == 1:
      user_persona = cs.summarize_user_persona(topic, previous_conversation, language)["response"]
      
  print("User Persona: ", user_persona)
  return user_persona
  

def test_create_scenario(topic, user_persona, language):
  result = cs.create_scenario(topic, user_persona, language)
  response = result["response"]
  print("Scenario Response:  ", response)
  print("Scenarios: ", result["scenarios"])
  return result["scenarios"], result["entire_story"]


def main():
  topic = 'harry potter'
  # topic = 'star wars'
  language = 'korean'
  # user_persona = test_user_person_creation(topic, language)
  user_persona = "이현구님은 슬리데린 가문의 마법사로, 야심차고 교활하며, 자기통제력이 강한 성격을 가지고 있습니다. 또한, 전략적이고 계산적인 면모를 가지고 있으며, 목표를 달성하기 위해 노력하는 모습을 보입니다."
  scenarios, entire_story = test_create_scenario(topic, user_persona, language)
  
  conversation = ""
  choice_result = ""
  total_choices = ""
  life = 10
  money = 10
  for i in range(len(scenarios)):
    this_round_story = f"{i}. {scenarios[i]["title"]}\n{scenarios[i]["story"]}\n\n"
    game_result = cs.play_game(topic, user_persona, language, entire_story, this_round_story, conversation, choice_result)
    print(f"{i+1}th Game Response: ", game_result["response"])
    selectable_choices = game_result["user_choices"]
    
    print(f"Round{i+1}: ", game_result["round_content"])
    print(f"Choices:\n", '\n'.join([f"{_choice_idx+1}: {choice}" for _choice_idx, choice in enumerate(selectable_choices)]))
    choice_idx = int(input(f"Select your choice_idx(1~{len(selectable_choices)}): "))
    choice_effect = game_result["choice_effects"][choice_idx-1]
    life_change = choice_effect["life"]
    money_change = choice_effect["money"]
    life += life_change
    money += money_change
    conversation += f"호스트: {game_result["round_content"]}\n플레이어: {game_result["user_choices"][choice_idx-1]}\n"
    choice_result = f"생명 포인트가 {str(life_change)+" 증가했습니다." if life_change >= 0 else str(life_change*(-1))+" 감소했습니다."}, 돈: {str(money_change)+" 증가했습니다." if money_change >= 0 else str(money_change*(-1))+" 감소했습니다."}\n"
    
    print("Conversation: ", conversation)
    print("Changed Life: ", life)
    print("Changed Money: ", money)
    print("Choice Result: ", choice_result)
    
    if life <= 0:
      choice_result += f" 그 결과 생명 포인트가 {life}으로 떨어져 게임이 종료되었습니다"
      bad_ending_scenario = cs.generate_bad_end(language, topic, user_persona, conversation, choice_result)["response"]
      print("Bad Ending Scenario: ", bad_ending_scenario)
      return
    if money <= 0:
      choice_result += f" 그 결과 소지한 돈이 {money}으로 떨어져 게임이 종료되었습니다"
      bad_ending_scenario = cs.generate_bad_end(language, topic, user_persona, conversation, choice_result)["response"]
      print("Bad Ending Scenario: ", bad_ending_scenario)
      return

  good_ending_scenario = cs.generate_good_end(language, topic, user_persona, entire_story, conversation)["response"]
  print("Good Ending Scenario: ", good_ending_scenario)
  return

if __name__ == "__main__":
  main()