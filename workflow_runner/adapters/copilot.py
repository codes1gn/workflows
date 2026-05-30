"""Copilot (VS Code) adapter — paths and conventions for GitHub Copilot."""
import os
from pathlib import Path


class CopilotAdapter:
    name = "copilot"

    def workflow_dir(self) -> str:
        # User-level: ~/.copilot/skills/workflows/data/
        user = Path.home() / ".copilot" / "skills" / "workflows" / "data"
        # Project-level: .github/copilot/workflows/ (in cwd)
        project = Path.cwd() / ".github" / "copilot" / "workflows"
        if project.is_dir():
            return str(project)
        return str(user)

    def agent_dir(self) -> str:
        project = Path.cwd() / ".github" / "copilot" / "agents"
        if project.is_dir():
            return str(project)
        return str(Path.home() / ".copilot" / "skills" / "workflows" / "agents")

    def skill_dir(self) -> str:
        return str(Path.home() / ".copilot" / "skills")

    def instructions_file(self) -> str:
        return str(Path.cwd() / ".github" / "copilot-instructions.md")
