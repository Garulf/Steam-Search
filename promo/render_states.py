"""Render every launcher state used by the ad with flow-render.

Each state is a flow-render Config (query box + result rows) pushed through
flow-render's own pipeline: Jinja template -> headless Chromium screenshot ->
transparent crop. Every state is rendered twice, with and without the caret,
so the ad can blink it during holds.

Output: promo/build/states/<name>.png, <name>.nocaret.png and manifest.json.
"""
import json
import sys
import tempfile
from pathlib import Path

from flow_render.config import Config
from flow_render.image import crop_to_content
from flow_render.renderer import render_from_config
from flow_render.result_config import resolve_icon
from flow_render.screenshot import capture_screenshot

HERE = Path(__file__).resolve().parent
ICONS = HERE / "icons"
OUT = HERE / "build" / "states"
PLUGIN = json.loads((HERE.parent / "data" / "plugin.json").read_text())

CSS = "win11-dark.css"
KEYWORD = PLUGIN["ActionKeyword"]


def icon(name):
    return resolve_icon(str(ICONS / f"{name}.png"))


def game(title, icon_name):
    return {"title": title, "subtitle": f"Launch {title}", "icon": icon(icon_name)}


DOOM_II = game("DOOM II", "doom2")
DOOM_3 = game("DOOM 3", "doom3")
DOOM = game("DOOM", "doom")
DOOM_ETERNAL = game("DOOM Eternal", "doom-eternal")
DOOM_3_BFG = game("DOOM 3: BFG Edition", "doom3-bfg")

ALL_DOOM = [DOOM_II, DOOM_3, DOOM, DOOM_ETERNAL, DOOM_3_BFG]


def steam_state(query, results, selection=0, keyword=KEYWORD):
    return Config(
        keyword=keyword,
        query=query,
        icon=icon("steam"),
        max_results=5,
        selection=selection,
        results=results,
        css=CSS,
    )


def states():
    # Typing the action keyword: no plugin results yet.
    yield "k1", steam_state("s", [], keyword="")
    yield "k2", steam_state("st", [], keyword="")
    yield "k3", steam_state("", [], keyword=KEYWORD)

    # "st doom" narrows to the DOOM games.
    for query in ("d", "do", "doo", "doom"):
        yield f"doom-{query}", steam_state(query, ALL_DOOM)
    for selection in range(1, 4):
        yield f"doom-sel{selection}", steam_state("doom", ALL_DOOM, selection=selection)

    # Fuzzy matching: "st d3bfg" finds DOOM 3: BFG Edition.
    yield "fz-d", steam_state("d", ALL_DOOM)
    yield "fz-d3", steam_state("d3", [DOOM_3, DOOM_3_BFG])
    for query in ("d3b", "d3bf", "d3bfg"):
        yield f"fz-{query}", steam_state(query, [DOOM_3_BFG])

    # Plugin manager install flow, typed one character at a time.
    install = "pm install steam search"
    pm_result = {
        "title": f"{PLUGIN['Name']} by {PLUGIN['Author']}",
        "subtitle": PLUGIN["Description"],
        "icon": icon("steam"),
    }
    for i in range(1, len(install) + 1):
        typed = install[:i]
        done = i == len(install)
        yield f"pm-{i:02d}", Config(
            keyword="",
            query=typed,
            query_suggestion=typed,
            icon=icon("plugin-manager"),
            max_results=1,
            results=[pm_result] if done else [],
            css=CSS,
        )


def render_png(config, destination, build_dir):
    html = build_dir / "output.html"
    render_from_config(config, str(html))
    raw = capture_screenshot(str(html))
    return crop_to_content(raw, destination)


def main():
    only = set(sys.argv[1:])
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = {}
    with tempfile.TemporaryDirectory(prefix="steam-search-ad-") as build_dir:
        for name, config in states():
            if only and name not in only:
                continue
            for caret in (True, False):
                config.show_caret = caret
                suffix = "" if caret else ".nocaret"
                path = render_png(config, OUT / f"{name}{suffix}.png", Path(build_dir))
                print(f"rendered {path.relative_to(HERE)}")
            manifest[name] = f"{name}.png"
    if not only:
        (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
