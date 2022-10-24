class SteamExecutableNotFound(Exception):
    def __init__(self, path) -> None:
        message = f'Could not locate steam.exe at: {path}'
        super().__init__(message)


class SteamLibraryNotFound(Exception):
    def __init__(self, path) -> None:
        message = f'Could not find Steam libraries manifest ("libraryfolders.vdf") at: {path}'
        super().__init__(message)
