from langchain_upstage import ChatUpstage
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import ast, json
import formatter
import config


    # """
    # Please answer in korean.
    # You are best TRPG game master, and user is playing the game as a player with your guidance.
    # The detailed information about the fictional universe of game is included in below Fictional Universe part.
    # You should make round description which will be displayed to player that can explain this round story to make player understand the situation.
    # Round Description should include the main event of this round story.
    # Round Description should be finished with the question to player to make a decision for the next step.
    # Round Description should consider this round story, entire story, player profile, player status, previous conversation, and previous round effect.
    # Round Description should be interesting and naturally connected to the previous conversation, with long and detailed explanation of story.
    # Round Description should be wrote in the tone of the game master.
    # Round Description must start with explanation of player's previous round result and reason if below Previous Round Result section is not empty.
    # Round Description should reflect the player's previous choices and their effects on this round story, so it can include slightly different from this round story but follow the entire story in big picture.
    # ---
    # Fictional Universe: {world_summary}
    # ---
    # Player Profile: {player_profile}
    # ---
    # Player Status: {player_status}
    # ---
    # Entire Story: {entire_story}
    # ---
    # This Round Story: {round_story}
    # ---
    # Previous Conversation: {previous_conversation}
    # ---
    # Previous Round Result: {previous_round_result}
    # ---
    # Round Description:
    # """
    
def create_initial_conversation(world_summary, player_profile, player_status, entire_story):
  llm = ChatUpstage()
  prompt_template = PromptTemplate.from_template(
    """
    Please answer in korean.
    You are best TRPG game master, and user is playing the game as a player with your guidance.
    The detailed information about the fictional universe of game is included in below Fictional Universe part.
    Please explain the initial introduction which includes the greeting message as a game master and explanation of the universe and situation to make player understand the context.
    Introduction should include brief explanation of the story before the first round begins, but do not include the spoiler of the detailed entire story.
    Introduction should include explanation of the player's profile and status to make player understand the context.
    Introduction should include background knowledge of the fictional universe to make player understand the situation.
    Introduction should be wrote in the tone of the game master.
    ---
    Fictional Universe: {world_summary}
    ---
    Player Profile: {player_profile}
    ---
    Player Status: {player_status}
    ---
    Entire Story: {entire_story}
    ---
    Introduction:
    """
  )
  chain = prompt_template | llm | StrOutputParser()
  introduction = chain.invoke({ "world_summary": world_summary, "player_profile": player_profile, "player_status": player_status, "entire_story": entire_story })
  return introduction


    
def create_round_description(world_summary, player_profile, player_status, entire_story, round_story, previous_conversation, previous_round_result):
  llm = ChatUpstage()
  prompt_template = PromptTemplate.from_template(
    """
    Please answer in korean.
    You are best TRPG game master, and user is playing the game as a player with your guidance.
    The detailed information about the fictional universe of game is included in below Fictional Universe part.
    Please create round description which will be displayed to player that can explain this round story to make player understand the situation.
    Round Description should include the main event of this round story.
    Round Description should be finished with the question to player to make a decision for the next step.
    Round Description should consider this round story, entire story, player profile, player status, previous conversation, and previous round effect.
    Round Description should be interesting and naturally connected to the previous conversation, with long and detailed explanation of story.
    Round Description should be wrote in the tone of the game master.
    Round Description must start with explanation of player's previous round result and reason if below Previous Round Result section is not empty.
    Round Description should reflect the player's previous choices and their effects on this round story, so it can include slightly different from this round story but follow the entire story in big picture.
    Round Description should not give fixed choice with number.
    ---
    Fictional Universe: {world_summary}
    ---
    Player Profile: {player_profile}
    ---
    Player Status: {player_status}
    ---
    Entire Story: {entire_story}
    ---
    This Round Story: {round_story}
    ---
    Previous Conversation: {previous_conversation}
    ---
    Previous Round Result: {previous_round_result}
    ---
    Round Description:
    """
  )
  chain = prompt_template | llm | StrOutputParser()
  round_description = chain.invoke({ "world_summary": world_summary, "player_profile": player_profile, "player_status": player_status, "entire_story": entire_story, "round_story": round_story, "previous_conversation": previous_conversation, "previous_round_result": previous_round_result })
  return round_description


