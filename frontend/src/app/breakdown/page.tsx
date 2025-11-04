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
    // 'Create a 10 minute outline by consolidating notes'
    const [idea, setIdea] = useState<string>('');
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
    // start styling
    type Styles = {
        [key: string]: React.CSSProperties;
    }
    const styles: Styles = {
        container: { maxWidth: 900, margin: '0 auto', padding: 24, fontFamily: 'system-ui, -apple-system, sans-serif' },
        section: { marginTop: 24, padding: 16, backgroundColor: '#f9f9f9', borderRadius: 8, border: '1px solid #e0e0e0' },
        label: {
            display: 'block', marginBottom: 8,
            fontWeight: 500, fontSize: 14, color: '#333',
            // textDecorationLine: 'underline'
        },
        textarea: { width: '100%', padding: 12, border: '1px solid #ddd', borderRadius: 6, fontSize: 14, fontFamily: 'inherit', resize: 'vertical' },
        input: { padding: 10, border: '1px solid #ddd', borderRadius: 6, fontSize: 14 },
        button: { padding: '10px 16px', backgroundColor: '#0066cc', color: 'white', border: 'none', borderRadius: 6, fontWeight: 500, cursor: 'pointer', transition: 'background 0.2s' },
        buttonHover: { backgroundColor: '#0052a3' },
        buttonDisabled: { backgroundColor: '#ccc', cursor: 'not-allowed' },
        error: { color: '#d32f2f', marginTop: 8, fontSize: 14 },
        planItem: { padding: 12, marginBottom: 12, backgroundColor: 'white', border: '2px solid #e0e0e0', borderRadius: 6, cursor: 'pointer', transition: 'all 0.2s' },
        planSelected: { borderColor: '#0066cc', backgroundColor: '#f0f7ff' },
        h1: { fontSize: 28, fontWeight: 600, marginBottom: 24, color: '#1a1a1a' },
        h2: { fontSize: 20, fontWeight: 600, marginTop: 24, marginBottom: 16, color: '#1a1a1a' },
        h3: { fontSize: 16, fontWeight: 600, marginTop: 16, marginBottom: 12, color: '#333' },
    };
    // end styling

    return (
        <section style={styles.container}>
            <h1 style={{...styles.h1}}>Breakdown Workbench</h1>
            <form onSubmit={onRefine} style={{ display: 'grid', gap: 12, maxWidth: 860 }}>
                <label style={{...styles.label}}>
                    <div>Idea</div>
                    <textarea
                        rows={4}
                        value={idea}
                        onChange={(e) => setIdea(e.target.value)}
                        style={{...styles.textarea}}
                    />
                </label>
                <button disabled={refineLoading || idea.length < 10} style={{ ...styles.button, ...(refineLoading || idea.length < 10 ? styles.buttonDisabled : {})}}>
                    {refineLoading ? 'Refining...' : 'Refine Idea'}
                </button>
            </form>
            {refineErr && <p style={{ ...styles.error }}>{refineErr}</p>}

            {refined && (
                <section style={styles.section}>
                    <h3 style={{...styles.h3}}>Refined Idea</h3>
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
                                            style={{ ...styles.input }}
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
                <label style={{...styles.label}}>
                    <div>Max steps per plan 3 to 7</div>
                    <input
                        type='number'
                        min={3}
                        max={7}
                        value={maxSteps}
                        onChange={(e) => setMaxSteps(parseInt(e.target.value || '5', 10))}
                        style={{ ...styles.input }}
                    />
                </label>
                <button disabled={breakLoading || !refined} style={{ ...styles.button, ...(breakLoading || !refined ? styles.buttonDisabled : {})}}>
                    {breakLoading ? 'Generating...' : 'Generate Plan Options'}
                </button>
            </form>
            {breakErr && <p style={{ ...styles.error }}>{breakErr}</p>}

            {plans && (
                <section style={styles.section}>
                    <h2 style={{...styles.h2}}>Plan Options</h2>
                    {plans.plans.map((plan, planIndex) => (
                        <div key={planIndex} style={{...styles.planItem, ...(selected === planIndex ? styles.planSelected : {})}}>
                            <label style={{...styles.label}}>
                                <input
                                    type='radio'
                                    name='plan'
                                    checked={selected === planIndex}
                                    onChange={() => setSelected(planIndex)}
                                    style={{ ...styles.input }}
                                />
                                <strong style={{marginLeft: 8}}>{plan.name}</strong>
                            </label>
                            <ol>{plan.steps.map((step, stepIndex) => <li key={stepIndex}>{step.text}</li>)}</ol>
                        </div>
                    ))}

                    <h3 style={{...styles.h3}}>Raw JSON</h3>
                    <Json data={plans} />
                </section>
            )}

            {plans && (
                <section style={styles.section}>
                    <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
                        <label style={{...styles.label}}>
                            Time estimates (minutes, optional):{' '}
                            <input
                                type='number'
                                min={15}
                                step={15}
                                value={budget as number | ''}
                                onChange={(e) => setBudget(e.target.value === '' ? '' : parseInt(e.target.value, 10))}
                                style={{ ...styles.input }}
                            />
                        </label>
                        <button disabled={selected === null || finalLoading} onClick={onFinalize} style={{ ...styles.button, ...(selected === null || finalLoading ? styles.buttonDisabled : {})}}>
                            {finalLoading ? 'Finalizing...' : 'Finalize Plan'}
                        </button>
                    </div>
                    {finalErr && <p style={{ ...styles.error }}>{finalErr}</p>}

                    {finalPlan && (
                        <section style={styles.section}>
                            <h3 style={{...styles.h3}}>Final Plan ({finalPlan.optionName})</h3>
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