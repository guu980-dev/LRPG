import re
import json
import ast
import requests
import gradio as gr
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_upstage import ChatUpstage

def generate_character_creation_questions(api_key, world_summary, language="korean"):
    llm = ChatUpstage(api_key=api_key)
    questions_prompt_template = PromptTemplate.from_template(
        """
        Based on the following novel context, generate five simple questions that a player should answer to help create a deeply personalized character for a fantasy RPG.
        The questions should explore different aspects of a potential character’s personality, background, and capabilities.
        For users who are not used to the story I want you to give several choices in the question.
        Write five questions in Korean(한글).
        Your response should be python list with strings consist of questions.
        ---
        Novel Context: {Context}
        ---
        Format: ['당신은 ...? (답변의 예시: ...): ', ...]
        ---
        Questions: 
        """
    )
    questions_chain = questions_prompt_template | llm | StrOutputParser()
    
    default_questions = [
        "당신의 캐릭터 이름은 무엇인가요? (스킵할시 자동으로 이름이 생성됩니다): ",
        "당신의 캐릭터의 성별은 무엇인가요? (스킵할시 자동으로 성별이 선택됩니다): ",
        "당신의 캐릭터는 몇살인가요? (스킵할시 자동으로 나이가 선택됩니다): ",
    ]
    while True:
        try:
            questions = questions_chain.invoke({"Context": world_summary})
            questions_list = ast.literal_eval(questions)
            questions_list = [question.replace('[', '').replace(']', '') for question in questions_list]
            return default_questions + questions_list
        except Exception as e:
            print(f"Error generating questions: {e}")
            continue


def create_character_profile(api_key, questions, answers, language="korean"):
    llm = ChatUpstage(api_key=api_key)
    character_creation_prompt_template = PromptTemplate.from_template(
        """
        Using the answers provided below, create a detailed character profile for a fantasy tabletop RPG.
        The character should reflect the given attributes. Please ensure to use the specified field names and format in your output consistently.
        Consider Player's answers as the input and generate a character profile based on the given context.
        When player's answer is not given, please use a appropriate value for corresponding fields made by yourself.

        **Output should strictly follow this format:**

        - name: "character name"
        - gender: "Male" or "Female"
        - age: age on integer
        - race: "character race"
        - job: "character job"
        - stamina: integer between [1, 100]
        - intelligence: integer between [1, 100]
        - combat_power: integer between [1, 100]
        - agility: integer between [1, 100]
        - background: "character background"

        **Player Answers:**
        qna:
        {qna}
        ---
        Please write the output in English.
        """
    )
    character_creation_chain = character_creation_prompt_template | llm | StrOutputParser()
    qna = [f"Q: {questions[i]}\nA: {answers[i]}" for i in range(len(questions))]
    character_description = character_creation_chain.invoke({"qna": qna, "Language": language})
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
    return character_dict


def run_question_generation(api_key, file_path):
    # Read the world summary from the uploaded file
    with open(file_path, 'r', encoding='utf-8') as file:
        world_summary = file.read()

    # Generate questions
    questions = generate_character_creation_questions(api_key, world_summary)
    
    return questions


def run_profile_generation(api_key, file_path, *answers):
    questions = run_question_generation(api_key, file_path)
    
    # Generate character profile
    character_description = create_character_profile(api_key, questions, answers)
    character_json = parse_character_data_to_json(character_description)
    return character_description, json.dumps(character_json, indent=4, ensure_ascii=False)


def main():
    with gr.Blocks() as demo:
        gr.Markdown("## Fantasy RPG Character Creator")
        
        with gr.Row():
            api_key_input = gr.Textbox(label="API Key", placeholder="Enter your API key here", type="password")
            file_input = gr.File(label="Upload World Summary Text File", type="filepath")

        questions_output = gr.JSON(label="Generated Questions")
        
        # Button to generate questions
        generate_questions_button = gr.Button("Generate Questions")

        # Answers input section
        answers_input = [gr.Textbox(label=f"Answer {i+1}", placeholder="Type your answer here") for i in range(8)]
        
        # Outputs for character description and JSON
        character_description_output = gr.Textbox(label="Character Description", lines=10)
        json_output = gr.JSON(label="Character JSON")
        
        # Button to run the profile generation
        generate_profile_button = gr.Button("Generate Character Profile")

        # Define button click actions
        def on_generate_questions(api_key, file_path):
            questions = run_question_generation(api_key, file_path)
            for i, question in enumerate(questions):
                answers_input[i].label = question
            return questions

        generate_questions_button.click(
            fn=on_generate_questions, 
            inputs=[api_key_input, file_input], 
            outputs=questions_output
        )

        generate_profile_button.click(
            fn=run_profile_generation, 
            inputs=[api_key_input, file_input, *answers_input], 
            outputs=[character_description_output, json_output]
        )

    # Launch the Gradio interface
    demo.launch()


if __name__ == "__main__":
    main()