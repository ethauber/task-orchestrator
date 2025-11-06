from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

from backend.llm import base_chat_llm
from backend.schemas import RefineRequest, RefineResponse


SYSTEM = (
    "You help clients turn vague ideas into a concreate 'refinedIdea' and up to three"
    " 'questions'. Questions must be short, specific, and only included if essential."
    " Use the following output schema exactly\n\n{format_instructions}"
)
# Populates the format_instructions
parser = PydanticOutputParser(pydantic_object=RefineResponse)

CLIENT = (
    "Idea:\n{idea}\n"
    "{context_block}"
)
# Populates the context_block
def _context_block(context: str | None) -> str:
    """Anything in RunnableParallel called with same input so still receies context"""
    return f"Additional context from the client:\n{context}" \
        if context else "No additional context"

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM),
    ("human", CLIENT)
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
