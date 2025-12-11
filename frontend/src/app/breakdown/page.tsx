'use client';
import { useState, FormEvent as ReactFormEvent, useEffect } from 'react';

import type {
    RefineResponse,
    BreakdownResponse,
    PlanResponse,
    PlanSummary,
    FullPlanResponse
} from '@/lib/types';
import { useStreamingAction, listPlans, savePlan, getPlan } from '@/lib/api';

import useSystemDarkMode from './systemAppearance';


export default function BreakdownPage() {
    // Step 1: refine
    // example 'Create a 10 minute outline by consolidating notes'
    const [idea, setIdea] = useState<string>('');
    const [refined, setRefined] = useState<RefineResponse | null>(null);
    const [answers, setAnswers] = useState<string[]>([]);
    const refineStream = useStreamingAction();

    // Step 2: breakdown
    const [maxSteps, setMaxSteps] = useState<number>(5);
    const [breakErr, setBreakErr] = useState<string>('');
    const [plans, setPlans] = useState<BreakdownResponse | null>(null);
    const breakdownStream = useStreamingAction();

    // Step 3: plan
    const [selected, setSelected] = useState<number | null>(null);
    const [budget, setBudget] = useState<number | ''>('');
    const [finalPlan, setFinalPlan] = useState<PlanResponse | null>(null);
    const [finalLoading, setFinalLoading] = useState(false);
    const [finalErr, setFinalErr] = useState<string>("");
    const finalizeStream = useStreamingAction()

    // Plan Persistence
    const [savedPlans, setSavedPlans] = useState<PlanSummary[]>([]);
    const [saveStatus, setSaveStatus] = useState<string>('');
    const [loadingSavedPlans, setLoadingSavedPlans] = useState<boolean>(false);
    const [loadingPlanById, setLoadingPlanById] = useState<boolean>(false);

    const isDarkMode = useSystemDarkMode();

    // Load saved plans on component mount
    useEffect(() => {
        fetchSavedPlans();
    }, []);

    const fetchSavedPlans = async () => {
        setLoadingSavedPlans(true);
        try {
            const plans = await listPlans();
            setSavedPlans(plans);
        } catch (error: any) {
            console.error("Failed to fetch saved plans:", error);
            // Optionally set an error state to display to the user
        } finally {
            setLoadingSavedPlans(false);
        }
    };


    async function onRefine(e: ReactFormEvent) {
        e.preventDefault();
        refineStream.setError('');
        setRefined(null);
        setPlans(null);
        setSelected(null);
        setFinalPlan(null);
        setAnswers([]);
        setSaveStatus(''); // Clear save status

        const result = await refineStream.run<RefineResponse>('/stream/refine', { idea });

        if (!result) return;

        setRefined(result);
        setAnswers(new Array(result.questions.length).fill(""));
    }

    async function onBreakdown(e: ReactFormEvent) {
        e.preventDefault();
        setBreakErr('');
        setPlans(null);
        setSelected(null);
        setFinalPlan(null);
        setSaveStatus(''); // Clear save status

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

        const result = await breakdownStream.run<BreakdownResponse>('/stream/breakdown', { definition, max_steps: maxSteps });
        if (!result) return;
        setPlans(result);
    }

    async function onFinalize() {
        if (!plans || selected === null) return;

        const result = await finalizeStream.run<PlanResponse>('/stream/plan', {
            optionName: plans.plans[selected].name,
            steps: plans.plans[selected].steps,
            total_minutes: budget === '' ? null : budget
        })
        if (!result) return;
        setFinalPlan(result);
    }

    async function onSavePlan() {
        if (!finalPlan) return;
        setSaveStatus('Saving...');
        try {
            const savedId = await savePlan(finalPlan);
            setSaveStatus(`Plan saved with ID: ${savedId}`);
            fetchSavedPlans(); // Refresh the list of saved plans
        } catch (error: any) {
            setSaveStatus(`Failed to save plan: ${error.message}`);
        }
    }

    async function onLoadPlan(planId: number) {
        setLoadingPlanById(true);
        setIdea(''); // Clear current state
        setRefined(null);
        setPlans(null);
        setSelected(null);
        setFinalPlan(null);
        setAnswers([]);
        setSaveStatus('');

        try {
            const fullPlan = await getPlan(planId);
            setFinalPlan(fullPlan.full_plan_data);
            setIdea(''); // Optionally set idea/refinedIdea from loaded plan if desired
        } catch (error: any) {
            console.error("Failed to load plan:", error);
            // Optionally set an error state to display to the user
        } finally {
            setLoadingPlanById(false);
        }
    }
    // end handlers
    // start styling
    // Color themes
    const colors = isDarkMode ? {
        bgPrimary: '#0a0a0a',
        bgSecondary: '#1a1a1a',
        bgTertiary: '#2a2a2a',
        textPrimary: '#e0e0e0',
        textSecondary: '#a0a0a0',
        border: '#404040',
        inputBg: '#1a1a1a',
        selectedBg: '#1a3a5a',
    } : {
        bgPrimary: '#ffffff',
        bgSecondary: '#f9f9f9',
        bgTertiary: '#ffffff',
        textPrimary: '#1a1a1a',
        textSecondary: '#333',
        border: '#e0e0e0',
        inputBg: '#ffffff',
        selectedBg: '#f0f7ff',
    };

    type Styles = {
        [key: string]: React.CSSProperties;
    }
    const styles: Styles = {
        container: { maxWidth: 900, margin: '0 auto', padding: 24, fontFamily: 'system-ui, -apple-system, sans-serif' },
        section: { marginTop: 24, padding: 16, backgroundColor: colors.bgSecondary, borderRadius: 8, border: `1px solid ${colors.border}` },
        label: {
            display: 'block', marginBottom: 8,
            fontWeight: 500, fontSize: 14, color: colors.textSecondary,
        },
        textarea: {
            width: '100%', padding: 12, border: `1px solid ${colors.border}`, borderRadius: 6,
            fontSize: 14, fontFamily: 'inherit', resize: 'vertical',
            backgroundColor: colors.inputBg, color: colors.textPrimary
        },
        input: {
            padding: 10, border: `1px solid ${colors.border}`, borderRadius: 6, fontSize: 14,
            backgroundColor: colors.inputBg, color: colors.textPrimary
        },
        button: { padding: '10px 16px', backgroundColor: '#0066cc', color: 'white', border: 'none', borderRadius: 6, fontWeight: 500, cursor: 'pointer', transition: 'background 0.2s' },
        buttonHover: { backgroundColor: '#0052a3' },
        buttonDisabled: { backgroundColor: '#ccc', cursor: 'not-allowed' },
        error: { color: '#d32f2f', marginTop: 8, fontSize: 14 },
        planItem: {
            padding: 12, marginBottom: 12, backgroundColor: colors.bgTertiary,
            borderWidth: 2, borderColor: colors.border, borderStyle: 'solid',
            borderRadius: 6, cursor: 'pointer', transition: 'all 0.2s'
        },
        planSelected: { borderColor: '#0066cc', backgroundColor: colors.selectedBg },
        h1: { fontSize: 28, fontWeight: 600, marginBottom: 24, color: colors.textPrimary },
        h2: { fontSize: 20, fontWeight: 600, marginTop: 24, marginBottom: 16, color: colors.textPrimary },
        h3: { fontSize: 16, fontWeight: 600, marginTop: 16, marginBottom: 12, color: colors.textSecondary },
        thinking: {
            marginTop: 12, padding: 12,
            backgroundColor: isDarkMode ? '#1a2a3a' : '#e3f2fd',
            border: `1px solid ${isDarkMode ? '#2a4a6a' : '#90caf9'}`,
            borderRadius: 6,
            fontSize: 13,
            fontFamily: 'monospace',
            color: isDarkMode ? '#90caf9' : '#1565c0',
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-word'
        },
    };
    // end styling

    return (
        <section style={styles.container}>
            <h1 style={{ ...styles.h1 }}>Breakdown Workbench</h1>
            <form onSubmit={onRefine} style={{ display: 'grid', gap: 12, maxWidth: 860 }}>
                <label style={{ ...styles.label }}>
                    <div>Idea</div>
                    <textarea
                        rows={4}
                        value={idea}
                        onChange={(e) => setIdea(e.target.value)}
                        style={{ ...styles.textarea }}
                    />
                </label>
                <button disabled={refineStream.loading || idea.length < 10} style={{ ...styles.button, ...(refineStream.loading || idea.length < 10 ? styles.buttonDisabled : {}) }}>
                    {refineStream.loading ? 'Refining...' : 'Refine Idea'}
                </button>
            </form>
            {refineStream.error && <p style={{ ...styles.error }}>{refineStream.error}</p>}

            {(refineStream.loading || refineStream.streaming) && (
                <div style={styles.thinking}>
                    <div style={{ fontSize: 11, fontWeight: 600, marginBottom: 8, opacity: 0.7 }}>
                        {refineStream.loading ? '🤖 AI is generating...' : '✅'}
                    </div>
                    {refineStream.streaming}
                </div>
            )}
            {refined && (
                <section style={styles.section}>
                    <h3 style={{ ...styles.h3 }}>Refined Idea</h3>
                    <textarea
                        rows={3}
                        style={styles.textarea}
                        value={refined.refinedIdea}
                        onChange={(e) => setRefined({ ...refined, refinedIdea: e.target.value })}
                    />

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
                </section>
            )}

            <form onSubmit={onBreakdown} style={{ display: 'grid', gap: 12, maxWidth: 860, marginTop: 24 }}>
                <label style={{ ...styles.label }}>
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
                <button disabled={breakdownStream.loading || !refined} style={{ ...styles.button, ...(breakdownStream.loading || !refined ? styles.buttonDisabled : {}) }}>
                    {breakdownStream.loading ? 'Generating...' : 'Generate Plan Options'}
                </button>
            </form>
            {breakErr && <p style={{ ...styles.error }}>{breakErr}</p>}

            {(breakdownStream.loading || breakdownStream.streaming) && (
                <div style={styles.thinking}>
                    <div style={{ fontSize: 11, fontWeight: 600, marginBottom: 8, opacity: 0.7 }}>
                        {breakdownStream.loading ? '🤖 AI is generating...' : '✅'}
                    </div>
                    {breakdownStream.streaming}
                </div>
            )}
            {plans && (
                <section style={styles.section}>
                    <h2 style={{ ...styles.h2 }}>Plan Options</h2>
                    {plans.plans.map((plan, planIndex) => (
                        <div key={planIndex} style={{ ...styles.planItem, ...(selected === planIndex ? styles.planSelected : {}) }}>
                            <label style={{ ...styles.label }}>
                                <input
                                    type='radio'
                                    name='plan'
                                    checked={selected === planIndex}
                                    onChange={() => setSelected(planIndex)}
                                    style={{ ...styles.input }}
                                />
                                <strong style={{ marginLeft: 8 }}>{plan.name}</strong>
                            </label>
                            <ol>{plan.steps.map((step: any, stepIndex: number) => (
                                <li key={stepIndex}>{typeof step === 'string' ? step : step.text}</li>
                            ))}</ol>
                        </div>
                    ))}
                </section>
            )}

            {plans && (
                <section style={styles.section}>
                    <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
                        <label style={{ ...styles.label }}>
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
                        <button disabled={selected === null || finalizeStream.loading} onClick={onFinalize} style={{ ...styles.button, ...(selected === null || finalizeStream.loading ? styles.buttonDisabled : {}) }}>
                            {finalizeStream.loading ? 'Finalizing...' : 'Finalize Plan'}
                        </button>
                    </div>
                    {finalErr && <p style={{ ...styles.error }}>{finalErr}</p>}

                    {(finalizeStream.loading || finalizeStream.streaming) && (
                        <div style={styles.thinking}>
                            <div style={{ fontSize: 11, fontWeight: 600, marginBottom: 8, opacity: 0.7 }}>
                                {finalizeStream.loading ? '🤖 AI is generating...' : '✅'}
                            </div>
                            {finalizeStream.streaming}
                        </div>
                    )}
                    {finalPlan && (
                        <section style={styles.section}>
                            <h3 style={{ ...styles.h3 }}>Final Plan ({finalPlan.optionName})</h3>
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
                            <button onClick={onSavePlan} disabled={saveStatus === 'Saving...'} style={{ ...styles.button, ...(saveStatus === 'Saving...' ? styles.buttonDisabled : {}) }}>
                                {saveStatus === 'Saving...' ? 'Saving...' : 'Save Plan'}
                            </button>
                            {saveStatus && <p style={{ marginTop: 8, fontSize: 14 }}>{saveStatus}</p>}
                        </section>
                    )}
                </section>
            )}

            <section style={styles.section}>
                <h2 style={{ ...styles.h2 }}>Saved Plans</h2>
                {loadingSavedPlans ? (
                    <p>Loading saved plans...</p>
                ) : savedPlans.length === 0 ? (
                    <p>No plans saved yet.</p>
                ) : (
                    <ul style={{ listStyle: 'none', padding: 0 }}>
                        {savedPlans.map((plan) => (
                            <li key={plan.id} style={{ marginBottom: 8, borderBottom: `1px solid ${colors.border}`, paddingBottom: 8 }}>
                                <div>
                                    <strong style={{ color: colors.textPrimary }}>{plan.option_name}</strong> (ID: {plan.id})
                                    <span style={{ fontSize: 12, color: colors.textSecondary, marginLeft: 8 }}>
                                        {new Date(plan.created_at).toLocaleString()}
                                    </span>
                                </div>
                                <p style={{ fontSize: 13, color: colors.textSecondary, margin: '4px 0' }}>
                                    Duration: {plan.total_duration} minutes
                                </p>
                                <button
                                    onClick={() => onLoadPlan(plan.id)}
                                    disabled={loadingPlanById}
                                    style={{ ...styles.button, padding: '6px 10px', fontSize: 12, ...(loadingPlanById ? styles.buttonDisabled : {}) }}
                                >
                                    {loadingPlanById ? 'Loading...' : 'Load'}
                                </button>
                            </li>
                        ))}
                    </ul>
                )}
            </section>
        </section>
    );
}