def create_round_result(world_summary, player_profile, player_status, round_description, player_response):
  llm = ChatUpstage()
  prompt_template = PromptTemplate.from_template(
    """
    Please answer in korean.
    You are best TRPG game master, and user is playing the game as a player with your guidance.
    The detailed information about the fictional universe of game is included in below Fictional Universe part.
    This round story is included in This Round Description part.
    Please create the effect from player's response from this round story, and reason to explain the effect.
    Effect should be calculated based on player response, player status, player profile, and round description.
    Effect should reduce or increase player status in range between (-10, 10) with reasonable amount from player response's action.
    Effect can be unexpected or different from player's intention to make the game more interesting.
    When unexpected effect is happened, reason should explain why the effect is happened based on player status and profile.
    Reason should explain why the effect is happened based on player response and round description.
    Reason should logically explain the amount of changes of player status.
    Reason should be wrote in the tone of the game master.
    Response should follow below format which is python dictionary consist of effect and reason.
    ---
    Fictional Universe: {world_summary}
    ---
    Player Profile: {player_profile}
    ---
    Player Status: {player_status}
    ---
    Round Description: {round_description}
    ---
    Player Response: {player_response}
    ---
    format:
    {{
      effect: {{
        life: integer of life amount change,
        money: integer of money amount change,
        stamina: integer of stamina amount change,
        intelligence: integer of intelligence amount change,
        combat_power: integer of combat power amount change,
        agility: integer of agility amount change,
      }}
      reason: "reason of the effect which is changes of player status based on player response and round description",
    }}
    ---
    """
  )
  chain = prompt_template | llm | StrOutputParser()
  
  while(True):
    try:
      response = chain.invoke({ "world_summary": world_summary, "player_profile": player_profile, "player_status": player_status, "round_description": round_description, "player_response": player_response })
      response_dict = json.loads(response)
      
      if response_dict.get('effect') == None or response_dict.get("reason") == None:
        raise Exception()

      return response_dict
    except:
      continue


def create_bad_ending(world_summary, player_profile, player_status, entire_story, round_story, previous_conversation, round_result):
  llm = ChatUpstage()
  prompt_template = PromptTemplate.from_template(
    """
    Please answer in korean.
    You are best TRPG game master, and user is playing the game as a player with your guidance.
    The detailed information about the fictional universe of game is included in below Fictional Universe part.
    Player played the game and reached the bad ending by previous decisions.
    Player reach bad ending when player status life or money is less or equal to 0.
    Please create bad ending scenario based on previous conversation and previous round's result.
    Consider fictional universe, player profile, player status, entire story, this round story, this round result, and previous conversation.
    Bad ending story should be interesting and naturally connected to the previous conversation.
    Bad ending should be wrote in the tone of the game master.
    Bad ending should mention the reason in story why player reached the bad ending and make the story interesting.
    Bad ending should mention the exact reason by telling player's status change.
    ---
    Fictional Universe: {world_summary}
    ---
    Player Profile: {player_profile}
    ---
    Player Status: {player_status}
    ---
    Entire Story: {entire_story}
    ---
    This Round Story: {round_story}
    ---
    This Round Result: {round_result}
    ---
    Previous Conversation: {previous_conversation}
    ---
    Bad Ending:
    """
  )
  chain = prompt_template | llm | StrOutputParser()
  bad_ending = chain.invoke({ "world_summary": world_summary, "player_profile": player_profile, "player_status": player_status, "entire_story": entire_story, "round_story": round_story, "round_result": round_result, "previous_conversation": previous_conversation })

  return bad_ending


def create_good_ending(world_summary, player_profile, player_status, entire_story, previous_conversation):
  llm = ChatUpstage()
  prompt_template = PromptTemplate.from_template(
    """
    Please answer in korean.
    You are best TRPG game master, and user is playing the game as a player with your guidance.
    The detailed information about the fictional universe of game is included in below Fictional Universe part.
    User played the game and reached the entire story's ending which means game win, so it's good ending.
    Please create good ending scenario based on previous conversation and entires story.
    
    Consider topic, content, user persona, entire story, and previous conversation to make the scenario.
    
    Good ending should be appropriate for the end of the story, which comprehensively organizes the entire story flow and the user's decisions.
    Good ending story should be interesting and naturally connected to the previous conversation.
    Good ending should be last part which finishes the game story and make user happy.
    Good ending should be wrote in the tone of the game master.
    ---
    Fictional Universe: {world_summary}
    ---
    Player Profile: {player_profile}
    ---
    Player Status: {player_status}
    ---
    Entire Story: {entire_story}
    ---
    Previous Conversation: {previous_conversation}
    ---
    Good Ending:
    """
  )
  chain = prompt_template | llm | StrOutputParser()
  good_ending = chain.invoke({ "world_summary": world_summary, "player_profile": player_profile, "player_status": player_status, "entire_story": entire_story, "previous_conversation": previous_conversation })

  return good_ending


