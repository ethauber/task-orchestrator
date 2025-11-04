from typing import List, Literal, Optional

from pydantic import (
    BaseModel, Field, field_validator, HttpUrl, model_validator
)


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
        examples=[
            # Health
            "Prepare 250 mL water and cold bottle compress",
            "Run 2-minute temple and jaw release at desk",

            # Cure for Ω
            "Define daily symptom log fields for one week",
            "Cluster logged symptoms by trigger and time of day",

            # Plan my path
            "List target AI platform roles and weekly learning blocks",
            "Schedule two certification study blocks this week"
        ],
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
        examples=[
            # Health
            (
                "Desk friendly plan to reduce tension headache within 30 minutes using hydration, "
                "100 mg caffeine if available, a cold bottle compress, a posture reset, and a short "
                "temple and jaw release. Assumes access to water and light caffeine."
            ),
            # Cure for Ω
            (
                "Research program to identify Ω: log triggers, cluster symptoms, prioritize likely causes, "
                "and run low risk experiments with defined observation windows and stop rules."
            ),
            # Plan my path
            (
                "Six month path toward AI platform roles with weekly learning blocks, two certifications, "
                "a public MVP, and portfolio updates, scheduled within hours per week constraint."
            )
        ]
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


class PlanRequest(BaseModel):
    """Finalize a selected option into an actionable plan with durations and light deps"""
    optionName: str = Field(
        ...,
        description='Human label of the selected option (e.g., \'Lean Plan\')'
    )
    steps: List[PlanStep] = Field(
        ...,
        description='Ordered steps from the selected option',
        min_length=3, max_length=12,
        examples=[]
    )
    total_minutes: Optional[int] = Field(
        default=None,
        description='Optional time budget to fit the plan into minutes. Round to 15 intervals',
        examples=[120, 240]
    )


class FinalStep(BaseModel):
    """Finalized step with duration and optional dependencies"""
    text: str = Field(
        ...,
        description='Same imperative ste text. concise',
        min_length=4, max_length=140
    )
    duration_minutes: int = Field(
        ...,
        description='Whole minutes. Multiples of 15',
        examples=[15, 30, 45, 60]
    )
    depends_on: Optional[List[int]] = Field(
        default=None,
        description='Optional 1-based indicies of prerequisite steps',
        examples=[[1], [2, 3]]
    )
    parked: bool = Field(
        default=False, description='True if moved out-of-scope to meet total_minutes'
    )

    @field_validator("depends_on", mode="before")
    @classmethod
    def coerce_depends_to_ints(cls, v):
        """
        LLM untrusted without tool calling yet.
        Coerce to ints and drop non integers
        """
        if v is None:
            return None

        if not isinstance(v, list):
            v = [v]

        coerced = []
        for x in v:
            try:
                coerced.append(int(x))
            except (TypeError, ValueError):
                print(f'Dropped non-coercible entry {x}')
                continue
        return coerced or None


class PlanResponse(BaseModel):
    """Final plan that fits constraints. Overflow steps are parked"""
    optionName: str = Field(..., examples=['Lean Plan'])
    steps: List[FinalStep] = Field(
        ..., description='Steps in execution order with durations and deps'
    )
    total_duration: int = Field(
        ...,
        description='Sum of non-parked durations (minutes).',
        examples=[90, 180]
    )
    parked_indices: List[int] = Field(
        default_factory=List,
        description='1-based indices of steps parked due to constraints',
        examples=[[5, 6]]
    )

    @model_validator(mode="after")
    def _normalize_dependencies(self):
        """
        After step length is known clamp to 1 to N, drop self dependencies,
        dedupe, and sort
        """
        n = len(self.steps)
        for idx, step in enumerate(self.steps, start=1):
            deps = step.depends_on
            if not deps:
                continue
            valid = {d for d in deps if 1 <= d <= n and d != idx}
            step.depends_on = sorted(valid) if valid else None
        return self
