"""WorkflowRunner — loads and executes workflow YAML definitions."""
import concurrent.futures
import datetime
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False

from workflow_runner.state import RunState
from workflow_runner.adapters.copilot import CopilotAdapter
from workflow_runner.adapters.cursor import CursorAdapter


def _load_yaml(path: str) -> Optional[Dict]:
    if not _HAS_YAML:
        # Minimal YAML-subset loader (name/description/phases only)
        return _minimal_yaml_load(path)
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _minimal_yaml_load(path: str) -> Optional[Dict]:
    """Very small YAML parser for simple key: value + list structures."""
    result = {}
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    current_list_key = None
    current_obj = None
    for line in lines:
        stripped = line.rstrip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("  - name:"):
            item = {"name": stripped.split(":", 1)[1].strip()}
            if current_list_key == "phases":
                result.setdefault("phases", []).append(item)
                current_obj = item
        elif stripped.startswith("    ") and current_obj is not None:
            if ":" in stripped:
                k, v = stripped.strip().split(":", 1)
                current_obj[k.strip()] = v.strip()
        elif ":" in stripped and not stripped.startswith(" "):
            k, v = stripped.split(":", 1)
            k = k.strip(); v = v.strip()
            result[k] = v
            if v == "":
                current_list_key = k
            else:
                current_list_key = None
                current_obj = None
    return result if result else None


def _resolve_template(template: str, variables: Dict[str, Any]) -> str:
    """Replace {{key}} placeholders in template."""
    def _sub(m):
        key = m.group(1).strip()
        return str(variables.get(key, m.group(0)))
    return re.sub(r"\{\{([^}]+)\}\}", _sub, template)


class AgentResult:
    def __init__(self, phase: str, agent_index: int, output: str, duration: float):
        self.phase = phase
        self.agent_index = agent_index
        self.output = output
        self.duration = duration

    def to_dict(self):
        return {
            "phase": self.phase,
            "agent_index": self.agent_index,
            "output": self.output,
            "duration": round(self.duration, 2),
        }


