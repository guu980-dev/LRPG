from langchain_chroma import Chroma
from langchain_upstage import UpstageEmbeddings
from langchain.docstore.document import Document
from langchain_core.prompts import PromptTemplate
from langchain_upstage import ChatUpstage
import os
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from generate_image import generate_image, download_image
import requests
from IPython.display import display, Image
from langchain_community.vectorstores.oraclevs import OracleVS
import oracledb
from langchain_community.vectorstores.utils import DistanceStrategy
import ast, json


dotenv_path = os.path.join(os.path.dirname(__file__), '.env') # Path to the .env file
load_dotenv(dotenv_path) # Load the environment variables from the .env file


def get_context(invoke_text, topic):
  username=os.environ["DB_USER"]
  password=os.environ["DB_PASSWORD"]
  dsn=os.environ["DSN"]
  con = oracledb.connect(user=username, password=password, dsn=dsn)
  try: 
    conn23c = oracledb.connect(user=username, password=password, dsn=dsn)
    print("Connection successful!", conn23c.version)
  except Exception as e:
    print("Connection failed!")
    
  upstage_embeddings = UpstageEmbeddings(model="solar-embedding-1-large")
  vector_store = OracleVS(client=conn23c, 
                          embedding_function=upstage_embeddings, 
                          table_name=f"text_embeddings_{topic}",
                          distance_strategy=DistanceStrategy.DOT_PRODUCT)
  retriever = vector_store.as_retriever()
  return retriever.invoke(invoke_text)


def make_user_persona(topic, user_answer, previous_conversation, language):
  llm = ChatUpstage()
  default_template = """
    Please answer in {language}.
    You are best TRPG host with {topic}. And user is playing game with you.
    The detailed information about the fictional universe of game is included in context.
    Please answer in a exciting tone as a host.
    Before starting the game, user wants to create a persona.
    Please provide 1 question to user to create a persona.
    You must make only one question per response.
    Each question should be related to user's character, such as name, gender, personality or any related features with the topic.
    When asking questions, please consider the topic and make the question interesting.
    You should consider previous conversation to prevent asking same questions, and make the diverse and context related questions.
    First question should include the introduction of the game.
    ---
    Context: {context}
    ---
    Previous Conversation: {previous_conversation}
  """

  prompt_template = PromptTemplate.from_template(default_template)
  chain = prompt_template | llm | StrOutputParser()
  # context = get_context(f"What is related information about {topic}?")
  context = ""

  response = chain.invoke({ "context": context, "topic": topic, "language": language, "previous_conversation": previous_conversation if previous_conversation else None })

  return {
    "response": response,
  }


# topic="HarryPotter", "Trump"
def summarize_user_persona(topic, previous_conversation, language):
  llm = ChatUpstage()
  default_template = """
    Please answer in {language}.
    You are best {topic} TRPG host, and user is playing game with you.
    The detailed information about the fictional universe of game is included in context.
    Please answer in a exciting tone as a host.
    Before starting the game, user wants to create a persona.
    You have finished asking questions to user to create a persona and it's included in the previous conversation.
    Please summarize the character's information and make the user's persona.
    Response will be used for context in game scenario so answer in appropriate format.
    Length of persona should not be too long or too short.
    Do not include any other information or rhetoric except user's persona.
    ---
    Context: {context}
    ---
    Previous Conversation: {previous_conversation}
    ---
    Summarized User Persona: 
  """

  prompt_template = PromptTemplate.from_template(default_template)
  chain = prompt_template | llm | StrOutputParser()
  # context = get_context(f"What is related information about {topic}?")
  context = ""

  response = chain.invoke({ "context": context, "topic": topic, "language": language, "previous_conversation": previous_conversation })
  response = response.replace("User Persona:", "게임을 진행하는 플레이어는 다음과 같은 캐릭터를 가지고 있습니다.")

  return {
    "response": response,
  }

def initialize_chat(topic, language):
  llm = ChatUpstage()
  prompt_template = PromptTemplate.from_template(
    """
    Please answer in {language} language.
    You are best D&D host. And user is playing D&D game with you.
    Please answer in a exciting tone as a host.
    User has to make choices in the game.
    User has 10 life points and 10 gold coins.
    Please make scenario of most interesting event from the following context, and provide diverse choices which user can select.
    For each round, you should provide at least 3 choices and total round should be less than 50.
    You should explain situation and choices in detail.
    If someone's conversation is included in the scenario, please express it in colloquial terms that fit the person's character as much as possible.
    Choices should be diverse and interesting, and each choice will reduce or increase user's life points or gold coins.
    If user make appropriate decision, user's life points or gold coins will increase.
    If user make inappropriate decision, user's life points or gold coins will decrease and decreasing amount should not be larger than amount of user owned.
    If the user choice is not included in suggestion, please ask him again to choose from the possible options.
    You should consider previous conversation and context to make the scenario.
    If user's life points or gold coins are less than 0, user will lose the game and get bad ending.
    Also when total round is more than 50, user will lose the game and get bad ending.
    If user's life points or gold coins are more than 20, user will win the game and get good ending.
    This is the first round of the game. Please provide the scenario and choices for the user.
    ---
    Context: {context}
    """
  )
  chain = prompt_template | llm | StrOutputParser()
  context = get_context(f"What is related information about {topic}?")

  response = chain.invoke({ "context": context, "language": language })

  return {
    "response": response,
    "previous_conversation": f"Host: {response}"
  }

