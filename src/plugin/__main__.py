from steam_client.utils import steam_from_registry

from steam_search import build_plugin

build_plugin(steam_from_registry()).run()
