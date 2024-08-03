create_custom_world_prompt = """Write a worldview story about {topic}.
You read the context and construct the story of the context in a new and creative way.
You must create a new world view by enriching and concretely providing the given content.

Context: {context}

please answer in {language}.
worldview:
"""


create_scenario_prompt = """You are best {topic} TRPG host, and user is playing game with you.
You understand the contnt. Write diverse, creative scenarios for your story. 
Each scenario is organically connected and an independent, organic story. Scenarios should not be similar.
The output format is list. Add {output_count} scenarios to the list.

Context: {context}

Response should be python list of {output_count} json element with <title> and <story>. 
The format must be json. 
please answer in {language}.
scenario:
"""


create_storyline_prompt = """You are best {topic} TRPG host, and user is playing game with you.
The detailed information about the fictional universe of game is included in context.
Please create a storyline with an interesting story and ending, with 5 rounds. 
The storyline must be an organic story.
Each round should include an interesting event and allow the user to move on with the appropriate choice for that step.
Scenario should be related to fictional universe and users persona.

Context: {context}

Response should be python list of {output_count} json element with <title> and <story>. 
The format must be json. 
Please answer in {language}.
storyline:"""