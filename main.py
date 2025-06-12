import httpx
from mcp.server.fastmcp import FastMCP
from typing import Dict, List, Optional, Any
import time
import jwt
import json
import os
import requests


# Disable SSL warnings if you're using verify=False
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
LIVE_COMMAND_REFERENCES = {
    # Live Users Commands (VERIFIED WORKING)
    "live_users_detail": "orgs%2Forg-services%2F{org_name}%2Fuser-identification%2Flive-users%2Flist%2Fdetail",
    "live_users_brief": "orgs%2Forg-services%2F{org_name}%2Fuser-identification%2Flive-users%2Flist%2Fbrief",
    "live_users": "orgs%2Forg-services%2F{org_name}%2Fuser-identification%2Flive-users%2Flist%2Fdetail",  # Default to detail
}

# Commands that require organization name - ADD THIS BLOCK
ORG_REQUIRED_COMMANDS = {
    "live_users_detail", "live_users_brief", "live_users"
}
# Helper function to resolve command references - ADD THIS FUNCTION
def resolve_command_reference(command_ref: str, org_name: str = None) -> str:
    """
    Resolve a short form command reference to the full URL-encoded command
    
    Args:
        command_ref: Short form reference (e.g., "live_users", "live_users_detail")
        org_name: Organization name (required for org-specific commands)
    
    Returns:
        Full URL-encoded command string
        
    Raises:
        ValueError: If command reference is unknown or org_name is missing when required
    """
    if command_ref not in LIVE_COMMAND_REFERENCES:
        available = list(LIVE_COMMAND_REFERENCES.keys())
        raise ValueError(f"Unknown command reference '{command_ref}'. Available: {available}")
    
    # Check if org name is required
    if command_ref in ORG_REQUIRED_COMMANDS and not org_name:
        raise ValueError(f"Organization name is required for command '{command_ref}'")
    
    # Get the command template
    command_template = LIVE_COMMAND_REFERENCES[command_ref]
    
    # Replace org name if needed
    if "{org_name}" in command_template:
        if not org_name:
            raise ValueError(f"Organization name is required for command '{command_ref}'")
        command = command_template.replace("{org_name}", org_name)
    else:
        command = command_template
    
    return command

def resolve_command_reference_live_pageable(command_ref: str, org_name: str = None) -> str:
    """
    Resolve a short form command reference to the full URL-encoded command
    
    Args:
        command_ref: Short form reference (e.g., "eip-cache-brief")
        org_name: Organization name (required for org-specific commands)
    
    Returns:
        Full command string
        
    Raises:
        ValueError: If command reference is unknown or org_name is missing when required
    """
    if command_ref not in LIVE_PAGEABLE_COMMAND_REFERENCES:
        available = list(LIVE_PAGEABLE_COMMAND_REFERENCES.keys())
        raise ValueError(f"Unknown command reference '{command_ref}'. Available: {available}")
    
    # Check if org name is required
    if command_ref in ORG_REQUIRED_COMMANDS and not org_name:
        raise ValueError(f"Organization name is required for command '{command_ref}'")
    
    # Get the command template
    command_template = LIVE_PAGEABLE_COMMAND_REFERENCES[command_ref]
    
    # Replace org name if needed
    if "{org_name}" in command_template:
        if not org_name:
            raise ValueError(f"Organization name is required for command '{command_ref}'")
        command = command_template.replace("{org_name}", org_name)
    else:
        command = command_template
    
    return command
class Director:
    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password
        """ Manages application lifespan """
        self.payload = {"client_id": os.environ['VN_CLIENT_ID'],
               "client_secret": os.environ['VN_CLIENT_SECRET'],
               "username": self.username,
               "password": self.password,
               "grant_type": "password"}
        self.regen_token()

    def regen_token(self):
        resp = requests.request("POST", url=f"{self.url}/auth/token",
                        headers={"Content-Type": "application/json", "Accept": "application/json"},
                        data=json.dumps(self.payload),
                        verify=False)

        mydata = resp.text
        jsondata = json.loads(mydata)
        self.access_token = jsondata['access_token']
        self.headers =   {
              'Authorization': f'Bearer {self.access_token}',
              "Accept": "application/json",
              "Content-Type": "application/json",
            }

    def get_header(self):
        decoded_token = jwt.decode(self.access_token, options={"verify_signature": False})
        exp = decoded_token['exp']
        if int(exp) <= int(time.time()):
            self.regen_token()

        return self.headers
        

director = Director(url=os.environ['DIRECTOR_URL'], username=os.environ['VN_USERNAME'], password=os.environ['VN_PASSWORD'])
mcp = FastMCP(name = "Versa API Server", instructions="This server is used for all Versa related apis",  dependencies=["requests","urllib3","pyjwt"])



