# -*- coding: utf-8 -*-
import json
import os
import re
import webbrowser


from flowlauncher import FlowLauncher


class Steamlauncher(FlowLauncher):

    def __init__(self):
        self.results = []
        self.games = []
        with open("./config.json", "r") as f:
            self.dirConfig = json.load(f)
        super().__init__()

    def grab_games(self):
        for config_dirs in self.dirConfig:
            if os.path.isdir(self.dirConfig[config_dirs]):
                steamapps_dir = self.dirConfig[config_dirs]
                for dir_file in os.scandir(steamapps_dir):
                    if "appmanifest" in dir_file.name:
                        game_id = dir_file.name.replace("appmanifest_", "").replace(
                            ".acf", ""
                        )
                        with open(dir_file.path) as f:
                            for line in f:
                                if line.find("name") > 0:
                                    game_title = (
                                        line.replace('"', "").replace("name", "").strip()
                                    )
                                    break
                            for line in f:
                                if line.find("installdir") > 0:
                                    install_dir = (
                                        line.replace('"', "").replace("installdir", "").strip()
                                    )
                                    break
                        app_dir = f'{steamapps_dir}\\common\\{install_dir}'
                        game_icon = self.grab_icon(game_title, app_dir)
                        game = {"game_id": game_id, "game_title": game_title, "game_icon": game_icon, "app_dir": app_dir}
                        if game not in self.games:
                            self.games.append(
                                game
                            )


    def grab_icon(self, game_title, app_dir):
        game_icon = "./icon/steam-icon.png"
        try:
            for game_file in os.scandir(app_dir):
                if game_file.name.lower().startswith(game_title.lower()[0]) and game_file.name.endswith('.exe'):
                    game_icon = f'{app_dir}\{game_file.name}'
                    break
            for game_file in os.scandir(app_dir):
                if game_file.name.endswith('.exe') and 'crash' not in game_file.name.lower() and 'loader' not in game_file.name.lower():
                    game_icon = f'{app_dir}\{game_file.name}'
                    break
        except FileNotFoundError:
            pass
        return game_icon

    def query(self, query):
        self.grab_games()
        q = query.lower()
        pattern = ".*?".join(q)
        regex = re.compile(pattern)
        for item in self.games:
            match = regex.search(item["game_title"].lower())
            if match:
                self.results.append(
                    {
                        "Title": item["game_title"],
                        "SubTitle": item["app_dir"],
                        "IcoPath": item["game_icon"],
                        "JsonRPCAction": {
                            "method": "launch_game",
                            "parameters": [item["game_id"]],
                            "dontHideAfterAction": False,
                        },
                    }
                )
        return self.results

    def launch_game(self, game_id):
        webbrowser.open("steam://rungameid/{}".format(game_id))


if __name__ == "__main__":
    Steamlauncher()
