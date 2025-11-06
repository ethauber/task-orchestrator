from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

from backend.llm import base_chat_llm, load_prompts
from backend.schemas import PlanRequest, PlanResponse, PlanStep


parser = PydanticOutputParser(pydantic_object=PlanResponse)

prompts_ = load_prompts('plan.json')

prompt = ChatPromptTemplate.from_messages([
    ('system', prompts_['system']),
    ('human', prompts_['human'])
])


def _steps_block(steps: list[PlanStep]) -> str:
    return '\n'.join(f'{i+1}. {s.text}' for i , s in enumerate(steps))


chain = (
    RunnableParallel(
        optionName=RunnablePassthrough(),
        steps_block=lambda x: _steps_block(x['steps']),
        total_minutes=lambda x: x.get('total_minutes'),
        format_instructions=lambda _: parser.get_format_instructions()
    )
    | prompt
    | base_chat_llm
    | parser
)


def plan_with_lc(req: PlanRequest) -> PlanResponse:
    return chain.invoke({
        'optionName': req.optionName,
        'steps': req.steps,
        'total_minutes': req.total_minutes
    })
