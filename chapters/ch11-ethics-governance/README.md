# Chapter 11 — Ethical, Legal, Privacy, and Security Foundations

**Status: runnable governance laboratory.** This is a small **synthetic, illustrative policy evaluator**, not a production access-control system or a substitute for IRB review, HIPAA analysis, legal advice, or institutional security controls.

## Run from the public repository root

```bash
python chapters/ch11-ethics-governance/exercise_11_1_policy_audit.py --output-dir outputs/ch11
python -m pytest -q tests/test_chapter11_lab.py
```

The script exports `asset_inventory.csv`, `role_policy.json`, `threat_model.json`, `audit_events.json`, and `governance_summary.json`. No real identities, credentials, patient records, or neural data are used.

## Student assignment (100 points)

1. **Assets and classification (15):** Explain why raw EEG, derivatives, identity linkage, and audit logs have different protection needs. Identify owners and retention dependencies.
2. **Policy decisions (20):** Trace six example access requests and their allow/deny results. Explain why a permitted role does not imply unrestricted access.
3. **Deny-by-default testing (15):** Verify that an unknown role and access to the identity-linkage asset are denied. Add one test for a new unauthorized request.
4. **Threat modeling (20):** Expand one of the five scenarios with an asset, threat actor, entry point, preventive control, detective control, response, and residual risk. Distinguish confidentiality, integrity, and availability consequences.
5. **Audit evidence (15):** Inspect event IDs, actor roles, action, resource, timestamp, decision, and correlation ID. Explain which details should be excluded from logs to avoid unnecessary disclosure.
6. **Clinical safety and governance (15):** Propose behavior for model unavailable, unsupported input, and model-version change. Explain which approvals, policies, and technical safeguards are missing from this teaching example.

**Submission:** five generated artifacts, an architecture and trust-boundary diagram, a policy-test demonstration, and a 1–2-page risk justification.

**Graduate extension:** Design a federated three-institution policy model where raw data cannot leave its site. Compare a controlled enclave with federated analysis, including model/update provenance, privacy leakage, and participant restrictions.

**Limits:** This demonstration does not implement authentication, encryption, external policy engines, real audit storage, institutional approvals, or enforceable authorization. Do not use it to protect real research data.