@mcp.tool()
async def get_all_appliance_status(limit: str, offset: str) -> Dict[str, Any]:
    """
    Get All Appliance Status

    Method: GET
    URL: /nextgen/appliance/status
    Parameters: limit, offset

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/nextgen/appliance/status"

    # Add query parameters
    query_params = {}

    if limit:
        query_params['limit'] = limit

    if offset:
        query_params['offset'] = offset

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),
            params=query_params
        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_single_appliance_status(id: str, byName: str) -> Dict[str, Any]:
    """
    Get Single Appliance Status

    Method: GET
    URL: /nextgen/appliance/status/{id}
    Parameters: byName

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/nextgen/appliance/status/{id}"
    url = url.replace('{id}', id)

    # Add query parameters
    query_params = {}

    if byName:
        query_params['byName'] = byName

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),
            params=query_params
        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_device_template_listing(deviceName: str, tenant: str) -> Dict[str, Any]:
    """
    Get Device Template Listing

    Method: GET
    URL: /nextgen/appliance/template_listing/{deviceName}
    Parameters: deviceName, tenant

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/nextgen/appliance/template_listing/{deviceName}"
    url = url.replace('{deviceName}', deviceName)

    # Add query parameters
    query_params = {}

    if tenant:
        query_params['tenant'] = tenant

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),
            params=query_params
        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_template_workflow(templateworkflowName: str) -> Dict[str, Any]:
    """
    Get Template Workflow

    Method: GET
    URL: /vnms/alltypes/workflow/templates/template/{templateworkflowName}
    Parameters: templateworkflowName

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/alltypes/workflow/templates/template/{templateworkflowName}"
    url = url.replace('{templateworkflowName}', templateworkflowName)

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),

        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_appliance_locations() -> Dict[str, Any]:
    """
    Get Appliance Locations

    Method: GET
    URL: /vnms/dashboard/appliance/location
    Parameters: None

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/dashboard/appliance/location"

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),

        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_routing_instance_information(applianceName: str) -> Dict[str, Any]:
    """
    Get Routing Instance Information

    Method: GET
    URL: /vnms/appliance/{applianceName}/routing-instances
    Parameters: applianceName

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/appliance/{applianceName}/routing-instances"
    url = url.replace('{applianceName}', applianceName)

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),

        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_all_appliances_by_type_and_tags(offset: str, limit: str, type: str, tags: str) -> Dict[str, Any]:
    """
    Get All Appliances By Type and Tags

    Method: GET
    URL: /vnms/appliance/appliance
    Parameters: offset, limit, type, tags

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/appliance/appliance"

    # Add query parameters
    query_params = {}

    if offset:
        query_params['offset'] = offset

    if limit:
        query_params['limit'] = limit

    if type:
        query_params['type'] = type

    if tags:
        query_params['tags'] = tags

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),
            params=query_params
        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_all_appliances_lite(filterString: str, limit: str, offset: str, org: str, tags: str) -> Dict[str, Any]:
    """
    Get All Appliances Lite

    Method: GET
    URL: /vnms/appliance/appliance/lite
    Parameters: filterString, limit, offset, org, tags

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/appliance/appliance/lite"

    # Add query parameters
    query_params = {}

    if filterString:
        query_params['filterString'] = filterString

    if limit:
        query_params['limit'] = limit

    if offset:
        query_params['offset'] = offset

    if org:
        query_params['org'] = org

    if tags:
        query_params['tags'] = tags

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),
            params=query_params
        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_all_appliances_liteview(exportToCSV: str, filterString: str, limit: str, offset: str, org: str, tags: str) -> Dict[str, Any]:
    """
    Get All Appliances LiteView

    Method: GET
    URL: /vnms/appliance/appliance/liteView
    Parameters: exportToCSV, filterString, limit, offset, org, tags

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/appliance/appliance/liteView"

    # Add query parameters
    query_params = {}

    if exportToCSV:
        query_params['exportToCSV'] = exportToCSV

    if filterString:
        query_params['filterString'] = filterString

    if limit:
        query_params['limit'] = limit

    if offset:
        query_params['offset'] = offset

    if org:
        query_params['org'] = org

    if tags:
        query_params['tags'] = tags

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),
            params=query_params
        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def search_appliance_by_name(limit: str, name: str, offset: str) -> Dict[str, Any]:
    """
    Search Appliance By Name

    Method: GET
    URL: /vnms/appliance/applianceByName
    Parameters: limit, name, offset

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/appliance/applianceByName"

    # Add query parameters
    query_params = {}

    if limit:
        query_params['limit'] = limit

    if name:
        query_params['name'] = name

    if offset:
        query_params['offset'] = offset

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),
            params=query_params
        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def export_appliance_configuration(applianceName: str, export_as_plain_text: str) -> Dict[str, Any]:
    """
    Export Appliance Configuration

    Method: GET
    URL: /vnms/appliance/export
    Parameters: applianceName, export-as-plain-text

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/appliance/export"

    # Add query parameters
    query_params = {}

    if applianceName:
        query_params['applianceName'] = applianceName

    if export_as_plain_text:
        query_params['export-as-plain-text'] = export_as_plain-text

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),
            params=query_params
        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_appliances_summary(filterByName: str) -> Dict[str, Any]:
    """
    Get Appliances Summary

    Method: GET
    URL: /vnms/appliance/summary
    Parameters: filterByName

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/appliance/summary"

    # Add query parameters
    query_params = {}

    if filterByName:
        query_params['filterByName'] = filterByName

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),
            params=query_params
        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_audit_logs(limit: str, offset: str, searchKey: str) -> Dict[str, Any]:
    """
    Get Audit Logs

    Method: GET
    URL: /vnms/audit/logs
    Parameters: limit, offset, searchKey

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/audit/logs"

    # Add query parameters
    query_params = {}

    if limit:
        query_params['limit'] = limit

    if offset:
        query_params['offset'] = offset

    if searchKey:
        query_params['searchKey'] = searchKey

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),
            params=query_params
        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def device_workflow_fetch_all(filters: str, limit: str, offset: str, orgname: str) -> Dict[str, Any]:
    """
    Device WorkFlow Fetch All

    Method: GET
    URL: /vnms/sdwan/workflow/devices
    Parameters: filters, limit, offset, orgname

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/sdwan/workflow/devices"

    # Add query parameters
    query_params = {}

    if filters:
        query_params['filters'] = filters

    if limit:
        query_params['limit'] = limit

    if offset:
        query_params['offset'] = offset

    if orgname:
        query_params['orgname'] = orgname

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),
            params=query_params
        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_specific_device_workflow(deviceName: str) -> Dict[str, Any]:
    """
    Get Specific Device WorkFlow

    Method: GET
    URL: /vnms/sdwan/workflow/devices/device/{deviceName}
    Parameters: deviceName

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/sdwan/workflow/devices/device/{deviceName}"
    url = url.replace('{deviceName}', deviceName)

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),

        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_template_bind_data_header_and_count(templateName: str, organization: str) -> Dict[str, Any]:
    """
    Get Template Bind Data Header and Count

    Method: GET
    URL: /vnms/sdwan/workflow/binddata/devices/header/template/{templateName}
    Parameters: templateName, organization

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/sdwan/workflow/binddata/devices/header/template/{templateName}"
    url = url.replace('{templateName}', templateName)

    # Add query parameters
    query_params = {}

    if organization:
        query_params['organization'] = organization

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),
            params=query_params
        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def template_fetch_all(limit: str, offset: str, orgname: str, searchKeyword: str) -> Dict[str, Any]:
    """
    Template Fetch All

    Method: GET
    URL: /vnms/sdwan/workflow/templates
    Parameters: limit, offset, orgname, searchKeyword

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/sdwan/workflow/templates"

    # Add query parameters
    query_params = {}

    if limit:
        query_params['limit'] = limit

    if offset:
        query_params['offset'] = offset

    if orgname:
        query_params['orgname'] = orgname

    if searchKeyword:
        query_params['searchKeyword'] = searchKeyword

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),
            params=query_params
        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_specific_template_workflow(templateworkflowName: str) -> Dict[str, Any]:
    """
    Get Specific Template WorkFlow

    Method: GET
    URL: /vnms/sdwan/workflow/templates/template/{templateworkflowName}
    Parameters: templateworkflowName

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/sdwan/workflow/templates/template/{templateworkflowName}"
    url = url.replace('{templateworkflowName}', templateworkflowName)

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),

        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def device_group_fetch_all(filters: str, limit: str, offset: str, organization: str) -> Dict[str, Any]:
    """
    Device Group Fetch All

    Method: GET
    URL: /nextgen/deviceGroup
    Parameters: filters, limit, offset, organization

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/nextgen/deviceGroup"

    # Add query parameters
    query_params = {}

    if filters:
        query_params['filters'] = filters

    if limit:
        query_params['limit'] = limit

    if offset:
        query_params['offset'] = offset

    if organization:
        query_params['organization'] = organization

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),
            params=query_params
        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_specific_device_group(deviceGroupName: str) -> Dict[str, Any]:
    """
    Get Specific Device Group

    Method: GET
    URL: /nextgen/deviceGroup/{deviceGroupName}
    Parameters: deviceGroupName

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/nextgen/deviceGroup/{deviceGroupName}"
    url = url.replace('{deviceGroupName}', deviceGroupName)

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),

        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_all_model_numbers() -> Dict[str, Any]:
    """
    Get All Model Numbers

    Method: GET
    URL: /nextgen/deviceGroup/modelNumbers
    Parameters: None

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/nextgen/deviceGroup/modelNumbers"

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),

        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def show_templates_associated_to_device(deviceName: str) -> Dict[str, Any]:
    """
    Show Templates Associated to Device

    Method: GET
    URL: /nextgen/device/{deviceName}
    Parameters: deviceName

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/nextgen/device/{deviceName}"
    url = url.replace('{deviceName}', deviceName)

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),

        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_all_assets(filters: str, limit: str, offset: str, organization: str) -> Dict[str, Any]:
    """
    Get All Assets

    Method: GET
    URL: /vnms/assets/asset
    Parameters: filters, limit, offset, organization

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/assets/asset"

    # Add query parameters
    query_params = {}

    if filters:
        query_params['filters'] = filters

    if limit:
        query_params['limit'] = limit

    if offset:
        query_params['offset'] = offset

    if organization:
        query_params['organization'] = organization

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),
            params=query_params
        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_next_page_data(filters: str, offset: str, queryId: str) -> Dict[str, Any]:
    """
    Get Next Page Data

    Method: GET
    URL: /vnms/dashboard/appliance/next_page_data
    Parameters: filters, offset, queryId

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/dashboard/appliance/next_page_data"

    # Add query parameters
    query_params = {}

    if filters:
        query_params['filters'] = filters

    if offset:
        query_params['offset'] = offset

    if queryId:
        query_params['queryId'] = queryId

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),
            params=query_params
        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_appliance_details_by_uuid(Uuid: str) -> Dict[str, Any]:
    """
    Get Appliance Details by UUID

    Method: GET
    URL: /vnms/dashboard/appliance/{Uuid}
    Parameters: Uuid

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/dashboard/appliance/{Uuid}"
    url = url.replace('{Uuid}', Uuid)

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),

        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_appliance_hardware(Uuid: str) -> Dict[str, Any]:
    """
    Get Appliance Hardware

    Method: GET
    URL: /vnms/dashboard/appliance/{Uuid}/hardware
    Parameters: Uuid

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/dashboard/appliance/{Uuid}/hardware"
    url = url.replace('{Uuid}', Uuid)

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),

        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_bw_measurement(applianceName: str, command: str, uuid: str) -> Dict[str, Any]:
    """
    Get BW Measurement

    Method: GET
    URL: /vnms/dashboard/appliance/{applianceName}/bandwidthservers
    Parameters: applianceName, command, uuid

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/dashboard/appliance/{applianceName}/bandwidthservers"
    url = url.replace('{applianceName}', applianceName)

    # Add query parameters
    query_params = {}

    if command:
        query_params['command'] = command

    if uuid:
        query_params['uuid'] = uuid

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),
            params=query_params
        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_appliance_capabilities(applianceName: str) -> Dict[str, Any]:
    """
    Get Appliance Capabilities

    Method: GET
    URL: /vnms/dashboard/appliance/{applianceName}/capabilities
    Parameters: applianceName

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/dashboard/appliance/{applianceName}/capabilities"
    url = url.replace('{applianceName}', applianceName)

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),

        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}
