from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import (
    RunnableLambda, RunnableParallel, RunnablePassthrough
)

from backend.llm import base_chat_llm, math_llm, load_prompts
from backend.llm.tools import normalize_duration
from backend.schemas import PlanRequest, PlanResponse, PlanStep


parser = PydanticOutputParser(pydantic_object=PlanResponse)

prompts_ = load_prompts('plan.json')

prompt = ChatPromptTemplate.from_messages([
    ('system', prompts_['system']),
    ('human', prompts_['human'])
])


def _steps_block(steps: list[PlanStep]) -> str:
    return '\n'.join(f'{i+1}. {s.text}' for i, s in enumerate(steps))


def _apply_tool_math(plan: PlanResponse) -> PlanResponse:
    """
    Receives the drafted plan, batch-sends all durations to the
    Tool-Bound LLM, executes the tools, and updates the plan.
    """
    print('Applying tool-based math normalization to plan durations...')
    batch_prompts: list = [
        [HumanMessage(content=f"Normalize a duration of {step.duration_minutes} minutes.")]
        for step in plan.steps
    ]

    results = math_llm.batch(batch_prompts)

    for i, (step, response) in enumerate(zip(plan.steps, results)):
        if response.tool_calls:
            call = response.tool_calls[0]
            old_val = step.duration_minutes

            step.duration_minutes = normalize_duration.invoke(call['args'])
            print(f'[Step {i}] Tool Used: {old_val} -> {step.duration_minutes}')
        else:
            print(f'[Step {i}] MISSED TOOL. LLM raw response: {response}')

    return plan


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
    | RunnableLambda(_apply_tool_math)
)


def plan_with_lc(req: PlanRequest) -> PlanResponse:
    print('Planning with LangChain plan_with_lc...')
    return chain.invoke({
        'optionName': req.optionName,
        'steps': req.steps,
        'total_minutes': req.total_minutes
    })
