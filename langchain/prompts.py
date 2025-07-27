from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from llm_client import LLMClient
from langchain_core.output_parsers import StrOutputParser   


template = """Tell me a {adjective} joke about {content}.
"""
prompt = PromptTemplate.from_template(template)
print(prompt) 

prompt.format(adjective="funny", content="chickens")


# Define a function to ensure proper formatting
def format_prompt(variables):
    return prompt.format(**variables)

llm = LLMClient()

# Create the chain with explicit formatting
joke_chain = (
    RunnableLambda(format_prompt)
    | llm.generate_response
    | StrOutputParser()
)

# Run the chain
response = joke_chain.invoke({"adjective": "funny", "content": "chickens"})
print(response)