@mcp.tool()
async def get_appliance_eip_data_by_mac(
    appliance_name: str, 
    org_name: str, 
    mac_address: str, 
    uuid: str, 
    detail_level: str = "brief"
) -> Dict[str, Any]:
    """
    Get EIP data filtered by MAC address from appliance live status
    
    Args:
        appliance_name: Name of the appliance (e.g., "SSE-BLR-LAB-GW1")
        org_name: Organization name (e.g., "DEMO-ORG-10")
        mac_address: MAC address from EIP cache (e.g., "52:54:00:a4:35:06")
        uuid: Appliance UUID for live status
        detail_level: Level of detail - only "brief" is supported
    
    Returns:
        Dictionary containing EIP data for the specified MAC address
        
    Example:
        get_appliance_eip_data_by_mac("SSE-BLR-LAB-GW1", "DEMO-ORG-10", "52:54:00:a4:35:06", "uuid-here")
    """
    import urllib.parse
    
    # URL encode the MAC address (: becomes %3A)
    encoded_mac = urllib.parse.quote(mac_address, safe='')
    
    # Construct the command with required leading %2F
    # CRITICAL: Must include leading %2F for the command to work
    command = f"%2Forgs%2Forg-services%2F{org_name}%2Feip%2Fdata%2Ffilter%2F{encoded_mac}%2F{detail_level}"
    
    # Call the existing live status function
    return await get_appliance_live_status(
        applianceName=appliance_name,
        command=command,
        uuid=uuid
    )

