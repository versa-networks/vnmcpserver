# MCP Server for Versa API

A server that exposes a subset of queryable resources from the Versa API through the MCP specification.

## License

Copyright © 2025 Versa Networks 

This software is proprietary. Users may use and modify this software for their own use, but redistribution in any form without explicit written permission is strictly prohibited.

For permissions beyond the scope of this license, please contact sridhariyer@versa-networks.com 

## About

This MCP server is specifically designed for querying the Versa API server. It exposes a subset of Versa API resources that can be queried through the MCP (Model Control Protocol) specification, which is still a work in progress.

**Note**: The MCP specification is currently missing many security checks. Please use this within a secured environment with trusted tools only.

## Prerequisites

This server uses [uv](https://docs.astral.sh/uv/guides/install-python/) for Python package management and installation.

## Setup

### General Setup

1. Clone the repository
2. Run `uv sync` to synchronize dependencies

### STDIO Mode Setup

1. Install the project:
   ```
   uv run mcp install main.py
   ```

2. Modify `mcp.conf` with appropriate values for your environment

3. Copy the configuration file to the appropriate location:
   - For Claude Desktop: Place in the designated config directory
   - For other applications: Deploy according to your application's requirements

### SSE Mode Setup

1. Modify `mcp.env` with appropriate values

2. Source the environment file:
   ```
   source mcp.env
   ```

3. Run the SSE server:
   ```
   uv run main_sse.py
   ```

4. Configure your Claude Desktop by setting the following in `claude_desktop_config.json`:
   ```json
   {
     "mcpServers": {
       "Versa API Server": {
         "command": "npx",
         "args": ["mcp-remote", "http://127.0.0.1:8000/sse"]
       }
     }
   }
   ```

   This uses [mcp-remote](https://www.npmjs.com/package/mcp-remote) to connect to the remote SSE server.

## Security Warning

This implementation of the MCP specification is missing many security checks. Please use this within a secured environment with trusted tools only.

