from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

from backend.llm import base_chat_llm, load_prompts
from backend.schemas import BreakdownRequest, BreakdownResponse


parser = PydanticOutputParser(pydantic_object=BreakdownResponse)

prompts_ = load_prompts('breakdown.json')

prompt = ChatPromptTemplate.from_messages([
    ('system', prompts_['system']), ('human', prompts_['human'])
])

chain = (
    RunnableParallel(
        definition=RunnablePassthrough(),
        max_steps=lambda x: x.get('max_steps', 7),
        format_instructions=lambda _: parser.get_format_instructions()
    )
    | prompt
    | base_chat_llm
    | parser
)


def breakdown_with_lc(req: BreakdownRequest) -> BreakdownResponse:
    return chain.invoke({
        'definition': req.definition, 'max_steps': req.max_steps
    })
