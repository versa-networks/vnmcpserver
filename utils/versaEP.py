# Define the API endpoints (GET only)
api_endpoints = {
    "Get All Appliance Status": {
        "url": "/nextgen/appliance/status",
        "method": "GET",
        "params": ["limit", "offset"]
    },
    "Get Single Appliance Status": {
        "url": "/nextgen/appliance/status/{id}",
        "method": "GET",
        "params": ["byName"]
    },
    "Get Device Template Listing": {
        "url": "/nextgen/appliance/template_listing/{deviceName}",
        "method": "GET",
        "params": ["deviceName", "tenant"]
    },
    "Get Template Workflow": {
        "url": "/vnms/alltypes/workflow/templates/template/{templateworkflowName}",
        "method": "GET",
        "params": ["templateworkflowName"]
    },
    "Get Appliance Locations": {
        "url": "/vnms/dashboard/appliance/location",
        "method": "GET",
        "params": []
    },
    "Get Routing Instance Information": {
        "url": "/vnms/appliance/{applianceName}/routing-instances",
        "method": "GET",
        "params": ["applianceName"]
    },
    "Get All Appliances By Type and Tags": {
        "url": "/vnms/appliance/appliance",
        "method": "GET",
        "params": ["offset", "limit","type", "tags"]
    },
    "Get All Appliances Lite": {
        "url": "/vnms/appliance/appliance/lite",
        "method": "GET",
        "params": ["filterString", "limit", "offset", "org", "tags"]
    },
    "Get All Appliances LiteView": {
        "url": "/vnms/appliance/appliance/liteView",
        "method": "GET",
        "params": ["exportToCSV", "filterString", "limit", "offset", "org", "tags"]
    },
    "Search Appliance By Name": {
        "url": "/vnms/appliance/applianceByName",
        "method": "GET",
        "params": ["limit", "name", "offset"]
    },
    "Export Appliance Configuration": {
        "url": "/vnms/appliance/export",
        "method": "GET",
        "params": ["applianceName", "export-as-plain-text"]
    },
    "Get Appliances Summary": {
        "url": "/vnms/appliance/summary",
        "method": "GET",
        "params": ["filterByName"]
    },
    "Get Audit Logs": {
        "url": "/vnms/audit/logs",
        "method": "GET",
        "params": ["limit", "offset", "searchKey"]
    },
    "Device WorkFlow Fetch All": {
        "url": "/vnms/sdwan/workflow/devices",
        "method": "GET",
        "params": ["filters", "limit", "offset", "orgname"]
    },
    "Get Specific Device WorkFlow": {
        "url": "/vnms/sdwan/workflow/devices/device/{deviceName}",
        "method": "GET",
        "params": ["deviceName"]
    },
    "Get Template Bind Data Header and Count": {
        "url": "/vnms/sdwan/workflow/binddata/devices/header/template/{templateName}",
        "method": "GET",
        "params": ["templateName", "organization"]
    },
    "Template Fetch All": {
        "url": "/vnms/sdwan/workflow/templates",
        "method": "GET",
        "params": ["limit", "offset", "orgname", "searchKeyword"]
    },
    "Get Specific Template WorkFlow": {
        "url": "/vnms/sdwan/workflow/templates/template/{templateworkflowName}",
        "method": "GET",
        "params": ["templateworkflowName"]
    },
    "Device Group Fetch All": {
        "url": "/nextgen/deviceGroup",
        "method": "GET",
        "params": ["filters", "limit", "offset", "organization"]
    },
    "Get Specific Device Group": {
        "url": "/nextgen/deviceGroup/{deviceGroupName}",
        "method": "GET",
        "params": ["deviceGroupName"]
    },
    "Get All Model Numbers": {
        "url": "/nextgen/deviceGroup/modelNumbers",
        "method": "GET",
        "params": []  # This API doesn't have any parameters
    },
    "Show Templates Associated to Device": {
        "url": "/nextgen/device/{deviceName}",
        "method": "GET",
        "params": ["deviceName"]
    },
    "Get All Assets": {
        "url": "/vnms/assets/asset",
        "method": "GET",
        "params": ["filters", "limit", "offset", "organization"]
    },
    "Get Next Page Data": {
        "url": "/vnms/dashboard/appliance/next_page_data",
        "method": "GET",
        "params": ["filters", "offset", "queryId"]
    },
    "Get Appliance Details by UUID": {
        "url": "/vnms/dashboard/appliance/{Uuid}",
        "method": "GET",
        "params": ["Uuid"]
    },
    "Get Appliance Hardware": {
        "url": "/vnms/dashboard/appliance/{Uuid}/hardware",
        "method": "GET",
        "params": ["Uuid"]
    },
    "Get BW Measurement": {
        "url": "/vnms/dashboard/appliance/{applianceName}/bandwidthservers",
        "method": "GET",
        "params": ["applianceName", "command", "uuid"]
    },
    "Get Appliance Capabilities": {
        "url": "/vnms/dashboard/appliance/{applianceName}/capabilities",
        "method": "GET",
        "params": ["applianceName"]
    },
    "Get Appliance Live Status": {
        "url": "/vnms/dashboard/appliance/{applianceName}/live",
        "method": "GET",
        "params": ["applianceName", "command", "decode", "fetch", "filters", "uuid"]
    },
    "Get Appliance Sync Status": {
        "url": "/vnms/dashboard/appliance/{applianceUUID}/syncStatus",
        "method": "GET",
        "params": ["applianceUUID"]
    },
    "Get Appliance Services": {
        "url": "/vnms/dashboard/applianceServices/{applianceName}",
        "method": "GET",
        "params": ["applianceName"]
    },
    "Get Appliance Status": {
        "url": "/vnms/dashboard/applianceStatus/{applianceUUID}",
        "method": "GET",
        "params": ["applianceUUID"]
    },
    "Get Appliance Status Brief": {
        "url": "/vnms/dashboard/applianceStatus/{applianceUUID}/brief",
        "method": "GET",
        "params": ["applianceUUID"]
    },
    "Get All Appliance Names": {
        "url": "/vnms/cloud/systems/getAllApplianceNames",
        "method": "GET",
        "params": []
    },
    "Get All Appliances Basic Details": {
        "url": "/vnms/cloud/systems/getAllAppliancesBasicDetails",
        "method": "GET",
        "params": ["limit", "offset"]
    },
    "Get Appliance Violations": {
        "url": "/vnms/dashboard/applianceviolations/{applianceName}",
        "method": "GET",
        "params": ["applianceName"]
    },
    "Get Enable Monitoring": {
        "url": "/vnms/dashboard/enableMonitoring",
        "method": "GET",
        "params": []
    },
    "Get Device Status Pulling Enabled": {
        "url": "/vnms/dashboard/getMonitorPullEnabled/{deviceName}",
        "method": "GET",
        "params": ["deviceName"]
    },
    "Get Health IKE": {
        "url": "/vnms/dashboard/health/ike",
        "method": "GET",
        "params": ["deviceName"]
    },
    "Get Health Interface": {
        "url": "/vnms/dashboard/health/interface",
        "method": "GET",
        "params": ["deviceName"]
    },
    "Get Health Path": {
        "url": "/vnms/dashboard/health/path",
        "method": "GET",
        "params": ["deviceName"]
    },
    "Get Devices in LTE": {
        "url": "/vnms/dashboard/lte/list",
        "method": "GET",
        "params": []
    },
    "Get Nav Tree Node": {
        "url": "/vnms/dashboard/navTree",
        "method": "GET",
        "params": ["appUUID", "forceRefresh", "skipCpeNodes"]
    },
    "Get Head-End Status": {
        "url": "/vnms/dashboard/status/headEnds",
        "method": "GET",
        "params": []
    },
    "Get VD Status": {
        "url": "/vnms/dashboard/vdStatus",
        "method": "GET",
        "params": []
    },
    "Get VD HA Details": {
        "url": "/vnms/dashboard/vdStatus/haDetails",
        "method": "GET",
        "params": []
    },
    "Get VD Package Info": {
        "url": "/vnms/dashboard/vdStatus/packageInfo",
        "method": "GET",
        "params": []
    },
    "Get Sys Details": {
        "url": "/vnms/dashboard/vdStatus/sysDetails",
        "method": "GET",
        "params": []
    },
    "Get Sys Uptime": {
        "url": "/vnms/dashboard/vdStatus/sysUptime",
        "method": "GET",
        "params": []
    },
    "Filter Paginate Alarm": {
        "url": "/vnms/fault/alarms/page",
        "method": "GET",
        "params": ["device_name", "filtertype", "force_refresh", "include_children", "is_cleared", "is_deep",
                   "last_alarm_text", "last_change_after", "last_change_before", "last_perceived_severity",
                   "last_status_change", "limit", "offset", "org", "show_system_alarm", "sort_column", "sort_order",
                   "type"]
    },
    "Get Alarm Handling": {
        "url": "/vnms/fault/alarm/handling",
        "method": "GET",
        "params": ["device_name", "managed_object", "org", "type", "specific_problem"]
    },
    "Get Alarm Summary Per Org": {
        "url": "/vnms/fault/alarms/summary/{org}",
        "method": "GET",
        "params": ["org", "include_children", "include_system"]
    },
    "Get Alarm Summary": {
        "url": "/vnms/fault/alarms/summary",
        "method": "GET",
        "params": []
    },
    "Get Alarm Types": {
        "url": "/vnms/fault/types",
        "method": "GET",
        "params": []
    },
    "Get All Filtered Alarms": {
        "url": "/vnms/fault/alarms",
        "method": "GET",
        "params": ["device_name", "filtertype", "is_cleared", "is_deep", "last_alarm_text", "last_change_after",
                   "last_change_before", "last_perceived_severity", "last_status_change", "org", "type"]
    },
    "Get Analytics Alarm Summary": {
        "url": "/vnms/fault/analytics/alarms/summary",
        "method": "GET",
        "params": []
    },
    "Get Analytics Alarms": {
        "url": "/vnms/fault/analytics/alarms",
        "method": "GET",
        "params": ["search_string", "severity"]
    },
    "Get Appliance Alarm Model": {
        "url": "/vnms/fault/appliance/alarm_model",
        "method": "GET",
        "params": []
    },
    "Get Appliance Alarm Types": {
        "url": "/vnms/fault/appliance/types",
        "method": "GET",
        "params": []
    },
    "Get Device Alarm Summary": {
        "url": "/vnms/fault/alarms/summary/device/{deviceName}",
        "method": "GET",
        "params": ["deviceName", "org"]
    },
    "Get Director Alarm Summary": {
        "url": "/vnms/fault/director/alarms/summary",
        "method": "GET",
        "params": []
    },
    "Get Director Alarms": {
        "url": "/vnms/fault/director/alarms",
        "method": "GET",
        "params": ["search_string", "severity"]
    },
    "Get Director Fail Over Alarms": {
        "url": "/vnms/fault/director/fail-over-alarms",
        "method": "GET",
        "params": []
    },
    "Get Director HA Alarms": {
        "url": "/vnms/fault/director/ha-alarms",
        "method": "GET",
        "params": []
    },
    "Get IMP Alarm Summary": {
        "url": "/vnms/fault/director/pop-up-summary",
        "method": "GET",
        "params": []
    },
    "Get IMP Alarms": {
        "url": "/vnms/fault/director/pop-up",
        "method": "GET",
        "params": []
    },
    "Get Status Change": {
        "url": "/vnms/fault/alarm/status",
        "method": "GET",
        "params": ["device_name", "managed_object", "org", "type", "specific_problem"]
    },
}
