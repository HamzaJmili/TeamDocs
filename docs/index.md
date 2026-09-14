# TeamDocs: knowledge with receipts

**A practical guide for users, recruiters, and the person maintaining the code.**

TeamDocs helps someone find information in a small company document library. Ask a question, see relevant evidence, and open the source. In live mode, an AI model can turn those passages into a short answer.

Imagine joining a company and asking: **“How do I get staging access?”** Instead of searching several handbooks, you get the access instructions and can inspect the original section immediately.

The included company, Northstar, is fictional. Its 20 documents are original demonstration content, not actual workplace policy. The default mode makes no model API calls.

![How the application works](_static/architecture.svg)

## Choose your path

- **Just exploring?** Start with the user guide.
- **Running the project?** Start with setup, then Render deployment.
- **Preparing an interview?** Read the architecture, decisions and interview guide.
- **Checking the claims?** Read evaluation and limitations.

```{toctree}
:maxdepth: 2
:caption: Project handbook

user-guide
setup
architecture
decisions
evaluation
deployment
interview
limitations
api
```