@mcp.tool()
async def extract_mac_addresses_from_eip_cache(eip_cache_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract MAC addresses from EIP cache results
    
    Args:
        eip_cache_result: Result from get_appliance_eip_details()
    
    Returns:
        Dictionary with list of MAC addresses and metadata
    """
    mac_addresses = []
    
    if 'collection' in eip_cache_result and 'eip' in eip_cache_result['collection']:
        for eip_entry in eip_cache_result['collection']['eip']:
            if 'mac-address' in eip_entry:
                mac_addresses.append(eip_entry['mac-address'])
    
    return {
        "mac_addresses": mac_addresses,
        "total_count": len(mac_addresses),
        "source_metadata": eip_cache_result.get('_metadata', {}),
        "success": True
    }

@mcp.tool()
async def get_eip_system_analysis(
    appliance_name: str, 
    org_name: str, 
    uuid: str,
    max_endpoints: int = 50
) -> Dict[str, Any]:
    """
    Complete workflow: Get EIP cache and detailed data for all endpoints. Helps to search system information, software status, OS versions, Realtime Posture etc.
    
    Args:
        appliance_name: Name of the appliance
        org_name: Organization name
        uuid: Appliance UUID
        max_endpoints: Maximum number of endpoints to process (default: 50)
    
    Returns:
        Dictionary with cache results and detailed data for each MAC
    """
    results = {
        'cache_summary': None,
        'detailed_data': {},
        'mac_addresses': [],
        'success_count': 0,
        'error_count': 0,
        'errors': [],
        'processing_summary': {}
    }
    
    try:
        # Step 1: Get EIP cache
        print(f"Getting EIP cache for {org_name} on {appliance_name}...")
        cache_result = await get_appliance_eip_details(
            appliance_name=appliance_name,
            org_name=org_name
        )
        results['cache_summary'] = cache_result
        
        # Step 2: Extract MAC addresses
        mac_extraction = await extract_mac_addresses_from_eip_cache(cache_result)
        mac_addresses = mac_extraction['mac_addresses']
        results['mac_addresses'] = mac_addresses
        
        total_macs = len(mac_addresses)
        results['processing_summary']['total_endpoints_found'] = total_macs
        
        if total_macs > max_endpoints:
            mac_addresses = mac_addresses[:max_endpoints]
            results['processing_summary']['limited_to'] = max_endpoints
            results['processing_summary']['skipped_endpoints'] = total_macs - max_endpoints
        
        print(f"Processing {len(mac_addresses)} MAC addresses out of {total_macs} found")
        
        # Step 3: Get detailed data for each MAC
        for i, mac in enumerate(mac_addresses, 1):
            try:
                print(f"Processing MAC {i}/{len(mac_addresses)}: {mac}")
                detailed_data = await get_appliance_eip_data_by_mac(
                    appliance_name=appliance_name,
                    org_name=org_name,
                    mac_address=mac,
                    uuid=uuid,
                    detail_level="brief"
                )
                results['detailed_data'][mac] = detailed_data
                results['success_count'] += 1
                print(f"✅ Success for MAC: {mac}")
                
            except Exception as e:
                error_msg = f"Error for MAC {mac}: {str(e)}"
                print(f"❌ {error_msg}")
                results['detailed_data'][mac] = {'error': str(e)}
                results['error_count'] += 1
                results['errors'].append(error_msg)
        
        results['processing_summary']['success_rate'] = f"{results['success_count']}/{len(mac_addresses)}"
        results['success'] = True
        
        return results
        
    except Exception as e:
        error_msg = f"Error in complete EIP analysis: {str(e)}"
        print(f"❌ {error_msg}")
        results['error'] = error_msg
        results['success'] = False
        return results

@mcp.tool()
async def get_appliance_live_status(
    applianceName: str, 
    command: str = "", 
    decode: str = "", 
    fetch: str = "", 
    filters: str = "", 
    uuid: str = "",
    # NEW PARAMETERS - Add these to your existing function
    command_ref: str = "",
    org_name: str = ""
) -> Dict[str, Any]:
    """
    Get Appliance Live Status with short form command references
    
    Original Parameters:
        applianceName: Name of the appliance
        command: Direct command string (if provided, overrides command_ref)
        decode: Decode parameter
        fetch: Fetch parameter  
        filters: Filters parameter
        uuid: UUID of the appliance
        
    NEW Short Form Parameters:
        command_ref: Short form command reference:
            # Live Users (VERIFIED):
            - "live_users" or "live_users_detail" : Live users detailed view
            - "live_users_brief" : Live users brief view
            
            
        org_name: Organization name (required for org-specific commands)
    
    Usage Examples:
        # Method 1: Short form (NEW)
        get_appliance_live_status(applianceName="SSE-BLR-LAB-GW1", uuid="uuid-here", 
                                 command_ref="live_users_detail", org_name="DEMO-ORG-10")
        
        # Method 2: Direct command (EXISTING - still works)
        get_appliance_live_status(applianceName="SSE-BLR-LAB-GW1", uuid="uuid-here",
                                 command="orgs%2Forg-services%2FDEMO-ORG-10%2F...")
    """
    
    # NEW LOGIC - Determine which command to use
    final_command = ""
    command_source = ""
    
    if command:
        # Direct command provided - use as is (EXISTING BEHAVIOR)
        final_command = command
        command_source = "direct_command"
    elif command_ref:
        # Short form reference provided - resolve it (NEW BEHAVIOR)
        try:
            final_command = resolve_command_reference(command_ref, org_name)
            command_source = f"command_ref:{command_ref}"
        except ValueError as e:
            return {
                "error": str(e),
                "success": False,
                "available_command_refs": list(LIVE_COMMAND_REFERENCES.keys()),
                "org_required_commands": list(ORG_REQUIRED_COMMANDS)
            }
    else:
        return {
            "error": "Either 'command' or 'command_ref' must be provided",
            "success": False,
            "available_command_refs": list(LIVE_COMMAND_REFERENCES.keys()),
            "usage": {
                "short_form": "Use 'command_ref' with optional 'org_name'",
                "direct": "Use 'command' parameter directly"
            }
        }
    
    url = f"{director.url}/vnms/dashboard/appliance/{applianceName}/live"
    url = url.replace('{applianceName}', applianceName)
    
    # Add query parameters
    query_params = {}
    if final_command:  # CHANGED: from 'command' to 'final_command'
        query_params['command'] = final_command
    if decode:
        query_params['decode'] = decode
    if fetch:
        query_params['fetch'] = fetch
    if filters:
        query_params['filters'] = filters
    if uuid:
        query_params['uuid'] = uuid
    
    # Make the request (EXISTING CODE - NO CHANGES)
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
                                    headers=director.get_header(),
                                    params=query_params)
    
    # Attempt to return JSON, fall back to text if not valid JSON (EXISTING CODE)
    try:
        result = response.json()
        # ADD METADATA (OPTIONAL - you can remove this if you don't want it)
        result["_metadata"] = {
            "command_source": command_source,
            "command_ref_used": command_ref if command_ref else "none",
            "org_name": org_name if org_name else "not_applicable",
            "final_command": final_command,
            "appliance_name": applianceName
        }
        return result
    except ValueError:
        return {"text": response.text}

# ============================================================================
# ADD THESE OPTIONAL CONVENIENCE FUNCTIONS AT THE END OF YOUR FILE (before if __name__ == "__main__":)
# ============================================================================

@mcp.tool()
async def get_live_users_by_org(applianceName: str, org_name: str, uuid: str, detail_level: str = "detail") -> Dict[str, Any]:
    """
    Convenience function to get live users for a specific organization
    
    Parameters:
        applianceName: Name of the appliance
        org_name: Organization name (e.g., "DEMO-ORG-10")
        uuid: UUID of the appliance
        detail_level: "detail" or "brief" (default: "detail")
    """
    command_ref = f"live_users_{detail_level}" if detail_level in ["brief", "detail"] else "live_users"
    
    return await get_appliance_live_status(
        applianceName=applianceName,
        uuid=uuid,
        command_ref=command_ref,
        org_name=org_name
    )

@mcp.tool()
async def get_available_command_refs() -> Dict[str, Any]:
    """
    Get all available command references and their requirements
    """
    return {
        "all_commands": list(LIVE_COMMAND_REFERENCES.keys()),
        "org_required_commands": list(ORG_REQUIRED_COMMANDS),
        "verified_working": ["live_users_detail", "live_users_brief"],
        "examples": {
            "live_users": "command_ref='live_users', org_name='DEMO-ORG-10'",
            "interfaces": "command_ref='interfaces' (no org needed)",
            "sessions_brief": "command_ref='sessions_brief', org_name='DEMO-ORG-10'"
        },
        "usage": {
            "short_form": "get_appliance_live_status(applianceName='SSE-BLR-LAB-GW1', uuid='uuid', command_ref='live_users', org_name='DEMO-ORG-10')",
            "direct_command": "get_appliance_live_status(applianceName='SSE-BLR-LAB-GW1', uuid='uuid', command='orgs%2Forg-services%2F...')"
        }
    }


@mcp.tool()
async def get_appliance_sync_status(applianceUUID: str) -> Dict[str, Any]:
    """
    Get Appliance Sync Status

    Method: GET
    URL: /vnms/dashboard/appliance/{applianceUUID}/syncStatus
    Parameters: applianceUUID

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/dashboard/appliance/{applianceUUID}/syncStatus"
    url = url.replace('{applianceUUID}', applianceUUID)

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),

        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_appliance_services(applianceName: str) -> Dict[str, Any]:
    """
    Get Appliance Services

    Method: GET
    URL: /vnms/dashboard/applianceServices/{applianceName}
    Parameters: applianceName

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/dashboard/applianceServices/{applianceName}"
    url = url.replace('{applianceName}', applianceName)

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),

        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_appliance_status(applianceUUID: str) -> Dict[str, Any]:
    """
    Get Appliance Status

    Method: GET
    URL: /vnms/dashboard/applianceStatus/{applianceUUID}
    Parameters: applianceUUID

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/dashboard/applianceStatus/{applianceUUID}"
    url = url.replace('{applianceUUID}', applianceUUID)

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),

        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_appliance_status_brief(applianceUUID: str) -> Dict[str, Any]:
    """
    Get Appliance Status Brief

    Method: GET
    URL: /vnms/dashboard/applianceStatus/{applianceUUID}/brief
    Parameters: applianceUUID

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/dashboard/applianceStatus/{applianceUUID}/brief"
    url = url.replace('{applianceUUID}', applianceUUID)

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),

        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_all_appliance_names() -> Dict[str, Any]:
    """
    Get All Appliance Names

    Method: GET
    URL: /vnms/cloud/systems/getAllApplianceNames
    Parameters: None

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/cloud/systems/getAllApplianceNames"

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),

        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_all_appliances_basic_details(limit: str, offset: str) -> Dict[str, Any]:
    """
    Get All Appliances Basic Details

    Method: GET
    URL: /vnms/cloud/systems/getAllAppliancesBasicDetails
    Parameters: limit, offset

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/cloud/systems/getAllAppliancesBasicDetails"

    # Add query parameters
    query_params = {}

    if limit:
        query_params['limit'] = limit

    if offset:
        query_params['offset'] = offset

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),
            params=query_params
        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_appliance_violations(applianceName: str) -> Dict[str, Any]:
    """
    Get Appliance Violations

    Method: GET
    URL: /vnms/dashboard/applianceviolations/{applianceName}
    Parameters: applianceName

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/dashboard/applianceviolations/{applianceName}"
    url = url.replace('{applianceName}', applianceName)

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),

        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_enable_monitoring() -> Dict[str, Any]:
    """
    Get Enable Monitoring

    Method: GET
    URL: /vnms/dashboard/enableMonitoring
    Parameters: None

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/dashboard/enableMonitoring"

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),

        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_device_status_pulling_enabled(deviceName: str) -> Dict[str, Any]:
    """
    Get Device Status Pulling Enabled

    Method: GET
    URL: /vnms/dashboard/getMonitorPullEnabled/{deviceName}
    Parameters: deviceName

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/dashboard/getMonitorPullEnabled/{deviceName}"
    url = url.replace('{deviceName}', deviceName)

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),

        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_health_ike(deviceName: str) -> Dict[str, Any]:
    """
    Get Health IKE

    Method: GET
    URL: /vnms/dashboard/health/ike
    Parameters: deviceName

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/dashboard/health/ike"

    # Add query parameters
    query_params = {}

    if deviceName:
        query_params['deviceName'] = deviceName

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),
            params=query_params
        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_health_interface(deviceName: str) -> Dict[str, Any]:
    """
    Get Health Interface

    Method: GET
    URL: /vnms/dashboard/health/interface
    Parameters: deviceName

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/dashboard/health/interface"

    # Add query parameters
    query_params = {}

    if deviceName:
        query_params['deviceName'] = deviceName

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),
            params=query_params
        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_health_path(deviceName: str) -> Dict[str, Any]:
    """
    Get Health Path

    Method: GET
    URL: /vnms/dashboard/health/path
    Parameters: deviceName

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/dashboard/health/path"

    # Add query parameters
    query_params = {}

    if deviceName:
        query_params['deviceName'] = deviceName

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),
            params=query_params
        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_devices_in_lte() -> Dict[str, Any]:
    """
    Get Devices in LTE

    Method: GET
    URL: /vnms/dashboard/lte/list
    Parameters: None

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/dashboard/lte/list"

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),

        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_nav_tree_node(appUUID: str, forceRefresh: str, skipCpeNodes: str) -> Dict[str, Any]:
    """
    Get Nav Tree Node

    Method: GET
    URL: /vnms/dashboard/navTree
    Parameters: appUUID, forceRefresh, skipCpeNodes

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/dashboard/navTree"

    # Add query parameters
    query_params = {}

    if appUUID:
        query_params['appUUID'] = appUUID

    if forceRefresh:
        query_params['forceRefresh'] = forceRefresh

    if skipCpeNodes:
        query_params['skipCpeNodes'] = skipCpeNodes

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),
            params=query_params
        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_head_end_status() -> Dict[str, Any]:
    """
    Get Head-End Status

    Method: GET
    URL: /vnms/dashboard/status/headEnds
    Parameters: None

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/dashboard/status/headEnds"

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),

        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_vd_status() -> Dict[str, Any]:
    """
    Get VD Status

    Method: GET
    URL: /vnms/dashboard/vdStatus
    Parameters: None

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/dashboard/vdStatus"

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),

        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_vd_ha_details() -> Dict[str, Any]:
    """
    Get VD HA Details

    Method: GET
    URL: /vnms/dashboard/vdStatus/haDetails
    Parameters: None

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/dashboard/vdStatus/haDetails"

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),

        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_vd_package_info() -> Dict[str, Any]:
    """
    Get VD Package Info

    Method: GET
    URL: /vnms/dashboard/vdStatus/packageInfo
    Parameters: None

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/dashboard/vdStatus/packageInfo"

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),

        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_sys_details() -> Dict[str, Any]:
    """
    Get Sys Details

    Method: GET
    URL: /vnms/dashboard/vdStatus/sysDetails
    Parameters: None

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/dashboard/vdStatus/sysDetails"

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),

        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_sys_uptime() -> Dict[str, Any]:
    """
    Get Sys Uptime

    Method: GET
    URL: /vnms/dashboard/vdStatus/sysUptime
    Parameters: None

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/dashboard/vdStatus/sysUptime"

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),

        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def filter_paginate_alarm(device_name: str, filtertype: str, force_refresh: str, include_children: str, is_cleared: str, is_deep: str, last_alarm_text: str, last_change_after: str, last_change_before: str, last_perceived_severity: str, last_status_change: str, limit: str, offset: str, org: str, show_system_alarm: str, sort_column: str, sort_order: str, type: str) -> Dict[str, Any]:
    """
    Filter Paginate Alarm

    Method: GET
    URL: /vnms/fault/alarms/page
    Parameters: device_name, filtertype, force_refresh, include_children, is_cleared, is_deep, last_alarm_text, last_change_after, last_change_before, last_perceived_severity, last_status_change, limit, offset, org, show_system_alarm, sort_column, sort_order, type

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/fault/alarms/page"

    # Add query parameters
    query_params = {}

    if device_name:
        query_params['device_name'] = device_name

    if filtertype:
        query_params['filtertype'] = filtertype

    if force_refresh:
        query_params['force_refresh'] = force_refresh

    if include_children:
        query_params['include_children'] = include_children

    if is_cleared:
        query_params['is_cleared'] = is_cleared

    if is_deep:
        query_params['is_deep'] = is_deep

    if last_alarm_text:
        query_params['last_alarm_text'] = last_alarm_text

    if last_change_after:
        query_params['last_change_after'] = last_change_after

    if last_change_before:
        query_params['last_change_before'] = last_change_before

    if last_perceived_severity:
        query_params['last_perceived_severity'] = last_perceived_severity

    if last_status_change:
        query_params['last_status_change'] = last_status_change

    if limit:
        query_params['limit'] = limit

    if offset:
        query_params['offset'] = offset

    if org:
        query_params['org'] = org

    if show_system_alarm:
        query_params['show_system_alarm'] = show_system_alarm

    if sort_column:
        query_params['sort_column'] = sort_column

    if sort_order:
        query_params['sort_order'] = sort_order

    if type:
        query_params['type'] = type

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),
            params=query_params
        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_alarm_handling(device_name: str, managed_object: str, org: str, type: str, specific_problem: str) -> Dict[str, Any]:
    """
    Get Alarm Handling

    Method: GET
    URL: /vnms/fault/alarm/handling
    Parameters: device_name, managed_object, org, type, specific_problem

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/fault/alarm/handling"

    # Add query parameters
    query_params = {}

    if device_name:
        query_params['device_name'] = device_name

    if managed_object:
        query_params['managed_object'] = managed_object

    if org:
        query_params['org'] = org

    if type:
        query_params['type'] = type

    if specific_problem:
        query_params['specific_problem'] = specific_problem

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),
            params=query_params
        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_alarm_summary_per_org(org: str, include_children: str, include_system: str) -> Dict[str, Any]:
    """
    Get Alarm Summary Per Org

    Method: GET
    URL: /vnms/fault/alarms/summary/{org}
    Parameters: org, include_children, include_system

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/fault/alarms/summary/{org}"
    url = url.replace('{org}', org)

    # Add query parameters
    query_params = {}

    if include_children:
        query_params['include_children'] = include_children

    if include_system:
        query_params['include_system'] = include_system

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),
            params=query_params
        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_alarm_summary() -> Dict[str, Any]:
    """
    Get Alarm Summary

    Method: GET
    URL: /vnms/fault/alarms/summary
    Parameters: None

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/fault/alarms/summary"

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),

        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_alarm_types() -> Dict[str, Any]:
    """
    Get Alarm Types

    Method: GET
    URL: /vnms/fault/types
    Parameters: None

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/fault/types"

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),

        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_all_filtered_alarms(device_name: str, filtertype: str, is_cleared: str, is_deep: str, last_alarm_text: str, last_change_after: str, last_change_before: str, last_perceived_severity: str, last_status_change: str, org: str, type: str) -> Dict[str, Any]:
    """
    Get All Filtered Alarms

    Method: GET
    URL: /vnms/fault/alarms
    Parameters: device_name, filtertype, is_cleared, is_deep, last_alarm_text, last_change_after, last_change_before, last_perceived_severity, last_status_change, org, type

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/fault/alarms"

    # Add query parameters
    query_params = {}

    if device_name:
        query_params['device_name'] = device_name

    if filtertype:
        query_params['filtertype'] = filtertype

    if is_cleared:
        query_params['is_cleared'] = is_cleared

    if is_deep:
        query_params['is_deep'] = is_deep

    if last_alarm_text:
        query_params['last_alarm_text'] = last_alarm_text

    if last_change_after:
        query_params['last_change_after'] = last_change_after

    if last_change_before:
        query_params['last_change_before'] = last_change_before

    if last_perceived_severity:
        query_params['last_perceived_severity'] = last_perceived_severity

    if last_status_change:
        query_params['last_status_change'] = last_status_change

    if org:
        query_params['org'] = org

    if type:
        query_params['type'] = type

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),
            params=query_params
        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_analytics_alarm_summary() -> Dict[str, Any]:
    """
    Get Analytics Alarm Summary

    Method: GET
    URL: /vnms/fault/analytics/alarms/summary
    Parameters: None

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/fault/analytics/alarms/summary"

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),

        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_analytics_alarms(search_string: str, severity: str) -> Dict[str, Any]:
    """
    Get Analytics Alarms

    Method: GET
    URL: /vnms/fault/analytics/alarms
    Parameters: search_string, severity

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/fault/analytics/alarms"

    # Add query parameters
    query_params = {}

    if search_string:
        query_params['search_string'] = search_string

    if severity:
        query_params['severity'] = severity

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),
            params=query_params
        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_appliance_alarm_model() -> Dict[str, Any]:
    """
    Get Appliance Alarm Model

    Method: GET
    URL: /vnms/fault/appliance/alarm_model
    Parameters: None

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/fault/appliance/alarm_model"

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),

        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_appliance_alarm_types() -> Dict[str, Any]:
    """
    Get Appliance Alarm Types

    Method: GET
    URL: /vnms/fault/appliance/types
    Parameters: None

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/fault/appliance/types"

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),

        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_device_alarm_summary(deviceName: str, org: str) -> Dict[str, Any]:
    """
    Get Device Alarm Summary

    Method: GET
    URL: /vnms/fault/alarms/summary/device/{deviceName}
    Parameters: deviceName, org

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/fault/alarms/summary/device/{deviceName}"
    url = url.replace('{deviceName}', deviceName)

    # Add query parameters
    query_params = {}

    if org:
        query_params['org'] = org

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),
            params=query_params
        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_director_alarm_summary() -> Dict[str, Any]:
    """
    Get Director Alarm Summary

    Method: GET
    URL: /vnms/fault/director/alarms/summary
    Parameters: None

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/fault/director/alarms/summary"

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),

        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_director_alarms(search_string: str, severity: str) -> Dict[str, Any]:
    """
    Get Director Alarms

    Method: GET
    URL: /vnms/fault/director/alarms
    Parameters: search_string, severity

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/fault/director/alarms"

    # Add query parameters
    query_params = {}

    if search_string:
        query_params['search_string'] = search_string

    if severity:
        query_params['severity'] = severity

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),
            params=query_params
        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_director_fail_over_alarms() -> Dict[str, Any]:
    """
    Get Director Fail Over Alarms

    Method: GET
    URL: /vnms/fault/director/fail-over-alarms
    Parameters: None

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/fault/director/fail-over-alarms"

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),

        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_director_ha_alarms() -> Dict[str, Any]:
    """
    Get Director HA Alarms

    Method: GET
    URL: /vnms/fault/director/ha-alarms
    Parameters: None

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/fault/director/ha-alarms"

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),

        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_imp_alarm_summary() -> Dict[str, Any]:
    """
    Get IMP Alarm Summary

    Method: GET
    URL: /vnms/fault/director/pop-up-summary
    Parameters: None

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/fault/director/pop-up-summary"

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),

        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_imp_alarms() -> Dict[str, Any]:
    """
    Get IMP Alarms

    Method: GET
    URL: /vnms/fault/director/pop-up
    Parameters: None

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/fault/director/pop-up"

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),

        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


