import re, json, ast
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_upstage import ChatUpstage

def generate_character_creation_questions(world_summary, language="korean"):
    llm = ChatUpstage()
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
    while(True):
        try:
            questions = questions_chain.invoke({ "Context": world_summary })
            questions_list = ast.literal_eval(questions)
            questions_list = [question.replace('[', '').replace(']', '') for question in questions_list]
            return default_questions + questions_list
        except:
            continue



def create_character_profile(questions, answers, language="korean"):
    llm = ChatUpstage()
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
    character_description = character_creation_chain.invoke({ "qna": qna, "Language": language})
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
    # return json.dumps(character_dict, indent=4, ensure_ascii=False)
    return character_dict

def main():
    with open("/Users/hyunkoolee/upstage_kai_llm/llm_dnd/harrypotter_scenario/world_summary.txt", "r", encoding="utf-8") as file:
        world_summary = file.read()
    
    # 질문 준비
    questions = generate_character_creation_questions(world_summary)
    character_description = create_character_profile(questions)
    character_json = parse_character_data_to_json(character_description)
    print(character_json)

if __name__ == "__main__":
    main()