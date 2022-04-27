from dataclasses import dataclass
from pathlib import Path
from typing import Union, TYPE_CHECKING
import webbrowser
import logging
from functools import cached_property
if TYPE_CHECKING:
    from steam import Steam

from vdfs import VDF
import crc_algorithms

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
        for appmanifest in Path(self.path).joinpath('steamapps').glob('appmanifest_*.acf'):
            try:
                manifest = VDF(appmanifest)
            except FileNotFoundError:
                logging.warning(f'Could not find game manifest ("{manifest}")')
                continue
            except SyntaxError:
                logging.warning(f'Could not parse game manifest ("{manifest}")')
                continue
            except KeyError:
                logging.warning(f'Unable to parse game manifest ("{manifest}")')
                continue
            else:                
                games.append(
                    LibraryItem(
                        name=manifest['AppState']['name'],
                        path=Path(self.path).joinpath(manifest['AppState']['installdir']),
                        id=manifest['AppState']['appid'],
                        image_dir=Path(self.steam.path).joinpath('appcache', 'librarycache'),
                    )
                )
        return games

class LibraryItem:
    """
    Base class for all library items.
    """

    def __init__(self, name:str, path:Union[str, Path], image_dir:Union[str, Path], id:str=None):
        self.name = name
        self.path = Path(path)
        self.image_dir = Path(image_dir)
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

    def get_image(self, type:str, sep='_') -> Path:
        id = self.id 
        if Path(self.image_dir).name == 'grid':
            # Grid images use short ID format
            id = self.short_id()
        return next(Path(self.image_dir).glob(f'{id}{sep}{type}.*'), None)

    @cached_property
    def icon(self) -> Path:
        """
        Return the icon for this library item.
        """
        return self.get_image('icon') or Path(self.unquoted_path())

    @cached_property
    def hero(self) -> Path:
        """
        Return the hero image for this library item.
        """
        return self.get_image('hero')

    @cached_property
    def logo(self) -> Path:
        """
        Return the logo for this library item.
        """
        return self.get_image('logo')

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

    def generate_id(self) -> str:
        """
        Generate Steam ID for this library item.
        """
        algorithm = crc_algorithms.Crc(width = 32, poly = 0x04C11DB7, reflect_in = True, xor_in = 0xffffffff, reflect_out = True, xor_out = 0xffffffff)
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
