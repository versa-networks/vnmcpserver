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
from datetime import datetime
from dataclasses import dataclass, field

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

# ============================================================================
# SAC Models and Configuration
# ============================================================================

@dataclass
class SACConfig:
    """SAC application configuration"""
    concerto_url: str = os.environ['CONCERTO_URL'] 
    username: str = os.environ.get('CONCERTO_USERNAME', os.environ['VN_USERNAME'])
    password: str = os.environ.get('CONCERTO_PASSWORD', os.environ['VN_PASSWORD'])
    client_id: str = os.environ.get('VN_CONCERTO_CLIENT_ID', os.environ['VN_CLIENT_ID'])
    client_secret: str = os.environ.get('VN_CONCERTO_CLIENT_SECRET', os.environ['VN_CLIENT_SECRET'])
    
    # Default values
    default_os_versions: List[str] = field(default_factory=lambda: [
        "Windows 10", "Windows 11", "Windows 7", "Windows 8", "Windows Server 2019"
    ])

@dataclass
class AuthenticationContext:
    """Holds authentication state"""
    session: requests.Session
    headers: Dict[str, str]
    tenant_uuid: str = ""

@dataclass
class GatewayInfo:
    """Gateway information model"""
    uuid: str
    name: str
    vpn_name: str
    pool_details: List[Dict[str, Any]]
    labels: List[str] = field(default_factory=list)
    fqdn: str = ""
    wan_interfaces: List[Dict] = field(default_factory=list)
    vpn_infos: List[Dict] = field(default_factory=list)
    
    # Pool-specific fields
    pool_info_uuid: Optional[str] = None
    pool_name: Optional[str] = None
    pool_prefix: Optional[str] = None
    key: Optional[str] = None
    text: Optional[str] = None
    value: Optional[str] = None

@dataclass
class SACResources:
    """Container for all SAC resources. When asked display the relevant informations"""
    authentication_profiles: List[Dict[str, Any]]
    sase_gateways: List[Dict[str, Any]]
    sase_gateways_full: Dict[str, Any]
    scim_users: List[Dict[str, Any]]
    client_rules: List[Dict[str, Any]]
    client_rules_full: Dict[str, Any]
    eip_profiles: List[Dict[str, Any]]
    eip_agents: List[Dict[str, Any]]
    version_control: int

