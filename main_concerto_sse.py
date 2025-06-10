import httpx
from mcp.server.fastmcp import FastMCP
from typing import Dict, List, Optional, Any, Union
import time
import jwt
import json
import os
import requests
from starlette.applications import Starlette
from starlette.routing import Mount, Host
import uvicorn

# Disable SSL warnings if you're using verify=False
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Concerto:
    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password
        """ Manages application lifespan """
        self.payload = {"client_id": os.environ['VN_CLIENT_ID'],
               "client_secret": os.environ['VN_CLIENT_SECRET'],
               "username": self.username,
               "password": self.password,
               "scope": "global",
               "grant_type": "password"}
        self.regen_token()

    def regen_token(self):
        resp = requests.request("POST", url=f"{self.url}/portalapi/v1/auth/token",
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

concerto = Concerto(url=os.environ['CONCERTO_URL'], username=os.environ['VN_USERNAME'], password=os.environ['VN_PASSWORD'])
mcp = FastMCP(
    name="Concerto API Server", 
    instructions="This server provides optimized access to Versa Concerto APIs through logical groupings", 
    dependencies=["requests", "urllib3", "pyjwt"]
)

def get_header(access_token: str) -> Dict[str, str]:
    """Create authentication headers for API requests"""
    return {
        'Authorization': f'Bearer {access_token}',
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


async def make_api_request(
    url: str, 
    endpoint: str, 
    access_token: str, 
    method: str = "GET",
    params: Optional[Dict[str, Any]] = None,
    body: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Generic API request helper"""
    full_url = f"{url}/portalapi{endpoint}"
    
    async with httpx.AsyncClient(verify=False) as client:
        if method.upper() == "GET":
            response = await client.get(
                full_url,
                headers=get_header(access_token),
                params=params or {}
            )
        elif method.upper() == "POST":
            response = await client.post(
                full_url,
                headers=get_header(access_token),
                params=params or {},
                json=body
            )
        elif method.upper() == "PUT":
            response = await client.put(
                full_url,
                headers=get_header(access_token),
                params=params or {},
                json=body
            )
        elif method.upper() == "DELETE":
            response = await client.delete(
                full_url,
                headers=get_header(access_token),
                params=params or {}
            )
    
    try:
        return response.json()
    except ValueError:
        return {"text": response.text, "status_code": response.status_code}

@mcp.tool()
async def get_tenant_uuid(self, tenant_name: str) -> str:
    """Get tenant UUID by name"""
        
    ep = f"/v1/tenants/tenant/name/{tenant_name}"
    op = await make_api_request(concerto.url, ep, concerto.access_token, params=None)
    print(f"Sridhar ---------> {op}")
    
    uuid = op["tenantInfo"]["uuid"]
    return uuid

@mcp.tool()
async def manage_notifications(
    action: str,
    tenant_uuid: Optional[str] = None,
    next_window_number: Optional[int] = 0,
    window_size: Optional[int] = 10,
    search_keyword: Optional[str] = None
) -> Dict[str, Any]:
    """
    Manage notifications across the Concerto platform
    
    Actions:
    - get_active_login: Get active login notifications
    - get_active: Get active notifications  
    - get_all: Get all notifications
    - get_tenant_active_login: Get tenant-specific active login notifications (requires tenant_uuid)
    - get_tenant_active: Get tenant-specific active notifications (requires tenant_uuid)
    
    Parameters:
    - action: The notification action to perform
    - tenant_uuid: Tenant UUID (required for tenant-specific actions)
    - next_window_number: Pagination cursor (default: 0)
    - window_size: Number of notifications per page (default: 10)
    - search_keyword: Search filter for notifications
    """
    
    params = {
        "nextWindowNumber": next_window_number,
        "windowSize": window_size
    }
    
    if search_keyword:
        params["searchKeyword"] = search_keyword
    
    endpoint_map = {
        "get_active_login": "/v1/settings/notification/active/login/summarize",
        "get_active": "/v1/settings/notification/active/summarize", 
        "get_all": "/v1/settings/notification/summarize",
        "get_tenant_active_login": f"/v1/settings/tenants/{tenant_uuid}/notification/active/login/summarize",
        "get_tenant_active": f"/v1/settings/tenants/{tenant_uuid}/notification/active/summarize"
    }
    
    if action not in endpoint_map:
        return {"error": f"Invalid action. Available actions: {list(endpoint_map.keys())}"}
    
    if action.startswith("get_tenant_") and not tenant_uuid:
        return {"error": "tenant_uuid is required for tenant-specific actions"}
    
    return await make_api_request(concerto.url, endpoint_map[action], concerto.access_token, params=params)

@mcp.tool()
async def manage_sase_operations(
    tenant_uuid: str,
    action: str,
    resource_path: Optional[str] = None,
    resource_id: Optional[str] = None,
    federated_path: Optional[str] = None,
    filters: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Manage comprehensive SASE operations and configurations
    
    Actions:
    - list_resources: List SASE resources by path
    - get_resource: Get specific SASE resource by ID
    - get_summary: Get summary of SASE resources
    
    Resource Paths (use full paths from SASE endpoints):
    APIDP:
    - apidp/connector/iaas: APIDP IaaS connectors
    - apidp/connector/saas: APIDP SaaS connectors
    - apidp/policy-rules/iaas/event: APIDP IaaS event-based policy rules
    - apidp/policy-rules/iaas/schedule: APIDP IaaS schedule-based policy rules
    - apidp/policy-rules/saas/event: APIDP SaaS event-based policy rules
    - apidp/policy-rules/saas/schedule: APIDP SaaS schedule-based policy rules
    - apidp/profile/atp: APIDP ATP profiles
    - apidp/profile/av: APIDP AV profiles
    - apidp/profile/casb/iaas: APIDP CASB IaaS profiles
    - apidp/profile/casb/saas: APIDP CASB SaaS profiles
    - apidp/profile/dlp/data-pattern: APIDP DLP data patterns
    - apidp/profile/dlp/data-protection: APIDP DLP data protection profiles
    - apidp/profile/dlp/rule: APIDP DLP rules
    - apidp/profile/dlp: APIDP DLP profiles
    - apidp/profile/domain: APIDP domain profiles
    - apidp/profile/user: APIDP user profiles
    - apidp/remote-browser-isolation/policy-rule: RBI policy rules
    
    Real-time Protection:
    - real-time/internet-protection: Internet protection
    - real-time/network-obfuscation: Network obfuscation
    - real-time/private-app-protection: Private app protection
    - real-time/profile/atp: Real-time ATP profiles
    - real-time/profile/av: Real-time AV profiles
    - real-time/profile/casb/constraints-profile: CASB constraints profiles
    - real-time/profile/casb: Real-time CASB profiles
    - real-time/profile/dlp/data-pattern: Real-time DLP data patterns
    - real-time/profile/dlp/data-protection: Real-time DLP data protection
    - real-time/profile/dlp/rule: Real-time DLP rules
    - real-time/profile/dlp: Real-time DLP profiles
    - real-time/profile/dnsf: DNS filtering profiles
    - real-time/profile/filef: File filtering profiles
    - real-time/profile/http-header: HTTP header profiles
    - real-time/profile/ipf: IP filtering profiles
    - real-time/profile/ips-override: IPS override profiles
    - real-time/profile/ips: IPS profiles
    - real-time/profile/rbi: RBI profiles
    - real-time/profile/urlf: URL filtering profiles
    - real-time/safesearch: Safe search configurations
    
    Access and Authentication:
    - authentication/profile: Authentication profiles
    - authentication/rule: Authentication rules
    - secure-access-clientless/rule: Clientless secure access rules
    - secure-access-client/profile: Client secure access profiles
    - secure-access-client/rule: Client secure access rules
    - captive-portal: Captive portal configurations
    
    Application and Network:
    - application-reverse-proxy: Application reverse proxy
    - private-application-reverse-proxy: Private application reverse proxy
    - bandwidth-limits/client-bandwidth-limits: Client bandwidth limits
    - bgp-policy: BGP policies
    - site-to-site-tunnels: Site-to-site tunnels
    - tls-decryption/profile: TLS decryption profiles
    - tls-decryption/rule: TLS decryption rules
    - tls-decryption/v2/rule: TLS decryption v2 rules
    
    Security and Monitoring:
    - email-protection/policy-rules: Email protection policy rules
    - email-protection/proxies: Email protection proxies
    - device-risk-profile: Device risk profiles
    - digital-experience-monitoring/client-based-profile: DEM client-based profiles
    - forensic-profile: Forensic profiles
    - legal-hold-profile: Legal hold profiles
    - quarantine-profile: Quarantine profiles
    - ueba/policy-rules: UEBA policy rules
    - ueba/profiles: UEBA profiles
    
    Partner Integrations:
    - partner-integration/endpoint-detection/crowdstrike: CrowdStrike integration
    - partner-integration/endpoint-detection/google-threat-intelligence: Google TI integration
    - partner-integration/endpoint-detection/microsoft-defender-endpoint: Microsoft Defender integration
    - partner-integration/microsoft: Microsoft integration
    
    Identity and Access:
    - scim: SCIM configurations
    - scim/group: SCIM groups
    - scim/user: SCIM users
    - terminal-server-agent: Terminal server agents
    
    Settings:
    - settings/applicationCategory: Application categories
    - settings/eip/eip-agent-profile: EIP agent profiles
    - settings/eip/eip-object: EIP objects
    - settings/eip/eip-profile: EIP profiles
    - settings/lan-interface: LAN interfaces
    - settings/notification-profile: Notification profiles
    - settings/operating-system: Operating systems
    - settings/securityAction: Security actions
    - settings/urlCategory: URL categories
    
    Certificates:
    - certificate: Certificate management
    - connectors/azure-connector: Azure connectors
    
    Parameters:
    - tenant_uuid: Tenant UUID
    - action: SASE action to perform
    - resource_path: Full path to SASE resource (e.g., "apidp/connector/iaas")
    - resource_id: Specific resource identifier
    - federated_path: Federated path for hierarchical resources
    - filters: Additional query filters
    """
    
    if action == "list_resources":
        if not resource_path:
            return {"error": "resource_path is required for list_resources action"}
        
        endpoint = f"/v1/tenants/{tenant_uuid}/sase/{resource_path}/summarize"
        if federated_path:
            endpoint = f"/v1/tenants/{tenant_uuid}/sase/{resource_path}/{federated_path}/summarize"
            
    elif action == "get_resource":
        if not resource_path or not resource_id:
            return {"error": "resource_path and resource_id are required for get_resource action"}
        
        endpoint = f"/v1/tenants/{tenant_uuid}/sase/{resource_path}/{resource_id}"
        
    elif action == "get_summary":
        endpoint = f"/v1/tenants/{tenant_uuid}/sase/summarize"
        
    else:
        return {"error": f"Invalid action. Available actions: list_resources, get_resource, get_summary"}
    
    return await make_api_request(concerto.url, endpoint, concerto.access_token, params=filters)

@mcp.tool()
async def manage_sdwan_operations(
    tenant_uuid: str, 
    action: str,
    resource_path: Optional[str] = None,
    resource_id: Optional[str] = None,
    federated_path: Optional[str] = None,
    filters: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Manage comprehensive SD-WAN operations, policies, and configurations
    
    Actions:
    - list_resources: List SD-WAN resources by path
    - get_resource: Get specific SD-WAN resource
    - get_summary: Get SD-WAN summary
    
    Resource Paths:
    Policy Categories:
    - policies/authentication/policy: Authentication policies
    - policies/authentication/profile: Authentication profiles
    - policies/network-service/dns-proxy-policy: DNS proxy policies
    - policies/network-service/dns-proxy-profile: DNS proxy profiles
    - policies/security/av: Anti-virus policies
    - policies/security/ipf: IP filtering policies
    - policies/security/ips: IPS policies
    - policies/security/tls-decryption: TLS decryption policies
    - policies/security/urlf: URL filtering policies
    - policies/system/alg-configurations: ALG configuration policies
    
    Profile Categories:
    - profile/security/tls-decryption: TLS decryption profiles
    
    Rule Categories:
    - rules/application/traffic-steering: Application traffic steering rules
    - rules/security/access-control: Security access control rules
    
    Parameters:
    - tenant_uuid: Tenant UUID
    - action: SD-WAN action to perform
    - resource_path: Full path to SD-WAN resource (e.g., "policies/security/av")
    - resource_id: Specific resource identifier
    - federated_path: Federated path for hierarchical resources
    - filters: Additional query filters
    """
    
    if action == "list_resources":
        if not resource_path:
            return {"error": "resource_path is required for list_resources action"}
        
        endpoint = f"/v1/tenants/{tenant_uuid}/sd-wan/{resource_path}/summarize"
        if federated_path:
            endpoint = f"/v1/tenants/{tenant_uuid}/sd-wan/{resource_path}/{federated_path}/summarize"
            
    elif action == "get_resource":
        if not resource_path or not resource_id:
            return {"error": "resource_path and resource_id are required for get_resource action"}
        
        endpoint = f"/v1/tenants/{tenant_uuid}/sd-wan/{resource_path}/{resource_id}"
        
    elif action == "get_summary":
        endpoint = f"/v1/tenants/{tenant_uuid}/sd-wan/summarize"
        
    else:
        return {"error": f"Invalid action. Available actions: list_resources, get_resource, get_summary"}
    
    return await make_api_request(concerto.url, endpoint, concerto.access_token, params=filters)

@mcp.tool()
async def manage_elements(
    tenant_uuid: str,
    action: str,
    element_type: Optional[str] = None,
    element_id: Optional[str] = None,
    federated_path: Optional[str] = None,
    filters: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Manage network elements like applications, endpoints, services, etc.
    
    Actions:
    - list_elements: List elements by type
    - get_element: Get specific element
    - get_summary: Get elements summary
    - search_elements: Search elements with filters
    - get_predefined: Get predefined applications (application type only)
    
    Element Types:
    - application: Applications and app categories (supports predefined and summarizeWithFilter)
    - endpoint: Network endpoints
    - services: Network services
    - servers: Server configurations
    - monitor: Monitoring configurations
    - nat-pool: NAT pool configurations
    - qos: QoS configurations
    - vpn-name: VPN name configurations
    
    Parameters:
    - tenant_uuid: Tenant UUID
    - action: Element action to perform
    - element_type: Type of element
    - element_id: Specific element identifier
    - federated_path: Federated path for hierarchical elements
    - filters: Additional query filters
    """
    
    if action == "list_elements":
        if not element_type:
            return {"error": "element_type is required for list_elements action"}
        
        endpoint = f"/v1/tenants/{tenant_uuid}/elements/{element_type}/summarize"
        if federated_path:
            endpoint = f"/v1/tenants/{tenant_uuid}/elements/{element_type}/{federated_path}/summarize"
            
    elif action == "get_element":
        if not element_type or not element_id:
            return {"error": "element_type and element_id are required for get_element action"}
        
        endpoint = f"/v1/tenants/{tenant_uuid}/elements/{element_type}/{element_id}"
        
    elif action == "get_summary":
        endpoint = f"/v1/tenants/{tenant_uuid}/elements/summarize"
        
    elif action == "search_elements":
        if not element_type:
            return {"error": "element_type is required for search_elements action"}
        
        endpoint = f"/v1/tenants/{tenant_uuid}/elements/{element_type}/summarizeWithFilter"
        
    elif action == "get_predefined":
        if element_type != "application":
            return {"error": "get_predefined action is only available for application element_type"}
        
        endpoint = f"/v1/tenants/{tenant_uuid}/elements/application/predefined/summarize"
        
    else:
        return {"error": f"Invalid action. Available actions: list_elements, get_element, get_summary, search_elements, get_predefined"}
    
    return await make_api_request(concerto.url, endpoint, concerto.access_token, params=filters)

@mcp.tool()
async def manage_policies_and_rules(
    tenant_uuid: str,
    action: str,
    resource_path: Optional[str] = None,
    policy_id: Optional[str] = None,
    federated_path: Optional[str] = None,
    rule_data: Optional[Dict[str, Any]] = None,
    filters: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Manage security policies and access control rules
    
    Actions:
    - list_policies: List policies by type
    - get_policy: Get specific policy
    - create_policy: Create new policy (requires rule_data)
    - update_policy: Update existing policy (requires policy_id and rule_data)
    - delete_policy: Delete policy (requires policy_id)
    - list_rules: List rules by type
    - get_rule: Get specific rule
    
    Policy/Rule Paths:
    Policy Categories:
    - policies/application/{category}: Application policies with category
    - policies/device/{category}: Device policies with category  
    - policies/network-service/{category}: Network service policies with category
    - policies/routing/{category}: Routing policies with category
    - policies/security/{category}: Security policies with category
    - policies/system/{category}: System policies with category
    - policies/vpn: VPN policies
    
    Rule Categories:
    - rules/application: Application rules
    - rules/device: Device rules
    - rules/network-service: Network service rules
    - rules/security: Security rules
    - rules/topology: Topology rules
    - rules/vpn: VPN rules
    
    Note: For policies with categories, provide the category in the resource_path like "policies/application/my-category"
    
    Parameters:
    - tenant_uuid: Tenant UUID
    - action: Policy/rule action to perform
    - resource_path: Full path to policy/rule resource (e.g., "policies/security/firewall")
    - policy_id: Specific policy/rule identifier
    - federated_path: Federated path for hierarchical resources
    - rule_data: Policy/rule configuration data (for create/update)
    - filters: Additional query filters
    """
    
    if action == "list_policies":
        if not resource_path:
            return {"error": "resource_path is required for list_policies action"}
        
        endpoint = f"/v1/tenants/{tenant_uuid}/{resource_path}/summarize"
        if federated_path:
            endpoint = f"/v1/tenants/{tenant_uuid}/{resource_path}/{federated_path}/summarize"
        method = "GET"
        
    elif action == "get_policy":
        if not resource_path or not policy_id:
            return {"error": "resource_path and policy_id are required for get_policy action"}
        
        endpoint = f"/v1/tenants/{tenant_uuid}/{resource_path}/{policy_id}"
        method = "GET"
        
    elif action == "create_policy":
        if not resource_path or not rule_data:
            return {"error": "resource_path and rule_data are required for create_policy action"}
        
        endpoint = f"/v1/tenants/{tenant_uuid}/{resource_path}"
        method = "POST"
        
    elif action == "update_policy":
        if not resource_path or not policy_id or not rule_data:
            return {"error": "resource_path, policy_id and rule_data are required for update_policy action"}
        
        endpoint = f"/v1/tenants/{tenant_uuid}/{resource_path}/{policy_id}"
        method = "PUT"
        
    elif action == "delete_policy":
        if not resource_path or not policy_id:
            return {"error": "resource_path and policy_id are required for delete_policy action"}
        
        endpoint = f"/v1/tenants/{tenant_uuid}/{resource_path}/{policy_id}"
        method = "DELETE"
        
    elif action == "list_rules":
        if not resource_path:
            return {"error": "resource_path is required for list_rules action"}
        
        endpoint = f"/v1/tenants/{tenant_uuid}/{resource_path}/summarize"
        if federated_path:
            endpoint = f"/v1/tenants/{tenant_uuid}/{resource_path}/{federated_path}/summarize"
        method = "GET"
        
    elif action == "get_rule":
        if not resource_path or not policy_id:
            return {"error": "resource_path and policy_id are required for get_rule action"}
        
        endpoint = f"/v1/tenants/{tenant_uuid}/{resource_path}/{policy_id}"
        method = "GET"
        
    else:
        return {"error": f"Invalid action. Available actions: list_policies, get_policy, create_policy, update_policy, delete_policy, list_rules, get_rule"}
    
    return await make_api_request(concerto.url, endpoint, concerto.access_token, method=method, params=filters, body=rule_data)

@mcp.tool()
async def manage_tenant_resources(
    tenant_uuid: str,
    action: str,
    resource_path: Optional[str] = None,
    sub_type: Optional[str] = None,
    uuid: Optional[str] = None,
    federated_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Manage tenant-level resources and configurations
    
    Actions:
    - get_info: Get basic tenant information
    - list_files: List tenant files and folders
    - list_subprofiles: List tenant subprofiles by type
    - list_global_settings: List global settings by type
    - list_sites: List all sites
    - get_site: Get specific site by UUID
    - list_profiles: List profiles by type
    
    Resource Paths for Global Settings:
    - global-setting/b2bIpSec: B2B IPSec settings
    - global-setting/sdwan-profile: SD-WAN profile settings
    
    Subprofile Types:
    - Any subprofile type available in the system
    
    Profile Types:
    - profiles/basic: Basic profiles
    - profiles/standard: Standard profiles
    
    File Resources:
    - file/folder: File folders
    
    Site Resources:
    - sites: All sites
    - sites/{uuid}: Specific site by UUID
    
    Parameters:
    - tenant_uuid: Tenant UUID
    - action: Action to perform
    - resource_path: Path to resource for specific operations
    - sub_type: Subprofile type for subprofile operations
    - uuid: Site UUID for site-specific operations
    - federated_path: Federated path for hierarchical resources
    """
    
    if action == "get_info":
        endpoint = f"/v1/tenants/{tenant_uuid}"
        
    elif action == "list_files":
        endpoint = f"/v1/tenants/{tenant_uuid}/file/folder/summarize"
        
    elif action == "list_subprofiles":
        if not sub_type:
            return {"error": "sub_type is required for list_subprofiles action"}
        
        endpoint = f"/v1/tenants/{tenant_uuid}/subprofiles/{sub_type}/summarize"
        if federated_path:
            endpoint = f"/v1/tenants/{tenant_uuid}/subprofiles/{sub_type}/{federated_path}/summarize"
            
    elif action == "list_global_settings":
        if not resource_path:
            return {"error": "resource_path is required for list_global_settings action"}
        
        endpoint = f"/v1/tenants/{tenant_uuid}/{resource_path}/summarize"
        
    elif action == "list_sites":
        endpoint = f"/v1/tenants/{tenant_uuid}/sites/summarize"
        
    elif action == "get_site":
        if not uuid:
            return {"error": "uuid is required for get_site action"}
        
        endpoint = f"/v1/tenants/{tenant_uuid}/sites/{uuid}/summarize"
        
    elif action == "list_profiles":
        if not resource_path:
            return {"error": "resource_path is required for list_profiles action"}
        
        endpoint = f"/v1/tenants/{tenant_uuid}/{resource_path}/summarize"
        
    else:
        return {"error": f"Invalid action. Available actions: get_info, list_files, list_subprofiles, list_global_settings, list_sites, get_site, list_profiles"}
    
    return await make_api_request(concerto.url, endpoint, concerto.access_token)

app = Starlette(
    routes=[
        Mount('/', mcp.sse_app()),
    ]
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
