import { useState, useCallback } from "react";
import { PlanSummary, FullPlanResponse, PlanResponse } from './types';

export const API =
    (process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000').replace(/\/$/, '');

export async function getJSON<T>(path: string): Promise<T> {
    const r = await fetch(`${API}${path}`, { cache: 'no-store' });
    if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
    return r.json();
}

export async function postJSON<T>(path: string, body: unknown): Promise<T> {
    const r = await fetch(`${API}${path}`, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify(body)
    });
    if (!r.ok) {
        const text = await r.text().catch(() => '');
        throw new Error(`${r.status} ${r.statusText} ${text}`);
    }
    return r.json();
}

export async function savePlan(planData: PlanResponse, initialIdea?: string, refinedIdea?: string): Promise<number> {
    const response = await postJSON<number>('/plans', {
        plan_data: planData,
        initial_idea: initialIdea,
        refined_idea: refinedIdea
    });
    return response;
}

export async function listPlans(): Promise<PlanSummary[]> {
    const response = await getJSON<PlanSummary[]>('/plans');
    return response;
}

export async function getPlan(planId: number): Promise<FullPlanResponse> {
    const response = await getJSON<FullPlanResponse>(`/plans/${planId}`);
    return response;
}


type StreamMessage<T> =
    | { type: 'thinking'; data: string }
    | { type: 'done'; data: T }
    | { type: 'error'; data: string };

export async function streamPost<T>(
    path: string,
    body: unknown,
    onContent: (text: string) => void
): Promise<T> {
    const res = await fetch(`${API}${path}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    })
    if (!res.ok) throw new Error(await res.text());

    const reader = res.body!.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    let finalData: T | null = null;

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
            if (!line.startsWith('data: ')) continue;

            const parsed = JSON.parse(line.slice(6)) as StreamMessage<T>;
            if (parsed.type === 'thinking') {
                onContent(parsed.data);
            } else if (parsed.type === 'done') {
                finalData = parsed.data;
            } else if (parsed.type === 'error') {
                throw new Error(parsed.data);
            }
        }
    }

    if (!finalData) throw new Error('No data received');
    return finalData;
}

export function useStreamingAction() {
    const [streaming, setStreaming] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const run = useCallback(
        async <T,>(path: string, body: unknown): Promise<T | null> => {
            setError("");
            setStreaming("");
            setLoading(true);

            try {
                const result = await streamPost<T>(
                    path, body,
                    (text) => setStreaming((prev) => prev + text)
                );
                return result;
            } catch (err: unknown) {
                setError(err instanceof Error ? err.message : String(err));
                return null;
            } finally {
                setLoading(false);
            }
        },
        []
    );

    return {
        streaming, loading, error,
        run,
        setError,      // for manual overrides
        setStreaming,  // optional
    };
}