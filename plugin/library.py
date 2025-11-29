from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union, TYPE_CHECKING
import webbrowser
import logging
from functools import cached_property
if TYPE_CHECKING:
    from steam import Steam

from .vdfs import VDF
from . import crc_algorithms

log = logging.getLogger(__name__)


@dataclass
class Library:
    steam: 'Steam'
    path: Union[str, Path]

    def games(self):
        """
        Return a list of games in this library.
        """
        games = []
        image_dir = LibraryImageDir(Path(self.steam.path).joinpath('appcache', 'librarycache'))
        for appmanifest in Path(self.path).joinpath('steamapps').glob('appmanifest_*.acf'):
            try:
                manifest = VDF(appmanifest)
            except FileNotFoundError:
                logging.debug(
                    f'Could not find game manifest ("{appmanifest}")')
                continue
            except SyntaxError:
                logging.debug(
                    f'Could not parse game manifest ("{appmanifest}")')
                continue
            except KeyError:
                logging.debug(
                    f'Unable to parse game manifest ("{appmanifest}")')
                continue
            try:
                games.append(
                    LibraryItem(
                        name=manifest['AppState']['name'],
                        path=Path(self.path).joinpath(
                            'steamapps', 'common', manifest['AppState']['installdir']),
                        id=manifest['AppState']['appid'],
                        image_dir=image_dir,
                    )
                )
            except KeyError:
                logging.debug(
                    f'Unable to parse game manifest ("{appmanifest}")')
                continue
        return games

class LibraryImageDir:
    """
    Caches the filesystem access of a library image directory
    """

    def __init__(self, image_dir: Union[str, Path]):
        image_dir = Path(image_dir)
        self.grid = image_dir.name == 'grid'
        self._files_cache = {}
        try:
            for file in image_dir.iterdir():
                haystack_prefix = file.name.split(".", 1)[0]
                self._files_cache[haystack_prefix] = file
        except FileNotFoundError:
            pass

    def get_image(self, id: str, type: str, sep='_') -> Optional[Path]:
        prefix = f'{id}{sep}{type}'
        alt_prefix = f'app_{id}{sep}{type}'
        try:
            for key, file in self._files_cache.items():
                if key.startswith(prefix) or key.startswith(alt_prefix):
                    return file
        except FileNotFoundError:
            return None
        return None


class LibraryItem:
    """
    Base class for all library items.
    """

    def __init__(self, name: str, path: Union[str, Path], image_dir: LibraryImageDir, id: str = None):
        self.name = name
        self.path = Path(path)
        self.image_dir = image_dir
        self._id = id
        self._image_id = self.id

    @property
    def id(self):
        """
        Return Steam ID for this library item.
        """
        if self._id is None:
            self._id = self.generate_id()
        return self._id

    def uri(self) -> str:
        """
        Return Steam run game URI for this item.
        """
        return f"steam://rungameid/{self.id}"

    def launch(self) -> None:
        """
        Launch this Steam library item.
        """
        from steam import Steam
        webbrowser.open(self.uri())

    def get_image(self, type: str, sep='_') -> Path:
        id = self.id
        if self.image_dir.grid:
            # Grid images use the short ID
            id = self.short_id()
        return self.image_dir.get_image(id, type, sep)

    @cached_property
    def icon(self) -> Path:
        """
        Return the icon for this library item.
        """
        img = self.get_image('icon')
        if img:
            return img
        exe = self._find_local_exe_icon()
        if exe:
            return exe
        return Path(self.unquoted_path())

    @cached_property
    def hero(self) -> Path:
        """
        Return the hero image for this library item.
        """
        img = self.get_image('hero')
        if img:
            return img
        return None

    @cached_property
    def logo(self) -> Path:
        """
        Return the logo for this library item.
        """
        img = self.get_image('logo')
        if img:
            return img
        return None

    @cached_property
    def poster(self) -> Path:
        """
        Return the box art for this library item.
        """
        return self.get_image('p', sep='')

    @cached_property
    def grid(self) -> str:
        """
        Return the grid image for this library item.
        """
        return self.get_image('', sep='')

    def _find_local_exe_icon(self) -> Optional[Path]:
        base = self.path
        try:
            if base.is_file() and base.suffix.lower() == ".exe":
                return base
            candidates = []
            name_no_space = self.name.replace(" ", "")
            dir_name = base.name
            candidates.extend([
                base.joinpath(f"{dir_name}.exe"),
                base.joinpath(f"{self.name}.exe"),
                base.joinpath(f"{name_no_space}.exe"),
                base.joinpath("Win64", f"{dir_name}-Win64-Shipping.exe"),
                base.joinpath("Binaries", "Win64", f"{dir_name}-Win64-Shipping.exe"),
                base.joinpath("Binaries", "Win64", f"{name_no_space}-Win64-Shipping.exe"),
            ])
            for p in candidates:
                if p.exists():
                    return p
            ue_dirs = [
                base.joinpath("Binaries", "Win64"),
                base.joinpath("Win64"),
                base.joinpath("bin"),
                base.joinpath("Bin"),
                base.joinpath("bin64"),
            ]
            for d in ue_dirs:
                if d.exists():
                    for child in d.glob("*.exe"):
                        return child
            for child in base.glob("*.exe"):
                return child
        except Exception:
            return None
        return None

    def generate_id(self) -> str:
        """
        Generate Steam ID for this library item.
        """
        algorithm = crc_algorithms.Crc(
            width=32, poly=0x04C11DB7, reflect_in=True, xor_in=0xffffffff, reflect_out=True, xor_out=0xffffffff)
        input_string = ''.join([str(self.path), self.name])
        top_32 = algorithm.bit_by_bit(input_string) | 0x80000000
        full_64 = (top_32 << 32) | 0x02000000
        return str(full_64)

    def short_id(self) -> str:
        """
        Return Steam shortened App ID.
        This is primarily used for shortcuts in the grid.
        """
        return str(int(self.id) >> int(32))

    def unquoted_path(self) -> str:
        """
        Strips LibraryItem's path of extraneous quutation marks.
        """
        if str(self.path).count('"') > 2:
            return str(self.path).replace('"', '', 2)
        else:
            return str(self.path).replace('"', '')
