#!/bin/bash
# github MCP Server launcher
# .secrets.envからAPIキーを読み込んで起動
set -a
source /home/__USERNAME__/.secrets.env
set +a
exec /home/__USERNAME__/.local/bin/github-mcp-server
