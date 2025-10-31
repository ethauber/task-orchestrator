from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator, HttpUrl


class Health(BaseModel):
    status: Literal['ok', 'degraded', 'error', 'waffles'] = Field(
        ..., description='Overall service health'
    )
    model: str = Field(
        ...,
        description='Primary model identifier the service is using',
        examples=['qwen2.5']
    )
    ollama_url: HttpUrl = Field(
        ...,
        description='Base URL for the Ollama endpoint',
        examples=['http://localhost:11434']
    )


class PingResponse(BaseModel):
    response: str = Field(
        ...,
        description='Simple echo to verify',
        examples=['pong', 'alive']
    )


class RefineRequest(BaseModel):
    """Client's initial idea optional extra context"""
    idea: str = Field(
        ...,
        description=(
            "A short maybe vague goal or todo list the client wants to pursue "
        ),
        examples=[
            'Relieve a tension headache quickly',
            'Cure for Ω',
            'Turn research notes into a talk outline',
            'Plan my path',
        ],
        min_length=5,  # Avoids throwaway words like 'hi' or 'help'
        max_length=255  # Keep idea short. Details go into context instead
    )
    context: Optional[str] = Field(
        default=None,
        description=(
            "Optional extra info or answers to likely clarifying questions. "
            "Plain text that imrpoves passes without back-and-forth."
        ),
        examples=[
            # Health
            (
                "Headache started 9:30 after two Zoom calls. Pain 5–6/10 at temples. "
                "Drank ~1.5 L water. Took 200 mg ibuprofen at 10 with little effect. "
                "Have cold water bottle, no ice. Usually 1–2 per month, worse with poor sleep. "
                "Slept 5 hours. Need relief within 30 minutes at my desk."
            ),
            # Cure for Ω
            (
                "Ω is a placeholder for a root cause I cannot name yet. Symptoms appear after long coding days. "
                "I want a research plan to identify Ω and experiments to validate or rule out causes."
            ),
            # Research via Obsidian
            (
                "Notes live in Obsidian under 'research/'. Goal is a 10 minute talk outline. "
                "Desired sections: Problem, Approach, Results, Next steps."
            ),
            # Plan my path
            (
                "Target domains: AI engineering or platform work. Time horizon: not enough time. "
                "Constraints: must be remote first, budget for two certifications, many hours per week."
            )
        ],
         max_length=2000
    )


class RefineResponse(BaseModel):
    """
    A clear refinement of the client's idea plus up to three short, specific clarifying questions.
    If no questions are needed, questions must be an empty list.
    """
    refinedIdea: str = Field(
        ...,
        description=(
            "A precise and insightful rearticulation of the concept, incorporating safe"
            " assumptions stated clearly and emphasizing its clarity and specificity"
        ),
        examples=[
            # Health
            (
                "Desk friendly plan to reduce tension headache within 30 minutes using hydration, "
                "100 mg caffeine if available, cold bottle compress, posture reset, and a 2 minute "
                "temple and jaw release. Assumes access to water and light caffeine."
            ),
            # Cure for Ω
            (
                "Research program to identify Ω: log triggers, cluster symptoms, prioritize likely causes, "
                "and run low risk experiments with defined observation windows and stop rules."
            ),
            # Obsidian research
            (
                "Create a 10 minute talk outline by consolidating Obsidian notes in 'research/' into "
                "Problem, Approach, Results, and Next steps with no more than three bullets per section."
            ),
            # Plan my path
            (
                "Six month path toward AI platform roles with weekly learning blocks, two certifications, "
                "a public MVP, and portfolio updates, scheduled within hours per week constraint."
            )
        ],
        min_length=20, max_length=600
    )
    questions: List[str] = Field(
        default_factory=list, max_length=3, min_length=0,
        description=(
            "Zero to three clarifying questions, each one sentence, only if truly needed "
            "to execute the plan. Must be actionable concise targeted"
        ),
        examples=[
            [
                # Health
                "Do you have access to tea, coffee, or another light source of caffeine?",
                "Does turning your neck increase the pain?",
                "Are you sensitive to caffeine late in the day?"
            ],
            [
                # Cure for Ω
                "Can you track onset times and preceding activities for one week?",
                "Are there known allergens or workspace factors to include in the log?",
                "Is it acceptable to try one variable change per day?"
            ],
            [
                # Obsidian research
                "Should citations appear inline or in a final references section?",
                "Is the audience technical or general?",
                "Do you want images or just text bullets?"
            ],
            [
                # Plan my path
                "Which two certifications are top priority?",
                "Do you prefer waffles or pancakes?",
                "Should the MVP be public on GitHub from day one?"
            ]
        ]
    )

    @field_validator("questions")
    @classmethod
    def trim_and_cap_each_question(cls, v: List[str]) -> List[str]:
        # Keep each question tight
        trimmed = [q.strip() for q in v]
        for q in trimmed:
            if len(q) > 200:
                raise ValueError("each question must be ≤ 200 characters")
        return trimmed


class PlanStep(BaseModel):
    """One actionable step. verb, object, and qualifier. < 15 words"""
    text: str = Field(
        ...,
        description='Asingle concise step starting with a strong verb < 15 words',
        min_length=4, max_length=140,
        # examples=[''],
    )


class PlanOption(BaseModel):
    """A named option. Lean or Thorough with 3 to 7 steps"""
    name: str = Field(
        ...,
        description='Human-readable option name',
        examples=['Lean Plan', 'Thorough Plan']
    )
    steps: List[PlanStep] = Field(
        ...,
        description='Ordered list of actionable steps',
        min_length=3, max_length=7
    )


class BreakdownRequest(BaseModel):
    """Approved definition of done or refined idea to turn into plan options"""
    definition: str = Field(
        ...,
        description='The clarified goal or definition of done to plan',
        # examples=['']
    )
    max_steps: Optional[int] = Field(
        default=7,
        description='hard ceiling for stepsper plan min 3 to max 7 recommended'
    )


class BreakdownResponse(BaseModel):
    """Two alternative plans to choose from."""
    plans: List[PlanOption] = Field(
        ...,
        description='Exactly two options. "Lean Plan" or "Thorough Plan"',
        min_length=2, max_length=2
    )
