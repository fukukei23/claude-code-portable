#!/bin/bash
# brave-search MCP Server launcher
# .secrets.envからAPIキーを読み込んで起動
set -a
source /home/__USERNAME__/.secrets.env
set +a
exec /home/__USERNAME__/.local/share/fnm/node-versions/v22.22.2/installation/bin/brave-search-mcp-server
