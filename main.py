import requests
from mcp.server.fastmcp import FastMCP
import time
import jwt
import json
import urllib3
import os
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
#director = {}

# Initialize the MCP server
mcp = FastMCP(name = "Versa API Server", instructions="This server is used for all Versa related apis",  dependencies=["requests","urllib3","pyjwt"])

# Disable SSL warnings if you're using verify=False



@mcp.resource("nextgen:///appliance/status?limit={limit}&offset={offset}")
def get_all_appliance_status(limit, offset) -> str:
    """
    Get All Appliance Status

    Method: GET
    URL: /nextgen/appliance/status
    Parameters: limit, offset
    """
    # Construct the URL
    url = f"{director.url}/nextgen/appliance/status"

    # Add query parameters
    query_params = {}

    if limit:
        query_params['limit'] = limit

    if offset:
        query_params['offset'] = offset

    # Append query parameters if any
    if query_params:
        url += '?' + '&'.join([f'{k}={v}' for k, v in query_params.items()])

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("nextgen:///appliance/status/{id}?byName={byName}")
def get_single_appliance_status(id, byName) -> str:
    """
    Get Single Appliance Status

    Method: GET
    URL: /nextgen/appliance/status/{id}
    Parameters: byName
    """
    # Construct the URL
    url = f"{director.url}/nextgen/appliance/status/{id}"
    url = url.replace('{id}', id)

    # Add query parameters
    query_params = {}

    if byName:
        query_params['byName'] = byName

    # Append query parameters if any
    if query_params:
        url += '?' + '&'.join([f'{k}={v}' for k, v in query_params.items()])

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("nextgen:///appliance/template_listing/{deviceName}?tenant={tenant}")
def get_device_template_listing(deviceName, tenant) -> str:
    """
    Get Device Template Listing

    Method: GET
    URL: /nextgen/appliance/template_listing/{deviceName}
    Parameters: deviceName, tenant
    """
    # Construct the URL
    url = f"{director.url}/nextgen/appliance/template_listing/{deviceName}"
    url = url.replace('{deviceName}', deviceName)

    # Add query parameters
    query_params = {}

    if tenant:
        query_params['tenant'] = tenant

    # Append query parameters if any
    if query_params:
        url += '?' + '&'.join([f'{k}={v}' for k, v in query_params.items()])

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///alltypes/workflow/templates/template/{templateworkflowName}")
def get_template_workflow(templateworkflowName) -> str:
    """
    Get Template Workflow

    Method: GET
    URL: /vnms/alltypes/workflow/templates/template/{templateworkflowName}
    Parameters: templateworkflowName
    """
    # Construct the URL
    url = f"{director.url}/vnms/alltypes/workflow/templates/template/{templateworkflowName}"
    url = url.replace('{templateworkflowName}', templateworkflowName)

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///dashboard/appliance/location")
def get_appliance_locations() -> str:
    """
    Get Appliance Locations

    Method: GET
    URL: /vnms/dashboard/appliance/location
    Parameters: None
    """
    # Construct the URL
    url = f"{director.url}/vnms/dashboard/appliance/location"

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///appliance/{applianceName}/routing-instances")
def get_routing_instance_information(applianceName) -> str:
    """
    Get Routing Instance Information

    Method: GET
    URL: /vnms/appliance/{applianceName}/routing-instances
    Parameters: applianceName
    """
    # Construct the URL
    url = f"{director.url}/vnms/appliance/{applianceName}/routing-instances"
    url = url.replace('{applianceName}', applianceName)

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///appliance/appliance?offset={offset}&limit={limit}&type={type}&tags={tags}")
def get_all_appliances_by_type_and_tags(offset, limit, type, tags) -> str:
    """
    Get All Appliances By Type and Tags

    Method: GET
    URL: /vnms/appliance/appliance
    Parameters: offset, limit, type, tags
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

    # Append query parameters if any
    if query_params:
        url += '?' + '&'.join([f'{k}={v}' for k, v in query_params.items()])

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///appliance/appliance/lite?filterString={filterString}&limit={limit}&offset={offset}&org={org}&tags={tags}")
def get_all_appliances_lite(filterString, limit, offset, org, tags) -> str:
    """
    Get All Appliances Lite

    Method: GET
    URL: /vnms/appliance/appliance/lite
    Parameters: filterString, limit, offset, org, tags
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

    # Append query parameters if any
    if query_params:
        url += '?' + '&'.join([f'{k}={v}' for k, v in query_params.items()])

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///appliance/appliance/liteView?exportToCSV={exportToCSV}&filterString={filterString}&limit={limit}&offset={offset}&org={org}&tags={tags}")
def get_all_appliances_liteview(exportToCSV, filterString, limit, offset, org, tags) -> str:
    """
    Get All Appliances LiteView

    Method: GET
    URL: /vnms/appliance/appliance/liteView
    Parameters: exportToCSV, filterString, limit, offset, org, tags
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

    # Append query parameters if any
    if query_params:
        url += '?' + '&'.join([f'{k}={v}' for k, v in query_params.items()])

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///appliance/applianceByName?limit={limit}&name={name}&offset={offset}")
def search_appliance_by_name(limit, name, offset) -> str:
    """
    Search Appliance By Name

    Method: GET
    URL: /vnms/appliance/applianceByName
    Parameters: limit, name, offset
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

    # Append query parameters if any
    if query_params:
        url += '?' + '&'.join([f'{k}={v}' for k, v in query_params.items()])

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///appliance/export?applianceName={applianceName}&export-as-plain-text={export_as_plain_text}")
def export_appliance_configuration(applianceName, export_as_plain_text) -> str:
    """
    Export Appliance Configuration

    Method: GET
    URL: /vnms/appliance/export
    Parameters: applianceName, export-as-plain-text
    """
    # Construct the URL
    url = f"{director.url}/vnms/appliance/export"

    # Add query parameters
    query_params = {}

    if applianceName:
        query_params['applianceName'] = applianceName

    if export_as_plain_text:
        query_params['export-as-plain-text'] = export_as_plain_text

    # Append query parameters if any
    if query_params:
        url += '?' + '&'.join([f'{k}={v}' for k, v in query_params.items()])

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///appliance/summary?filterByName={filterByName}")
def get_appliances_summary(filterByName) -> str:
    """
    Get Appliances Summary

    Method: GET
    URL: /vnms/appliance/summary
    Parameters: filterByName
    """
    # Construct the URL
    url = f"{director.url}/vnms/appliance/summary"

    # Add query parameters
    query_params = {}

    if filterByName:
        query_params['filterByName'] = filterByName

    # Append query parameters if any
    if query_params:
        url += '?' + '&'.join([f'{k}={v}' for k, v in query_params.items()])

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///audit/logs?limit={limit}&offset={offset}&searchKey={searchKey}")
def get_audit_logs(limit, offset, searchKey) -> str:
    """
    Get Audit Logs

    Method: GET
    URL: /vnms/audit/logs
    Parameters: limit, offset, searchKey
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

    # Append query parameters if any
    if query_params:
        url += '?' + '&'.join([f'{k}={v}' for k, v in query_params.items()])

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///sdwan/workflow/devices?filters={filters}&limit={limit}&offset={offset}&orgname={orgname}")
def device_workflow_fetch_all(filters, limit, offset, orgname) -> str:
    """
    Device WorkFlow Fetch All

    Method: GET
    URL: /vnms/sdwan/workflow/devices
    Parameters: filters, limit, offset, orgname
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

    # Append query parameters if any
    if query_params:
        url += '?' + '&'.join([f'{k}={v}' for k, v in query_params.items()])

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///sdwan/workflow/devices/device/{deviceName}")
def get_specific_device_workflow(deviceName) -> str:
    """
    Get Specific Device WorkFlow

    Method: GET
    URL: /vnms/sdwan/workflow/devices/device/{deviceName}
    Parameters: deviceName
    """
    # Construct the URL
    url = f"{director.url}/vnms/sdwan/workflow/devices/device/{deviceName}"
    url = url.replace('{deviceName}', deviceName)

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///sdwan/workflow/binddata/devices/header/template/{templateName}?organization={organization}")
def get_template_bind_data_header_and_count(templateName, organization) -> str:
    """
    Get Template Bind Data Header and Count

    Method: GET
    URL: /vnms/sdwan/workflow/binddata/devices/header/template/{templateName}
    Parameters: templateName, organization
    """
    # Construct the URL
    url = f"{director.url}/vnms/sdwan/workflow/binddata/devices/header/template/{templateName}"
    url = url.replace('{templateName}', templateName)

    # Add query parameters
    query_params = {}

    if organization:
        query_params['organization'] = organization

    # Append query parameters if any
    if query_params:
        url += '?' + '&'.join([f'{k}={v}' for k, v in query_params.items()])

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///sdwan/workflow/templates?limit={limit}&offset={offset}&orgname={orgname}&searchKeyword={searchKeyword}")
def template_fetch_all(limit, offset, orgname, searchKeyword) -> str:
    """
    Template Fetch All

    Method: GET
    URL: /vnms/sdwan/workflow/templates
    Parameters: limit, offset, orgname, searchKeyword
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

    # Append query parameters if any
    if query_params:
        url += '?' + '&'.join([f'{k}={v}' for k, v in query_params.items()])

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///sdwan/workflow/templates/template/{templateworkflowName}")
def get_specific_template_workflow(templateworkflowName) -> str:
    """
    Get Specific Template WorkFlow

    Method: GET
    URL: /vnms/sdwan/workflow/templates/template/{templateworkflowName}
    Parameters: templateworkflowName
    """
    # Construct the URL
    url = f"{director.url}/vnms/sdwan/workflow/templates/template/{templateworkflowName}"
    url = url.replace('{templateworkflowName}', templateworkflowName)

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("nextgen:///deviceGroup?filters={filters}&limit={limit}&offset={offset}&organization={organization}")
def device_group_fetch_all(filters, limit, offset, organization) -> str:
    """
    Device Group Fetch All

    Method: GET
    URL: /nextgen/deviceGroup
    Parameters: filters, limit, offset, organization
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

    # Append query parameters if any
    if query_params:
        url += '?' + '&'.join([f'{k}={v}' for k, v in query_params.items()])

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("nextgen:///deviceGroup/{deviceGroupName}")
def get_specific_device_group(deviceGroupName) -> str:
    """
    Get Specific Device Group

    Method: GET
    URL: /nextgen/deviceGroup/{deviceGroupName}
    Parameters: deviceGroupName
    """
    # Construct the URL
    url = f"{director.url}/nextgen/deviceGroup/{deviceGroupName}"
    url = url.replace('{deviceGroupName}', deviceGroupName)

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("nextgen:///deviceGroup/modelNumbers")
def get_all_model_numbers() -> str:
    """
    Get All Model Numbers

    Method: GET
    URL: /nextgen/deviceGroup/modelNumbers
    Parameters: None
    """
    # Construct the URL
    url = f"{director.url}/nextgen/deviceGroup/modelNumbers"

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("nextgen:///device/{deviceName}")
def show_templates_associated_to_device(deviceName) -> str:
    """
    Show Templates Associated to Device

    Method: GET
    URL: /nextgen/device/{deviceName}
    Parameters: deviceName
    """
    # Construct the URL
    url = f"{director.url}/nextgen/device/{deviceName}"
    url = url.replace('{deviceName}', deviceName)

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///assets/asset?filters={filters}&limit={limit}&offset={offset}&organization={organization}")
def get_all_assets(filters, limit, offset, organization) -> str:
    """
    Get All Assets

    Method: GET
    URL: /vnms/assets/asset
    Parameters: filters, limit, offset, organization
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

    # Append query parameters if any
    if query_params:
        url += '?' + '&'.join([f'{k}={v}' for k, v in query_params.items()])

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///dashboard/appliance/next_page_data?filters={filters}&offset={offset}&queryId={queryId}")
def get_next_page_data(filters, offset, queryId) -> str:
    """
    Get Next Page Data

    Method: GET
    URL: /vnms/dashboard/appliance/next_page_data
    Parameters: filters, offset, queryId
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

    # Append query parameters if any
    if query_params:
        url += '?' + '&'.join([f'{k}={v}' for k, v in query_params.items()])

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///dashboard/appliance/{Uuid}")
def get_appliance_details_by_uuid(Uuid) -> str:
    """
    Get Appliance Details by UUID

    Method: GET
    URL: /vnms/dashboard/appliance/{Uuid}
    Parameters: Uuid
    """
    # Construct the URL
    url = f"{director.url}/vnms/dashboard/appliance/{Uuid}"
    url = url.replace('{Uuid}', Uuid)

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///dashboard/appliance/{Uuid}/hardware")
def get_appliance_hardware(Uuid) -> str:
    """
    Get Appliance Hardware

    Method: GET
    URL: /vnms/dashboard/appliance/{Uuid}/hardware
    Parameters: Uuid
    """
    # Construct the URL
    url = f"{director.url}/vnms/dashboard/appliance/{Uuid}/hardware"
    url = url.replace('{Uuid}', Uuid)

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///dashboard/appliance/{applianceName}/bandwidthservers?command={command}&uuid={uuid}")
def get_bw_measurement(applianceName, command, uuid) -> str:
    """
    Get BW Measurement

    Method: GET
    URL: /vnms/dashboard/appliance/{applianceName}/bandwidthservers
    Parameters: applianceName, command, uuid
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

    # Append query parameters if any
    if query_params:
        url += '?' + '&'.join([f'{k}={v}' for k, v in query_params.items()])

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///dashboard/appliance/{applianceName}/capabilities")
def get_appliance_capabilities(applianceName) -> str:
    """
    Get Appliance Capabilities

    Method: GET
    URL: /vnms/dashboard/appliance/{applianceName}/capabilities
    Parameters: applianceName
    """
    # Construct the URL
    url = f"{director.url}/vnms/dashboard/appliance/{applianceName}/capabilities"
    url = url.replace('{applianceName}', applianceName)

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///dashboard/appliance/{applianceName}/live?command={command}&decode={decode}&fetch={fetch}&filters={filters}&uuid={uuid}")
def get_appliance_live_status(applianceName, command, decode, fetch, filters, uuid) -> str:
    """
    Get Appliance Live Status

    Method: GET
    URL: /vnms/dashboard/appliance/{applianceName}/live
    Parameters: applianceName, command, decode, fetch, filters, uuid
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

    # Append query parameters if any
    if query_params:
        url += '?' + '&'.join([f'{k}={v}' for k, v in query_params.items()])

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///dashboard/appliance/{applianceUUID}/syncStatus")
def get_appliance_sync_status(applianceUUID) -> str:
    """
    Get Appliance Sync Status

    Method: GET
    URL: /vnms/dashboard/appliance/{applianceUUID}/syncStatus
    Parameters: applianceUUID
    """
    # Construct the URL
    url = f"{director.url}/vnms/dashboard/appliance/{applianceUUID}/syncStatus"
    url = url.replace('{applianceUUID}', applianceUUID)

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///dashboard/applianceServices/{applianceName}")
def get_appliance_services(applianceName) -> str:
    """
    Get Appliance Services

    Method: GET
    URL: /vnms/dashboard/applianceServices/{applianceName}
    Parameters: applianceName
    """
    # Construct the URL
    url = f"{director.url}/vnms/dashboard/applianceServices/{applianceName}"
    url = url.replace('{applianceName}', applianceName)

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///dashboard/applianceStatus/{applianceUUID}")
def get_appliance_status(applianceUUID) -> str:
    """
    Get Appliance Status

    Method: GET
    URL: /vnms/dashboard/applianceStatus/{applianceUUID}
    Parameters: applianceUUID
    """
    # Construct the URL
    url = f"{director.url}/vnms/dashboard/applianceStatus/{applianceUUID}"
    url = url.replace('{applianceUUID}', applianceUUID)

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///dashboard/applianceStatus/{applianceUUID}/brief")
def get_appliance_status_brief(applianceUUID) -> str:
    """
    Get Appliance Status Brief

    Method: GET
    URL: /vnms/dashboard/applianceStatus/{applianceUUID}/brief
    Parameters: applianceUUID
    """
    # Construct the URL
    url = f"{director.url}/vnms/dashboard/applianceStatus/{applianceUUID}/brief"
    url = url.replace('{applianceUUID}', applianceUUID)

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///cloud/systems/getAllApplianceNames")
def get_all_appliance_names() -> str:
    """
    Get All Appliance Names

    Method: GET /vnms/cloud/systems/getAllApplianceNames"
    Parameters: None
    """
    # Construct the URL
    url = f"{director.url}/vnms/cloud/systems/getAllApplianceNames"

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///cloud/systems/getAllAppliancesBasicDetails?limit={limit}&offset={offset}")
def get_all_appliances_basic_details(limit, offset) -> str:
    """
    Get All Appliances Basic Details

    Method: GET
    URL: /vnms/cloud/systems/getAllAppliancesBasicDetails
    Parameters: limit, offset
    """
    # Construct the URL
    url = f"{director.url}/vnms/cloud/systems/getAllAppliancesBasicDetails"

    # Add query parameters
    query_params = {}

    if limit:
        query_params['limit'] = limit

    if offset:
        query_params['offset'] = offset

    # Append query parameters if any
    if query_params:
        url += '?' + '&'.join([f'{k}={v}' for k, v in query_params.items()])

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///dashboard/applianceviolations/{applianceName}")
def get_appliance_violations(applianceName) -> str:
    """
    Get Appliance Violations

    Method: GET
    URL: /vnms/dashboard/applianceviolations/{applianceName}
    Parameters: applianceName
    """
    # Construct the URL
    url = f"{director.url}/vnms/dashboard/applianceviolations/{applianceName}"
    url = url.replace('{applianceName}', applianceName)

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///dashboard/enableMonitoring")
def get_enable_monitoring() -> str:
    """
    Get Enable Monitoring

    Method: GET
    URL: /vnms/dashboard/enableMonitoring
    Parameters: None
    """
    # Construct the URL
    url = f"{director.url}/vnms/dashboard/enableMonitoring"

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///dashboard/getMonitorPullEnabled/{deviceName}")
def get_device_status_pulling_enabled(deviceName) -> str:
    """
    Get Device Status Pulling Enabled

    Method: GET
    URL: /vnms/dashboard/getMonitorPullEnabled/{deviceName}
    Parameters: deviceName
    """
    # Construct the URL
    url = f"{director.url}/vnms/dashboard/getMonitorPullEnabled/{deviceName}"
    url = url.replace('{deviceName}', deviceName)

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///dashboard/health/ike?deviceName={deviceName}")
def get_health_ike(deviceName) -> str:
    """
    Get Health IKE

    Method: GET
    URL: /vnms/dashboard/health/ike
    Parameters: deviceName
    """
    # Construct the URL
    url = f"{director.url}/vnms/dashboard/health/ike"

    # Add query parameters
    query_params = {}

    if deviceName:
        query_params['deviceName'] = deviceName

    # Append query parameters if any
    if query_params:
        url += '?' + '&'.join([f'{k}={v}' for k, v in query_params.items()])

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///dashboard/health/interface?deviceName={deviceName}")
def get_health_interface(deviceName) -> str:
    """
    Get Health Interface

    Method: GET
    URL: /vnms/dashboard/health/interface
    Parameters: deviceName
    """
    # Construct the URL
    url = f"{director.url}/vnms/dashboard/health/interface"

    # Add query parameters
    query_params = {}

    if deviceName:
        query_params['deviceName'] = deviceName

    # Append query parameters if any
    if query_params:
        url += '?' + '&'.join([f'{k}={v}' for k, v in query_params.items()])

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///dashboard/health/path?deviceName={deviceName}")
def get_health_path(deviceName) -> str:
    """
    Get Health Path

    Method: GET
    URL: /vnms/dashboard/health/path
    Parameters: deviceName
    """
    # Construct the URL
    url = f"{director.url}/vnms/dashboard/health/path"

    # Add query parameters
    query_params = {}

    if deviceName:
        query_params['deviceName'] = deviceName

    # Append query parameters if any
    if query_params:
        url += '?' + '&'.join([f'{k}={v}' for k, v in query_params.items()])

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///dashboard/lte/list")
def get_devices_in_lte() -> str:
    """
    Get Devices in LTE

    Method: GET
    URL: /vnms/dashboard/lte/list
    Parameters: None
    """
    # Construct the URL
    url = f"{director.url}/vnms/dashboard/lte/list"

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///dashboard/navTree?appUUID={appUUID}&forceRefresh={forceRefresh}&skipCpeNodes={skipCpeNodes}")
def get_nav_tree_node(appUUID, forceRefresh, skipCpeNodes) -> str:
    """
    Get Nav Tree Node

    Method: GET
    URL: /vnms/dashboard/navTree
    Parameters: appUUID, forceRefresh, skipCpeNodes
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

    # Append query parameters if any
    if query_params:
        url += '?' + '&'.join([f'{k}={v}' for k, v in query_params.items()])

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///dashboard/status/headEnds")
def get_head_end_status() -> str:
    """
    Get Head-End Status

    Method: GET
    URL: /vnms/dashboard/status/headEnds
    Parameters: None
    """
    # Construct the URL
    url = f"{director.url}/vnms/dashboard/status/headEnds"

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///dashboard/vdStatus")
def get_vd_status() -> str:
    """
    Get VD Status

    Method: GET
    URL: /vnms/dashboard/vdStatus
    Parameters: None
    """
    # Construct the URL
    url = f"{director.url}/vnms/dashboard/vdStatus"

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///dashboard/vdStatus/haDetails")
def get_vd_ha_details() -> str:
    """
    Get VD HA Details

    Method: GET
    URL: /vnms/dashboard/vdStatus/haDetails
    Parameters: None
    """
    # Construct the URL
    url = f"{director.url}/vnms/dashboard/vdStatus/haDetails"

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///dashboard/vdStatus/packageInfo")
def get_vd_package_info() -> str:
    """
    Get VD Package Info

    Method: GET
    URL: /vnms/dashboard/vdStatus/packageInfo
    Parameters: None
    """
    # Construct the URL
    url = f"{director.url}/vnms/dashboard/vdStatus/packageInfo"

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///dashboard/vdStatus/sysDetails")
def get_sys_details() -> str:
    """
    Get Sys Details

    Method: GET
    URL: /vnms/dashboard/vdStatus/sysDetails
    Parameters: None
    """
    # Construct the URL
    url = f"{director.url}/vnms/dashboard/vdStatus/sysDetails"

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///dashboard/vdStatus/sysUptime")
def get_sys_uptime() -> str:
    """
    Get Sys Uptime

    Method: GET
    URL: /vnms/dashboard/vdStatus/sysUptime
    Parameters: None
    """
    # Construct the URL
    url = f"{director.url}/vnms/dashboard/vdStatus/sysUptime"

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///fault/alarms/page?device_name={device_name}&filtertype={filtertype}&force_refresh={force_refresh}&include_children={include_children}&is_cleared={is_cleared}&is_deep={is_deep}&last_alarm_text={last_alarm_text}&last_change_after={last_change_after}&last_change_before={last_change_before}&last_perceived_severity={last_perceived_severity}&last_status_change={last_status_change}&limit={limit}&offset={offset}&org={org}&show_system_alarm={show_system_alarm}&sort_column={sort_column}&sort_order={sort_order}&type={type}")
def filter_paginate_alarm(device_name, filtertype, force_refresh, include_children, is_cleared, is_deep, last_alarm_text, last_change_after, last_change_before, last_perceived_severity, last_status_change, limit, offset, org, show_system_alarm, sort_column, sort_order, type) -> str:
    """
    Filter Paginate Alarm

    Method: GET
    URL: /vnms/fault/alarms/page
    Parameters: device_name, filtertype, force_refresh, include_children, is_cleared, is_deep, last_alarm_text, last_change_after, last_change_before, last_perceived_severity, last_status_change, limit, offset, org, show_system_alarm, sort_column, sort_order, type
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

    # Append query parameters if any
    if query_params:
        url += '?' + '&'.join([f'{k}={v}' for k, v in query_params.items()])

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///fault/alarm/handling?device_name={device_name}&managed_object={managed_object}&org={org}&type={type}&specific_problem={specific_problem}")
def get_alarm_handling(device_name, managed_object, org, type, specific_problem) -> str:
    """
    Get Alarm Handling

    Method: GET
    URL: /vnms/fault/alarm/handling
    Parameters: device_name, managed_object, org, type, specific_problem
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

    # Append query parameters if any
    if query_params:
        url += '?' + '&'.join([f'{k}={v}' for k, v in query_params.items()])

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///fault/alarms/summary/{org}?include_children={include_children}&include_system={include_system}")
def get_alarm_summary_per_org(org, include_children, include_system) -> str:
    """
    Get Alarm Summary Per Org

    Method: GET
    URL: /vnms/fault/alarms/summary/{org}
    Parameters: org, include_children, include_system
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

    # Append query parameters if any
    if query_params:
        url += '?' + '&'.join([f'{k}={v}' for k, v in query_params.items()])

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///fault/alarms/summary")
def get_alarm_summary() -> str:
    """
    Get Alarm Summary

    Method: GET
    URL: /vnms/fault/alarms/summary
    Parameters: None
    """
    # Construct the URL
    url = f"{director.url}/vnms/fault/alarms/summary"

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///fault/types")
def get_alarm_types() -> str:
    """
    Get Alarm Types

    Method: GET
    URL: /vnms/fault/types
    Parameters: None
    """
    # Construct the URL
    url = f"{director.url}/vnms/fault/types"

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///fault/alarms?device_name={device_name}&filtertype={filtertype}&is_cleared={is_cleared}&is_deep={is_deep}&last_alarm_text={last_alarm_text}&last_change_after={last_change_after}&last_change_before={last_change_before}&last_perceived_severity={last_perceived_severity}&last_status_change={last_status_change}&org={org}&type={type}")
def get_all_filtered_alarms(device_name, filtertype, is_cleared, is_deep, last_alarm_text, last_change_after, last_change_before, last_perceived_severity, last_status_change, org, type) -> str:
    """
    Get All Filtered Alarms

    Method: GET
    URL: /vnms/fault/alarms
    Parameters: device_name, filtertype, is_cleared, is_deep, last_alarm_text, last_change_after, last_change_before, last_perceived_severity, last_status_change, org, type
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

    # Append query parameters if any
    if query_params:
        url += '?' + '&'.join([f'{k}={v}' for k, v in query_params.items()])

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///fault/analytics/alarms/summary")
def get_analytics_alarm_summary() -> str:
    """
    Get Analytics Alarm Summary

    Method: GET
    URL: /vnms/fault/analytics/alarms/summary
    Parameters: None
    """
    # Construct the URL
    url = f"{director.url}/vnms/fault/analytics/alarms/summary"

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///fault/analytics/alarms?search_string={search_string}&severity={severity}")
def get_analytics_alarms(search_string, severity) -> str:
    """
    Get Analytics Alarms

    Method: GET
    URL: /vnms/fault/analytics/alarms
    Parameters: search_string, severity
    """
    # Construct the URL
    url = f"{director.url}/vnms/fault/analytics/alarms"

    # Add query parameters
    query_params = {}

    if search_string:
        query_params['search_string'] = search_string

    if severity:
        query_params['severity'] = severity

    # Append query parameters if any
    if query_params:
        url += '?' + '&'.join([f'{k}={v}' for k, v in query_params.items()])

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///fault/appliance/alarm_model")
def get_appliance_alarm_model() -> str:
    """
    Get Appliance Alarm Model

    Method: GET
    URL: /vnms/fault/appliance/alarm_model
    Parameters: None
    """
    # Construct the URL
    url = f"{director.url}/vnms/fault/appliance/alarm_model"

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///fault/appliance/types")
def get_appliance_alarm_types() -> str:
    """
    Get Appliance Alarm Types

    Method: GET
    URL: /vnms/fault/appliance/types
    Parameters: None
    """
    # Construct the URL
    url = f"{director.url}/vnms/fault/appliance/types"

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///fault/alarms/summary/device/{deviceName}?org={org}")
def get_device_alarm_summary(deviceName, org) -> str:
    """
    Get Device Alarm Summary

    Method: GET
    URL: /vnms/fault/alarms/summary/device/{deviceName}
    Parameters: deviceName, org
    """
    # Construct the URL
    url = f"{director.url}/vnms/fault/alarms/summary/device/{deviceName}"
    url = url.replace('{deviceName}', deviceName)

    # Add query parameters
    query_params = {}

    if org:
        query_params['org'] = org

    # Append query parameters if any
    if query_params:
        url += '?' + '&'.join([f'{k}={v}' for k, v in query_params.items()])

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///fault/director/alarms/summary")
def get_director_alarm_summary() -> str:
    """
    Get Director Alarm Summary

    Method: GET
    URL: /vnms/fault/director/alarms/summary
    Parameters: None
    """
    # Construct the URL
    url = f"{director.url}/vnms/fault/director/alarms/summary"

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///fault/director/alarms?search_string={search_string}&severity={severity}")
def get_director_alarms(search_string, severity) -> str:
    """
    Get Director Alarms

    Method: GET
    URL: /vnms/fault/director/alarms
    Parameters: search_string, severity
    """
    # Construct the URL
    url = f"{director.url}/vnms/fault/director/alarms"

    # Add query parameters
    query_params = {}

    if search_string:
        query_params['search_string'] = search_string

    if severity:
        query_params['severity'] = severity

    # Append query parameters if any
    if query_params:
        url += '?' + '&'.join([f'{k}={v}' for k, v in query_params.items()])

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///fault/director/fail-over-alarms")
def get_director_fail_over_alarms() -> str:
    """
    Get Director Fail Over Alarms

    Method: GET
    URL: /vnms/fault/director/fail-over-alarms
    Parameters: None
    """
    # Construct the URL
    url = f"{director.url}/vnms/fault/director/fail-over-alarms"

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///fault/director/ha-alarms")
def get_director_ha_alarms() -> str:
    """
    Get Director HA Alarms

    Method: GET
    URL: /vnms/fault/director/ha-alarms
    Parameters: None
    """
    # Construct the URL
    url = f"{director.url}/vnms/fault/director/ha-alarms"

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///fault/director/pop-up-summary")
def get_imp_alarm_summary() -> str:
    """
    Get IMP Alarm Summary

    Method: GET
    URL: /vnms/fault/director/pop-up-summary
    Parameters: None
    """
    # Construct the URL
    url = f"{director.url}/vnms/fault/director/pop-up-summary"

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///fault/director/pop-up")
def get_imp_alarms() -> str:
    """
    Get IMP Alarms

    Method: GET
    URL: /vnms/fault/director/pop-up
    Parameters: None
    """
    # Construct the URL
    url = f"{director.url}/vnms/fault/director/pop-up"

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text


@mcp.resource("vnms:///fault/alarm/status?device_name={device_name}&managed_object={managed_object}&org={org}&type={type}&specific_problem={specific_problem}")
def get_status_change(device_name, managed_object, org, type, specific_problem) -> str:
    """
    Get Status Change

    Method: GET
    URL: /vnms/fault/alarm/status
    Parameters: device_name, managed_object, org, type, specific_problem
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

    # Append query parameters if any
    if query_params:
        url += '?' + '&'.join([f'{k}={v}' for k, v in query_params.items()])

    # Make the request
    response = requests.request("GET", url, headers=director.get_header(), data={}, verify=False)
    return response.text