@mcp.tool()
async def get_status_change(device_name: str, managed_object: str, org: str, type: str, specific_problem: str) -> Dict[str, Any]:
    """
    Get Status Change

    Method: GET
    URL: /vnms/fault/alarm/status
    Parameters: device_name, managed_object, org, type, specific_problem

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/fault/alarm/status"

    # Add query parameters
    query_params = {}

    if device_name:
        query_params['device_name'] = device_name

    if managed_object:
        query_params['managed_object'] = managed_object

    if org:
        query_params['org'] = org

    if type:
        query_params['type'] = type

    if specific_problem:
        query_params['specific_problem'] = specific_problem

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),
            params=query_params
        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}

@mcp.tool()
async def get_appliance_sessions_summary(applianceName: str, uuid: str, org: str) -> Dict[str, Any]:
    """
    Get Appliance Sessions Summary

    Method: GET
    URL: /vnms/dashboard/appliance/{applianceName}/live
    Parameters: applianceName, uuid, command (sessions summary for specific org)

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/dashboard/appliance/{applianceName}/live"
    url = url.replace('{applianceName}', applianceName)

    # Add query parameters
    query_params = {}
    
    if uuid:
        query_params['uuid'] = uuid
    
    # Construct the command for sessions summary
    if org:
        query_params['command'] = f"/orgs/org/{org}/sessions/summary"

    # Make the request
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, 
            headers=director.get_header(),
            params=query_params
        )

    # Attempt to return JSON, fall back to text if not valid JSON
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}

