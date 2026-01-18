# Strategic Roadmap: Next-Gen Capabilities

This document outlines the strategic roadmap for elevating **Task-Orchestrator** into an intelligent, agentic system. These initiatives focus on integrating cutting-edge Generative AI capabilities—specifically Multimodal reasoning, Retrieval-Augmented Generation (RAG), and Autonomous Tool Execution—to demonstrate advanced proficiency in modern AI software engineering.

---

## 1. Multimodal Ideation ("Whiteboard-to-Plan")

**Objective:** Enable the system to accept and reason over visual inputs, bridging the gap between analog brainstorming (whiteboards, sketches) and digital task management.

*   **Core Capability:** **Vision Language Models (VLMs)**.
*   **User Value:** Users can photograph a messy whiteboard session or upload a screenshot of a technical diagram, and the system will parse the visual information to generate a structured plan.
*   **Technical Implementation:**
    *   **Frontend:** Integrate a drag-and-drop file upload interface supporting image formats (PNG, JPG, WEBP).
    *   **Backend:** Refactor the `/refine` endpoint to handle `multipart/form-data`.
    *   **AI:** Integrate local VLMs (e.g., `Llava` or `Qwen-VL` via Ollama). Use LangChain's multimodal abstractions to combine visual tokens with text prompts for the refinement chain.

## 2. Context-Aware Planning (RAG)

**Objective:** Ground the AI's reasoning in user-provided documents, moving beyond generic knowledge to hyper-personalized, context-specific planning.

*   **Core Capability:** **Retrieval-Augmented Generation (RAG)**.
*   **User Value:** A user can upload a syllabus, a requirements doc, or a codebase snippet. The system generates a plan that explicitly references and adheres to the constraints and data found in those documents.
*   **Technical Implementation:**
    *   **Frontend:** File attachment UI for documents (PDF, TXT, MD).
    *   **Backend:** Implement a transient ingestion pipeline using `LangChain` document loaders and text splitters.
    *   **Vector Store:** Utilize a lightweight, local vector store (e.g., `Chroma` or `FAISS`) with local embeddings (e.g., `nomic-embed-text`) to retrieve relevant context chunks during the `/breakdown` phase.

## 3. Autonomous Step Execution (Agentic Workflow)

**Objective:** Transition the system from a passive planner to an active agent capable of performing work.

*   **Core Capability:** **Agentic Loops & Tool Use (Function Calling)**.
*   **User Value:** Instead of just listing "Research competitors," the system provides a "Run" button. Upon clicking, the system actively searches the web, aggregates findings, and attaches a summary to the task.
*   **Technical Implementation:**
    *   **Backend:** Extend the existing **LangGraph** architecture to include an "Executor" node. Define a registry of tools (e.g., `WebSearch`, `Calculator`, `FileIO`).
    *   **Frontend:** Implement a real-time streaming UI to visualize the agent's chain of thought (e.g., *"Thinking...", "Calling Tool: Search...", "Processing Result..."*), providing transparency and trust.

    ### Design Decision: Search Tool Provider
    For the initial implementation, **DuckDuckGo Search** (via `langchain-community`) is selected over alternatives like Google/SerpApi or Tavily.
    *   **Zero Config:** It requires no API keys, preserving the project's "clone and run" simplicity.
    *   **Privacy:** It aligns with the local-first, privacy-conscious philosophy of the architecture.
    *   **Simplicity:** It allows for rapid prototyping of the agentic loop without external dependencies.
    *   *Note:* For future production-grade requirements (e.g., cleaner markdown extraction), paid APIs like Tavily may be considered.

---

**Execution Strategy:**
The recommended immediate priority is **Feature #3 (Autonomous Step Execution)**. This builds directly upon the existing `mcp_server` and `LangGraph` foundation and delivers the most significant shift in user experience—transforming the application from a text generator into a productivity agent.