class WorkflowRunner:
    MAX_PARALLEL = 16
    MAX_TOTAL = 1000

    def __init__(self):
        self.adapters = [CopilotAdapter(), CursorAdapter()]
        self._workflow_dirs = self._collect_dirs()

    def _collect_dirs(self) -> List[str]:
        dirs = []
        for adapter in self.adapters:
            d = adapter.workflow_dir()
            if d and os.path.isdir(d):
                dirs.append(d)
        # Built-in workflows (alongside this package)
        pkg_dir = Path(__file__).parent.parent / "builtin-workflows"
        if pkg_dir.is_dir():
            dirs.append(str(pkg_dir))
        return dirs

    def list_all(self) -> List[Dict]:
        seen = set()
        results = []
        for d in self._workflow_dirs:
            for f in sorted(Path(d).glob("*.yaml")):
                if f.stem not in seen:
                    seen.add(f.stem)
                    wf = _load_yaml(str(f)) or {}
                    results.append({
                        "name": wf.get("name", f.stem),
                        "description": wf.get("description", ""),
                        "path": str(f),
                    })
        return results

    def load(self, name: str) -> Optional[Dict]:
        for d in self._workflow_dirs:
            p = Path(d) / f"{name}.yaml"
            if p.exists():
                return _load_yaml(str(p))
        return None

    def scaffold(self, name: str, description: str):
        adapter = self.adapters[0]
        d = Path(adapter.workflow_dir())
        d.mkdir(parents=True, exist_ok=True)
        out = d / f"{name}.yaml"
        template = f"""name: {name}
description: {description}
version: 1.0.0
max_parallel_agents: 4
max_total_agents: 50

phases:
  - name: research
    description: Initial research phase
    agents: 1
    parallel: false
    prompt_template: |
      Query: {{{{query}}}}
      Perform comprehensive research and return your findings as JSON.

  - name: synthesize
    description: Synthesize findings into final output
    agents: 1
    parallel: false
    depends_on: [research]
    prompt_template: |
      Synthesize the following research into a clear, actionable output:
      {{{{phases.research.results}}}}
"""
        out.write_text(template, encoding="utf-8")

    def execute(
        self,
        workflow: Dict,
        variables: Dict[str, Any],
        state: RunState,
        dry_run: bool = False,
        verbose: bool = False,
    ):
        name = workflow.get("name", "unknown")
        phases = workflow.get("phases", [])
        max_parallel = min(
            int(workflow.get("max_parallel_agents", 4)), self.MAX_PARALLEL
        )
        print(f"\n[wf] Running workflow: {name}")
        print(f"[wf] Phases: {', '.join(p['name'] for p in phases)}")
        if dry_run:
            print("[wf] DRY RUN — no agents will be spawned\n")
            for phase in phases:
                print(f"  Phase '{phase['name']}':")
                print(f"    agents: {phase.get('agents', 1)}")
                print(f"    parallel: {phase.get('parallel', False)}")
                prompt = _resolve_template(phase.get("prompt_template", ""), variables)
                print(f"    prompt: {prompt[:80].strip()}...")
            print()
            return

        state.start(workflow)
        total_spawned = 0

        for phase in phases:
            phase_name = phase["name"]
            num_agents = int(phase.get("agents", 1))
            is_parallel = phase.get("parallel", False)
            prompt_template = phase.get("prompt_template", "No prompt defined.")

            print(f"\n[wf] Phase: {phase_name} — {num_agents} agent(s), parallel={is_parallel}")
            state.begin_phase(phase_name)

            phase_results = []

            if total_spawned + num_agents > self.MAX_TOTAL:
                print(f"[wf] WARNING: max_total_agents ({self.MAX_TOTAL}) would be exceeded. Capping.")
                num_agents = max(0, self.MAX_TOTAL - total_spawned)

            effective_parallel = min(num_agents, max_parallel)

            def run_agent(idx, tpl=prompt_template, vars_=variables, pname=phase_name):
                agent_vars = dict(vars_)
                agent_vars["agent_index"] = idx
                prompt = _resolve_template(tpl, agent_vars)
                t0 = time.time()
                output = self._call_agent(prompt, pname, idx, verbose)
                return AgentResult(pname, idx, output, time.time() - t0)

            if is_parallel and num_agents > 1:
                with concurrent.futures.ThreadPoolExecutor(max_workers=effective_parallel) as pool:
                    futures = {pool.submit(run_agent, i): i for i in range(num_agents)}
                    for fut in concurrent.futures.as_completed(futures):
                        result = fut.result()
                        phase_results.append(result)
                        if verbose:
                            print(f"  [agent {result.agent_index}] done ({result.duration:.1f}s): {result.output[:60]}")
            else:
                for i in range(num_agents):
                    result = run_agent(i)
                    phase_results.append(result)
                    if verbose:
                        print(f"  [agent {result.agent_index}] done ({result.duration:.1f}s): {result.output[:60]}")

            total_spawned += num_agents
            variables[f"phases.{phase_name}.results"] = json.dumps(
                [r.to_dict() for r in phase_results], indent=2
            )
            state.complete_phase(phase_name, phase_results)
            print(f"[wf] Phase '{phase_name}' complete ({len(phase_results)} agents)")

        state.finish()
        print(f"\n[wf] Workflow '{name}' complete. Total agents: {total_spawned}")
        state.save()

    def _call_agent(self, prompt: str, phase: str, idx: int, verbose: bool) -> str:
        """
        Spawn an LLM agent. In production, calls the platform LLM API.
        Requires ANTHROPIC_API_KEY or OPENAI_API_KEY in environment.
        Falls back to a structured placeholder if no API key is set.
        """
        api_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            # Structured simulation mode (useful for dry tests / CI)
            time.sleep(0.05)
            return json.dumps({
                "phase": phase,
                "agent": idx,
                "status": "simulated",
                "note": "Set ANTHROPIC_API_KEY or OPENAI_API_KEY to run real agents",
                "prompt_preview": prompt[:120],
            })
        # Prefer Anthropic
        anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
        if anthropic_key:
            return self._call_anthropic(prompt, anthropic_key)
        return self._call_openai(prompt, os.environ["OPENAI_API_KEY"])

    def _call_anthropic(self, prompt: str, api_key: str) -> str:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            msg = client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
            )
            return msg.content[0].text
        except Exception as e:
            return json.dumps({"error": str(e), "phase": "anthropic-call"})

    def _call_openai(self, prompt: str, api_key: str) -> str:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4096,
            )
            return resp.choices[0].message.content
        except Exception as e:
            return json.dumps({"error": str(e), "phase": "openai-call"})
