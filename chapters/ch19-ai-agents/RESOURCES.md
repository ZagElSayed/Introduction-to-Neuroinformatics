# Open resources and primary readings

- [Python standard-library documentation](https://docs.python.org/3/library/): JSON, pathlib, hashing, dataclasses, and logging.
- [ReAct paper](https://arxiv.org/abs/2210.03629): interleaving model-generated action selection with observations.
- [Toolformer paper](https://arxiv.org/abs/2302.04761): learned API use, a different training question from wiring a runtime.
- [RAG paper](https://arxiv.org/abs/2005.11401): retrieval plus generation; this studio uses exact retrieval of one approved recipe, not a vector index or generative RAG model.
- [Building effective agents](https://www.anthropic.com/research/building-effective-agents): workflow/agent distinctions and implementation patterns; tooling details evolve.
- [MCP versioned tools specification](https://modelcontextprotocol.io/specification/2025-11-25/server/tools): interoperability concepts. The studio uses local functions and does not implement an MCP server.
- [SciPy periodogram documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.periodogram.html): density scaling and one-sided conventions. To compare with this studio, pass the same explicitly constructed symmetric Hann array and detrending choices.
- [MNE-Python documentation](https://mne.tools/stable/index.html) and [PhysioNet EEGMMIDB](https://physionet.org/content/eegmmidb/1.0.0/): possible real-data extensions requiring a new input contract and approved analysis recipe.
- [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework): lifecycle risk-management background.

- [Ollama local chat API](https://docs.ollama.com/api/chat), [structured outputs](https://docs.ollama.com/capabilities/structured-outputs), and [setup](https://docs.ollama.com/quickstart): optional local model adapter; use a local model and record its version/digest.

No framework is needed for the core lab. A framework may simplify external model adapters, durable state, or tool transport later; evaluate that benefit against its added dependencies. Record versions and consult the current official documentation when implementing an extension.
