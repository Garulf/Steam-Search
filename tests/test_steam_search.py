import runpy
from pathlib import Path

import steam_client.utils
from pyflowlauncher import Plugin

from conftest import APPS, FakeSteam

PLUGIN_DIR = Path(__file__).resolve().parents[1] / "src" / "plugin"


def titles(response):
    return [result["Title"] for result in response["Result"]]


def test_empty_query_lists_every_app_except_redistributables(call):
    response = call("query", "")
    assert titles(response) == ["DOOM II", "DOOM 3", "DOOM", "Portal 2", "RetroArch"]
    assert {result["Score"] for result in response["Result"]} == {0}


def test_query_keeps_fuzzy_matches_only(call):
    response = call("query", "doom")
    assert titles(response) == ["DOOM II", "DOOM 3", "DOOM"]
    assert all(isinstance(result["Score"], int) and result["Score"] > 0 for result in response["Result"])


def test_redistributables_are_hidden_from_search(call):
    assert titles(call("query", "steamworks")) == []


def test_result_launches_game_and_shows_box_art(call):
    (result,) = call("query", "portal")["Result"]
    assert result["SubTitle"] == "Launch Portal 2"
    assert Path(result["IcoPath"]) == Path("C:/Steam/appcache/librarycache/620/icon.jpg")
    assert result["JsonRPCAction"] == {"Method": "run_game_id", "Parameters": ["620"], "DontHideAfterAction": False}
    assert result["Preview"] == {
        "PreviewImagePath": str(Path("C:/Steam/appcache/librarycache/620/library_600x900.jpg")),
        "Description": "Portal 2",
        "IsMedia": True,
        "PreviewDeligate": "",
    }


def test_run_game_id_opens_steam_uri(call, monkeypatch):
    opened = []
    monkeypatch.setattr("webbrowser.open", opened.append)
    call("run_game_id", "620")
    assert opened == ["steam://rungameid/620"]


def test_context_menu_is_empty(call):
    assert call("context_menu", None) is None


def test_entry_point_reads_steam_from_registry(monkeypatch):
    steam = FakeSteam(APPS)
    started = []
    monkeypatch.setattr(steam_client.utils, "steam_from_registry", lambda: steam)
    monkeypatch.setattr(Plugin, "run", lambda plugin: started.append(plugin))
    runpy.run_path(str(PLUGIN_DIR), run_name="__main__")
    assert len(started) == 1
