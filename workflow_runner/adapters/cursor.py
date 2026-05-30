"""Cursor adapter — paths and conventions for Cursor IDE."""
import os
from pathlib import Path


class CursorAdapter:
    name = "cursor"

    def workflow_dir(self) -> str:
        project = Path.cwd() / ".cursor" / "workflows"
        if project.is_dir():
            return str(project)
        return str(Path.home() / ".cursor" / "workflows")

    def agent_dir(self) -> str:
        project = Path.cwd() / ".cursor" / "agents"
        if project.is_dir():
            return str(project)
        return str(Path.home() / ".cursor" / "agents")

    def skill_dir(self) -> str:
        return str(Path.home() / ".cursor" / "skills")

    def rules_dir(self) -> str:
        return str(Path.cwd() / ".cursor" / "rules")
