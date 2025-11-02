'use client';
import { useEffect, useState } from 'react';
import { API, getJSON } from '@/lib/api';
import { Json } from '@/components/Json';

type Health = { status: string; model: string; ollama_url: string };
type Ping = { response: string };

export default function HealthPage() {
    const [health, setHealth] = useState<Health | null>(null);
    const [ping, setPing] = useState<Ping | null>(null);
    const [err, setErr] = useState<string>("");

    useEffect(() => {
        (async () => {
            try {
                const h = await getJSON<Health>('/health');
                setHealth(h);
                const p = await getJSON<Ping>('/llm/ping');
                setPing(p);
            } catch (e: any) {
                setErr(String(e));
            }
        })();
    }, []);

    return (
        <section>
            <h1>Service Health </h1>
            { err && <p style={{ color: 'crimson' }}>{err}</p> }
            <h3>Backend</h3>
            <Json data={health ?? { loading: true, api: `${API}/health`}} />
            <h3>LLM Ping</h3>
            <Json data={ping ?? { loading: true, api: `${API}/llm/ping`}} />
        </section>
    )
}