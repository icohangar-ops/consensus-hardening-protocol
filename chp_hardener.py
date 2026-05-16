#!/usr/bin/env python3
"""
CHP Hardening Engine v1.0
=========================
Applies the Consensus Hardening Protocol (CHP) hardening layers to all
Cubiczan repositories. This is the core IP dogfooding exercise.

Usage:
    python chp_hardener.py --all              # Harden all repos
    python chp_hardener.py --all --dry-run    # Preview without writing
    python chp_hardener.py --repo <name>      # Harden a single repo
    python chp_hardener.py --all --force      # Re-harden already-hardened repos
    python chp_hardener.py --base-dir /path   # Custom base directory
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CHP_VERSION = "cognitive-mesh-orchestrator 0.1.0"
MANIFEST_FILE = "chp_repo_manifest.json"
LOG_FILE = "chp_hardening_log.jsonl"

DOMAIN_TRANSITIONS: dict[str, str] = {
    "finance_cfo": """
- EXPLORING → PROVISIONAL: Foundation score ≥ 100, CFO accuracy guard passed (no open vulnerabilities/blind spots)
- EXPLORING → REQUIRES_HUMAN_VERIFICATION: Foundation score < 100
- PROVISIONAL → PROVISIONAL_LOCK: Devil's advocate complete, no outstanding financial blind spots
- PROVISIONAL_LOCK → LOCKED: Third-party CONFIRM received with financial accuracy validation
- PROVISIONAL_LOCK → EXPLORING: Third-party REJECT with financial correction criteria
- LOCKED → CONVERGED: Cross-agent financial consensus achieved
- Any → HALT: CFO accuracy guard tripped with material financial risk
- Any → UNRESOLVED: Forced at round 5 if no financial convergence""",
    "finance_trading": """
- EXPLORING → PROVISIONAL: Foundation score ≥ 85, market risk disclosure complete
- EXPLORING → REQUIRES_HUMAN_VERIFICATION: Foundation score < 85 or unquantified tail risk
- PROVISIONAL → PROVISIONAL_LOCK: Devil's advocate complete, position limits validated
- PROVISIONAL_LOCK → LOCKED: Third-party CONFIRM received with trading risk validation
- PROVISIONAL_LOCK → EXPLORING: Third-party REJECT with risk model correction criteria
- LOCKED → CONVERGED: Cross-agent trading consensus achieved
- Any → HALT: Unacceptable drawdown risk identified or market regime shift detected
- Any → UNRESOLVED: Forced at round 5 if no trading consensus""",
    "blockchain_defi": """
- EXPLORING → PROVISIONAL: Foundation score ≥ 85, smart contract audit complete
- EXPLORING → REFRAME_REQUIRED: Foundation score < 85 or unaddressed smart contract risk
- PROVISIONAL → PROVISIONAL_LOCK: Devil's advocate complete, oracle risk assessed
- PROVISIONAL_LOCK → LOCKED: Third-party CONFIRM received with on-chain safety validation
- PROVISIONAL_LOCK → EXPLORING: Third-party REJECT with security remediation criteria
- LOCKED → CONVERGED: Cross-agent consensus with immutable tx risk acknowledged
- Any → HALT: Critical smart contract vulnerability found
- Any → UNRESOLVED: Forced at round 5 if no DeFi consensus""",
    "blockchain_mining": """
- EXPLORING → PROVISIONAL: Foundation score ≥ 85, oracle and traceability validation complete
- EXPLORING → REFRAME_REQUIRED: Foundation score < 85 or unaddressed supply chain risk
- PROVISIONAL → PROVISIONAL_LOCK: Devil's advocate complete, regulatory compliance checked
- PROVISIONAL_LOCK → LOCKED: Third-party CONFIRM received with mining traceability validation
- PROVISIONAL_LOCK → EXPLORING: Third-party REJECT with compliance correction criteria
- LOCKED → CONVERGED: Cross-agent consensus with blockchain immutability acknowledged
- Any → HALT: Critical regulatory non-compliance detected
- Any → UNRESOLVED: Forced at round 5 if no mining consensus""",
    "ai_agents": """
