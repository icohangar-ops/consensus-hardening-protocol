# CHP Hardening Analysis
## Leveraging TLP v2.2.4 Mechanics — VCL-Free, CHP-Branded

**Prepared for:** Sam Desigan / Cubiczan  
**Date:** 2026-05-18  
**Scope:** Gap analysis between the current Consensus Hardening Protocol repo and TLP v2.2.4, with actionable hardening recommendations  
**Constraint:** All VCL (Value Constraint Ladder) references removed. CHP remains the code brand throughout.

---

## 1. Executive Summary

CHP already implements the structural backbone of TLP — R0 gate, foundation attack, adversarial disclosure, EXPLORING → PROVISIONAL_LOCK → LOCKED state machine, payload envelopes, third-party validation, and council spawn primitives. What it's missing are the **enforcement teeth** that make TLP a hardened protocol rather than a suggested workflow. The gaps fall into five categories:

| Gap Category | Severity | Effort |
|---|---|---|
| **Phase gate enforcement** — spec must lock before implementation | Critical | Medium |
| **Payload integrity** — echo verification, marker validation, retransmission | Critical | Low |
| **Round discipline** — max 5, R5 forcing, flip criteria on every PROVISIONAL | High | Low |
| **Model parity gate** — halt on significant asymmetry | Medium | Low |
| **Blind spot & vulnerability tracking** — carried forward, audited at closure | Medium | Medium |

The SuperServe sandbox integration and the FinancialAnalysisGuard are genuine differentiators that TLP doesn't have. The hardening work is about **tightening the state machine and adding enforcement primitives**, not rearchitecting.

---

## 2. What CHP Already Has (No Action Needed)

These are implemented and aligned with TLP. Confirming so we don't over-engineer:

- R0 gate (Solvable / Scoped / Valid / Worth_it) with FATAL halt
- Foundation Disclosure (3 weakest assumptions, 2 invalidation conditions, 1 key vulnerability)
- Foundation Attack with scoring and ≥70% gate
- Pre-session context check with DUPLICATE / RELATED / SPARSE assessment
- EXPLORING → PROVISIONAL → PROVISIONAL_LOCK → LOCKED → CONVERGED status progression
- Third-party validation requirement before LOCKED
- `BEGIN_PAYLOAD` / `END_PAYLOAD` envelopes
- `STATE_SNAPSHOT` persistence
- Origin 3-section contract (Core Problem, Partner Packet, Transmission Checklist)
- Partner 7-section contract (Item Agreements, Winner Framing, Scoring Table, Objections, Frameworks, Convergence Plan, State Snapshot)
- Council spawn primitive for high-stakes / low-confidence
- `TriangulationRunner` adversary pass
- `AdversaryMeshAgent` wrapper
- SuperServe sandbox execution (CHP-unique, not in TLP)
- `FinancialAnalysisGuard` with 100% verification floor (CHP-unique)
- CFO accuracy policy demoting unresolved outputs (CHP-unique)

---

## 3. Critical Gaps — Must Fix

### 3.1 Phase Gate Enforcement

**TLP spec:** Phase 1 (Spec Convergence, Rounds 1–2) must LOCK or PROVISIONAL_LOCK before Phase 2 (Implementation QA, Rounds 3–5) can begin. If Round >2 and Phase 1 status is still EXPLORING or PROVISIONAL → `PHASE_GATE_FAIL` → HALT.

**CHP status:** README mentions "Phase 1 gate enforcement before implementation rounds" but the enforcement logic is unclear. The `PROVISIONAL_LOCK` bridge (a Phase 1 item at ≥90% from both sides but awaiting third-party can proceed to Phase 2, where third-party validation acts as the Phase 2 entry test) is not documented.

**Action items:**