def make_conversation(user_choice, previous_conversation, user_persona, language):
  llm = ChatUpstage()
  prompt_template = PromptTemplate.from_template(
    """
    Please answer in {language} language.
    You are best D&D host. And user is playing D&D game with you.
    Please answer in a exciting tone as a host.
    User has to make choices in the game.
    User has 10 life points and 10 gold coins.
    Please make scenario of most interesting event from the following context, and provide diverse choices which user can select.
    For each round, you should provide at least 3 choices and total round should be less than 50.
    You should explain situation and choices in detail.
    If someone's conversation is included in the scenario, please express it in colloquial terms that fit the person's character as much as possible.
    Choices should be diverse and interesting, and each choice will reduce or increase user's life points or gold coins.
    If user make appropriate decision, user's life points or gold coins will increase.
    If user make inappropriate decision, user's life points or gold coins will decrease and decreasing amount should not be larger than amount of user owned.
    When user select a choice, you should provide the result of the choice, but you should not show result before user select the choice.
    If the user choice is not included in suggestion, please ask him again to choose from the possible options.
    You should consider user's persona, previous conversation and context to make the scenario.
    If user's life points or gold coins are less than 0, user will lose the game and get bad ending and print <<END>> on last.
    Also when total round is more than 50, user will lose the game and get bad ending and print <<END>> on last.
    If user's life points or gold coins are more than 20, user will win the game and get good ending and print <<END>> on last.
    ---
    User Choice: {user_choice}
    ---
    Previous Conversation: {previous_conversation}
    ---
    Context: {context}
    ---
    User Persona: {user_persona}
    """
  )
  chain = prompt_template | llm | StrOutputParser()
  context = get_context(f"What is related information about {user_choice}?")

  response = chain.invoke({ "user_choice": user_choice, "previous_conversation": previous_conversation, "context": context, "user_persona": user_persona, "language": language })

  return {
    "response": response,
    "is_last": response.find("<<END>>") == -1,
    "previous_conversation": f"{previous_conversation}\nUser: {user_choice}\nHost: {response}"
  }


  # prompt_template = PromptTemplate.from_template(
  #   """
  #   Please answer in {language}.
  #   You are best {topic} TRPG host, and user is playing game with you.
  #   The detailed information about the fictional universe of game is included in context.
  #   Please create a scenario with an interesting story and ending, with 5 rounds.
  #   Each round should include an interesting event and allow the user to move on with the appropriate choice for that step.
  #   Scenario should be related to fictional universe and user's persona.
  #   Response format should follow the below format.
  #   ---
  #   Context: {context}
  #   ---
  #   User Persona: {user_persona}
  #   ---
  #   Format:
  #   1: [주요 이벤트 1의 제목]
  #   [주요 이벤트 1의 줄거리] <END>
  #   2: [주요 이벤트 2의 제목]
  #   [주요 이벤트 2의 줄거리] <END>
  #   3: [주요 이벤트 3의 제목]
  #   [주요 이벤트 3의 줄거리] <END>
  #   4: [주요 이벤트 4의 제목]
  #   [주요 이벤트 4의 줄거리] <END>
  #   5: [주요 이벤트 5의 제목]
  #   [주요 이벤트 5의 줄거리] <END>
  #   ---
  #   Scenario:
  #   1.
  #   2.
  #   3.
  #   4.
  #   5.
  #   """
  # )
def create_scenario(topic, user_persona, language):
  llm = ChatUpstage()
  prompt_template = PromptTemplate.from_template(
    """
    Please answer in {language}.
    You are best {topic} TRPG host, and user is playing game with you.
    The detailed information about the fictional universe of game is included in context.
    Please create a scenario with an interesting story and ending, with 5 rounds.
    Each round should include an interesting event and allow the user to move on with the appropriate choice for that step.
    Scenario should be related to fictional universe and user's persona.
    Response should be python list of 5 json element with "title" and "story".
    ---
    Context: {context}
    ---
    User Persona: {user_persona}
    ---
    Scenario:
    """
  )
  chain = prompt_template | llm | StrOutputParser()
  # context = get_context(f"What is related information about {user_choice}?")
  context = ""

  while(True):
    try:
      response = chain.invoke({ "topic": topic, "context": context, "user_persona": user_persona, "language": language })
      scenarios = ast.literal_eval(response)
      entire_story = [f"{idx}. {scenario["title"]}\n{scenario["story"]}\n\n" for idx, scenario in enumerate(scenarios)]
      
      return {
        "response": response,
        "scenarios": scenarios,
        "entire_story": entire_story,
      }
    except:
      continue


