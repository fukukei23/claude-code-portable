#!/bin/bash
# MiniMax MCP Server launcher - Claude Desktop用
# Python unbuffered mode (-u) でnull byte問題を回避
set -a
source /home/__USERNAME__/.secrets.env
set +a
exec python3 -u /home/__USERNAME__/.claude/scripts/mcp/minimax-mcp-server.py
