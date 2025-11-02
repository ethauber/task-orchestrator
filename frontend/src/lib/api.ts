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