# Three guided notebooks

| Notebook | Open in Colab | Result |
|---|---|---|
| 01 — Understand the loop | [Open](https://colab.research.google.com/github/ZagElSayed/Introduction-to-Neuroinformatics/blob/main/chapters/ch19-ai-agents/notebooks/01_understand_the_loop.ipynb) | Inspect tools, state, an ordinary run, and a stopped run |
| 02 — Build an analysis assistant | [Open](https://colab.research.google.com/github/ZagElSayed/Introduction-to-Neuroinformatics/blob/main/chapters/ch19-ai-agents/notebooks/02_build_an_analysis_assistant.ipynb) | Trace the spectral recipe and replace the baseline chooser |
| 03 — Evaluate and review | [Open](https://colab.research.google.com/github/ZagElSayed/Introduction-to-Neuroinformatics/blob/main/chapters/ch19-ai-agents/notebooks/03_evaluate_and_review.ipynb) | Generate the 20-case table and author a separate review record |

Local use: open notebooks from this directory's `notebooks/` folder or use `python run_demo.py`. The bootstrap prefers `agent_studio.py` in the local chapter directory; otherwise it downloads a pinned source revision from the public student repository, records its SHA-256, and prints the provenance. A local edited copy is identified as local and also hashed. The three notebooks share the same module, not hidden state; each can run independently. Source downloads need internet; the core analysis requires no network.

Each notebook is distributed without executed outputs. Run all cells in your own environment and retain `agent_source_manifest.json`, reports, and logs. Review cells default to an empty decision; edit them only after inspecting the displayed artifact. The studio never promotes a report to a final derivatives directory.

Figure anchors: 19.1–19.2 (model versus system; loop), 19.3–19.4 (scope and tool boundary), 19.5 (evidence retrieval), 19.6 (optional multi-role extension), 19.7–19.8 (malformed proposals and meaningful review), 19.9 (trajectory evaluation), 19.10 (NeuroBridge orchestration). The default path implements no clinical actions, MCP service, or vector RAG. Notebook 02 includes a disabled-by-default local Ollama planner extension requiring a separately installed local model.

Pinned source revision for downloaded runtime and optional adapter: `faf63f0f09cba07291e8c3d09ef95974b8404d77`. Local edited files are used as local copies and recorded by content hash.