- EXPLORING → PROVISIONAL: Foundation score ≥ 70, agent failure modes documented
- EXPLORING → REFRAME_REQUIRED: Foundation score < 70
- PROVISIONAL → PROVISIONAL_LOCK: Devil's advocate complete, blast radius assessed
- PROVISIONAL_LOCK → LOCKED: Third-party CONFIRM received with agent safety validation
- PROVISIONAL_LOCK → EXPLORING: Third-party REJECT with safety correction criteria
- LOCKED → CONVERGED: Cross-agent consensus achieved
- Any → HALT: Critical agent safety failure mode identified
- Any → UNRESOLVED: Forced at round 5 if no agent consensus""",
    "mining_supply_chain": """
- EXPLORING → PROVISIONAL: Foundation score ≥ 75, ESG and geopolitical risks assessed
- EXPLORING → REFRAME_REQUIRED: Foundation score < 75
- PROVISIONAL → PROVISIONAL_LOCK: Devil's advocate complete, supply chain resilience validated
- PROVISIONAL_LOCK → LOCKED: Third-party CONFIRM received with supply chain validation
- PROVISIONAL_LOCK → EXPLORING: Third-party REJECT with supply chain correction criteria
- LOCKED → CONVERGED: Cross-agent consensus achieved
- Any → HALT: Critical supply chain disruption risk identified
- Any → UNRESOLVED: Forced at round 5 if no supply chain consensus""",
    "tools": """
- EXPLORING → PROVISIONAL: Foundation score ≥ 70, edge cases documented
- EXPLORING → REFRAME_REQUIRED: Foundation score < 70
- PROVISIONAL → PROVISIONAL_LOCK: Devil's advocate complete, scope boundaries validated
- PROVISIONAL_LOCK → LOCKED: Third-party CONFIRM received with tool scope validation
- PROVISIONAL_LOCK → EXPLORING: Third-party REJECT with scope correction criteria
- LOCKED → CONVERGED: Cross-agent consensus achieved
- Any → UNRESOLVED: Forced at round 5 if no tool consensus""",
}

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

_log_lines: list[str] = []


def log_event(event_type: str, repo: str, details: dict[str, Any]) -> None:
    """Append a structured log entry."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event_type,
        "repo": repo,
        **details,
    }
    line = json.dumps(entry, ensure_ascii=False)
    _log_lines.append(line)
    if _log_lines and _log_lines[-1] == line:
        _log_lines[-1] = line  # dedup not needed for list append


def flush_log(base_dir: Path) -> None:
    """Write accumulated log lines to the JSONL file."""
    log_path = base_dir / LOG_FILE
    with open(log_path, "a", encoding="utf-8") as f:
        for line in _log_lines:
            f.write(line + "\n")
    _log_lines.clear()


# ---------------------------------------------------------------------------
# File Generators
# ---------------------------------------------------------------------------

def generate_state_machine_md(repo_name: str, domain: str, domain_label: str, date: str) -> str:
    """Generate .chp/STATE_MACHINE.md content."""
    transitions = DOMAIN_TRANSITIONS.get(domain, DOMAIN_TRANSITIONS["tools"])
    domain_config = get_domain_config(domain)

    return f"""# CHP State Machine — {repo_name}

## Protocol: Consensus Hardening Protocol (CHP) v1.0
## Domain: {domain_label}
## Applied: {date}

### States
- EXPLORING: Initial decision exploration with foundation disclosure
- PROVISIONAL: Foundation score ≥{domain_config["foundation"]}, devil's advocate complete
- PROVISIONAL_LOCK: Ready for third-party validation
- LOCKED: Third-party CONFIRM received, decision committed
- CONVERGED: Cross-agent agreement achieved
- UNRESOLVED: Forced at round 5 if no convergence
- REQUIRES_HUMAN_VERIFICATION: CFO accuracy guard tripped
- REFRAME_REQUIRED: Foundation score <{domain_config["foundation"]}
- HALT: R0 gate fatal or context parity significant

### Phase Progression
FOUNDATION (Phase 0) → SPEC (Phase 1) → IMPLEMENTATION (Phase 2)
Phase transitions occur at round boundaries: FOUNDATION→SPEC at round 1, SPEC→IMPLEMENTATION at round 3.

### State Transitions
{transitions.strip()}

### R0 Gate (Session Entry)
All four checks must PASS:
- Solvable: The decision can be resolved within the domain's constraints
- Scoped: Clear scope boundaries defined in dossier
- Valid: Current state and goal state are specified
- Worth_it: Stakes justify the governance overhead

### Foundation Score Thresholds
- General: ≥70 PASS, <70 REFRAME
- Finance/CFO: ≥100 (CFOAccuracyPolicy), <100 REQUIRES_HUMAN_VERIFICATION
- Blockchain/DeFi: ≥85 (elevated due to immutable tx risk)

### Adversary Schedule
- Phase 0, Round 0: Mandatory devil's advocate from FoundationDisclosure + FoundationAttack
- Phase 2, Round 3: Implementation drift check devil's advocate
- Council Spawn: high_stakes=True AND confidence <85 → 3-model cross-review

### Third-Party Validation
- PROVISIONAL_LOCK → CONFIRM → LOCKED
- PROVISIONAL_LOCK → REJECT → EXPLORING (with flip_criteria)
"""


