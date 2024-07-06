from langchain_chroma import Chroma
from langchain_upstage import UpstageEmbeddings
from langchain.docstore.document import Document
from langchain_core.prompts import PromptTemplate
from langchain_upstage import ChatUpstage
import os
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from generate_image import generate_image, download_image

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

def get_context(invoke_text):
  sample_text_list = [
  "마법사의 나무는 마법 지팡이의 재료 중 최상급의 재료로 알려져 있다",
  "There are Weasleys' Wizard Wheezes nearby the Diagon Alley",
  "Diangon Alley is a place where you can buy magic wands",
  "Hogwart is a school for witches and wizards",
]
  sample_docs = [Document(page_content=text) for text in sample_text_list]
  vectorstore = Chroma.from_documents(
      documents=sample_docs,
      embedding=UpstageEmbeddings(model="solar-embedding-1-large"),
  )
  retriever = vectorstore.as_retriever()

  return retriever.invoke(invoke_text)


def make_user_persona(topic, user_answer, previous_conversation, language):
  llm = ChatUpstage()
  default_template = """
    Please answer in {language} language.
    You are best D&D host with {topic}. And user is playing game with you.
    Please answer in a exciting tone as a host.
    Before starting the game, user wants to create a persona.
    Please provide 1 question to user to create a persona.
    You must make only one question per response.
    Each question should be related to user's character, such as name, gender, personality or any related features with the topic.
    When asking questions, please consider the topic and make the question interesting.
    You should consider previous conversation's questions.
    Question should not ask same things from previous questions, and should be diverse and interesting.
    Do not ask similar questions from previous questions.
    First question should include the introduction of the game.
    ---
    Context: {context}
    ---
    Previous Conversation: {previous_conversation}
  """

  prompt_template = PromptTemplate.from_template(default_template)
  chain = prompt_template | llm | StrOutputParser()
  context = get_context(f"What is related information about {topic}?")

  response = chain.invoke({ "context": context, "topic": topic, "language": language, "previous_conversation": previous_conversation if previous_conversation else None })

  return {
    "response": response,
  }


def summarize_user_persona(topic, previous_conversation, language):
  llm = ChatUpstage()
  default_template = """
    Please answer in {language} language.
    You are best D&D host with {topic}. And user is playing game with you.
    Please answer in a exciting tone as a host.
    Before starting the game, user wants to create a persona.
    You have finished asking questions to user to create a persona and it's included on the previous conversation.
    Please summary information and create the user's persona with detail.
    ---
    Context: {context}
    ---
    Previous Conversation: {previous_conversation}
  """

  prompt_template = PromptTemplate.from_template(default_template)
  chain = prompt_template | llm | StrOutputParser()
  context = get_context(f"What is related information about {topic}?")

  response = chain.invoke({ "context": context, "topic": topic, "language": language, "previous_conversation": previous_conversation })

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
    When user select a choice, you should provide the result of the choice, but you should not show result before user select the choice.
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


def convert_to_image_prompt(topic, user_persona, host_message):
  llm = ChatUpstage()
  prompt_template = PromptTemplate.from_template(
    """
    Please provide visual prompt of the host message which will be used for text-image generation.
    Host message is D&D game scenario with choices on {topic}.
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

  response = chain.invoke({ "host_message": host_message, "context": context, "user_persona": user_persona })

  return {
    "response": response
  }


def generate_scenario_image():
  prompt_response = convert_to_image_prompt()["response"]
  image_url = generate_image(prompt_response)
  image_data = download_image(image_url)

  return image_data, image_url


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
    previous_conversation =  f"{previous_conversation}\nUser: {user_persona_answer}\n"

    if i == 4:
      user_persona = summarize_user_persona(topic, previous_conversation, language)["response"]
  
  # Initialize Game
  init_chat = initialize_chat(topic, language)
  print(init_chat["response"])

  # Play Game
  while True:
    user_choice = input("Enter your choice: ")
    response = make_conversation(user_choice, init_chat["previous_conversation"], user_persona, language)
    print(response["response"])

    if response["is_last"]:
      break

  return

if __name__ == "__main__":
  main()