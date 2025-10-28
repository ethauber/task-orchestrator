"use client";
import { useEffect, useState } from "react";

export default function Home() {
  const [data, setData] = useState<any>(null);
  const [err, setErr] = useState<string>("");

  useEffect(() => {
    const url = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000") + "/health";
    fetch(url).then(r => r.json()).then(setData).catch(e => setErr(String(e)));
  }, []);

  return (
    <main style={{ padding: 24 }}>
      <h1>Task-Orchestrator</h1>
      <h2>Backend Health</h2>
      {err && <pre style={{color:"crimson"}}>{err}</pre>}
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </main>
  );
}