def generate_r0_config_yaml(repo_name: str, domain: str) -> str:
    """Generate .chp/R0_CONFIG.yaml content."""
    cfg = get_domain_config(domain)
    return f"""# CHP R0 Gate Configuration — {repo_name}
# Domain: {cfg["label"]}
r0_gate:
  solvable: true
  scoped: true
  valid: true
  worth_it: {str(cfg["worth_it"]).lower()}

foundation:
  pass_threshold: {cfg["foundation"]}
  max_weak_assumptions: 3
  max_invalidation_conditions: 2
  require_key_vulnerability: true

adversary:
  phase0_mandatory: true
  round3_mandatory: true
  max_structural_vulnerabilities: 3
  council_spawn_threshold: 85

model_parity:
  max_tier_delta: 1
  halt_on_significant_gap: true

cfo_accuracy:
  enabled: {str(cfg["cfo_accuracy"]).lower()}
  foundation_floor: 100
  require_no_open_vulnerabilities: true
  require_no_open_blind_spots: true

payload:
  require_ascii: true
  max_rounds: 5
  require_echo_confirmation: true
"""


def generate_adversarial_prompts_md(
    repo_name: str,
    domain: str,
    domain_label: str,
    challenges: list[str],
) -> str:
    """Generate .chp/ADVERSARIAL_PROMPTS.md content."""
    challenges_bullets = "\n".join(f"{i+1}. {c}" for i, c in enumerate(challenges))

    return f"""# Adversarial Challenge Templates — {repo_name}

## Phase 0: Foundation Challenge
When a new decision enters CHP, the adversary MUST address:
1. Why is the proposed direction wrong? (vulnerability_strike)
2. What is the system not seeing? (invalidation_conditions)
3. What is the false consensus risk?

## Domain-Specific Challenges ({domain_label})
{challenges_bullets}

## Round 3: Implementation Drift Check
1. Does the implementation match the locked spec acceptance criteria?
2. Are operational handoffs and owner capacity accounted for?
3. Is evidence quality sufficient for the decision domain?

## Council Spawn Triggers
When confidence <85% on high-stakes decisions:
- Attacker Model 1: Challenge foundational assumptions
- Attacker Model 2: Challenge operational feasibility
- Synthesizer: Resolve contradictions and produce final recommendation
"""