def play_game(game_scenario, world_summary, player_profile):
  entire_story = [f"{idx+1}. {scenario["title"]}\n{scenario["story"]}\n\n" for idx, scenario in enumerate(game_scenario)]
  conversation = ""
  previous_conversation = ""
  previous_round_result = ""
  player_status = { "life": 10, "money": 10, **player_profile["params"] }
  player_profile_str = formatter.player_profile_to_str(player_profile)
  introduction = create_initial_conversation(world_summary, player_profile_str, player_status, entire_story)
  print(introduction)
  print('-----------------------------\n')
  for round_idx, round_scenario in enumerate(game_scenario):
    # Display this round story
    round_story = f"{round_idx+1}. {round_scenario["title"]}: {round_scenario["story"]}\n"
    round_description = create_round_description(world_summary, player_profile_str, player_status, entire_story, round_story, previous_conversation, previous_round_result)
    print(f"Round {round_idx+1}: {round_description}")

    # Get player's response
    player_response = input("당신만의 결정을 내려주세요! 하나의 문장으로 당신이 할 행동과 그에 대한 근거와 이유를 명확하게 설명해주세요: ")
    conversation += f"Game Master: {round_description}\nPlayer: {player_response}\n"

    # Reflect the result and update player status
    round_result = create_round_result(world_summary, player_profile_str, player_status, round_description, player_response)
    round_effect = round_result["effect"]
    round_result_explanation = round_result["reason"]  
    for key, value in round_effect.items():
      if player_status.get(key) is not None:
        player_status[key] += value

    # Update previous conversation and round effect
    previous_conversation = conversation
    previous_round_result = formatter.to_round_result(round_effect, round_result_explanation)

    # Check whether player lose the game
    if player_status["life"] <= 0 or player_status["money"] <= 0:
      bad_ending = create_bad_ending(world_summary, player_profile_str, player_status, entire_story, round_story, previous_conversation, previous_round_result)
      print(bad_ending)
      return



  # Reach the good ending of the game
  good_ending = create_good_ending(world_summary, player_profile_str, player_status, entire_story, previous_conversation)
  print(good_ending)
  return

if __name__ == "__main__":
  game_scenario = [
    {
      "title": "호그와트로의 초대",
      "story": "플레이어들은 각자 호그와트 마법학교로부터 편지를 받습니다. 편지에는 특별한 임무가 주어졌으며, 이 임무를 완수하면 마법사의 유산을 받을 수 있다는 내용이 적혀 있습니다. 호그와트에 도착한 플레이어들은 알버스 덤블도어 교수에게서 직접 임무의 첫 번째 단서를 받습니다. 첫 번째 임무는 금지된 숲에서 특별한 마법 생물을 찾아내는 것입니다. 이 생물은 마법사의 유산으로 가는 길을 알려주는 중요한 열쇠입니다."
    },
    {
      "title": "고대의 서적",
      "story": "첫 번째 단서에서 얻은 정보를 바탕으로 플레이어들은 호그와트 도서관의 금서 섹션에서 고대의 서적을 찾아야 합니다. 이 서적에는 마법사의 유산에 대한 중요한 정보가 담겨있습니다. 그러나 서적을 찾는 것은 쉽지 않습니다. 호그와트의 다양한 퍼즐과 함정을 풀어야 하며, 경쟁하는 다른 학생들과 마법 대결을 벌여야 할 수도 있습니다."
    },
    {
      "title": "비밀의 방",
      "story": "고대의 서적에서 얻은 단서로 플레이어들은 호그와트 내에 숨겨진 비밀의 방을 찾아야 합니다. 이 방은 마법사의 유산과 관련된 또 다른 단서를 가지고 있습니다. 비밀의 방에 들어가기 위해서는 호그와트의 역사를 깊이 이해해야 하며, 과거의 마법사들이 남긴 여러 가지 시험을 통과해야 합니다"
    },
    {
      "title": "시간의 미로",
      "story": "비밀의 방에서 얻은 단서는 플레이어들을 시간의 미로로 안내합니다. 시간의 미로는 마법으로 보호된 장소로, 과거와 현재가 교차하는 곳입니다. 플레이어들은 미로 속에서 과거의 중요한 사건들을 목격하고, 이를 통해 마법사의 유산에 대한 마지막 단서를 얻어야 합니다. 하지만 미로 속에는 강력한 적과 함정이 도사리고 있습니다."
    },
    {
      "title": "마법사의 유산",
      "story": "모든 단서를 모은 플레이어들은 마침내 마법사의 유산이 숨겨진 장소에 도착합니다. 이곳에서 최종 보스와의 결전이 벌어집니다. 보스를 물리치고 유산을 손에 넣기 위해서는 플레이어들의 모든 지혜와 용기가 필요합니다. 최종 결전을 승리한 후, 플레이어들은 마법사의 유산을 손에 넣고 각자의 길을 떠납니다."
    }
  ]
  world_summary = "이 TRPG의 세계관은 해리포터 시리즈의 마법 세계를 배경으로 합니다. 플레이어들은 호그와트 마법학교의 학생으로, 전설적인 마법사의 유산을 찾기 위한 특별한 임무를 받습니다. 이 세계는 마법, 신비로운 생물, 고대의 비밀, 그리고 위험이 가득한 곳으로, 플레이어들은 호그와트 내외의 다양한 장소를 탐험하며 퍼즐과 적들을 상대해야 합니다. 각 단계를 통해 마법사의 유산에 가까워지며, 그 과정에서 마법의 지식과 능력을 향상시키고 협동과 용기를 시험받게 됩니다. 이 시나리오는 플레이어들이 마법 세계의 깊은 비밀을 풀어가며, 자신의 잠재력을 발휘하는 흥미진진한 모험을 제공합니다."
  player_profile = {
    "name": "이현구",
    "gender": "male",
    "job": "마법사",
    "params": {
      "stamina": 34,
      "intelligence": 58,
      "combat_power": 45,
      "agility": 100
    }
  }
  play_game(game_scenario, world_summary, player_profile)