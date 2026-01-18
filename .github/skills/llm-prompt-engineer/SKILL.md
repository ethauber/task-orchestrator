# Skill: LLM Prompt Engineer

## Description
This skill guides the creation and modification of LLM prompts stored in the `backend/llm/prompts/` directory.

## Rules
1.  **File Format:** All prompts must be stored as **JSON** files.
2.  **Structure:** The JSON object must have at least two keys: `system` and `human`.
    *   `system`: The instructions for the AI behavior.
    *   `human`: The template for the user's input.
3.  **Variables:** Preserve existing variables wrapped in curly braces (e.g., `{input}`, `{steps}`). Do NOT remove them unless explicitly instructed.
4.  **JSON Validity:** Ensure the file is valid JSON. Escape quotes within strings (e.g., `"`). Use `\n` for newlines.
5.  **Naming:** Filenames should be snake_case (e.g., `plan_refinement.json`).

## Example
**File:** `backend/llm/prompts/example.json`

```json
{
    "system": "You are a helpful assistant.\n\nRules:\n1. Be concise.\n2. Use markdown.",
    "human": "Please help me with: {user_query}"
}
```

## Procedure
1.  **Read:** If modifying, read the existing file first to understand the context and variables.
2.  **Edit:** Apply changes to the `system` or `human` fields.
3.  **Verify:** Check that all brackets match and JSON is valid.