1. Add `PhaseGate` class to `src/cme/chp/` with explicit state checks:
   - `LOCKED` → proceed to Phase 2
   - `PROVISIONAL_LOCK` → proceed (third-party validation becomes Phase 2 entry condition)
   - `EXPLORING` or `PROVISIONAL` at Round >2 → `PHASE_GATE_FAIL` verdict, halt protocol
2. Wire `PhaseGate.check()` into the round advancement logic so it's impossible to skip
3. Add test: attempt to advance to Round 3 with Phase 1 in EXPLORING → assert HALT

### 3.2 Payload Integrity Enforcement

**TLP spec:** Every payload requires a `PAYLOAD_ECHO` in the STATE_SNAPSHOT confirming receipt of the prior payload by ID. Missing marker → retransmit with new ID. Echo mismatch → reject + resend. The 6-character alphanumeric ID is structurally required.

**CHP status:** `BEGIN_PAYLOAD` / `END_PAYLOAD` envelopes and `PAYLOAD_ECHO` are referenced but the **rejection and retransmission logic** is not documented as implemented.

**Action items:**

1. Add `PayloadValidator` class:
   - `validate_echo(received_id, expected_id) → CONFIRMED | MISMATCH`
   - `on_mismatch() → generate_new_id() + retransmit()`
   - `on_missing_marker() → retransmit_with_new_id()`
2. Generate 6-char alphanumeric IDs deterministically (e.g., `hashlib.sha256(round + content)[:6]`)
3. Make echo validation a gate — no state advancement without confirmed echo
4. Add tests: missing echo → retransmit; mismatched echo → reject + resend

### 3.3 Round 5 Forcing

**TLP spec:** Round 5 is terminal. No item can remain PROVISIONAL at Round 5 — it must be forced to LOCKED (if ≥90% + third-party) or UNRESOLVED. Max 5 rounds is a hard constraint.

**CHP status:** "Round 5 PROVISIONAL → UNRESOLVED forcing" and "max-5-round enforcement" are listed as implemented. **Verify** that the forcing logic handles the edge case where an item is at PROVISIONAL_LOCK (≥90% but awaiting third-party) at Round 5 — TLP says this should also resolve, not hang.

**Action items:**

1. Audit the R5 forcing code path for PROVISIONAL_LOCK items without third-party confirmation
2. Decision: either auto-escalate to UNRESOLVED (conservative) or allow a grace window for third-party (pragmatic). Document the choice.
3. Add test: PROVISIONAL_LOCK at R5 without third-party → assert resolution

---

## 4. High-Priority Gaps — Should Fix

### 4.1 Model Parity Gate

**TLP spec (v2.2.4 addition):** Before session declaration, both models must be declared. If the delta is SIGNIFICANT (full generation gap) → HALT with user-facing warning. If MINOR → proceed with advisory logged in STATE_SNAPSHOT.

**CHP status:** "Model parity checks that halt on significant asymmetry" is listed but the delta classification logic (NONE / MINOR / SIGNIFICANT) and the user-facing HALT rendering are not detailed.

**Action items:**

1. Add `ModelParityGate` with explicit delta definitions:
   - `NONE`: same tier, same generation
   - `MINOR`: one tier difference (e.g., Sonnet vs GPT-4o)
   - `SIGNIFICANT`: full generation gap or major capability difference
2. On SIGNIFICANT → halt with structured error output (no emoji blocks in code — use clear text labels like `[HALT]`)
3. On MINOR → log advisory in STATE_SNAPSHOT, continue
4. Store model declarations in session metadata for audit trail

### 4.2 Flip Criteria Enforcement

**TLP spec:** Every item at PROVISIONAL status must have explicit `FLIP_CRITERIA` — the specific evidence that would change the position. This is not optional.

**CHP status:** "flip criteria" is mentioned in partner packet primitives but it's unclear whether the protocol **enforces** that PROVISIONAL items without flip criteria are rejected.

**Action items:**