class Logger:
    """Simple logging utility"""
    @staticmethod
    def log(message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        prefix = {
            "INFO": "✅",
            "ERROR": "❌",
            "WARNING": "⚠️",
            "DEBUG": "🔍"
        }.get(level, "📝")
        print(f"[{timestamp}] {prefix} {message}")

concerto = Concerto(url=os.environ['CONCERTO_URL'], username=os.environ['VN_USERNAME'], password=os.environ['VN_PASSWORD'])
mcp = FastMCP(
    name="Concerto API Server with SAC Support", 
    instructions="This server provides optimized access to Versa Concerto APIs through logical groupings, including comprehensive Secure Access Client (SAC) rule management capabilities", 
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

# ============================================================================
# SAC API Client
# ============================================================================

class SACApiClient:
    """Handles all API interactions with the SAC system"""
    
    def __init__(self, config: SACConfig):
        self.config = config
        self._auth_context: Optional[AuthenticationContext] = None
        
    @property
    def auth_context(self) -> AuthenticationContext:
        """Get or create authentication context"""
        if not self._auth_context:
            self._auth_context = self._authenticate()
        return self._auth_context
        
    def _authenticate(self) -> AuthenticationContext:
        """Authenticate with the SAC API"""
        session = requests.Session()
        
        # Get CSRF token
        csrf_response = session.get(
            f"{self.config.concerto_url}/portalapi/swagger-ui.html", 
            verify=False
        )
        
        # Extract CSRF token using the same method as the working function
        cookies = session.cookies.get_dict()
        csrf_token = cookies.get("ECP-CSRF-TOKEN")
        if not csrf_token:
            raise ValueError("CSRF token not found")
            
        headers = {
            "accept": "application/json",
            "content-type": "application/x-www-form-urlencoded",
            "origin": self.config.concerto_url,
            "referer": f"{self.config.concerto_url}/portalapi/swagger-ui.html",
            "x-requested-with": "XMLHttpRequest",
            "X-CSRF-Token": csrf_token
        }
        
        # Login
        login_data = {
            "grant_type": "password",
            "scope": "global",
            "username": self.config.username,
            "password": self.config.password,
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret
        }
        
        # Fixed: Explicitly pass cookies in the POST request
        token_response = session.post(
            f"{self.config.concerto_url}/portalapi/v1/auth/token",
            headers=headers,
            cookies=session.cookies,  # <-- This was missing!
            data=login_data,
            verify=False
        )
        token_response.raise_for_status()
        
        access_token = token_response.json().get("access_token")
        headers["authorization"] = f"Bearer {access_token}"
        headers["accept-language"] = "en"
        
        Logger.log("Authentication successful")
        
        return AuthenticationContext(
            session=session,
            headers=headers
        )
    def get_tenant_uuid(self, tenant_name: str) -> str:
        """Get tenant UUID by name"""
        # Check if we already have it
        if self.auth_context.tenant_uuid:
            return self.auth_context.tenant_uuid
            
        url = f"{self.config.concerto_url}/portalapi/v1/tenants/tenant/name/{tenant_name}"
        response = self.auth_context.session.get(
            url, 
            headers=self.auth_context.headers, 
            verify=False
        )
        response.raise_for_status()
        
        uuid = response.json().get("tenantInfo", {}).get("uuid")
        self.auth_context.tenant_uuid = uuid
        Logger.log(f"Tenant UUID: {uuid}")
        return uuid
        
    def fetch_resource(self, url: str) -> Any:
        """Fetch a resource from the API"""
        response = self.auth_context.session.get(
            url,
            headers=self.auth_context.headers,
            verify=False
        )
        response.raise_for_status()
        return response.json()
        
    def post_resource(self, url: str, data: Dict[str, Any]) -> requests.Response:
        """Post data to the API"""
        headers = self.auth_context.headers.copy()
        headers["Content-Type"] = "application/json"
        
        response = self.auth_context.session.post(
            url,
            headers=headers,
            json=data,
            verify=False
        )
        return response
        
    def delete_resource(self, url: str) -> requests.Response:
        """Delete a resource"""
        return self.auth_context.session.delete(
            url,
            headers=self.auth_context.headers,
            verify=False
        )
        
    def reset_auth(self):
        """Reset authentication (force re-authentication on next request)"""
        self._auth_context = None

# ============================================================================
# SAC Resource Manager
# ============================================================================

class ResourceManager:
    """Manages fetching SAC resources"""
    
    def __init__(self, api_client: SACApiClient, config: SACConfig):
        self.api_client = api_client
        self.config = config
        
    def fetch_all_resources(self, tenant_name: str) -> SACResources:
        """Fetch all SAC resources and return as structured data"""
        tenant_uuid = self.api_client.get_tenant_uuid(tenant_name)
        
        # Fetch all resources in parallel (conceptually)
        resources = SACResources(
            authentication_profiles=self._fetch_authentication_profiles(tenant_uuid),
            sase_gateways=[], # Will be populated from full data
            sase_gateways_full=self._fetch_gateways_full(tenant_uuid),
            scim_users=self._fetch_scim_users(tenant_uuid),
            client_rules=[], # Will be populated from full data
            client_rules_full=self._fetch_client_rules_full(tenant_uuid),
            eip_profiles=self._fetch_eip_profiles(tenant_uuid),
            eip_agents=self._fetch_eip_agents(tenant_uuid),
            version_control=0 # Will be set from client rules
        )
        
        # Extract simplified data from full responses
        resources.sase_gateways = self._extract_gateways(resources.sase_gateways_full)
        rules_data = self._extract_client_rules(resources.client_rules_full)
        resources.client_rules = rules_data["rules"]
        resources.version_control = rules_data["version_control"]
        
        return resources
        
    def _fetch_authentication_profiles(self, tenant_uuid: str) -> List[Dict[str, Any]]:
        """Fetch authentication profiles"""
        url = f"{self.config.concerto_url}/portalapi/v1/tenants/{tenant_uuid}/sase/secure-access-client/summarize/profile?nextWindowNumber=0&windowSize=2147483647"
        data = self.api_client.fetch_resource(url)
        return self._extract_name_uuid_items(data)
        
    def _fetch_gateways_full(self, tenant_uuid: str) -> Dict[str, Any]:
        """Fetch full gateway data"""
        url = f"{self.config.concerto_url}/portalapi/v1/tenants/{tenant_uuid}/regions/sasegateways"
        return self.api_client.fetch_resource(url)
        
    def _fetch_scim_users(self, tenant_uuid: str) -> List[Dict[str, Any]]:
        """Fetch SCIM users and display the available users when asked by user"""
        url = f"{self.config.concerto_url}/portalapi/v1/tenants/{tenant_uuid}/sase/scim/summarize?global=&include-user-group=true"
        data = self.api_client.fetch_resource(url)
        
        users = []
        for entry in data.get("data", []):
            for user in entry.get("users", []):
                users.append({
                    "user_name": user.get("user_name"),
                    "display_name": user.get("display_name"),
                    "email": user.get("email")
                })
        return users
        
    def _fetch_client_rules_full(self, tenant_uuid: str) -> Dict[str, Any]:
        """Fetch full client rules data"""
        url = f"{self.config.concerto_url}/portalapi/v1/tenants/{tenant_uuid}/sase/secure-access-client/summarize/rule?nextWindowNumber=0&windowSize=2147483647"
        return self.api_client.fetch_resource(url)
        
    def _fetch_eip_profiles(self, tenant_uuid: str) -> List[Dict[str, Any]]:
        """Fetch all EIP profiles and display for the user to choose when asked. Try to filter as well."""
        url = f"{self.config.concerto_url}/portalapi/v1/tenants/{tenant_uuid}/director-mapping/eip-profile?nextWindowNumber=0&windowSize=2147483647"
        data = self.api_client.fetch_resource(url)
        return self._extract_name_uuid_items(data)
        
    def _fetch_eip_agents(self, tenant_uuid: str) -> List[Dict[str, Any]]:
        """Fetch all EIP agents"""
        url = f"{self.config.concerto_url}/portalapi/v1/tenants/{tenant_uuid}/director-mapping/eip-agent?nextWindowNumber=0&windowSize=2147483647"
        data = self.api_client.fetch_resource(url)
        return self._extract_name_uuid_items(data)
        
    def _extract_name_uuid_items(self, data: Any) -> List[Dict[str, str]]:
        """Extract items with name and uuid from response data"""
        items = data if isinstance(data, list) else data.get("data", [])
        return [
            {"name": item.get("name"), "uuid": item.get("uuid")}
            for item in items
            if item.get("name") and item.get("uuid")
        ]
        
    def _extract_gateways(self, gateways_full: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract gateway names and UUIDs from full data"""
        gateways = []
        for region in gateways_full.get("data", []):
            for gateway in region.get("saseGatewayInfos", []):
                gateways.append({
                    "gatewayName": gateway.get("gatewayName"),
                    "gatewayUUID": gateway.get("gatewayUUID")
                })
        return gateways
        
    def _extract_client_rules(self, rules_full: Dict[str, Any]) -> Dict[str, Any]:
        """Extract client rules and version control from full data"""
        rules = [
            {"name": rule.get("name"), "uuid": rule.get("uuid")}
            for rule in rules_full.get("data", [])
            if rule.get("name") and rule.get("uuid")
        ]
        
        version_control = rules_full.get("versionControl", 0)
        
        return {
            "rules": rules,
            "version_control": version_control
        }

# ============================================================================
# SAC Rule Builder
# ============================================================================

class SACRuleBuilder:
    """Builds SAC rule payloads"""
    
    def __init__(self, config: SACConfig):
        self.config = config
        
    def build_rule(
        self,
        resources: SACResources,
        rule_name: str,
        selected_users: Optional[List[str]] = None,
        selected_os: Optional[List[str]] = None,
        add_eip: bool = False,
        eip_agent_name: Optional[str] = None,
        eip_profile_names: Optional[List[str]] = None,
        place_rule_top: bool = True
    ) -> Dict[str, Any]:
        """Build a SAC rule payload"""
        
        # Set defaults
        if not selected_users:
            selected_users = [user["user_name"] for user in resources.scim_users]
        if not selected_os:
            selected_os = self.config.default_os_versions
            
        # Build gateway infos
        gateway_infos = self._build_gateway_infos(
            resources.sase_gateways, 
            resources.sase_gateways_full
        )
        if not gateway_infos:
            raise ValueError("No valid gateways found")
            
        # Build payload
        payload = self._create_base_payload(
            rule_name=rule_name,
            sac_profile_uuid=resources.authentication_profiles[0]["uuid"],
            gateway_infos=gateway_infos,
            vpn_name=gateway_infos[0]["vpnName"],
            selected_users=selected_users,
            selected_os=selected_os,
            scim_users=resources.scim_users,
            version_control=resources.version_control,
            place_rule_top=place_rule_top
        )
        
        # Add EIP if requested
        if add_eip:
            self._add_eip_config(
                payload, 
                eip_agent_name, 
                eip_profile_names,
                resources.eip_agents,
                resources.eip_profiles
            )
            
        return payload
        
    def _build_gateway_infos(
        self, 
        gateways: List[Dict], 
        gateways_full: Dict
    ) -> List[Dict[str, Any]]:
        """Build gateway information objects"""
        gateway_infos = []
        
        for gateway in gateways:
            gateway_name = gateway["gatewayName"]
            
            # Find full gateway info
            for region in gateways_full.get("data", []):
                for gw_info in region.get("saseGatewayInfos", []):
                    if gw_info.get("gatewayName") == gateway_name:
                        gateway_info = self._create_gateway_info(gw_info)
                        gateway_infos.append(gateway_info)
                        break
                        
        return gateway_infos
        
    def _create_gateway_info(self, gw_data: Dict) -> Dict[str, Any]:
        """Create gateway info dict from raw data"""
        vpn_info = gw_data.get("vpnInfos", [{}])[0]
        vpn_name = vpn_info.get("vpnName", "")
        pools = vpn_info.get("tenantSaseGatewayVPNClientPoolInfos", [])
        
        gateway_info = {
            "gatewayUUID": gw_data.get("gatewayUUID"),
            "gatewayName": gw_data.get("gatewayName"),
            "vpnName": vpn_name,
            "poolDetails": [
                {
                    "poolName": pool.get("poolName"),
                    "poolPrefix": pool.get("poolPrefix"),
                    "poolInfoUUID": pool.get("poolInfoUUID")
                }
                for pool in pools
            ] if pools else [],
            "gatewayLabels": gw_data.get("gatewayLabels", []),
            "gwFQDN": gw_data.get("gwFQDN", ""),
            "wanInterfaces": gw_data.get("wanInterfaces", []),
            "vpnInfos": gw_data.get("vpnInfos", [])
        }
        
        # Add pool-specific fields if pools exist
        if pools:
            first_pool = pools[0]
            gateway_info.update({
                "poolInfoUUID": first_pool.get("poolInfoUUID"),
                "poolName": first_pool.get("poolName"),
                "poolPrefix": first_pool.get("poolPrefix"),
                "key": f"{first_pool.get('poolPrefix')}-{first_pool.get('poolName')}",
                "text": f"{first_pool.get('poolPrefix')}-{first_pool.get('poolName')}",
                "value": first_pool.get("poolPrefix")
            })
            
        return gateway_info
    def _build_gateway_groups(self, gateway_infos: List[Dict]) -> List[str]:
        """Build gateway groups from actual gateway labels"""
        gateway_groups = set()
        
        # Extract labels from all gateways
        for gateway_info in gateway_infos:
            labels = gateway_info.get("gatewayLabels", [])
            if labels:
                # Handle different label formats that might be returned by the API
                for label in labels:
                    if isinstance(label, str):
                        gateway_groups.add(label)
                    elif isinstance(label, dict):
                        # If labels are objects, extract relevant fields
                        label_name = label.get("name") or label.get("label") or label.get("value")
                        if label_name:
                            gateway_groups.add(label_name)
        
        # Return as sorted list for consistency
        return sorted(list(gateway_groups))        
    def _create_base_payload(
        self,
        rule_name: str,
        sac_profile_uuid: str,
        gateway_infos: List[Dict],
        vpn_name: str,
        selected_users: List[str],
        selected_os: List[str],
        scim_users: List[Dict],
        version_control: int,
        place_rule_top: bool
    ) -> Dict[str, Any]:
        gateway_groups = self._build_gateway_groups(gateway_infos)
        """Create base rule payload"""
        return {
            "name": rule_name,
            "version": "1",
            "attributes": {
                "action": {
                    "value": {
                        "clientConfiguration": {
                            "clientControl": {
                                "passwordExpiryWarnBefore": 10,
                                "portalLifetime": 1440,
                                "maxiumNumber": 10,
                                "alwaysOn": True,
                                "displayGateway": True,
                                "allowClientCustomization": True,
                                "rememberCredentials": True,
                                "alwaysOnDetail": {
                                    "disconnect": "Interval",
                                    "intervalValue": 300,
                                    "overrideEnabled": True,
                                    "override": 120,
                                    "fail": "Open"
                                },
                                "tunnelMonitoringDetail": {
                                    "interval": 60,
                                    "intervalRetry": 10,
                                    "connectionRetry": 5
                                },
                                "reconnectDetail": {
                                    "interval": 10,
                                    "retry-count": 5
                                }
                            },
                            "mfa": {"enabled": False},
                            "vpnType": {"ipSec": True, "protocolOrder": ["IPSEC"]},
                            "profileUuid": sac_profile_uuid
                        },
                        "gateway": {
                            "gatewayInfos": gateway_infos,
                            "gatewayGroups": gateway_groups,
                            "vpnName": vpn_name
                        },
                        "trafficSteering": {
                            "subscription": "vsa-swg",
                            "action": "force-tunnel",
                            "actionMessage": f"Welcome to {rule_name}"
                        }
                    }
                },
                "match": {
                    "value": {
                        "sourceEndpoint": {
                            "operatingSystems": [
                                {"operatingSystem": "Windows", "operatingVersion": selected_os}
                            ]
                        },
                        "users": {
                            "users": [
                                {
                                    "name": next(
                                        (u["display_name"] for u in scim_users if u["user_name"] == user),
                                        user
                                    ),
                                    "id": user,
                                    "description": "testing"
                                }
                                for user in selected_users
                            ],
                            "profile": {
                                "type": "SASE_SCIM_AUTHENTICATION",
                                "subtype": "SASE_SCIM_AUTHENTICATION"
                            },
                            "userMatchType": "selected"
                        },
                        "deviceStatus": {"type": "all-devices"},
                        "sourceAddress": {"addressNegate": False}
                    }
                }
            },
            "initialFormMode": "CREATE",
            "enabled": True,
            "order": {"top": place_rule_top} if place_rule_top else {"bottom": True},
            "subtype": "RULE",
            "type": "CLIENT_ACCESS",
            "formMode": "CREATE",
            "deploy": False,
            "versionControl": version_control
        }
        
    def _add_eip_config(
        self,
        payload: Dict[str, Any],
        eip_agent_name: Optional[str],
        eip_profile_names: Optional[List[str]],
        eip_agents: List[Dict[str, str]],
        eip_profiles: List[Dict[str, str]]
    ) -> None:
        """Add EIP configuration to payload"""
        if eip_agent_name:
            agent = next(
                (a for a in eip_agents if a["name"] == eip_agent_name),
                None
            )
            if not agent:
                raise ValueError(f"EIP Agent '{eip_agent_name}' not found")
                
            payload["attributes"]["action"]["value"]["eip"] = {
                "type": "predefined",
                "uuid": agent["uuid"],
                "name": agent["name"]
            }
            
        if eip_profile_names:
            matched_profiles = []
            
            for profile_name in eip_profile_names:
                profile = next(
                    (p for p in eip_profiles if p["name"] == profile_name),
                    None
                )
                if not profile:
                    raise ValueError(f"EIP Profile '{profile_name}' not found")
                    
                matched_profiles.append({
                    "uuid": profile["uuid"],
                    "name": profile["name"]
                })
                
            payload["attributes"]["match"]["value"]["eip"] = {
                "predefined": matched_profiles
            }

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

# ============================================================================
# SAC MCP Tools Setup
# ============================================================================

# Initialize SAC components
sac_config = SACConfig()
sac_api_client = SACApiClient(sac_config)
sac_resource_manager = ResourceManager(sac_api_client, sac_config)
sac_rule_builder = SACRuleBuilder(sac_config)

@mcp.tool()
async def fetch_sac_resources(tenant_name: str) -> Dict[str, Any]:
    """Fetch and display current SAC resources"""
    try:
        resources = sac_resource_manager.fetch_all_resources(tenant_name)
        
        return {
            "status": "success",
            "data": {
                "authentication_profiles": {
                    "count": len(resources.authentication_profiles),
                    "profiles": resources.authentication_profiles
                },
                "gateways": {
                    "count": len(resources.sase_gateways),
                    "gateways": resources.sase_gateways
                },
                "scim_users": {
                    "count": len(resources.scim_users),
                    "users": resources.scim_users
                },
                "client_rules": {
                    "count": len(resources.client_rules),
                    "rules": resources.client_rules
                },
                "eip_profiles": {
                    "count": len(resources.eip_profiles),
                    "profiles": resources.eip_profiles  # This will show all EIP profiles with names & UUIDs
                },
                "eip_agents": {
                    "count": len(resources.eip_agents),
                    "agents": resources.eip_agents      # This will show all EIP agents with names & UUIDs
                },
                "version_control": resources.version_control
            }
        }
    except Exception as e:
        Logger.log(f"Error fetching resources: {str(e)}", "ERROR")
        return {"status": "error", "message": str(e)}

@mcp.tool()
async def configure_sac_rule_default(
    tenant_name: str, 
    rule_name: str
) -> Dict[str, Any]:
    """Configure SAC Rule using ALL SCIM users and default Windows OS versions"""
    return await configure_sac_rule_custom(
        tenant_name=tenant_name,
        rule_name=rule_name,
        selected_usernames=[],
        selected_operating_systems=[]
    )

@mcp.tool()
async def configure_sac_rule_custom(
    tenant_name: str,
    rule_name: str,
    selected_usernames: List[str],
    selected_operating_systems: List[str],
    place_rule_top: bool = True
) -> Dict[str, Any]:
    """Configure SAC Rule with specific users and operating systems"""
    try:
        # Fetch all resources
        resources = sac_resource_manager.fetch_all_resources(tenant_name)
        
        # Build rule
        payload = sac_rule_builder.build_rule(
            resources=resources,
            rule_name=rule_name,
            selected_users=selected_usernames if selected_usernames else None,
            selected_os=selected_operating_systems if selected_operating_systems else None,
            place_rule_top=place_rule_top
        )
        
        # Post rule
        return await _post_sac_rule(payload)
        
    except Exception as e:
        Logger.log(f"Error configuring rule: {str(e)}", "ERROR")
        return {"status": "error", "message": str(e)}

@mcp.tool()
async def configure_sac_rule_with_eip(
    tenant_name: str,
    rule_name: str,
    add_eip_config: bool = False,
    selected_eip_agent_name: str = "",
    selected_eip_profile_names: str = "",
    selected_scim_usernames: str = "",
    selected_os_versions: str = "",
    place_rule_top: bool = True
) -> Dict[str, Any]:
    """Build SAC rule payload with optional EIP configs"""
    try:
        # Parse comma-separated strings
        users = [u.strip() for u in selected_scim_usernames.split(",") if u.strip()] if selected_scim_usernames else []
        os_versions = [o.strip() for o in selected_os_versions.split(",") if o.strip()] if selected_os_versions else []
        eip_profiles = [p.strip() for p in selected_eip_profile_names.split(",") if p.strip()] if selected_eip_profile_names else []
        
        # Fetch all resources
        resources = sac_resource_manager.fetch_all_resources(tenant_name)
        
        # Build rule
        payload = sac_rule_builder.build_rule(
            resources=resources,
            rule_name=rule_name,
            selected_users=users if users else None,
            selected_os=os_versions if os_versions else None,
            add_eip=add_eip_config,
            eip_agent_name=selected_eip_agent_name if selected_eip_agent_name else None,
            eip_profile_names=eip_profiles if eip_profiles else None,
            place_rule_top=place_rule_top
        )
        
        # Post rule
        return await _post_sac_rule(payload)
        
    except Exception as e:
        Logger.log(f"Error configuring rule with EIP: {str(e)}", "ERROR")
        return {"status": "error", "message": str(e)}

@mcp.tool()
async def delete_sac_rules(
    tenant_name: str,
    rule_names: str
) -> Dict[str, Any]:
    """Delete one or more SAC rules based on names (comma-separated)"""
    try:
        # Fetch current resources
        resources = sac_resource_manager.fetch_all_resources(tenant_name)
        
        # Parse rule names
        rule_list = [r.strip() for r in rule_names.split(",") if r.strip()]
        
        # Determine rules to delete
        if "all" in [r.lower() for r in rule_list]:
            rules_to_delete = resources.client_rules
        else:
            rules_to_delete = [r for r in resources.client_rules if r["name"] in rule_list]
            
        if not rules_to_delete:
            return {"status": "error", "message": "No matching rules found to delete"}
            
        # Delete rules
        deletion_results = []
        for rule in rules_to_delete:
            result = await _delete_single_sac_rule(rule)
            deletion_results.append(result)
            
        return {"status": "completed", "results": deletion_results}
        
    except Exception as e:
        Logger.log(f"Error deleting rules: {str(e)}", "ERROR")
        return {"status": "error", "message": str(e)}

async def _post_sac_rule(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Post a SAC rule to the API"""
    try:
        url = f"{sac_config.concerto_url}/portalapi/v1/tenants/{sac_api_client.auth_context.tenant_uuid}/sase/secure-access-client/rule"
        response = sac_api_client.post_resource(url, payload)
        response.raise_for_status()
        
        Logger.log("Rule posted successfully")
        return {"status": "success", "response": response.json()}
        
    except requests.exceptions.HTTPError as e:
        Logger.log(f"HTTP Error posting rule: {str(e)}", "ERROR")
        try:
            return {"status": "error", "message": response.json()}
        except:
            return {"status": "error", "message": response.text}
            
    except Exception as e:
        Logger.log(f"Error posting rule: {str(e)}", "ERROR")
        return {"status": "error", "message": str(e)}

async def _delete_single_sac_rule(rule: Dict[str, str]) -> Dict[str, Any]:
    """Delete a single SAC rule"""
    try:
        url = f"{sac_config.concerto_url}/portalapi/v1/tenants/{sac_api_client.auth_context.tenant_uuid}/sase/secure-access-client/{rule['uuid']}"
        response = sac_api_client.delete_resource(url)
        
        if response.status_code == 200:
            Logger.log(f"Deleted rule '{rule['name']}' successfully")
            return {"rule": rule["name"], "status": "deleted"}
        else:
            return {
                "rule": rule["name"],
                "status": "error",
                "details": f"Status Code: {response.status_code} - {response.text}"
            }
            
    except Exception as e:
        return {
            "rule": rule["name"],
            "status": "error",
            "details": str(e)
        }

app = Starlette(
    routes=[
        Mount('/', mcp.sse_app()),
    ]
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