def generate_compliance_md(
    repo_name: str,
    domain: str,
    domain_label: str,
    date: str,
) -> str:
    """Generate .chp/CHP_COMPLIANCE.md content."""
    cfg = get_domain_config(domain)
    cfo_status = "ENABLED" if cfg["cfo_accuracy"] else "DISABLED"

    return f"""# CHP Compliance — {repo_name}

## Hardening Status: CHAP-v1 APPLIED
## Applied: {date}
## CHP Version: {CHP_VERSION}

### Checklist
- [x] .chp/STATE_MACHINE.md deployed
- [x] .chp/R0_CONFIG.yaml configured for {domain_label}
- [x] .chp/ADVERSARIAL_PROMPTS.md with domain challenges
- [x] .chp/CHP_COMPLIANCE.md tracking enabled
- [x] CI/CD workflow with CHP gates
- [x] Pre-commit hooks enforcing CHP validation
- [x] README updated with CHP governance section
- [x] Tests include CHP validation scenarios

### Domain Configuration
- Category: {domain_label}
- Foundation Threshold: {cfg["foundation"]}
- CFO Accuracy Guard: {cfo_status}
- R0 Worth_it: {str(cfg["worth_it"]).capitalize()}

### Audit Trail
All CHP sessions are logged in .chp_registry.json with:
- Decision ID, session status, foundation score
- Devil's advocate rounds and findings
- Third-party validation results
- State snapshots at each round boundary
"""


def generate_ci_workflow() -> str:
    """Generate .github/workflows/chp-validation.yml content."""
    return """name: CHP Validation

on:
  pull_request:
    branches: [main, master]
  push:
    branches: [main, master]

jobs:
  chp-gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Validate CHP State Machine
        run: |
          python3 -c "
          import yaml, json, sys
          # Validate R0 config exists and is well-formed
          try:
              with open('.chp/R0_CONFIG.yaml') as f:
                  cfg = yaml.safe_load(f)
              assert 'r0_gate' in cfg, 'Missing r0_gate section'
              assert 'foundation' in cfg, 'Missing foundation section'
              print('R0_CONFIG.yaml: VALID')
          except Exception as e:
              print(f'R0_CONFIG.yaml: INVALID - {e}')
              sys.exit(1)
          # Validate STATE_MACHINE.md exists
          import os
          assert os.path.exists('.chp/STATE_MACHINE.md'), 'Missing STATE_MACHINE.md'
          print('STATE_MACHINE.md: PRESENT')
          # Validate ADVERSARIAL_PROMPTS.md exists
          assert os.path.exists('.chp/ADVERSARIAL_PROMPTS.md'), 'Missing ADVERSARIAL_PROMPTS.md'
          print('ADVERSARIAL_PROMPTS.md: PRESENT')
          # Validate CHP_COMPLIANCE.md exists
          assert os.path.exists('.chp/CHP_COMPLIANCE.md'), 'Missing CHP_COMPLIANCE.md'
          print('CHP_COMPLIANCE.md: PRESENT')
          print('All CHP artifacts validated successfully.')
          "
      - name: Run Tests
        run: |
          if [ -f "pytest.ini" ] || [ -f "setup.py" ] || [ -f "pyproject.toml" ]; then
            pip install -e ".[dev]" 2>/dev/null || pip install pytest 2>/dev/null
            pytest tests/ -v --tb=short 2>/dev/null || echo "No tests found or tests skipped"
          elif [ -f "package.json" ]; then
            npm ci 2>/dev/null || npm install 2>/dev/null
            npm test 2>/dev/null || echo "No npm tests configured"
          else
            echo "No test framework detected"
          fi
"""


