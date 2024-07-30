from langchain_upstage import ChatUpstage
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

def generate_chain(prompt, prompt_variable, llm=ChatUpstage(), parser = StrOutputParser()):
    prompt_template = PromptTemplate.from_template(prompt)
    chain = prompt_template | llm | parser
    answer = chain.invoke(prompt_variable)
    return answer