export type RefineResponse = {
    refinedIdea: string;
    questions: string[];
};

export type PlanStep = { text: string };
export type PlanOption = { name: string; steps: PlanStep[] };
export type BreakdownResponse = { plans: PlanOption[] };

export type FinalStep = {
    text: string; duration_minutes:number; depends_on?: number[];
    parked: boolean
};

export type PlanResponse = {
    optionName: string; steps: FinalStep[]; total_duration: number;
    parked_indices: number[]
};