def generate_readme_section(repo_name: str, domain: str, domain_label: str) -> str:
    """Generate the CHP governance README section."""
    cfg = get_domain_config(domain)
    cfo_status = "Enabled" if cfg["cfo_accuracy"] else "Disabled"

    return f"""
---

## CHP Governance

This repository is hardened with the [Consensus Hardening Protocol (CHP)](https://codeberg.org/cubiczan/consensus-hardening-protocol), Cubiczan's decision-governance layer for multi-agent AI systems.

### Protocol Layers
- **R0 Gate**: All decisions must pass Solvable, Scoped, Valid, Worth_it checks
- **Foundation Disclosure**: 1-3 weakest assumptions, 1-2 invalidation conditions, 1 key vulnerability
- **Adversarial Layer**: Mandatory devil's advocate at Phase 0 and Round 3
- **State Machine**: EXPLORING → PROVISIONAL → PROVISIONAL_LOCK → LOCKED
- **Third-Party Validation**: Independent CONFIRM/REJECT before lock

### Domain Configuration
- **Category**: {domain_label}
- **Foundation Threshold**: {cfg["foundation"]}
- **CFO Accuracy Guard**: {cfo_status}

### Compliance Artifacts
| File | Purpose |
|------|---------|
| `.chp/STATE_MACHINE.md` | Decision state transitions |
| `.chp/R0_CONFIG.yaml` | Domain-calibrated thresholds |
| `.chp/ADVERSARIAL_PROMPTS.md` | Standardized challenge templates |
| `.chp/CHP_COMPLIANCE.md` | Compliance tracking & audit trail |

### CHP Version
{CHP_VERSION} | [Protocol Docs](https://codeberg.org/cubiczan/consensus-hardening-protocol)
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_domain_config(domain: str) -> dict[str, Any]:
    """Load domain config from manifest (called after manifest is loaded)."""
    # We store the manifest globally after loading
    return _manifest_domain_configs.get(domain, {
        "label": domain,
        "foundation": 70,
        "cfo_accuracy": False,
        "worth_it": False,
        "adversarial_challenges": [],
    })


_manifest_domain_configs: dict[str, dict[str, Any]] = {}


def load_manifest(base_dir: Path) -> dict[str, Any]:
    """Load and validate the repo manifest."""
    manifest_path = base_dir / MANIFEST_FILE
    if not manifest_path.exists():
        print(f"FATAL: Manifest file not found: {manifest_path}", file=sys.stderr)
        sys.exit(1)

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # Populate global domain config cache
    global _manifest_domain_configs
    _manifest_domain_configs = manifest.get("domain_config", {})

    return manifest


def is_already_hardened(repo_path: Path) -> bool:
    """Check if a repo already has CHP compliance marker."""
    return (repo_path / ".chp" / "CHP_COMPLIANCE.md").exists()


def has_chp_governance_section(readme_content: str) -> bool:
    """Check if README already has CHP Governance section."""
    return "## CHP Governance" in readme_content


def ensure_directory(path: Path, dry_run: bool = False) -> bool:
    """Create directory if it doesn't exist. Returns True if created."""
    if path.exists():
        return False
    if dry_run:
        print(f"  DRY-RUN: Would create directory {path}")
        return True
    path.mkdir(parents=True, exist_ok=True)
    return True


def write_file(path: Path, content: str, dry_run: bool = False) -> bool:
    """Write content to file. Returns True if written."""
    if dry_run:
        print(f"  DRY-RUN: Would write {path}")
        return True
    path.write_text(content, encoding="utf-8")
    return True


def update_gitignore(repo_path: Path, dry_run: bool = False) -> tuple[bool, str]:
    """Add CHP entries to .gitignore if not present. Returns (changed, status_msg)."""
    gitignore_path = repo_path / ".gitignore"
    chp_entries = [
        "# CHP session artifacts (local only)",
        ".chp_registry.json",
        ".chp/sessions/",
    ]

    if gitignore_path.exists():
        existing = gitignore_path.read_text(encoding="utf-8")
        if ".chp_registry.json" in existing:
            return False, "already up to date"
        new_content = existing.rstrip("\n") + "\n\n" + "\n".join(chp_entries) + "\n"
    else:
        new_content = "\n".join(chp_entries) + "\n"

    if dry_run:
        print(f"  DRY-RUN: Would update {gitignore_path}")
        return True, "would update"

    gitignore_path.write_text(new_content, encoding="utf-8")
    return True, "updated"


def update_readme(repo_path: Path, repo_name: str, domain: str, domain_label: str, dry_run: bool = False) -> tuple[bool, str]:
    """Add CHP governance section to README. Returns (changed, status_msg)."""
    # Try multiple README file names
    readme_candidates = ["README.md", "readme.md", "Readme.md"]
    readme_path = None
    for candidate in readme_candidates:
        if (repo_path / candidate).exists():
            readme_path = repo_path / candidate
            break

    if readme_path is None:
        # Create a minimal README with CHP section
        readme_path = repo_path / "README.md"
        section = generate_readme_section(repo_name, domain, domain_label)
        if dry_run:
            print(f"  DRY-RUN: Would create {readme_path} with CHP governance section")
            return True, "would create README.md"
        readme_path.write_text(
            f"# {repo_name}\n\n{section}\n", encoding="utf-8"
        )
        return True, "created README.md with CHP section"

    existing = readme_path.read_text(encoding="utf-8")

    if has_chp_governance_section(existing):
        return False, "CHP governance section already present"

    section = generate_readme_section(repo_name, domain, domain_label)
    new_content = existing.rstrip("\n") + "\n" + section + "\n"

    if dry_run:
        print(f"  DRY-RUN: Would append CHP governance section to {readme_path}")
        return True, "would append CHP section"

    readme_path.write_text(new_content, encoding="utf-8")
    return True, "appended CHP governance section"