@mcp.tool()
async def get_appliance_session_extensive_details(
    appliance_name: str,
    org_name: str,
    offset: int = 1,
    limit: int = 25,
    fields: str = "access-policy,forward-fec-parity-pkt-tx,forward-multi-link-total-tx,application,destination-ip,destination-port,dropped-forward-byte-count,dropped-forward-pkt-count,dropped-reverse-byte-count,dropped-reverse-pkt-count,external-service-chaining,forward-byte-count,forward-egress-branch,forward-egress-ckt,forward-egress-interface,forward-egress-vrf,forward-fc,forward-ingress-ckt,forward-ingress-interface,forward-offload,forward-pkt-count,forward-plp,idle-for,idle-timeout,is-child,nat-destination-ip,nat-destination-port,nat-direction,nat-rule-name,nat-source-ip,nat-source-port,natted,parent-sess-id,pbf-enabled,protocol,reverse-byte-count,reverse-egress-ckt,reverse-egress-interface,reverse-egress-vrf,reverse-fc,reverse-ingress-branch,reverse-ingress-ckt,reverse-ingress-interface,reverse-offload,reverse-pkt-count,reverse-plp,rx-wan-ckt,sdwan,sess-id,session-age,session-provider-zone,source-ip,source-port,tx-branch,tx-wan-ckt,vsn-id,vsn-vid,reverse-fec-parity-pkt-rx,reverse-fec-pkt-lost,reverse-fec-pkt-recovered,reverse-fec-recovery-rate,reverse-multi-link-total-rx,reverse-released-pkt-count,forward-replicated-pkt-count,reverse-multi-link-total-tx,reverse-held-pkt-count,reverse-released-pkt-count,reverse-dup-dropped-pkt-count,reverse-replication-recovery-rate,reverse-fec-dup-parity-pkt-dropped,reverse-fec-pkt-held-count,forward-multi-link-total-rx,forward-fec-parity-pkt-rx,forward-fec-recovery-rate,device,pbf-wan-ackt-enc,reverse-egress-branch,forward-sdwan-rule-name,reverse-sdwan-rule-name,multi-link-mode,forward-fec-pkt-lost,forward-fec-pkt-recovered,forward-fec-pkt-held-count,forward-fec-pkt-released-count,forward-released-pkt-count,reverse-fec-parity-pkt-tx, nsh-peer-source-ip, nsh-peer-destination-ip, nsh-peer-source-port, nsh-peer-destination-port, nsh-peer-protocol, forward-sdwan-flow-key, reverse-sdwan-flow-key,forward-sdwan-te-nexthop-info,reverse-sdwan-te-nexthop-info"
) -> Dict[str, Any]:
    """
    Get detailed session extensive information from appliance using POST request
    
    Method: POST
    URL: /vnms/dashboard/appliance/{applianceName}/live_pageable
    
    Args:
        appliance_name: Name of the appliance (e.g., "SSE-BLR-LAB-GW1")
        org_name: Organization/tenant name (e.g., "ACME", "DEMO-ORG-01")
        offset: Starting record number (default: 1)
        limit: Number of records to return (default: 25)
        fields: Comma-separated list of fields to return
    
    Returns:
        JSON response from the API containing detailed session information
    """
    
    # Construct the URL using the same pattern as existing functions
    url = f"{director.url}/vnms/dashboard/appliance/{appliance_name}/live_pageable"
    
    # Construct the payload
    payload = {
        "command": f"orgs/org[name='{org_name}']/sessions/extensive",
        "fields": fields,
        "offset": offset,
        "limit": limit,
        "dataType": "PagedSessions"
    }
    
    try:
        # Make the POST request using the same pattern as existing functions
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.post(
                url,
                headers=director.get_header(),
                json=payload,
                timeout=30
            )
            
        # Attempt to return JSON, fall back to text if not valid JSON
        try:
            return response.json()
        except ValueError:
            return {"text": response.text, "status_code": response.status_code}
            
    except Exception as e:
        return {
            "error": f"Request failed: {str(e)}",
            "url": url,
            "payload": payload
        }

