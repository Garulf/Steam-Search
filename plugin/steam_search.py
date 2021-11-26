# -*- coding: utf-8 -*-
import json
import os
import re
import webbrowser
from pathlib import Path

from helper import Steam

from flox import Flox


class SteamSearch(Flox):
    def __init__(self):
        self._steam = Steam()
        super().__init__()

    def query(self, query):
        games = self._steam.all_games()
        q = query.lower()
        pattern = ".*?".join(q)
        regex = re.compile(pattern)
        for game in games:
            match = regex.search(game.name.lower())
            if match: 
                self.add_item(
                    title=game.name,
                    subtitle=str(game.install_path()),
                    icon=str(game.icon()),
                    method="launch_game",
                    parameters=[game.id],
                    context=[game.id] 
                )

    def context_menu(self, data):
        game_id = data[0]
        self.add_item(
            title="Show in Steam store",
            subtitle="Opens game's Steam store page",
            method="launch_store",
            parameters=[game_id] 
        )
        self.add_item(
            title="Uninstall Game",
            subtitle="Uninstall this game from your Steam library",
            method="uninstall_game",
            parameters=[game_id] 
        )
        

    def launch_game(self, game_id):
        webbrowser.open("steam://rungameid/{}".format(game_id))

    def launch_store(self, game_id):
        webbrowser.open("steam://store/{}".format(game_id))

    def uninstall_game(self, game_id):
        webbrowser.open("steam://uninstall/{}".format(game_id))


if __name__ == "__main__":
    SteamSearch()