# ""
#     Please answer in {language}.
#     You are best {topic} TRPG host, and user is playing game with you.
#     The detailed information about the fictional universe of game is included in context.
#     Please create this round's content based on User Persona, Entire Story, This Round Story, and Previous Conversation.
#     You should make 1. round content which will be displayed to user that can explain the situation, 2. user choices which will be displayed to user that can explain the choice's action, and 3. choice effect which will not be displayed to user that can explain the effect of the choice.
#     User has life points and coins which will be affected by the choices.
#     Each choice should be diverse and interesting, and reduce or increase user's life points or coins but this effect should not be mentioned in the choice.
#     You should consider previous conversation and user's choices to make the content and mention their effect on the beginning.
#     Story should be interesting and naturally connected to the previous conversation.
#     Your response should be python dictionary with below format.
#     ---
#     Context: {context}
#     ---
#     User Persona: {user_persona}
#     ---
#     Entire Story: {entire_story}
#     ---
#     This Round Story: {round_story}
#     ---
#     Previous Conversation: {previous_conversation}
#     ---
#     format:
#     \{
#       round_story: \"Story to display to player\",
#       user_choices: ["Choice 1 description", "Choice 2 description", "Choice 3 description"],
#       choice_effect: [\{ "money": integer of money amount change, "life: integer of life amount change \}],
#     \}
#       User Choice:
#       - [Choice1: Description]
#       - [Choice2: Description]
#       - [Choice3: Description]
#       Choice Effect:
#       - [Choice1: Money+2, Life-1]
#       - [Choice2: Life-2]
#       - [Choice3: Life+4, Money+1]
#     ---
#     Round Story:
#     User Choice:
#     Choice Effect:
#     """

def play_game(topic, user_persona, language, entire_story, round_story, previous_conversation, previous_choice_effect):
  llm = ChatUpstage()
  prompt_template = PromptTemplate.from_template(
    """
    Please answer in {language}.
    You are best {topic} TRPG host, and user is playing game with you.
    The detailed information about the fictional universe of game is included in context.
    Please create this round's content based on User Persona, Entire Story, This Round Story, and Previous Conversation.
    You should make 1. round content which will be displayed to user that can explain the situation, 2. user choices which will be displayed to user that can explain the choice's action, and 3. choice effect which will not be displayed to user that can explain the effect of the choice.
    User has life points and coins which will be affected by the choices.
    Choices should be at least 3 and total round should be less than 7.
    Each choice should be diverse and interesting, and reduce or increase user's life points or coins between (-10, 10), but this effect should not be shown in user choices.
    The effect of each choice must change the logical and reasonable amount as a result of the actions taken by the choice.
    Each choice should be long and detailed with explanation of the choice's action.
    You should consider previous conversation and user's choices to make the content and mention their effect on the beginning.
    Round content must start with explanation of user's previous choices and their effects if below Previous Choice Effect is not empty.
    Round content should be interesting and naturally connected to the previous conversation, with long and detailed explanation of the situation.
    Your response should be python dictionary with below format.
    ---
    Context: {context}
    ---
    User Persona: {user_persona}
    ---
    Entire Story: {entire_story}
    ---
    This Round Story: {round_story}
    ---
    Previous Conversation: {previous_conversation}
    ---
    Previous Choice Effect: {previous_choice_effect}
    ---
    format:
    {{
      round_content: \"Explanation of previous choice's effect and changes by it's result from the story. And then, Story explanation to show player\",
      user_choices: ["Choice 1 description", "Choice 2 description", "Choice 3 description"],
      choice_effects: [{{ "money": integer of money amount change, "life: integer of life amount change }}],
    }}
    ---
    """
  )
  chain = prompt_template | llm | StrOutputParser()
  # context = get_context(f"What is related information about {user_choice}?")
  context = ""

  while(True):
    try:
      response = chain.invoke({ "language": language, "topic": topic, "context": context, "user_persona": user_persona, "entire_story": entire_story, "round_story": round_story, "previous_conversation": previous_conversation, "previous_choice_effect": previous_choice_effect })
      response_dict = json.loads(response)

      return {
        "response": response,
        "round_content": response_dict["round_content"],
        "user_choices": response_dict["user_choices"],
        "choice_effects": response_dict["choice_effects"],
      }
    except:
      continue


