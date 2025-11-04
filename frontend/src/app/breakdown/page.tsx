'use client';
import { useState, FormEvent as ReactFormEvent } from 'react';
import { postJSON } from '@/lib/api';
import { Json } from '@/components/Json';

type RefineResponse = {
    refinedIdea: string;
    questions: string[];
};

type PlanStep = { text: string };
type PlanOption = { name: string; steps: PlanStep[] };
type BreakdownResponse = { plans: PlanOption[] };

type FinalStep = {
    text: string; duration_minutes:number; depends_on?: number[];
    parked: boolean
};
type PlanResponse = {
    optionName: string; steps: FinalStep[]; total_duration: number;
    parked_indices: number[]
};

export default function BreakdownPage() {
    // Step 1: refine
    const [idea, setIdea] = useState<string>('Create a 10 minute outline by consolidating notes');
    const [refineLoading, setRefineLoading] = useState(false);
    const [refineErr, setRefineErr] = useState<string>('');
    const [refined, setRefined] = useState<RefineResponse | null>(null);
    const [answers, setAnswers] = useState<string[]>([]);

    // Step 2: breakdown
    const [maxSteps, setMaxSteps] = useState<number>(5);
    const [breakLoading, setBreakLoading] = useState(false);
    const [breakErr, setBreakErr] = useState<string>('');
    const [plans, setPlans] = useState<BreakdownResponse | null>(null);

    // Step 3: plan
    const [selected, setSelected] = useState<number | null>(null);
    const [budget, setBudget] = useState<number | ''>('');
    const [finalPlan, setFinalPlan] = useState<any>(null);
    const [finalLoading, setFinalLoading] = useState(false);
    const [finalErr, setFinalErr] = useState<string>("");

    // start handlers
    async function onRefine(e: ReactFormEvent) {
        e.preventDefault();
        setRefineErr('');
        setRefined(null);
        setPlans(null);
        setSelected(null);
        setFinalPlan(null);
        setAnswers([]);
        try {
            setRefineLoading(true);
            const json = await postJSON<RefineResponse>('/refine', { idea });
            setRefined(json);
            setAnswers(new Array(json.questions.length).fill(''));
        } catch (error: any) {
            setRefineErr(String(error));
        } finally {
            setRefineLoading(false);
        }
    }

    async function onBreakdown(e: ReactFormEvent) {
        e.preventDefault();
        setBreakErr('');
        setPlans(null);
        setSelected(null);
        setFinalPlan(null);

        // Build definition: prefer refinedIdea; append Q&A context if any
        const baseDef = refined?.refinedIdea?.trim().length ? refined!.refinedIdea : idea;
        const answeredPairs =
        refined && refined.questions.length
            ? refined.questions
                .map((q, i) => {
                const a = (answers[i] ?? "").trim();
                return a ? `Q: ${q}\nA: ${a}` : "";
                })
                .filter(Boolean)
                .join("\n")
            : "";

        const definition = answeredPairs ? `${baseDef}\n\n${answeredPairs}` : baseDef;

        try {
            setBreakLoading(true);
            const json = await postJSON<BreakdownResponse>('/breakdown', {
                definition,
                max_steps: maxSteps
            });
            setPlans(json);
        } catch (error: any) {
            setBreakErr(String(error));
        } finally {
            setBreakLoading(false);
        }
    }

    async function onFinalize() {
        if (!plans || selected === null) return;
        try {
            setFinalErr('');
            setFinalPlan(null);
            setFinalLoading(true);
            const pick = plans.plans[selected];
            const body = {
                optionName: pick.name,
                steps: pick.steps,
                total_minutes: budget === '' ? null : budget
            };
            const json = await postJSON<PlanResponse>('/plan', body);
            setFinalPlan(json);
        } catch (error: any) {
            setFinalErr(String(error));
            setFinalPlan(null);
        } finally {
            setFinalLoading(false);
        }
    }
    // end handlers

    return (
        <section>
            <h1>Breakdown Workbench</h1>
            <form onSubmit={onRefine} style={{ display: 'grid', gap: 12, maxWidth: 860 }}>
                <label>
                    <div>Idea</div>
                    <textarea
                        rows={4}
                        value={idea}
                        onChange={(e) => setIdea(e.target.value)}
                        style={{ width: '100%' }}
                    />
                </label>
                <button disabled={refineLoading || idea.length < 10}>
                    {refineLoading ? 'Refining...' : 'Refine Idea'}
                </button>
            </form>
            {refineErr && <p style={{ color: 'crimson', marginTop: 8}}>{refineErr}</p>}

            {refined && (
                <section style={{ marginTop: 16 }}>
                    <h3>Refined Idea</h3>
                    <p>{refined.refinedIdea}</p>

                    {refined.questions.length > 0 && (
                        <>
                            <h4>Clarifying questions</h4>
                            <ol style={{ display: 'grid', gap: 8 }}>
                                {refined.questions.map((question, qIndex) => (
                                    <li key={qIndex}>
                                        <div style={{ marginBottom: 4 }}>{question}</div>
                                        <input
                                            type='text'
                                            value={answers[qIndex] ?? ''}
                                            onChange={(e) => {
                                                const next = answers.slice();
                                                next[qIndex] = e.target.value;
                                                setAnswers(next);
                                            }}
                                            placeholder='Your answer (optional)'
                                            style={{ width: '100%' }}
                                        />
                                    </li>
                                ))}
                            </ol>
                        </>
                    )}
                    <h4>Refine JSON</h4>
                    <Json data={refined}/>
                </section>
            )}

            <form onSubmit={onBreakdown} style={{ display: 'grid', gap: 12, maxWidth: 860, marginTop: 24 }}>
                <label>
                    <div>Max steps per plan 3 to 7</div>
                    <input
                        type='number'
                        min={3}
                        max={7}
                        value={maxSteps}
                        onChange={(e) => setMaxSteps(parseInt(e.target.value || '5', 10))}
                    />
                </label>
                <button disabled={breakLoading || (!refined && idea.length < 20)}>
                    {breakLoading ? 'Generating...' : 'Generate Plan Options'}
                </button>
            </form>
            {breakErr && <p style={{ color: 'crimson', marginTop: 8 }}>{breakErr}</p>}

            {plans && (
                <section style={{ marginTop: 24 }}>
                    <h2>Plan Options</h2>
                    {plans.plans.map((plan, planIndex) => (
                        <div key={planIndex} style={{ marginBottom: 16 }}>
                            <label style={{ display: 'flex', alignItems: 'center', gap: 8}}>
                                <input
                                    type='radio'
                                    name='plan'
                                    checked={selected === planIndex}
                                    onChange={() => setSelected(planIndex)}
                                />
                                <strong>{plan.name}</strong>
                            </label>
                            <ol>{plan.steps.map((step, stepIndex) => <li key={stepIndex}>{step.text}</li>)}</ol>
                        </div>
                    ))}

                    <h3>Raw JSON</h3>
                    <Json data={plans} />
                </section>
            )}

            {plans && (
                <section style={{ marginTop: 16 }}>
                    <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
                        <label>
                            Time estimates (minutes, optional):{' '}
                            <input
                                type='number'
                                min={15}
                                step={15}
                                value={budget as number | ''}
                                onChange={(e) => setBudget(e.target.value === '' ? '' : parseInt(e.target.value, 10))}
                            />
                        </label>
                        <button disabled={selected === null || finalLoading} onClick={onFinalize}>
                            {finalLoading ? 'Finalizing...' : 'Finalize Plan'}
                        </button>
                    </div>
                    {finalErr && <p style={{ color: 'crimson', marginTop: 8 }}>{finalErr}</p>}

                    {finalPlan && (
                        <section style={{ marginTop: 12 }}>
                            <h3>Final Plan ({finalPlan.optionName})</h3>
                            <p>Total duration: {finalPlan.total_duration} min</p>
                            <ol>
                                {finalPlan.steps.map((step: any, stepIndex: any) => (
                                    <li key={stepIndex}>
                                        {step.text} - {step.duration_minutes} min
                                        {step.parked ? ' (parked)' : ''}
                                        {step.depends_on?.length ? ` | deps ${step.depends_on.join(',')}` : ''}
                                    </li>
                                ))}
                            </ol>
                            <h4>Raw JSON</h4>
                            <Json data={finalPlan} />
                        </section>
                    )}
                </section>
            )}
        </section>
    );
}