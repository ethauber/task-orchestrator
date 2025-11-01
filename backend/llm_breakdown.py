import os
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from backend.schemas import BreakdownRequest, BreakdownResponse

OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
MODEL_NAME = os.getenv('MODEL_NAME', 'qwen2.5:7b')

llm = ChatOllama(
    model=MODEL_NAME,
    base_url=OLLAMA_BASE_URL,
    temperature=0.114942
)

parser = PydanticOutputParser(pydantic_object=BreakdownResponse)

SYSTEM = (
    'You are a planning assistant. Given a clear goal (Definition of done), '
    'produce exactly TWO plan options. A Lean Plan and a Thorough Plan. '
    'Each plan has 3 to 7 steps. Each step is a single imperative sentence '
    'starting with a strong verb, under 15 words, concrete, and actionable. '
    'Do NOT include durations, scheduling, or owners. Use the schema exactly\n\n'
    '{format_instructions}'
)

HUMAN = (
    'Definition of done:\n{definition}\n\n'
    'Max steps per plan: {max_steps}\n'
)

prompt = ChatPromptTemplate.from_messages([
    ('system', SYSTEM), ('human', HUMAN)
])

chain = (
    RunnableParallel(
        definition=RunnablePassthrough(),
        max_steps=lambda x: x.get('max_steps', 7),
        format_instructions=lambda _: parser.get_format_instructions()
    )
    | prompt
    | llm
    | parser
)

def breakdown_with_lc(req: BreakdownRequest) -> BreakdownResponse:
    return chain.invoke({'definition': req.definition, 'max_steps': req.max_steps})
