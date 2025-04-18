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
async def get_appliance_live_status(applianceName: str, command: str, decode: str, fetch: str, filters: str, uuid: str) -> Dict[str, Any]:
    """
    Get Appliance Live Status

    Method: GET
    URL: /vnms/dashboard/appliance/{applianceName}/live
    Parameters: applianceName, command, decode, fetch, filters, uuid

    Returns:
        JSON response from the API
    """
    # Construct the URL
    url = f"{director.url}/vnms/dashboard/appliance/{applianceName}/live"
    url = url.replace('{applianceName}', applianceName)

    # Add query parameters
    query_params = {}

    if command:
        query_params['command'] = command

    if decode:
        query_params['decode'] = decode

    if fetch:
        query_params['fetch'] = fetch

    if filters:
        query_params['filters'] = filters

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



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(mcp.app, host="0.0.0.0", port=8000)