# EIP Command References
EIP_COMMAND_REFERENCES = {
    "eip-cache-brief": "orgs/org-services[name='{org_name}']/eip/cache/brief",
    "eip-cache-detail": "orgs/org-services[name='{org_name}']/eip/cache/detail",
    "eip-cache": "orgs/org-services[name='{org_name}']/eip/cache"
}

# EIP commands that require org_name
EIP_ORG_REQUIRED_COMMANDS = [
    "eip-cache-brief",
    "eip-cache-detail", 
    "eip-cache"
]

def resolve_eip_command_reference(command_ref: str, org_name: str = None) -> str:
    """
    Resolve a short form EIP command reference to the full command
    
    Args:
        command_ref: Short form reference (e.g., "eip-cache-brief")
        org_name: Organization name (required for org-specific commands)
    
    Returns:
        Full command string
        
    Raises:
        ValueError: If command reference is unknown or org_name is missing when required
    """
    if command_ref not in EIP_COMMAND_REFERENCES:
        available = list(EIP_COMMAND_REFERENCES.keys())
        raise ValueError(f"Unknown EIP command reference '{command_ref}'. Available: {available}")
    
    # Check if org name is required
    if command_ref in EIP_ORG_REQUIRED_COMMANDS and not org_name:
        raise ValueError(f"Organization name is required for EIP command '{command_ref}'")
    
    # Get the command template
    command_template = EIP_COMMAND_REFERENCES[command_ref]
    
    # Replace org name if needed
    if "{org_name}" in command_template:
        if not org_name:
            raise ValueError(f"Organization name is required for EIP command '{command_ref}'")
        command = command_template.replace("{org_name}", org_name)
    else:
        command = command_template
    
    return command

