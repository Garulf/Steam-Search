# -*- coding: utf-8 -*-
import webbrowser

from helper import Steam, SteamLibraryNotFound, SteamExecutableNotFound

from flox import Flox, ICON_SETTINGS


class SteamSearch(Flox):

    def query(self, query):
        try:
            self._steam = Steam(self.settings.get('steam_path'))
            if self.settings.get('steam_path') is None or self.settings.get('steam_path') == '':
                self.settings['steam_path'] = str(self._steam.steam_path)
            games = self._steam.all_games()
        except (SteamLibraryNotFound, SteamExecutableNotFound):
            self.add_item(
                title="Steam library not found!",
                subtitle="Please set your Steam library path in the settings",
                method=self.open_setting_dialog,
                icon=ICON_SETTINGS
            )
            return
        q = query.lower()
        for game in games:
            if q in game.name.lower(): 
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
            title="Show News",
            subtitle="Opens game's news page in Steam",
            method="launch_news",
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

    def launch_news(self, game_id):
        webbrowser.open("steam://appnews/{}".format(game_id))

if __name__ == "__main__":
    SteamSearch()
