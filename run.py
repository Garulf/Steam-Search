import sys
import os

plugindir = os.path.abspath(os.path.dirname(__file__))
plugin_root = sys.argv[0]
os.chdir(os.path.dirname(os.path.abspath(plugin_root)))
sys.path.append(plugindir)
sys.path.append(os.path.join(plugindir, "lib"))
sys.path.append(os.path.join(plugindir, "plugin"))

from plugin.main import SteamSearch

if __name__ == "__main__":
    SteamSearch()
    