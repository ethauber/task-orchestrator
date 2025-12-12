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

export type PlanSaveRequest = {
    plan_data: PlanResponse;
    initial_idea?: string;
    refined_idea?: string;
};

export type PlanSummary = {
    id: number;
    option_name: string;
    initial_idea?: string;
    total_duration: number;
    created_at: string;
    updated_at: string;
};

export type FullPlanResponse = {
    id: number;
    option_name: string;
    initial_idea?: string;
    refined_idea?: string;
    total_duration: number;
    full_plan_data: PlanResponse;
    created_at: string;
    updated_at: string;
};