@mcp.tool()
async def get_appliance_eip_details(
    appliance_name: str,
    org_name: str,
    offset: int = 1,
    limit: int = 25,
    fields: str = "serial-number, ip-address, mac-address, eip-agent-profile, eip-object-count, eip-object-list, eip-profile-count, eip-profile-list, host-id, last-update-time, status, username",
    command_ref: str = "eip-cache-brief",
    command: str = None,
    auto_paginate: bool = False,
    max_records: int = 1000
) -> Dict[str, Any]:
    """
    Get EIP (Endpoint Information Protection) details from appliance
    
    Method: POST
    URL: /vnms/dashboard/appliance/{applianceName}/live_pageable
    
    Args:
        appliance_name: Name of the appliance (e.g., "SSE-BLR-LAB-GW1")
        org_name: Organization/tenant name (e.g., "DEMO-ORG-10")
        offset: Starting record number (default: 1)
        limit: Number of records per page (default: 25)
        fields: Comma-separated list of fields to return
        command_ref: EIP command reference (default: "eip-cache-brief")
        command: Direct command string (overrides command_ref if provided)
        auto_paginate: If True, automatically fetch all pages (default: False)
        max_records: Maximum number of records to fetch when auto_paginate=True (default: 1000)
    
    Returns:
        JSON response from the API containing EIP information
        When auto_paginate=True, returns all records combined with pagination metadata
    """
    
    # Determine which command to use
    if command:
        final_command = command
        command_source = "direct_command"
    elif command_ref:
        try:
            final_command = resolve_eip_command_reference(command_ref, org_name)
            command_source = f"command_ref:{command_ref}"
        except ValueError as e:
            return {
                "error": str(e),
                "available_eip_command_refs": list(EIP_COMMAND_REFERENCES.keys()),
                "org_required_commands": EIP_ORG_REQUIRED_COMMANDS
            }
    else:
        try:
            final_command = resolve_eip_command_reference("eip-cache-brief", org_name)
            command_source = "command_ref:eip-cache-brief"
            command_ref = "eip-cache-brief"
        except ValueError as e:
            return {"error": str(e)}
    
    url = f"{director.url}/vnms/dashboard/appliance/{appliance_name}/live_pageable"
    
    async def fetch_page(page_offset: int, page_limit: int) -> Dict[str, Any]:
        """Fetch a single page of data"""
        payload = {
            "command": final_command,
            "fields": fields,
            "dataType": "eip",
            "offset": page_offset,
            "limit": page_limit
        }
        
        try:
            async with httpx.AsyncClient(verify=False) as client:
                response = await client.post(
                    url,
                    headers=director.get_header(),
                    json=payload,
                    timeout=30
                )
            return response.json()
        except Exception as e:
            return {"error": f"Failed to fetch page at offset {page_offset}: {str(e)}"}
    
    if not auto_paginate:
        # Single page request (original behavior)
        result = await fetch_page(offset, limit)
        
        if "error" not in result and "_metadata" not in result:
            result["_metadata"] = {
                "command_source": command_source,
                "command_ref_used": command_ref,
                "org_name": org_name,
                "final_command": final_command,
                "appliance_name": appliance_name,
                "data_type": "eip",
                "pagination": {
                    "single_page": True,
                    "offset": offset,
                    "limit": limit
                }
            }
        
        return result
    
    else:
        # Auto-pagination: fetch all pages
        all_records = []
        current_offset = offset
        page_count = 0
        total_fetched = 0
        errors = []
        
        while total_fetched < max_records:
            # Calculate how many records to fetch in this page
            remaining_records = max_records - total_fetched
            current_limit = min(limit, remaining_records)
            
            # Fetch the page
            page_result = await fetch_page(current_offset, current_limit)
            
            if "error" in page_result:
                errors.append(f"Page {page_count + 1} (offset {current_offset}): {page_result['error']}")
                break
            
            # Extract records from the page
            page_records = []
            if "collection" in page_result:
                # Handle different collection types
                for collection_type, records in page_result["collection"].items():
                    if isinstance(records, list):
                        page_records.extend(records)
                    elif isinstance(records, dict):
                        page_records.append(records)
            
            # If no records returned, we've reached the end
            if not page_records:
                break
            
            all_records.extend(page_records)
            total_fetched += len(page_records)
            page_count += 1
            
            # If we got fewer records than requested, we've reached the end
            if len(page_records) < current_limit:
                break
            
            # Prepare for next page
            current_offset += current_limit
        
        # Construct the combined result
        result = {
            "collection": {
                "eip": all_records
            },
            "_metadata": {
                "command_source": command_source,
                "command_ref_used": command_ref,
                "org_name": org_name,
                "final_command": final_command,
                "appliance_name": appliance_name,
                "data_type": "eip",
                "pagination": {
                    "auto_paginated": True,
                    "total_records_fetched": total_fetched,
                    "total_pages_fetched": page_count,
                    "starting_offset": offset,
                    "records_per_page": limit,
                    "max_records_limit": max_records,
                    "reached_max_limit": total_fetched >= max_records,
                    "errors": errors if errors else None
                }
            }
        }
        
        if errors:
            result["_warnings"] = {
                "pagination_errors": errors,
                "partial_data": True
            }
        
        return result

@mcp.tool()
async def get_all_appliance_eip_details(
    appliance_name: str,
    org_name: str,
    fields: str = "serial-number, ip-address, mac-address, eip-agent-profile, eip-object-count, eip-profile-count, host-id, last-update-time, status, username",
    command_ref: str = "eip-cache-brief",
    max_records: int = 5000,
    batch_size: int = 100
) -> Dict[str, Any]:
    """
    Convenience function to get ALL EIP details with automatic pagination
    
    Args:
        appliance_name: Name of the appliance
        org_name: Organization/tenant name  
        fields: Comma-separated list of fields to return
        command_ref: EIP command reference
        max_records: Maximum number of records to fetch (default: 5000)
        batch_size: Number of records per API call (default: 100)
    
    Returns:
        All EIP records combined with pagination metadata
    """
    return await get_appliance_eip_details(
        appliance_name=appliance_name,
        org_name=org_name,
        offset=1,
        limit=batch_size,
        fields=fields,
        command_ref=command_ref,
        auto_paginate=True,
        max_records=max_records
    )
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(mcp.app, host="0.0.0.0", port=8000)