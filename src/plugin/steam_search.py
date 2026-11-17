from pyflowlauncher import Plugin, Result
from pyflowlauncher.models.result import PreviewInfo
from steam_client.commands import run_game_id
from steam_client.steam import Steam

BLACKLISTED_APP_NAMES = frozenset({"steamworks common redistributables"})


def build_plugin(steam: Steam) -> Plugin:
    plugin = Plugin([run_game_id])

    @plugin.on_method
    async def query(query: str):
        for game in steam.library.all_apps():
            if game.name.casefold() in BLACKLISTED_APP_NAMES:
                continue
            score = 0
            if query:
                match_data = await plugin.launcher.api.fuzzy_search(
                    query,
                    game.name,
                )
                if match_data.score < match_data.score_cutoff:
                    continue
                score = int(match_data.score)
            preview_info = PreviewInfo(
                PreviewImagePath=str(game.grid) if game.grid else None,
                Description=game.name,
                IsMedia=True,
                PreviewDeligate=""
            )
            yield Result(
                title=game.name,
                subtitle=f"Launch {game.name}",
                icon=game.icon,
                score=score,
                preview=preview_info
            ).add_action(run_game_id, parameters=[game.appid])

    return plugin