def generate_bad_end(language, topic, user_persona, previous_conversation, previous_choice_effect):
  llm = ChatUpstage()
  prompt_template = PromptTemplate.from_template(
    """
    Please answer in {language}.
    You are best {topic} TRPG host, and user is playing game with you.
    The detailed information about the fictional universe of game is included in context.
    User played the game and reached the bad ending by previous choice.
    Please create bad ending scenario based on previous conversation and previous choice's effect.
    Consider topic, content, user persona, previous conversation and previous choice's effect to make the scenario.
    Bad ending story should be interesting and naturally connected to the previous conversation.
    You should mention the reason of bad ending and make the story interesting.
    ---
    Context: {context}
    ---
    User Persona: {user_persona}
    ---
    Previous Conversation: {previous_conversation}
    ---
    Previous Choice Effect: {previous_choice_effect}
    ---
    Bad Ending Scenario:
    """
  )
  chain = prompt_template | llm | StrOutputParser()
  # context = get_context(f"What is related information about {user_choice}?")
  context = ""

  response = chain.invoke({ "language": language, "topic": topic, "context": context, "user_persona": user_persona, "previous_conversation": previous_conversation, "previous_choice_effect": previous_choice_effect })

  return {
    "response": response,
  }


def generate_good_end(language, topic, user_persona, entire_story, previous_conversation):
  llm = ChatUpstage()
  prompt_template = PromptTemplate.from_template(
    """
    Please answer in {language}.
    You are best {topic} TRPG host, and user is playing game with you.
    The detailed information about the fictional universe of game is included in context.
    User played the game and reached the entire story's ending which means game win, so it's good ending.
    Please create good ending scenario based on previous conversation and entires story and user choices.
    Consider topic, content, user persona, entire story, and previous conversation to make the scenario.
    Good ending story should be interesting and naturally connected to the previous conversation.
    Good ending should be last part which finishes the game story and make user happy.
    You should mention the reason of bad ending and make the story interesting.
    ---
    Context: {context}
    ---
    User Persona: {user_persona}
    ---
    Entire Story: {entire_story}
    ---
    Previous Conversation: {previous_conversation}
    ---
    Good Ending Scenario:
    """
  )
  chain = prompt_template | llm | StrOutputParser()
  # context = get_context(f"What is related information about {user_choice}?")
  context = ""

  response = chain.invoke({ "language": language, "topic": topic, "context": context, "user_persona": user_persona, "entire_story": entire_story, "previous_conversation": previous_conversation })

  return {
    "response": response,
  }

def convert_to_image_prompt(topic, user_persona, host_message):
  llm = ChatUpstage()
  prompt_template = PromptTemplate.from_template(
    """
    Please provide visual prompt of the host message which will be used for text-image generation.
    Host message is D&D game scenario scene with choices on {topic}.
    Visual prompt should consider the context and user persona.
    Visual prompt should represent the scenario's scene and choices in the image.
    ---
    User Persona: {user_persona}
    ---
    Context: {context}
    ---
    Host Message: {host_message}
    """
  )
  chain = prompt_template | llm | StrOutputParser()
  context = get_context(f"What is related information about {topic}?")

  response = chain.invoke({ "topic": topic, "host_message": host_message, "context": context, "user_persona": user_persona })

  return {
    "response": response
  }


def generate_scenario_image(topic, user_persona, host_message):
  prompt_response = convert_to_image_prompt(topic, user_persona, host_message)["response"]
  image_url = generate_image(prompt_response)
  image_data = download_image(image_url)

  return image_data, image_url


def display_image_from_url(url):
  response = requests.get(url)
  img = Image(data=response.content)
  display(img)


def main():
  topic = input("Enter the topic: ")
  language = input("Enter the language: ")
  user_persona = None
  previous_conversation = None
  

  # Create User Persona
  user_persona_answer = None
  for i in range(5):
    question = make_user_persona(topic, user_persona_answer, previous_conversation, language)
    if i == 0:
      previous_conversation = f"Host: {question['response']}"
    else:
      previous_conversation = f"{previous_conversation}\nHost: {question['response']}\n"

    print(question["response"])
    user_persona_answer = input("Enter your answer: ")
    previous_conversation =  f"{previous_conversation}\nUser: {user_persona_answer}\nHost: "

    if i == 4:
      user_persona = summarize_user_persona(topic, previous_conversation, language)["response"]
  
  # Initialize Game
  init_chat = initialize_chat(topic, language)
  print(init_chat["response"])

  # Play Game
  while True:
    user_choice = input("Enter your choice: ")
    response = make_conversation(user_choice, init_chat["previous_conversation"], user_persona, language)

    # image_data, image_url = generate_scenario_image(topic, user_persona, response["response"])
    # print("IMAGE_URL: ", image_url)
    # display_image_from_url(image_url)

    print(response["response"])

    if response["is_last"]:
      break

  return

if __name__ == "__main__":
  main()