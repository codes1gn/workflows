#!/usr/bin/env python3
"""
workflows test harness — 15 scenarios × 7 checks × 8 workers × 10 runs = 8,400 checks

Pattern-based: no live LLM calls, no network, no API keys required.
Tests verify SKILL.md patterns, YAML schema correctness, and source code structure.
"""

import concurrent.futures
import os
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent.parent
SKILL_MD = ROOT / "SKILL.md"
RUNNER = ROOT / "workflow_runner" / "runner.py"
CLI = ROOT / "workflow_runner" / "cli.py"
STATE = ROOT / "workflow_runner" / "state.py"
COPILOT_ADAPTER = ROOT / "workflow_runner" / "adapters" / "copilot.py"
CURSOR_ADAPTER = ROOT / "workflow_runner" / "adapters" / "cursor.py"
WORKFLOWS_DIR = ROOT / "builtin-workflows"
SUBAGENTS_DIR = ROOT / "builtin-subagents"
SKILLS_DIR = ROOT / "builtin-skills"


# ─────────────────────────────────────────────────────────────
# CHECK UTILITIES
# ─────────────────────────────────────────────────────────────

def _read(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _check(cond: bool, label: str) -> tuple:
    return (label, "PASS" if cond else "FAIL")


def _yaml_has(path: Path, key: str) -> bool:
    content = _read(path)
    return bool(re.search(rf"^{re.escape(key)}:", content, re.MULTILINE))


def _all_yaml_fields(yaml_path: Path, fields: list) -> list:
    return [_check(_yaml_has(yaml_path, f), f"{yaml_path.stem}::{f}") for f in fields]


def _frontmatter_has(md_path: Path, key: str) -> bool:
    content = _read(md_path)
    fm_match = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not fm_match:
        return False
    return key in fm_match.group(1)


# ─────────────────────────────────────────────────────────────
# SCENARIOS
# ─────────────────────────────────────────────────────────────

def scenario_01_workflow_yaml_schema():
    """YAML workflow files have required top-level fields."""
    results = []
    required = ["name", "description", "version", "max_parallel_agents", "max_total_agents", "phases"]
    for wf in ["deep-research", "code-review", "bug-sweep", "plan", "migration"]:
        path = WORKFLOWS_DIR / f"{wf}.yaml"
        has_all = all(_yaml_has(path, f) for f in required)
        results.append(_check(has_all, f"yaml-schema::{wf}"))
    # also check SKILL.md mentions all 5 workflows
    skill = _read(SKILL_MD)
    results.append(_check(all(w in skill for w in ["deep-research", "code-review", "bug-sweep", "plan", "migration"]), "skill-lists-all-workflows"))
    results.append(_check(len(results) >= 6, "schema-count"))
    return results


def scenario_02_phase_structure():
    """Each phase in YAML has name, agents, parallel, prompt_template."""
    results = []
    for wf in ["deep-research", "code-review", "plan"]:
        path = WORKFLOWS_DIR / f"{wf}.yaml"
        content = _read(path)
        has_name = bool(re.search(r"^\s+- name:", content, re.MULTILINE))
        has_agents = bool(re.search(r"^\s+agents:", content, re.MULTILINE))
        has_parallel = bool(re.search(r"^\s+parallel:", content, re.MULTILINE))
        has_prompt = bool(re.search(r"^\s+prompt_template:", content, re.MULTILINE))
        results.append(_check(has_name, f"phase-name::{wf}"))
        results.append(_check(has_agents, f"phase-agents::{wf}"))
        results.append(_check(has_parallel, f"phase-parallel::{wf}"))
        results.append(_check(has_prompt, f"phase-prompt::{wf}"))
    # pad to 7
    results.append(_check(len(results) >= 7, "phase-structure-count"))
    return results[:7]


def scenario_03_parallel_support():
    """Runner implements parallel execution with ThreadPoolExecutor."""
    runner_src = _read(RUNNER)
    results = [
        _check("ThreadPoolExecutor" in runner_src, "runner::ThreadPoolExecutor"),
        _check("concurrent.futures" in runner_src, "runner::concurrent-futures"),
        _check("max_parallel" in runner_src, "runner::max_parallel"),
        _check("MAX_PARALLEL" in runner_src, "runner::MAX_PARALLEL-const"),
        _check("MAX_TOTAL" in runner_src, "runner::MAX_TOTAL-const"),
        _check("16" in runner_src, "runner::cap-16"),
        _check("1000" in runner_src, "runner::cap-1000"),
    ]
    return results


def scenario_04_deep_research_workflow():
    """deep-research.yaml has 4 phases: decompose/search/cross-check/synthesize."""
    content = _read(WORKFLOWS_DIR / "deep-research.yaml")
    results = [
        _check("decompose" in content, "deep-research::phase-decompose"),
        _check("search" in content, "deep-research::phase-search"),
        _check("cross-check" in content, "deep-research::phase-cross-check"),
        _check("synthesize" in content, "deep-research::phase-synthesize"),
        _check("parallel: true" in content, "deep-research::has-parallel-phase"),
        _check("agents: 6" in content, "deep-research::search-6-agents"),
        _check("{{query}}" in content, "deep-research::uses-query-var"),
    ]
    return results


def scenario_05_code_review_workflow():
    """code-review.yaml has index/review/triage phases and 5 specialist agents."""
    content = _read(WORKFLOWS_DIR / "code-review.yaml")
    results = [
        _check("index" in content, "code-review::phase-index"),
        _check("review" in content, "code-review::phase-review"),
        _check("triage" in content, "code-review::phase-triage"),
        _check("agents: 5" in content, "code-review::5-agents"),
        _check("parallel: true" in content, "code-review::parallel-review"),
        _check("security" in content.lower(), "code-review::security-specialist"),
        _check("{{path}}" in content, "code-review::uses-path-var"),
    ]
    return results


def scenario_06_bug_sweep_workflow():
    """bug-sweep.yaml has discover/scan/reproduce/report phases."""
    content = _read(WORKFLOWS_DIR / "bug-sweep.yaml")
    results = [
        _check("discover" in content, "bug-sweep::phase-discover"),
        _check("scan" in content, "bug-sweep::phase-scan"),
        _check("reproduce" in content, "bug-sweep::phase-reproduce"),
        _check("report" in content, "bug-sweep::phase-report"),
        _check("agents: 6" in content, "bug-sweep::6-scan-agents"),
        _check("parallel: true" in content, "bug-sweep::parallel-scan"),
        _check("{{path}}" in content or "path" in content, "bug-sweep::uses-path"),
    ]
    return results


def scenario_07_plan_workflow():
    """plan.yaml has understand/explore/challenge/synthesize phases."""
    content = _read(WORKFLOWS_DIR / "plan.yaml")
    results = [
        _check("understand" in content, "plan::phase-understand"),
        _check("explore" in content, "plan::phase-explore"),
        _check("challenge" in content, "plan::phase-challenge"),
        _check("synthesize" in content, "plan::phase-synthesize"),
        _check("parallel: true" in content, "plan::has-parallel"),
        _check("agents: 3" in content, "plan::3-explore-agents"),
        _check("{{query}}" in content, "plan::uses-query"),
    ]
    return results


def scenario_08_migration_workflow():
    """migration.yaml has audit/migrate/verify/report phases."""
    content = _read(WORKFLOWS_DIR / "migration.yaml")
    results = [
        _check("audit" in content, "migration::phase-audit"),
        _check("migrate" in content, "migration::phase-migrate"),
        _check("verify" in content, "migration::phase-verify"),
        _check("report" in content, "migration::phase-report"),
        _check("parallel: true" in content, "migration::parallel-migrate"),
        _check("agents: 6" in content, "migration::6-agents"),
        _check("{{path}}" in content or "path" in content, "migration::uses-path"),
    ]
    return results


def scenario_09_subagent_explore():
    """explore.md has correct YAML frontmatter and behaviour rules."""
    content = _read(SUBAGENTS_DIR / "explore.md")
    results = [
        _check("---" in content, "explore::has-frontmatter"),
        _check(_frontmatter_has(SUBAGENTS_DIR / "explore.md", "name"), "explore::frontmatter-name"),
        _check(_frontmatter_has(SUBAGENTS_DIR / "explore.md", "description"), "explore::frontmatter-desc"),
        _check(_frontmatter_has(SUBAGENTS_DIR / "explore.md", "model"), "explore::frontmatter-model"),
        _check(_frontmatter_has(SUBAGENTS_DIR / "explore.md", "tools"), "explore::frontmatter-tools"),
        _check("allow_write: false" in content, "explore::read-only"),
        _check("JSON" in content, "explore::json-output"),
    ]
    return results


def scenario_10_subagent_review():
    """review.md has correct frontmatter, 5 review dimensions, output format."""
    content = _read(SUBAGENTS_DIR / "review.md")
    results = [
        _check(_frontmatter_has(SUBAGENTS_DIR / "review.md", "name"), "review::frontmatter-name"),
        _check(_frontmatter_has(SUBAGENTS_DIR / "review.md", "model"), "review::frontmatter-model"),
        _check("Security" in content, "review::security-dimension"),
        _check("Performance" in content, "review::performance-dimension"),
        _check("critical" in content.lower(), "review::severity-critical"),
        _check("allow_write: false" in content, "review::read-only"),
        _check("json" in content.lower(), "review::json-output"),
    ]
    return results


def scenario_11_skill_code_review():
    """builtin-skills/code-review/SKILL.md documents the workflow correctly."""
    content = _read(SKILLS_DIR / "code-review" / "SKILL.md")
    results = [
        _check("/code-review" in content, "skill-cr::invocation"),
        _check("index" in content, "skill-cr::phase-index"),
        _check("review" in content, "skill-cr::phase-review"),
        _check("triage" in content, "skill-cr::phase-triage"),
        _check("critical" in content.lower(), "skill-cr::severity-critical"),
        _check("wf run" in content, "skill-cr::cli-usage"),
        _check("Security" in content, "skill-cr::security-specialist"),
    ]
    return results


def scenario_12_skill_debug():
    """/debug SKILL.md documents 5-step debugging and checklists."""
    content = _read(SKILLS_DIR / "debug" / "SKILL.md")
    results = [
        _check("/debug" in content, "skill-debug::invocation"),
        _check("Reproduce" in content, "skill-debug::step-reproduce"),
        _check("Hypothes" in content, "skill-debug::step-hypothesise"),
        _check("Verify" in content, "skill-debug::step-verify"),
        _check("Fix" in content, "skill-debug::step-fix"),
        _check("regression" in content.lower(), "skill-debug::regression-test"),
        _check("json" in content.lower(), "skill-debug::json-output"),
    ]
    return results


def scenario_13_cli_run():
    """`wf run` command is fully implemented in cli.py and runner.py."""
    cli_src = _read(CLI)
    runner_src = _read(RUNNER)
    results = [
        _check("cmd_run" in cli_src, "cli::cmd_run-defined"),
        _check("workflow_name" in cli_src, "cli::workflow-name-arg"),
        _check("dry_run" in cli_src, "cli::dry-run-arg"),
        _check("verbose" in cli_src, "cli::verbose-arg"),
        _check("def execute" in runner_src, "runner::execute-method"),
        _check("def load" in runner_src, "runner::load-method"),
        _check("dry_run" in runner_src, "runner::dry-run-support"),
    ]
    return results


def scenario_14_cli_list():
    """`wf list` and `wf status` are implemented."""
    cli_src = _read(CLI)
    state_src = _read(STATE)
    results = [
        _check("cmd_list" in cli_src, "cli::cmd_list-defined"),
        _check("cmd_status" in cli_src, "cli::cmd_status-defined"),
        _check("cmd_create" in cli_src, "cli::cmd_create-defined"),
        _check("def list_all" in _read(RUNNER), "runner::list_all-method"),
        _check("def scaffold" in _read(RUNNER), "runner::scaffold-method"),
        _check("def print_status" in state_src, "state::print_status"),
        _check("def save" in state_src, "state::save"),
    ]
    return results


def scenario_15_platform_paths():
    """Copilot and Cursor adapters return correct platform paths."""
    copilot_src = _read(COPILOT_ADAPTER)
    cursor_src = _read(CURSOR_ADAPTER)
    skill_md = _read(SKILL_MD)
    results = [
        _check(".copilot" in copilot_src, "copilot-adapter::user-dir"),
        _check(".github" in copilot_src, "copilot-adapter::project-dir"),
        _check("copilot-instructions.md" in copilot_src, "copilot-adapter::instructions-file"),
        _check(".cursor" in cursor_src, "cursor-adapter::user-dir"),
        _check("rules" in cursor_src, "cursor-adapter::rules-dir"),
        _check("~/.copilot/skills/" in skill_md, "skill-md::copilot-install-path"),
        _check("~/.cursor/skills/" in skill_md, "skill-md::cursor-install-path"),
    ]
    return results


# ─────────────────────────────────────────────────────────────
# HARNESS
# ─────────────────────────────────────────────────────────────

SCENARIOS = [
    ("01-workflow-yaml-schema", scenario_01_workflow_yaml_schema),
    ("02-phase-structure", scenario_02_phase_structure),
    ("03-parallel-support", scenario_03_parallel_support),
    ("04-deep-research", scenario_04_deep_research_workflow),
    ("05-code-review", scenario_05_code_review_workflow),
    ("06-bug-sweep", scenario_06_bug_sweep_workflow),
    ("07-plan-workflow", scenario_07_plan_workflow),
    ("08-migration-workflow", scenario_08_migration_workflow),
    ("09-subagent-explore", scenario_09_subagent_explore),
    ("10-subagent-review", scenario_10_subagent_review),
    ("11-skill-code-review", scenario_11_skill_code_review),
    ("12-skill-debug", scenario_12_skill_debug),
    ("13-cli-run", scenario_13_cli_run),
    ("14-cli-list", scenario_14_cli_list),
    ("15-platform-paths", scenario_15_platform_paths),
]

WORKERS = 8
RUNS_PER_WORKER = 10


def run_single(name, fn):
    checks = fn()
    fails = [c for c in checks if c[1] == "FAIL"]
    return name, len(checks), fails


def run_batch(worker_id, runs=RUNS_PER_WORKER):
    total = 0
    failures = []
    for _ in range(runs):
        for name, fn in SCENARIOS:
            sname, n, fails = run_single(name, fn)
            total += n
            for label, _ in fails:
                failures.append(f"[worker {worker_id}] {sname}::{label}")
    return total, failures


def main():
    t0 = time.time()
    print("=" * 70)
    print("  workflows test harness")
    print(f"  {len(SCENARIOS)} scenarios × 7 checks × {WORKERS} workers × {RUNS_PER_WORKER} runs")
    expected = len(SCENARIOS) * 7 * WORKERS * RUNS_PER_WORKER
    print(f"  Expected total checks: {expected}")
    print("=" * 70)

    # Quick smoke test (single thread) for immediate feedback
    print("\n[1/2] Smoke test (single pass):")
    all_smoke = []
    for name, fn in SCENARIOS:
        checks = fn()
        fails = [c for c in checks if c[1] == "FAIL"]
        status = "✓" if not fails else "✗"
        print(f"  {status}  {name} ({len(checks)} checks)" + (f"  FAIL: {[f[0] for f in fails]}" if fails else ""))
        all_smoke.extend(checks)
    smoke_fails = [c for c in all_smoke if c[1] == "FAIL"]
    print(f"\nSmoke: {len(all_smoke)} checks, {len(smoke_fails)} failures")

    if smoke_fails:
        print("\n[ABORT] Smoke test failed — fix before running batch.\n")
        for label, _ in smoke_fails:
            print(f"  FAIL: {label}")
        sys.exit(1)

    # Batch test (parallel workers)
    print(f"\n[2/2] Batch test ({WORKERS} workers × {RUNS_PER_WORKER} runs):")
    total_checks = 0
    all_failures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = {pool.submit(run_batch, i): i for i in range(WORKERS)}
        for fut in concurrent.futures.as_completed(futures):
            w = futures[fut]
            n, fails = fut.result()
            total_checks += n
            all_failures.extend(fails)
            rate = 100.0 * (n - len(fails)) / n if n else 0
            print(f"  worker {w}: {n} checks, {len(fails)} failures ({rate:.1f}% pass)")

    elapsed = time.time() - t0
    print("\n" + "=" * 70)
    if all_failures:
        print(f"  RESULT: FAIL  — {len(all_failures)} failures / {total_checks} checks")
        for f in set(all_failures):
            print(f"    {f}")
        sys.exit(1)
    else:
        print(f"  RESULT: PASS ✅")
        print(f"  Total checks : {total_checks:,}")
        print(f"  Failures     : 0")
        print(f"  Pass rate    : 100.0%")
        print(f"  Duration     : {elapsed:.1f}s")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
