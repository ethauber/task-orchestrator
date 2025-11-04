'use client';
import { useState, FormEvent as ReactFormEvent } from 'react';
import { postJSON } from '@/lib/api';
import { Json } from '@/components/Json';

type PlanStep = { text: string };
type PlanOption = { name: string; steps: PlanStep[] };
type BreakdownResponse = { plans: PlanOption[] };

export default function BreakdownPage() {
    const [definition, setDefinition] = useState<string>(
        'Create a 10 minute talk outline by consolidating notes'
    );
    const [maxSteps, setMaxSteps] = useState<number>(5);
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState<BreakdownResponse | null>(null);
    const [err, setErr] = useState<string>('');
    // state for plan endpoint
    const [selected, setSelected] = useState<number | null>(null);
    const [budget, setBudget] = useState<number | ''>('');
    const [finalPlan, setFinalPlan] = useState<any>(null);
    const [finalLoading, setFinalLoading] = useState(false);
    const [finalErr, setFinalErr] = useState<string>("");

    async function handleSubmit(e: ReactFormEvent) {
        e.preventDefault();
        setErr('');
        setLoading(true);
        setData(null);
        try {
            const json = await postJSON<BreakdownResponse>('/breakdown', {
                definition,
                max_steps: maxSteps
            });
            setData(json);
        } catch (error) {
            setErr(String(e));
        } finally {
            setLoading(false);
        }
    }

    return (
        <section>
            <h1>Breakdown Workbench</h1>
            <form onSubmit={handleSubmit} style={{ display: 'grid', gap: 12, maxWidth: 860 }}>
                <label>
                    <div>Defintion of done</div>
                    <textarea
                        rows={6}
                        value={definition}
                        onChange={(e) => setDefinition(e.target.value)}
                        style={{ width: '100%' }}
                    />
                </label>
                <label>
                    <div>Max steps per plan (3 to 7)</div>
                    <input
                        type='number'
                        min={3}
                        max={7}
                        value={maxSteps}
                        onChange={(e) => setMaxSteps(parseInt(e.target.value || '5', 10))}
                    />
                </label>
                <button disabled={loading || definition.length < 20}>
                    {loading ? 'Generating...' : 'Generate Plan Options'}
                </button>
            </form>

            {err && <p style={{ color: 'crimson', marginTop: 12 }}>{err}</p>}

        {data && (
        <section style={{ marginTop: 24 }}>
            <h2>Plan Options</h2>

            {data.plans.map((plan, planIndex) => (
            <div key={planIndex} style={{ marginBottom: 16 }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <input
                    type="radio"
                    name="plan"
                    checked={selected === planIndex}
                    onChange={() => setSelected(planIndex)}
                />
                <strong>{plan.name}</strong>
                </label>

                <ol>
                {plan.steps.map((step: { text: string }, stepIndex: number) => (
                    <li key={stepIndex}>{step.text}</li>
                ))}
                </ol>
            </div>
            ))}

            {/* Controls belong OUTSIDE the map */}
            <div style={{ display: "flex", gap: 12, alignItems: "center", marginTop: 8 }}>
            <label>
                Time budget (minutes, optional):{" "}
                <input
                type="number"
                min={15}
                step={15}
                value={budget as number | ""}
                onChange={(e) =>
                    setBudget(e.target.value === "" ? "" : parseInt(e.target.value, 10))
                }
                />
            </label>

            <button
                disabled={selected === null || finalLoading}
                onClick={async () => {
                try {
                    setFinalErr('');
                    setFinalPlan(null);
                    setFinalLoading(true);

                    const pick = data.plans[selected as number];
                    const body = {
                        optionName: pick.name,
                        steps: pick.steps,
                        total_minutes: budget === '' ? null : budget
                    };
                    const json = await postJSON('/plan', body);
                    setFinalPlan(json);
                } catch (e) {
                    console.error(e);
                    setFinalErr(String(e));
                    setFinalPlan(null);
                } finally {
                    setFinalLoading(false);
                }
                }}
            >
                {finalLoading ? 'Finalizing...' : 'Finalize Plan'}
            </button>
            </div>

            {/* finalPlan goes RIGHT HERE, still inside the same <section> */}
            {finalPlan && (
            <section style={{ marginTop: 16 }}>
                <h3>Final Plan {finalPlan.optionName ? `(${finalPlan.optionName})` : ""}</h3>
                {"total_duration" in finalPlan && (
                <p>Total duration: {finalPlan.total_duration} min</p>
                )}
                {"steps" in finalPlan && Array.isArray(finalPlan.steps) && (
                <ol>
                    {finalPlan.steps.map((s: any, i: number) => (
                    <li key={i}>
                        {s.text} — {s.duration_minutes} min
                        {s.parked ? " (parked)" : ""}
                        {s.depends_on?.length ? ` | deps: ${s.depends_on.join(",")}` : ""}
                    </li>
                    ))}
                </ol>
                )}
            </section>
            )}

            <h3>Raw JSON</h3>
            <Json data={data} />
        </section>
        )}
        </section>
    );
}