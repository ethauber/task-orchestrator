from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

from backend.llm import base_chat_llm
from backend.schemas import PlanRequest, PlanResponse, PlanStep


parser = PydanticOutputParser(pydantic_object=PlanResponse)

SYSTEM = (
    'You finalize a selected plan into discrete steps with durations.\n'
    'Rules:\n'
    '1) Keep original step order and wording. Only sharpen if unclear.\n'
    '2) duration_minutes are whole minutes ini 15-minute increments (min 15).\n'
    '3) If total_minutes is given fit within it by marking later steps parked=true.\n'
    '4) Add minimal dependencies only when truly necessary (use 1-based indices).\n'
    '5) Return the output schema exactly.\n\n'
    '{format_instructions}'
)

HUMAN = (
    'Selected option: {optionName}\n'
    'Steps (in order):\n{steps_block}\n'
    'Time budget (minutes, optional): {total_minutes}\n'
)

prompt = ChatPromptTemplate.from_messages([
    ('system', SYSTEM),
    ('human', HUMAN)
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
