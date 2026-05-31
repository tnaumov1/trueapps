import logging
from pathlib import Path
from typing import Any

import yaml

log = logging.getLogger(__name__)
COMPOSE_FILENAMES = ("compose.yml", "compose.yaml", "docker-compose.yml", "docker-compose.yaml")


def find_compose_file(app_dir: Path) -> Path | None:
    for name in COMPOSE_FILENAMES:
        candidate = app_dir / name
        if candidate.is_file():
            return candidate
    return None


def discover_apps(apps_dir: Path, only: str | None) -> list[Path]:
    if not apps_dir.is_dir():
        raise RuntimeError(f"apps dir not found: {apps_dir}")
    dirs = sorted(p for p in apps_dir.iterdir() if p.is_dir())
    if only:
        dirs = [p for p in dirs if p.name == only]
        if not dirs:
            raise RuntimeError(f"app {only} not found under {apps_dir}")
    return dirs


def compose_equal(local_yaml: str, remote_config: dict[str, Any]) -> bool:
    local = yaml.safe_load(local_yaml) or {}
    return local == remote_config


def find_app_compose(app_dir: Path) -> tuple[str, Path] | None:
    app_name = app_dir.name
    compose_file = find_compose_file(app_dir)

    if compose_file is None:
        log.warning("skip [%s]: no compose file in %s", app_name, app_dir)
        return None

    return app_name, compose_file
