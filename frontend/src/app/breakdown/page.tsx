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
                    {data.plans.map((p, i) => (
                        <div key={i} style={{ marginBottom: 16 }}>
                            <h3>{p.name}</h3>
                            <ol>
                                {p.steps.map((s, j) => <li key={j}>{s.text}</li>)}
                            </ol>
                        </div>
                    ))}
                    <h3>Raw JSON</h3>
                    <Json data={data} />
                </section>
            )}
        </section>
    );
}