1. Add validation rule: `if status == PROVISIONAL and flip_criteria is None → REJECT`
2. Surface missing flip criteria as a transmission checklist failure
3. Add test: PROVISIONAL item without flip criteria → assert rejection

### 4.3 Single-Winner Scoring Enforcement

**TLP spec:** Scoring table must have exactly one winner. No ties. Inferior options get a 2-line elimination note.

**CHP status:** "single-winner scoring validation" is listed as implemented. Confirm the elimination note requirement is enforced.

**Action items:**

1. Verify scoring table validation rejects ties
2. Add elimination note as a required field (not optional)
3. Add test: scoring table with tie → assert rejection

### 4.4 Devil's Advocate at Round 3 Entry

**TLP spec:** Devil's Advocate runs twice — once after Phase 0 Foundation Attack, once at Round 3 entry (Phase 2 entry). The second devil's advocate is explicitly about challenging whether convergence is premature.

**CHP status:** "Phase 0 devil's advocate capture and Round 3 implementation devil's advocate support" is listed. Verify the Round 3 trigger is automatic (not optional) and that it produces the three required arguments: WHY_DIRECTION_WRONG, WHAT_NOT_SEEING, FALSE_CONSENSUS_RISK.

**Action items:**

1. Make Round 3 devil's advocate a gate — cannot proceed to Round 3 scoring until devil's advocate completes
2. Require all three arguments (not just freeform text)
3. Feed devil's advocate output into STRUCTURAL_VULNERABILITIES carried forward

---

## 5. Medium-Priority Gaps — Strengthen Over Time

### 5.1 Blind Spot Tracking (Replaces VCL)

**Context:** TLP uses VCL (Value Constraint Ladder) for altitude diagnosis — a 10-rung ladder from Physical (R1) to Ontology (R10) that classifies where each decision item sits. You've asked to remove all VCL references.

**What VCL actually does:** It forces both parties to diagnose *why* a lower-level fix won't work by identifying the constraint altitude. This prevents the protocol from cycling on symptoms when the real constraint is structural.

**CHP replacement — Constraint Altitude Tagging (CAT):**

Instead of the full 10-rung VCL ladder, implement a simpler 3-tier constraint classification that serves the same diagnostic function under the CHP brand:

| Tier | Label | Maps to | Example |
|---|---|---|---|
| **T1** | Tactical | Execution-level (task, process, habit) | "We need to fix the deployment script" |
| **T2** | Structural | System/capability/relationship | "Our CI pipeline architecture can't support this" |
| **T3** | Strategic | Identity/values/philosophy | "This conflicts with our risk tolerance as a company" |

**Rule:** Higher tier constrains lower. If a T1 fix keeps failing, diagnose whether a T2 or T3 constraint is blocking it.

**Action items:**

1. Add `ConstraintAltitude` enum: `TACTICAL`, `STRUCTURAL`, `STRATEGIC`
2. Require constraint altitude tag on every objection (currently objections are freeform)
3. Add batching rule: resolve T3 first, then T2, then T1
4. Remove all VCL references from existing code and docs
5. Update STATE_SNAPSHOT to carry `CONSTRAINT_DIAGNOSIS` per item

### 5.2 Blind Spot & Structural Vulnerability Audit at Closure

**TLP spec:** Convergence closure requires:
- `BLIND_SPOTS_FINAL` with Resolved and Accepted lists
- `STRUCTURAL_VULNERABILITIES_FINAL` with Addressed and Accepted_Risk lists
- These are auditable — they're part of the permanent decision record

**CHP status:** The convergence-closure primitive exists but the README doesn't mention blind spot or vulnerability final audits.

**Action items:**

1. Add `ClosureAudit` dataclass:
   - `blind_spots_resolved: List[str]`
   - `blind_spots_accepted: List[str]`
   - `vulnerabilities_addressed: List[str]`
   - `vulnerabilities_accepted_risk: List[str]`
