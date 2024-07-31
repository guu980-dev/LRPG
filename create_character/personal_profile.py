import re
import json
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_upstage import ChatUpstage

def generate_character_creation_questions(world_summary, language="korean"):
    llm = ChatUpstage()
    questions_prompt_template = PromptTemplate.from_template(
        """
        Based on the following novel context, generate five simple questions that a player should answer to help create a deeply personalized character for a fantasy RPG.
        The questions should explore different aspects of a potential character’s personality, background, and capabilities.
        For users who are not used to the story I want you to give several choices in the question

        Write five questions in {Language}

       **Output should strictly follow this format:**

        - Question1 (example: )
        - Question2 (example: )
        - Question3 (example: )
        - Question4 (example: )
        - Question5 (example: )

        ---
        Novel Context: {Context}
        """
    )
    questions_chain = questions_prompt_template | llm | StrOutputParser()
    questions = questions_chain.invoke({"Language": language, "Context": world_summary})
    print(questions)
    questions = questions.strip().split('\n')
    return questions

def create_character_profile(questions, language="korean"):
    llm = ChatUpstage()
    character_creation_prompt_template = PromptTemplate.from_template(
        """
        Using the answers provided below, create a detailed character profile for a fantasy tabletop RPG.
        The character should reflect the given attributes. Please ensure to use the specified field names and format in your output consistently.

        **Output should strictly follow this format:**

        - name: [character name]
        - gender: [male/female/other]
        - age: [age range or exact age]
        - race: [character race]
        - job: [character job]
        - stamina: [1-100]
        - intelligence: [1-100]
        - combat_power: [1-100]
        - agility: [1-100]
        - background: [character background]

        **Player Answers:**
        - {answer1}
        - {answer2}
        - {answer3}
        - {answer4}
        - {answer5}
        ---
        Please write the output in English.
        """
    )
    character_creation_chain = character_creation_prompt_template | llm | StrOutputParser()
    answers = {}
    for i, question in enumerate(questions):
        print(f"Question {i+1}: {question}")
        answers[f"answer{i+1}"] = input("Your answer: ")
    character_description = character_creation_chain.invoke({**answers, "Language": language})
    return character_description

def parse_character_data_to_json(text):
    fields = {
        'name': r"- name: (.*)",
        'gender': r"- gender: (.*)",
        'age': r"- age: (\d+)",
        'race': r"- race: (.*)",
        'job': r"- job: (.*)",
        'background': r"- background: (.*)"
    }
    param_fields = {
        'stamina': r"- stamina: (\d+)",
        'intelligence': r"- intelligence: (\d+)",
        'combat_power': r"- combat_power: (\d+)",
        'agility': r"- agility: (\d+)"
    }
    character_dict = {}
    params_dict = {}
    for key, pattern in fields.items():
        match = re.search(pattern, text)
        if match:
            character_dict[key] = match.group(1)
    for key, pattern in param_fields.items():
        match = re.search(pattern, text)
        if match:
            params_dict[key] = int(match.group(1))
    character_dict['params'] = params_dict
    return json.dumps(character_dict, indent=4, ensure_ascii=False)

def main():
    with open("/path/to/Harry_Potter_summary.txt", "r", encoding="utf-8") as file:
        world_summary = file.read()
    questions = generate_character_creation_questions(world_summary)
    character_description = create_character_profile(questions)
    print("Your generated character details:")
    print(character_description)
    character_json = parse_character_data_to_json(character_description)
    print(character_json)

if __name__ == "__main__":
    main()