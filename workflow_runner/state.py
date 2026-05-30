"""RunState — tracks workflow execution progress and persists results."""
import json
import os
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


STATE_DIR = Path.home() / ".copilot" / "skills" / "workflows" / "data" / "runs"


class RunState:
    def __init__(self, workflow_name: str):
        self.workflow_name = workflow_name
        self.run_id = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        self.status = "initialized"
        self.phases: Dict[str, Any] = {}
        self.started_at: Optional[str] = None
        self.finished_at: Optional[str] = None

    def start(self, workflow: Dict):
        self.status = "running"
        self.started_at = datetime.datetime.now().isoformat()

    def begin_phase(self, phase_name: str):
        self.phases[phase_name] = {"status": "running", "results": []}

    def complete_phase(self, phase_name: str, results: List):
        self.phases[phase_name] = {
            "status": "done",
            "results": [r.to_dict() for r in results],
        }

    def finish(self):
        self.status = "done"
        self.finished_at = datetime.datetime.now().isoformat()

    def save(self):
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        path = STATE_DIR / f"{self.run_id}-{self.workflow_name}.json"
        data = {
            "run_id": self.run_id,
            "workflow": self.workflow_name,
            "status": self.status,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "phases": self.phases,
        }
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def print_status(self):
        print(f"\n[wf] Run: {self.run_id}  Workflow: {self.workflow_name}  Status: {self.status}")
        if self.started_at:
            print(f"     Started:  {self.started_at}")
        if self.finished_at:
            print(f"     Finished: {self.finished_at}")
        print(f"\n  {'PHASE':<25} {'STATUS':<12} {'AGENTS'}")
        print("  " + "-" * 55)
        for pname, pdata in self.phases.items():
            n = len(pdata.get("results", []))
            print(f"  {pname:<25} {pdata.get('status', '?'):<12} {n}")
        print()

    @classmethod
    def load_latest(cls) -> Optional["RunState"]:
        if not STATE_DIR.exists():
            return None
        files = sorted(STATE_DIR.glob("*.json"), reverse=True)
        if not files:
            return None
        data = json.loads(files[0].read_text(encoding="utf-8"))
        state = cls(data.get("workflow", "unknown"))
        state.run_id = data.get("run_id", "?")
        state.status = data.get("status", "?")
        state.started_at = data.get("started_at")
        state.finished_at = data.get("finished_at")
        state.phases = data.get("phases", {})
        return state