2. Require ClosureAudit as a mandatory field in convergence closure output
3. For finance workflows: if `vulnerabilities_accepted_risk` is non-empty, auto-tag output as `REQUIRES_HUMAN_VERIFICATION` (consistent with existing CFO accuracy policy)

### 5.3 Pre-Flight Prior Beliefs Declaration

**TLP spec:** Round 1 requires each party to declare:
- `MY_PRIOR_BELIEFS`: position + confidence (0–100%) per item
- `BLIND_SPOTS`: 1–3 areas of acknowledged uncertainty

This creates an auditable record of where each party started, making it possible to detect confirmation bias.

**CHP status:** Not mentioned in README. Likely not implemented.

**Action items:**

1. Add `PreFlight` dataclass with prior beliefs and blind spots
2. Require pre-flight in Round 1 output (origin and partner)
3. At closure, compare final positions to pre-flight — flag items where position didn't change despite objections (potential confirmation bias signal)

### 5.4 Interruption Recovery

**TLP spec:** If a session is interrupted mid-round, the protocol captures partial state and offers options: Continue, Restart Phase, or Next Round. This prevents data loss in long sessions.

**CHP status:** Not mentioned. Given that CHP sessions can involve multiple rounds across multiple models (with a human bridge), interruption recovery is operationally important.

**Action items:**

1. Add `InterruptionRecovery` class that captures:
   - Current phase and round
   - Last completed section
   - All decision item states
   - Foundation score (if Phase 0 complete)
2. On resume, surface recovery options and allow continuation from last good state
3. Store partial state in the same persistence layer as STATE_SNAPSHOT

### 5.5 Section Limit Enforcement

**TLP spec:** Hard limits on every section — 3 lines/item for agreements, 4 sentences for winner framing, 5 max objections at 2 lines each, etc. If exceeded → "tighten -1 next round."

**CHP status:** Strict packet contract checks are listed but section-level limits aren't detailed.

**Action items:**

1. Add section limit constants to the packet validator
2. On limit exceeded: log warning + flag for tightening in next round
3. Useful for controlling token costs when running through LLM APIs

---

## 6. Structural Recommendations (CHP-Specific)

These are not TLP gaps — they're hardening opportunities unique to CHP's architecture.

### 6.1 Unify the Raw Text Parser

**README explicitly calls out** "raw text parser for converting partner 7-section packets into the structured packet model" as remaining work. This is a blocker for true cross-model interop. Without it, partner packets from ChatGPT or other models can't be ingested programmatically.

**Recommendation:** Build a section-boundary parser that:
- Splits on section headers (ITEM_AGREEMENTS, WINNER_FRAMING, etc.)
- Validates section count (7 for standard, 2 for Phase 0 / Council)
- Extracts structured fields (agreement percentages, status labels, flip criteria)
- Rejects malformed packets with specific error messages

### 6.2 Harden the FinancialAnalysisGuard → CHP Pipeline

The 100% verification floor for finance is a strong policy. Harden it by:

1. Making the guard a formal CHP gate (not a post-hoc check) — if the guard fires, the CHP session state should reflect it (e.g., auto-set status to UNRESOLVED)
2. Logging guard triggers in the STATE_SNAPSHOT for audit trail
3. Adding a `GUARD_TRIGGER` section to the convergence closure report

### 6.3 SuperServe as Third-Party Validator

TLP requires third-party validation before LOCKED. CHP has SuperServe sandboxes. Natural fit:

- For code proposals: SuperServe sandbox execution *is* the third-party validation
- Run the proposal in isolation, capture exit code + output, use pass/fail as the validation result
- Log sandbox ID in `THIRD_PARTY_VALIDATION` block for audit

This turns SuperServe from an R0-only gate into a full lifecycle validator.

---

## 7. Implementation Priority Matrix

