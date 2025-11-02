"use client";
import { useEffect, useState } from "react";

export default function Home() {
  return (
    <section>
      <h1>Task-Orchestrator</h1>
      <p>Pick a page from the nav to get started:</p>
      <ul>
        <li><a href='/health'>Service Health</a></li>
        <li><a href='/breakdown'>Breakdown Workbench</a></li>
      </ul>
    </section>
  )
}
