'use client';
import { useState, FormEvent as ReactFormEvent } from 'react';

import type {
    RefineResponse,
    BreakdownResponse,
    PlanResponse
} from '@/lib/types';
import { postJSON, streamPost, useStreamingAction } from '@/lib/api';
import { Json } from '@/components/Json';

import useSystemDarkMode from './systemAppearance';


export default function BreakdownPage() {
    // Step 1: refine
    // example 'Create a 10 minute outline by consolidating notes'
    const [idea, setIdea] = useState<string>('');
    // const [refineLoading, setRefineLoading] = useState(false);
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
    //
    const isDarkMode = useSystemDarkMode();

    const refineStream = useStreamingAction();
    const breakdownStream = useStreamingAction();
    const finalizeStream = useStreamingAction()

    async function onRefine(e: ReactFormEvent) {
        e.preventDefault();
        refineStream.setError('');
        setRefined(null);
        setPlans(null);
        setSelected(null);
        setFinalPlan(null);
        setAnswers([]);

        // try {
        //     setRefineLoading(true);
        //     const json = await postJSON<RefineResponse>('/refine', { idea });
        //     setRefined(json);
        //     setAnswers(new Array(json.questions.length).fill(''));
        // } catch (error: any) {
        //     setRefineErr(String(error));
        // } finally {
        //     setRefineLoading(false);
        // }
        const result = await refineStream.run<RefineResponse>('/stream/refine', { idea });

        if (!result) return;

        setRefined(result);
        // setAnswers(new Array(result.questions.length).fill(""));
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
                <button disabled={refineStream.loading || idea.length < 10} style={{ ...styles.button, ...(refineStream.loading || idea.length < 10 ? styles.buttonDisabled : {})}}>
                    {refineStream.loading ? 'Refining...' : 'Refine Idea'}
                </button>
            </form>
            {refineStream.error && <p style={{ ...styles.error }}>{refineStream.error}</p>}

            {refineStream.streaming && (
                <div style={styles.thinking}>
                    <div style={{ fontSize: 11, fontWeight: 600, marginBottom: 8, opacity: 0.7 }}>
                        🤔 AI is thinking...
                    </div>
                    {refineStream.streaming}
                </div>
            )}
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

                    {/* <h3 style={{...styles.h3}}>Raw JSON</h3>
                    <Json data={plans} /> */}
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
                            {/* <h4>Raw JSON</h4>
                            <Json data={finalPlan} /> */}
                        </section>
                    )}
                </section>
            )}
        </section>
    );
}