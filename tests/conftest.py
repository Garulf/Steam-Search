import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List

import pytest

from steam_search import build_plugin


@dataclass
class FakeApp:
    appid: str
    name: str

    @property
    def icon(self) -> Path:
        return Path("C:/Steam/appcache/librarycache") / self.appid / "icon.jpg"

    @property
    def grid(self) -> Path:
        return Path("C:/Steam/appcache/librarycache") / self.appid / "library_600x900.jpg"


class FakeLibrary:
    def __init__(self, apps: List[FakeApp]):
        self._apps = apps

    def all_apps(self):
        return iter(self._apps)


class FakeSteam:
    def __init__(self, apps: List[FakeApp]):
        self.apps = apps

    @property
    def library(self) -> FakeLibrary:
        return FakeLibrary(self.apps)


APPS = [
    FakeApp("2280", "DOOM II"),
    FakeApp("208200", "DOOM 3"),
    FakeApp("379720", "DOOM"),
    FakeApp("228980", "Steamworks Common Redistributables"),
    FakeApp("620", "Portal 2"),
    FakeApp("3051235328", "RetroArch"),
]


@pytest.fixture
def plugin(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "argv", [str(tmp_path / "run.py")])
    return build_plugin(FakeSteam(APPS))


@pytest.fixture
def call(plugin, monkeypatch, capsys):
    def call(method, *parameters):
        request = {"method": method, "parameters": list(parameters)}
        monkeypatch.setattr(sys, "argv", [sys.argv[0], json.dumps(request)])
        plugin.run()
        out = capsys.readouterr().out
        return json.loads(out) if out else None

    return call
