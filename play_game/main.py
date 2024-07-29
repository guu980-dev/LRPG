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
    Effect should reduce or increase player status between (-10, 10) with reasonable amount from player's response.
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

      return {
        "effect": response_dict["effect"],
        "reason": response_dict["reason"]
      }
    except:
      continue


def create_bad_ending(world_summary, player_profile, player_status, entire_story, round_story, previous_conversation, round_result):
  llm = ChatUpstage()
  prompt_template = PromptTemplate.from_template(
    """
    Please answer in korean.
    You are best TRPG game master, and user is playing the game as a player with your guidance.
    The detailed information about the fictional universe of game is included in below Fictional Universe part.
    User played the game and reached the bad ending by previous decisions.
    Please create bad ending scenario based on previous conversation and previous round's result.
    Consider fictional universe, player profile, player status, entire story, this round story, this round result, and previous conversation.
    Bad ending story should be interesting and naturally connected to the previous conversation.
    Bad ending should be wrote in the tone of the game master.
    Bad ending should mention the reason why player reached the bad ending and make the story interesting.
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
  for round_idx, round_scenario in enumerate(game_scenario):
    # Display this round story
    round_story = f"{round_scenario["title"]} - {round_scenario["story"]}\n"
    round_description = create_round_description(world_summary, player_profile, player_status, entire_story, round_story, previous_conversation, previous_round_result)
    print(f"Round {round_idx+1}: {round_description}")

    # Get player's response
    player_response = input("Make your own decision. Answer in full sentence: ")
    conversation += f"Game Master: {round_description}\nPlayer: {player_response}\n"

    # Reflect the result and update player status
    round_effect, round_result_explanation = create_round_result(world_summary, player_profile, player_status, round_description, player_response)
    for key, value in round_effect.items():
      if player_status.get(key) is not None:
        player_status[key] += value

    # Check whether player lose the game
    if player_status["life"] <= 0 or player_status["money"] <= 0:
      bad_ending = create_bad_ending()
      print(bad_ending)
      return

    # Update previous conversation and round effect
    previous_conversation = conversation
    previous_round_result = formatter.to_round_result(round_effect, round_result_explanation)

  # Reach the good ending of the game
  good_ending = create_good_ending()
  print(good_ending)
  return