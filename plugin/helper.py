import winreg as reg
from winreg import HKEY_CURRENT_USER, HKEY_LOCAL_MACHINE

STEAM_REG_KEY = r"SOFTWARE\WOW6432Node\Valve\Steam"

with reg.OpenKey(HKEY_LOCAL_MACHINE, "SOFTWARE\WOW6432Node\Valve\Steam") as hkey:
    try:
        steam_path = reg.QueryValueEx(hkey, "InstallPath")[0]
    except FileNotFoundError:
        steam_path = None

STEAM_PATH = steam_path
