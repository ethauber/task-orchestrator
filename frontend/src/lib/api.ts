import { useState, useCallback } from "react";

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

export async function streamPost<T>(
    path: string,
    body: any,
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
            if (line.startsWith('data: ')) {
                const data = JSON.parse(line.slice(6));
                if (data.type === 'thinking') {
                    onContent(data.data);
                } else if (data.type === 'done') {
                    finalData = data.data;
                } else if (data.type === 'error') {
                    throw new Error(data.data);
                }
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
    async <T,>(path: string, body: any): Promise<T | null> => {
      setError("");
      setStreaming("");
      setLoading(true);

      try {
        const result = await streamPost<T>(
          path, body,
          (text) => setStreaming((prev) => prev + text)
        );
        return result;
      } catch (err: any) {
        setError(String(err));
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