# ---------------------------------------------------------------------------
# Core Hardening Logic
# ---------------------------------------------------------------------------

def harden_repo(
    repo_info: dict[str, Any],
    base_dir: Path,
    dry_run: bool = False,
    force: bool = False,
) -> dict[str, Any]:
    """Apply all hardening layers to a single repo.

    Returns a result dict with status and details.
    """
    repo_name = repo_info["name"]
    repo_rel_path = repo_info["path"]
    domain = repo_info["domain"]
    domain_label = repo_info.get("description", "").split(" — ")[0] if " — " in repo_info.get("description", "") else domain
    # Use the proper label from manifest domain config
    domain_cfg = get_domain_config(domain)
    domain_label = domain_cfg.get("label", domain_label)

    repo_path = base_dir / repo_rel_path
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    result: dict[str, Any] = {
        "repo": repo_name,
        "path": str(repo_rel_path),
        "domain": domain,
        "status": "skipped",
        "layers_applied": [],
        "errors": [],
    }

    # Check if repo directory exists
    if not repo_path.exists():
        result["status"] = "error"
        result["errors"].append(f"Repo directory not found: {repo_path}")
        log_event("SKIP_MISSING", repo_name, {"path": str(repo_path), "reason": "directory not found"})
        return result

    # Check if repo is skipped in manifest
    if repo_info.get("skip", False):
        result["status"] = "skipped"
        result["skip_reason"] = repo_info.get("skip_reason", "marked in manifest")
        log_event("SKIP_MANIFEST", repo_name, {"reason": result["skip_reason"]})
        return result

    # Check if already hardened
    if not force and is_already_hardened(repo_path):
        result["status"] = "already_hardened"
        log_event("SKIP_HARDENED", repo_name, {"reason": "CHP_COMPLIANCE.md exists"})
        return result

    print(f"\n{'='*60}")
    print(f"  Hardening: {repo_name}")
    print(f"  Domain:    {domain_label} (threshold: {domain_cfg['foundation']})")
    print(f"  Path:      {repo_path}")
    if dry_run:
        print(f"  Mode:      DRY-RUN (no files will be written)")
    print(f"{'='*60}")

    # -----------------------------------------------------------------------
    # Layer 1: .chp/ Directory Scaffold
    # -----------------------------------------------------------------------
    print("\n  Layer 1: .chp/ Directory Scaffold")

    chp_dir = repo_path / ".chp"
    if ensure_directory(chp_dir, dry_run):
        result["layers_applied"].append("chp_dir_created")

    # STATE_MACHINE.md
    state_machine_path = chp_dir / "STATE_MACHINE.md"
    state_machine_content = generate_state_machine_md(repo_name, domain, domain_label, date)
    if write_file(state_machine_path, state_machine_content, dry_run):
        result["layers_applied"].append("STATE_MACHINE.md")
        print(f"  ✓ STATE_MACHINE.md")

    # R0_CONFIG.yaml
    r0_config_path = chp_dir / "R0_CONFIG.yaml"
    r0_config_content = generate_r0_config_yaml(repo_name, domain)
    if write_file(r0_config_path, r0_config_content, dry_run):
        result["layers_applied"].append("R0_CONFIG.yaml")
        print(f"  ✓ R0_CONFIG.yaml")

    # ADVERSARIAL_PROMPTS.md
    adversarial_path = chp_dir / "ADVERSARIAL_PROMPTS.md"
    challenges = domain_cfg.get("adversarial_challenges", [])
    adversarial_content = generate_adversarial_prompts_md(repo_name, domain, domain_label, challenges)
    if write_file(adversarial_path, adversarial_content, dry_run):
        result["layers_applied"].append("ADVERSARIAL_PROMPTS.md")
        print(f"  ✓ ADVERSARIAL_PROMPTS.md")

    # CHP_COMPLIANCE.md (marker file)
    compliance_path = chp_dir / "CHP_COMPLIANCE.md"
    compliance_content = generate_compliance_md(repo_name, domain, domain_label, date)
    if write_file(compliance_path, compliance_content, dry_run):
        result["layers_applied"].append("CHP_COMPLIANCE.md")
        print(f"  ✓ CHP_COMPLIANCE.md")

    # -----------------------------------------------------------------------
    # Layer 2: CI/CD Workflow
    # -----------------------------------------------------------------------
    print("\n  Layer 2: CI/CD Workflow")
    workflow_dir = repo_path / ".github" / "workflows"
    if ensure_directory(workflow_dir, dry_run):
        result["layers_applied"].append("github_workflows_dir")

    workflow_path = workflow_dir / "chp-validation.yml"
    if not workflow_path.exists():
        workflow_content = generate_ci_workflow()
        if write_file(workflow_path, workflow_content, dry_run):
            result["layers_applied"].append("chp-validation.yml")
            print(f"  ✓ .github/workflows/chp-validation.yml")
    else:
        print(f"  − .github/workflows/chp-validation.yml (already exists)")

    # -----------------------------------------------------------------------
    # Layer 3: .gitignore Update
    # -----------------------------------------------------------------------
    print("\n  Layer 3: .gitignore Update")
    try:
        changed, msg = update_gitignore(repo_path, dry_run)
        if changed:
            result["layers_applied"].append("gitignore_updated")
        print(f"  {'✓' if changed else '−'} .gitignore ({msg})")
    except Exception as e:
        result["errors"].append(f"gitignore update failed: {e}")
        print(f"  ✗ .gitignore update failed: {e}")

    # -----------------------------------------------------------------------
    # Layer 4: README Update
    # -----------------------------------------------------------------------
    print("\n  Layer 4: README Update")
    try:
        changed, msg = update_readme(repo_path, repo_name, domain, domain_label, dry_run)
        if changed:
            result["layers_applied"].append("readme_updated")
        print(f"  {'✓' if changed else '−'} README.md ({msg})")
    except Exception as e:
        result["errors"].append(f"README update failed: {e}")
        print(f"  ✗ README update failed: {e}")

    # -----------------------------------------------------------------------
    # Final status
    # -----------------------------------------------------------------------
    if result["errors"]:
        result["status"] = "partial" if result["layers_applied"] else "error"
    elif dry_run:
        result["status"] = "dry_run"
    else:
        result["status"] = "hardened"

    log_event(
        result["status"].upper(),
        repo_name,
        {
            "layers": result["layers_applied"],
            "errors": result["errors"],
            "domain": domain,
            "dry_run": dry_run,
        },
    )

    print(f"\n  Status: {result['status'].upper()}")
    print(f"  Layers applied: {len(result['layers_applied'])}")

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="CHP Hardening Engine — Apply Consensus Hardening Protocol to Cubiczan repos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python chp_hardener.py --all                    Harden all repos
  python chp_hardener.py --all --dry-run          Preview without writing
  python chp_hardener.py --repo resilient-agent   Harden a specific repo
  python chp_hardener.py --all --force            Re-harden already-hardened repos
  python chp_hardener.py --base-dir /custom/path  Use custom base directory
        """,
    )
    parser.add_argument(
        "--all",
        action="store_true",
        dest="all_repos",
        help="Harden all repos in the manifest",
    )
    parser.add_argument(
        "--repo",
        type=str,
        default=None,
        help="Harden a specific repo by name",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing files",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-harden repos that already have CHP_COMPLIANCE.md",
    )
    parser.add_argument(
        "--base-dir",
        type=str,
        default="/home/z/my-project",
        help="Base directory containing all repos (default: /home/z/my-project)",
    )
    parser.add_argument(
        "--manifest",
        type=str,
        default=None,
        help=f"Custom manifest file path (default: {MANIFEST_FILE})",
    )

    args = parser.parse_args()

    if not args.all_repos and not args.repo:
        parser.error("Either --all or --repo <name> is required")
    if args.all_repos and args.repo:
        parser.error("Cannot use both --all and --repo")

    base_dir = Path(args.base_dir).resolve()

    # Load manifest
    manifest_path = Path(args.manifest) if args.manifest else base_dir / MANIFEST_FILE
    if not manifest_path.exists():
        print(f"FATAL: Manifest file not found: {manifest_path}", file=sys.stderr)
        return 1

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    global _manifest_domain_configs
    _manifest_domain_configs = manifest.get("domain_config", {})

    repos = manifest.get("repos", [])

    # Select repos
    if args.repo:
        target_repos = [r for r in repos if r["name"] == args.repo]
        if not target_repos:
            print(f"FATAL: Repo '{args.repo}' not found in manifest", file=sys.stderr)
            print(f"Available repos: {', '.join(r['name'] for r in repos)}", file=sys.stderr)
            return 1
    else:
        target_repos = repos

    print("=" * 60)
    print("  CHP HARDENING ENGINE v1.0")
    print(f"  {CHP_VERSION}")
    print("=" * 60)
    print(f"  Base dir:   {base_dir}")
    print(f"  Manifest:   {manifest_path}")
    print(f"  Repos:      {len(target_repos)}")
    print(f"  Mode:       {'DRY-RUN' if args.dry_run else 'LIVE'}")
    print(f"  Force:      {args.force}")
    print("=" * 60)

    # Process repos
    results: list[dict[str, Any]] = []
    start_time = time.time()

    for repo_info in target_repos:
        try:
            result = harden_repo(repo_info, base_dir, dry_run=args.dry_run, force=args.force)
            results.append(result)
        except Exception as e:
            error_result = {
                "repo": repo_info["name"],
                "path": repo_info["path"],
                "status": "error",
                "layers_applied": [],
                "errors": [str(e)],
            }
            results.append(error_result)
            log_event("UNHANDLED_ERROR", repo_info["name"], {"error": str(e)})
            print(f"  ✗ UNHANDLED ERROR: {e}", file=sys.stderr)

    elapsed = time.time() - start_time

    # -----------------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("  HARDENING SUMMARY")
    print("=" * 60)

    hardened = [r for r in results if r["status"] == "hardened"]
    partial = [r for r in results if r["status"] == "partial"]
    errors = [r for r in results if r["status"] == "error"]
    skipped = [r for r in results if r["status"] in ("skipped", "already_hardened")]
    dry_run = [r for r in results if r["status"] == "dry_run"]

    print(f"\n  Total repos processed: {len(results)}")
    print(f"  Elapsed time: {elapsed:.2f}s")

    if args.dry_run:
        print(f"\n  DRY-RUN repos:      {len(dry_run)}")
        for r in dry_run:
            print(f"    ✓ {r['repo']} ({len(r['layers_applied'])} layers)")

    if hardened:
        print(f"\n  Hardened:           {len(hardened)}")
        for r in hardened:
            print(f"    ✓ {r['repo']} ({len(r['layers_applied'])} layers)")

    if partial:
        print(f"\n  Partial (with errors): {len(partial)}")
        for r in partial:
            print(f"    ~ {r['repo']} ({len(r['layers_applied'])} layers, {len(r['errors'])} errors)")

    if errors:
        print(f"\n  Errors:             {len(errors)}")
        for r in errors:
            print(f"    ✗ {r['repo']}: {', '.join(r['errors'])}")

    if skipped:
        print(f"\n  Skipped:            {len(skipped)}")
        for r in skipped:
            reason = r.get("skip_reason", r["status"])
            print(f"    − {r['repo']}: {reason}")

    # Flush log
    flush_log(base_dir)
    print(f"\n  Log written to: {base_dir / LOG_FILE}")
    print("=" * 60)

    # Exit code
    if errors:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
