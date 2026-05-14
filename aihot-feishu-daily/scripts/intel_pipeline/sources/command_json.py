from __future__ import annotations

import json
import subprocess
from pathlib import Path

from intel_pipeline.config import expand_command_arg

from .base import SourceAdapter, SourceResult


class CommandJsonAdapter(SourceAdapter):
    def expanded_candidates(self) -> list[list[str]]:
        candidates = self.config.get("command_candidates") or []
        if self.config.get("command"):
            candidates.append(self.config["command"])
        return [
            [expand_command_arg(str(part), self.context.repo_root) for part in candidate]
            for candidate in candidates
        ]

    @staticmethod
    def command_script_exists(command: list[str]) -> bool:
        script_args = [
            Path(part)
            for part in command
            if part.endswith(".py") and (part.startswith("/") or "/" in part)
        ]
        return not script_args or all(path.exists() for path in script_args)

    def fetch(self) -> SourceResult:
        selected_command: list[str] | None = None
        for command in self.expanded_candidates():
            if self.command_script_exists(command):
                selected_command = command
                break
        if not selected_command:
            raise FileNotFoundError(f"No runnable command candidate for source {self.config['id']}")

        result = subprocess.run(
            selected_command,
            check=False,
            capture_output=True,
            text=True,
            timeout=int(self.config.get("timeout") or 90),
        )
        if result.returncode != 0:
            message = (result.stderr or result.stdout or "").strip()
            raise RuntimeError(f"{self.config['id']} command failed: {message}")

        packet = json.loads(result.stdout)
        items = packet.get("items") or []
        for item in items:
            item["sourceFeed"] = self.config["id"]

        meta = {
            "items": len(items),
            "adapter": self.config["adapter"],
        }
        for key in self.config.get("packet_meta_keys") or []:
            if key in packet:
                meta[key] = packet.get(key)
        if self.config.get("debug_command"):
            meta["command"] = selected_command
        return SourceResult(items=items, packet=meta)

