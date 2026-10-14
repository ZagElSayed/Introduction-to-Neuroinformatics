# Chapter 10 — Primary Resources

These are reference materials, not additional requirements to install or deploy services.

| Resource | Read for | Connect to the assignment |
|---|---|---|
| [NIST definition of cloud computing](https://doi.org/10.6028/NIST.SP.800-145) | Cloud service characteristics | Explain how cloud differs from simply using a remote server |
| [PostgreSQL transactions](https://www.postgresql.org/docs/current/tutorial-transactions.html) | All-or-nothing database updates | Explain why catalog transactions do not automatically include external object storage |
| [Nextflow caching and resuming](https://docs.seqera.io/nextflow/cache-and-resume) | Task hashes, cache modes, retained outputs | Identify assumptions before reusing a previous derivative |
| [Snakemake documentation](https://snakemake.readthedocs.io/en/stable/) | Rules and dependencies | Express validation and publication as separate tasks |
| [Apptainer GPU support](https://apptainer.org/docs/user/main/gpu.html) | Host drivers and container dependencies | Explain what image pinning leaves outside the image |
| [Python `os.replace`](https://docs.python.org/3/library/os.html#os.replace) | File replacement and its scope | Distinguish local publication from distributed commit and crash recovery |
| [HTTP semantics, status 202](https://www.rfc-editor.org/rfc/rfc9110.html#section-15.3.3) | Accepted asynchronous processing | Explain why accepted does not mean scientifically approved |
| [Python SQLite interface](https://docs.python.org/3/library/sqlite3.html) | Local SQL catalog and transaction handling | Follow the run-to-artifact index in Exercise 10.2 |
| [DataLad handbook](https://handbook.datalad.org/) | Versioned data/code relationships | Plan how dataset versions and execution evidence are connected |

Chapter 9 establishes standards and semantic validation. Chapter 10 operates the workflow. Chapter 11 governs access and intended use. Later signal-processing chapters define scientifically justified preprocessing; this centering exercise does not replace them.

## Read alongside the revised figures

Use Figures 10.1–10.8 as a connected design review: lifecycle, catalog, compute placement, dependencies, reproducibility stack, observability, recovery, and final NeuroBridge handoff. The README maps each figure to code or a design deliverable. Exercise 10.2 deliberately provides a local recovery demonstration rather than asserting independent backup or RPO/RTO performance. No cloud or clinical service is required.
