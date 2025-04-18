#!/usr/bin/env python
# File name:    genMCP.py
# Date:         2025/04/17 16:36
# Author:       Sridhar V Iyer (iyer@sridharv.net)
# Description: 


import sys
from versaEP import *

def generate_mcp_resources(api_endpoints):
    """
    Automatically converts API endpoint dictionary to async mcp.tool definitions using httpx
    
    Args:
        api_endpoints: Dictionary of API endpoints
    
    Returns:
        String containing all async mcp.tool definitions
    """
    import re
    from textwrap import dedent
    
    tools = []
    
    # First, add the necessary imports
    header = """
    import httpx
    from mcp.server.fastmcp import FastMCP
    from typing import Dict, List, Optional, Any
    
    # Initialize the MCP server
    mcp = FastMCP("API Server")
    
    # Disable SSL warnings if you're using verify=False
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    """
    
    for name, endpoint in api_endpoints.items():
        # Create a valid Python function name from the endpoint name
        function_name = name.lower().replace(' ', '_').replace('-', '_')
        
        # Extract path parameters from URL
        path_params = re.findall(r'{(\w+)}', endpoint['url'])
        
        # Determine which params are query params (those not in path)
        query_params = [p for p in endpoint['params'] if p not in path_params]
        
        # Create function parameters with type hints
        params_with_types = []
        for param in path_params + query_params:
            params_with_types.append(f"{param}: str")
        
        params_list = ", ".join(params_with_types)
        
        # Build the tool definition
        tool_def = f"""
        @mcp.tool()
        async def {function_name}({params_list}) -> Dict[str, Any]:
            \"\"\"
            {name}
            
            Method: {endpoint['method']}
            URL: {endpoint['url']}
            Parameters: {', '.join(endpoint['params']) if endpoint['params'] else 'None'}
            
            Returns:
                JSON response from the API
            \"\"\"
            # Construct the URL
            url = f"{{director.url}}{endpoint['url']}"
        """
        
        # Replace path parameters in the URL
        for param in path_params:
            tool_def += f"    url = url.replace('{{{param}}}', {param})\n"
        
        # Add query parameters if any exist
        if query_params:
            tool_def += """
            # Add query parameters
            query_params = {}
            """
            for param in query_params:
                tool_def += f"""
            if {param}:
                query_params['{param}'] = {param}
                """
        
        # Complete the function
        tool_def += f"""
            # Make the request
            async with httpx.AsyncClient(verify=False) as client:
                response = await client.{endpoint['method'].lower()}(url, 
                    headers=director.get_header(),
                    {'params=query_params' if query_params else ''}
                )
            
            # Attempt to return JSON, fall back to text if not valid JSON
            try:
                return response.json()
            except ValueError:
                return {{"text": response.text}}
        """
        
        tools.append(dedent(tool_def))
    
    # Add a main block to run the server
    footer = """
    if __name__ == "__main__":
        import uvicorn
        uvicorn.run(mcp.app, host="0.0.0.0", port=8000)
    """
    
    return dedent(header) + "\n\n" + "\n".join(tools) + "\n\n" + dedent(footer)


mcp_resources = generate_mcp_resources(api_endpoints)
with open('mcp_resources.py', 'w') as f:
	f.write(mcp_resources)
