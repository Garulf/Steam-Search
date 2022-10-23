from dataclasses import dataclass, Field
from pathlib import Path
from typing import Union, TYPE_CHECKING
from distutils.util import strtobool
from collections import UserList

from .vdfs import VDF
from .library import LibraryItem
if TYPE_CHECKING:
    from steam import Steam


STEAMID64IDENT = 76561197960265728
SCREENSHOTS_DIR = '760'
TRUE = "1"
FALSE = "0"


@dataclass
class LoginUser:
    ID: str
    AccountName: str
    PersonaName: str
    MostRecent: str
    steam_path: Union[str, Path]
    RememberPassword: str = None
    WantsOfflineMode: str = None
    SkipOfflineModeWarning: str = None
    AllowAutoLogin: str = None
    Timestamp: str = None

    @property
    def steamid(self) -> str:
        """
        Return SteamID64 for this user.
        """
        return str(int(self.ID) - STEAMID64IDENT)

    @property
    def path(self) -> Path:
        """
        Return userdata path for this user.
        """
        return self.steam_path.joinpath('userdata', self.steamid)

    @property
    def screenshots_path(self) -> Path:
        """
        Return screenshots path for this user.
        """
        return self.path.joinpath(SCREENSHOTS_DIR)

    @property
    def grid_path(self) -> Path:
        """
        Return grid path for this user.
        """
        return self.path.joinpath('config', 'grid')

    @property
    def shortcuts_path(self) -> Path:
        """
        Return shortcuts path for this user.
        """
        return self.path.joinpath('config', 'shortcuts.vdf')

    def shortcuts(self) -> list:
        _list = []
        if not self.shortcuts_path.exists():
            return _list
        with open(self.shortcuts_path, 'rb') as file:
            _shortcuts = file.read()
            # Steam Rom Manager sometimes uses lowercase...
            _shortcuts = _shortcuts.replace(b'appname\x00', b'AppName\x00')
        split = _shortcuts.split(b'AppName\x00')[1:]
        if len(split) == 0:
            return _list
        for shortcut in _shortcuts.split(b'AppName\x00')[1:]:
            _list.append(
                LibraryItem(
                    name=shortcut.split(b'\x00')[0].decode('utf-8'),
                    path=shortcut.split(b'\x00')[2].decode('utf-8'),
                    image_dir=self.grid_path
                )
            )
        return _list


class LoginUsers(UserList):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def most_recent(self) -> LoginUser:
        for user in self:
            if user.MostRecent == TRUE:
                return user
        return None
