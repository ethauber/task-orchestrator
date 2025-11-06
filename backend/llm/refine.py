from json import load
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

from backend.llm import base_chat_llm, load_prompts
from backend.schemas import RefineRequest, RefineResponse


# Populates the format_instructions
parser = PydanticOutputParser(pydantic_object=RefineResponse)

prompts_ = load_prompts('refine.json')


# Populates the context_block
def _context_block(context: str | None) -> str:
    """Anything in RunnableParallel called
       with the same input will still receive context"""
    return f"Additional context from the client:\n{context}" \
        if context else "No additional context"


prompt = ChatPromptTemplate.from_messages([
    ("system", prompts_['refine.json']),
    ("human", prompts_['human.json'])
])

chain = (
    RunnableParallel(
        idea=RunnablePassthrough(),  # Convienent helper to forward value
        context_block=lambda x: _context_block(x.get('context')),
        # Ignore input and use parser instructions
        format_instructions=lambda _: parser.get_format_instructions()
    )
    | prompt
    | base_chat_llm
    | parser
)


def refine_with_lang(req: RefineRequest) -> RefineResponse:
    """Invoke the chain and return a validated RefineResponse"""
    return chain.invoke({'idea': req.idea, 'context': req.context})