| Priority | Item | Files Affected | Est. Effort |
|---|---|---|---|
| **P0** | Phase gate enforcement (3.1) | `chp/gates.py`, round advancement logic | 1 day |
| **P0** | Payload integrity enforcement (3.2) | `chp/payload.py` or new `chp/integrity.py` | 0.5 day |
| **P0** | R5 forcing audit (3.3) | `chp/state.py` | 0.5 day |
| **P1** | Model parity gate (4.1) | `chp/gates.py`, session init | 0.5 day |
| **P1** | Flip criteria enforcement (4.2) | `chp/packet.py`, validator | 0.5 day |
| **P1** | Devil's advocate R3 gate (4.4) | `chp/adversary.py` | 0.5 day |
| **P1** | Raw text parser (6.1) | New `chp/parser.py` | 2 days |
| **P2** | Constraint Altitude Tagging — VCL replacement (5.1) | New `chp/constraint.py`, objection model | 1 day |
| **P2** | Closure audit (5.2) | `chp/closure.py` | 0.5 day |
| **P2** | Pre-flight declarations (5.3) | `chp/preflight.py` | 0.5 day |
| **P2** | Interruption recovery (5.4) | `chp/recovery.py` | 1 day |
| **P2** | Section limit enforcement (5.5) | `chp/packet.py` | 0.5 day |
| **P2** | SuperServe as third-party validator (6.3) | `chp_superserve.py`, validation pipeline | 1 day |
| **P2** | FinancialAnalysisGuard → CHP gate (6.2) | `chp/gates.py`, `finance/guard.py` | 0.5 day |

**Total estimated effort:** ~10 developer-days for full hardening.

---

## 8. VCL Removal Checklist

All references to VCL (Value Constraint Ladder) should be removed from:

- [ ] README.md — replace "VCL diagnosis" with "Constraint Altitude Tagging (CAT)"
- [ ] `src/cme/chp/` — remove VCL diagnosis from origin packet template, replace with CAT
- [ ] Partner packet SHAPE_LOCK — remove VCL section requirement, add CAT requirement on objections
- [ ] STATE_SNAPSHOT — remove VCL fields, add `CONSTRAINT_DIAGNOSIS` per item
- [ ] Transmission checklist — remove "VCL present" check, add "Constraint altitude tagged" check
- [ ] Tests — update any VCL-specific assertions
- [ ] Subsystem table in README — remove "VCL diagnosis" from CHP description
- [ ] Verification checklist — remove "VCL present" line

The CAT replacement (Section 5.1) gives you the same diagnostic function — forcing constraint-level diagnosis on objections — without the TLP-branded terminology.

---

## 9. Updated README Subsystem Table (Proposed)

| Subsystem | Role | Spec |
|---|---|---|
| **Consensus Hardening Protocol** | Cross-model decision hardening with gates, packets, lock states, adversarial foundation attack, constraint altitude tagging, and third-party validation | `cme.chp` |
| **Cognitive Mesh Protocol** | Structured expansion ↔ compression reasoning with grounding checks | `cognitive-mesh-protocol.skill` |
| **Context Engineering Framework** | Layered short/long-term memory + entity/event/task schema | `context-engineering-framework.skill` |
| **Agentic Context Engineering** | Evolving playbooks with Generator/Reflector/Curator, delta-only updates | `agentic-context-engineering.skill` |
| *Statement & workflow synthesizer* | Turns multi-agent output into a vivid problem statement + executable workflow | *(bundled)* |

---

## 10. Bottom Line

CHP is 70–75% of the way to a fully hardened protocol. The remaining work is enforcement logic, not new concepts. The three critical items (phase gate, payload integrity, R5 forcing) are each under a day of work and would close the biggest reliability gaps. The Constraint Altitude Tagging replacement for VCL is clean, simpler, and brand-aligned.

The SuperServe integration is a genuine moat — TLP has no execution sandbox concept. Extending it from R0-only to full-lifecycle third-party validation would be the single highest-leverage differentiator for CHP as a product.
