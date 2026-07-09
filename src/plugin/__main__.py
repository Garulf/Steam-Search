from pyflowlauncher import Plugin, Result
from steam_client.utils import steam_from_registry
from steam_client.commands import run_game_id
from pyflowlauncher.models.result import PreviewInfo

plugin = Plugin([run_game_id])
steam = steam_from_registry()


@plugin.on_method
async def query(query: str):
    for game in steam.library.games():
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
            PreviewImagePath=str(game.grid),
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


plugin.run()
