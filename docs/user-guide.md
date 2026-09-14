# Using TeamDocs

## Choose the interface language

Use the **English / Français** selector in the top bar. TeamDocs remembers your choice in this browser. Navigation, buttons, filters, status messages and evaluation labels switch immediately, including on mobile.

This setting translates the interface only. Document titles, source passages, evaluation questions and AI answers retain their original text. The starter cards keep their original English question when submitted, and collection values sent to the API do not change. The project documentation remains in English. No translation API call or additional key is needed.

## Ask the library

Type a question and press Enter or select **Find answers**. Shift+Enter inserts a new line. The `/` shortcut focuses the question field when you are not already typing elsewhere.

Try these examples:

- How do I request access to the staging environment?
- What should I do during my first week?
- How do I report a security incident?
- When must I submit an expense claim?

Choose a collection if your question belongs to People, Engineering, Security, IT Support or Product. A filter limits which documents can be retrieved; it does not grant permissions.

## Read the evidence

Numbered source buttons open the original passage in the source reader. The highlighted section is the one referenced by the result. You can also download the original Markdown or PDF document. PDF citations retain the original page number; Markdown citations use section names.

The source panel can contain additional retrieved passages that were not cited. These are ranked search results, not proof that every passage answers your question.

## Understand the two modes

| Mode | What happens | What to expect |
| --- | --- | --- |
| Demo | Real BM25 keyword retrieval; selected sentences are quoted verbatim | No AI key, no generated answer, and limited handling of paraphrases |
| Live | Keyword, semantic or hybrid retrieval; the model writes source-linked claims | Requires API credentials and prebuilt embeddings; may still make mistakes |

Demo mode uses a simple word-overlap rule to decide whether to display an excerpt. It may find a related passage for an unanswerable question. **An excerpt is not a confident answer or a calibrated refusal.**

In live mode, the model is instructed to decline questions that the passages cannot support. This is a model behavior to evaluate, not a guarantee.

## Explore the library and quality lab

The library lets you filter documents by title or description, then open their passages. The quality lab shows the checked-in evaluation report and explains its scope. It does not manufacture performance numbers when no report exists.

## Feedback and privacy

Helpful/not-helpful feedback is attached to the current answer ID in server memory. It is temporary, has no account association, and disappears on restart. Questions are not stored by the application. In live mode, questions and selected passages are sent to your selected AI provider (Gemini or OpenAI); use only public demonstration content. OpenAI calls request `store=false`; provider data policies still apply. Gemini free-tier data may be used to improve Google products. This public demo is not designed for confidential material.

