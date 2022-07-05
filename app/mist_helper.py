"""SRX configuration helper class."""
# pylint: disable=inconsistent-return-statements

# Standard library
from typing import List, Optional, Any
import json

# Third Party
from pydantic import BaseModel
from jinja2 import Environment, FileSystemLoader
import requests


# -----------------------------------------------------------------------------
# Jinja2 parameters
# -----------------------------------------------------------------------------
file_loader = FileSystemLoader("templates")
env = Environment(loader=file_loader)
env.trim_blocks = True
env.lstrip_blocks = True
env.rstrip_blocks = True


# -----------------------------------------------------------------------------
# Marvis Issues data modeling: Connectivity Issues
# -----------------------------------------------------------------------------
class AuthFailures(BaseModel):
    """Marvis Connectivity Issues: Auth Failures."""

    scope: int
    wlan: Optional[int] = 0
    radius: Optional[int] = 0
    total: Optional[int] = 0


class DhcpFailures(BaseModel):
    """Marvis Connectivity Issues: DHCP Failures."""

    scope: int
    MARVIS_EVENT_CLIENT_DHCP_FAILURE: Optional[int] = 0
    dhcp: Optional[int] = 0
    total: Optional[int] = 0


class ArpFailures(BaseModel):
    """Marvis Connectivity Issues: ARP Failures."""

    scope: int
    CLIENT_GW_ARP_FAILURE: Optional[int] = 0
    total: Optional[int] = 0


class DnsFailures(BaseModel):
    """Marvis Connectivity Issues: DNS Failures."""

    scope: int
    MARVIS_DNS_FAILURE: Optional[int] = 0
    dns: Optional[int] = 0
    total: Optional[int] = 0


class Connectivity(BaseModel):
    """Mapping out object."""

    auth_failure: AuthFailures
    dhcp_failure: DhcpFailures
    arp_failure: ArpFailures
    dns_failure: DnsFailures


# -----------------------------------------------------------------------------
# Marvis Issues data modeling: AP Issues
# -----------------------------------------------------------------------------
class ApDisconnect(BaseModel):
    """Marvis Connectivity Issues: DNS Failures."""

    ap: Optional[int] = 0
    switch: Optional[int] = 0


class EthernetError(BaseModel):
    """Marvis Connectivity Issues: DNS Failures."""

    ap: Optional[int] = 0


class HealthCheck(BaseModel):
    """Marvis Connectivity Issues: DNS Failures."""

    ap: Optional[int] = 0


class Capacity(BaseModel):
    """Marvis Connectivity Issues: DNS Failures."""

    ap: Optional[int] = 0


class Coverage(BaseModel):
    """Marvis Connectivity Issues: DNS Failures."""

    ap: Optional[int] = 0


class AccessPoint(BaseModel):
    """Helper for interacting with the Mist API."""

    ap_disconnect: ApDisconnect
    ethernet_error: EthernetError
    health_check: HealthCheck
    insufficient_capacity: Capacity
    insufficient_coverage: Coverage


# -----------------------------------------------------------------------------
# Marvis Issues data modeling: Switch Issues
# -----------------------------------------------------------------------------
class BadCable(BaseModel):
    """Marvis Connectivity Issues: DNS Failures."""

    interface: Optional[int] = 0


class MissingVlan(BaseModel):
    """Marvis Connectivity Issues: DNS Failures."""

    switch: Optional[int] = 0


class DuplexMismatch(BaseModel):
    """Marvis Connectivity Issues: DNS Failures."""

    interface: Optional[int] = 0


class PortFlapping(BaseModel):
    """Marvis Connectivity Issues: DNS Failures."""

    interface: Optional[int] = 0


class SpanningTreeLoop(BaseModel):
    """Marvis Connectivity Issues: DNS Failures."""

    site: Optional[int] = 0


class Switch(BaseModel):
    """Helper for interacting with the Mist API."""

    bad_cable: BadCable
    missing_vlan: MissingVlan
    negotiation_mismatch: DuplexMismatch
    port_flap: PortFlapping
    stp_loop: SpanningTreeLoop


# -----------------------------------------------------------------------------
# Marvis Issues data modeling: Gateway Issues
# -----------------------------------------------------------------------------
class BadWanLink(BaseModel):
    """Marvis Connectivity Issues: DNS Failures."""

    interface: Optional[int] = 0


class BadCable(BaseModel):
    """Marvis Connectivity Issues: DNS Failures."""

    interface: Optional[int] = 0
    ap: Optional[int] = 0


class VpnPathDown(BaseModel):
    """Marvis Connectivity Issues: DNS Failures."""

    interface: Optional[int] = 0


class Gateway(BaseModel):
    """Helper for interacting with the Mist API."""

    bad_wan_link: BadWanLink
    bad_cable: BadCable
    vpn_path_down: VpnPathDown


# -----------------------------------------------------------------------------
# Marvis Issues data modeling: Layer1 Issues
# -----------------------------------------------------------------------------
class Layer1(BaseModel):
    """Helper for interacting with the Mist API."""

    bad_cable: Optional[BadCable] = 0


# -----------------------------------------------------------------------------
# Marvis Issues object
# -----------------------------------------------------------------------------
class MarvisIssues(BaseModel):
    """Helping structure an object to hold issues from Marvis."""

    connectivity: Optional[Connectivity] = None
    ap: Optional[AccessPoint] = None
    switch: Optional[Switch] = None
    gateway: Optional[Gateway] = None
    layer_1: Optional[Layer1] = None

    def __init__(self, **data: Any):
        """
        Here we manipulate pydandic's BaseModel auto-generated __init__ method.
          - run our connectivity issues through the `_total_count()` function.
          - create new objects to hold the return value.
          - update the object with the correct counter.
        """

        super().__init__(**data)

        # ---------------------------------------------------------------------
        # Creating a 'total' by adding the values of our dictionary k/v pairs
        # ---------------------------------------------------------------------
        self.connectivity.arp_failure.total = self._total_count(
            self.connectivity.arp_failure.dict()
        )
        self.connectivity.auth_failure.total = self._total_count(
            self.connectivity.auth_failure.dict()
        )
        self.connectivity.dhcp_failure.total = self._total_count(
            self.connectivity.dhcp_failure.dict()
        )
        self.connectivity.dns_failure.total = self._total_count(
            self.connectivity.dns_failure.dict()
        )

    def _total_count(self, payload):
        """Loop over a dictionary and add the value of its k/v pairs."""
        total = 0
        for key, value in payload.items():
            total = total + value

        return total


# -----------------------------------------------------------------------------
# Site Alerts object
# -----------------------------------------------------------------------------
class Results(BaseModel):
    """Helping structure an object to hold alerts from a site."""

    aps: Optional[List[str]] = []
    bssids: Optional[List[str]] = []
    client_count: Optional[int] = 0
    count: int
    group: str
    hostnames: List[str]
    id: str
    incident_count: Optional[int] = 0
    last_seen: int
    macs: Optional[List[str]] = []
    org_id: str
    reasons: Optional[List[str]] = []
    servers: Optional[List[str]] = []
    severity: str
    site_id: str
    switches: Optional[List[str]] = []
    ssids: Optional[List[str]] = []
    timestamp: int
    type: str
    vlans: Optional[List[int]] = []


class SiteAlerts(BaseModel):
    """Helping structure an object to hold alerts from a site."""

    results: List[Results] = None
    start: Optional[int] = None
    end: Optional[int] = None
    limit: Optional[int] = None
    total: Optional[int] = None


# -----------------------------------------------------------------------------
# Mist API helper object
# -----------------------------------------------------------------------------
class MistApi(BaseModel):
    """Helping structure an object to hold issues from Marvis."""

    api_token: str
    baseurl: Optional[str] = "api.mist.com/api/v1"
    headers: Optional[dict] = {}
    path: Optional[str] = "self"

    def __init__(self, **data: Any):
        """
        Here we manipulate pydandic's BaseModel auto-generated __init__ method.
          - create json payload based on data stored in YAML config file
        """

        super().__init__(**data)

        self.baseurl = f"https://{self.baseurl}"

        self.headers = {
            "Accept": "*/*",
            "Authorization": f"Token {self.api_token}",
            "Content-Type": "application/json",
        }

    def _path_strip(self, path):
        """Strip off leading / within the url path and return full url."""

        if path[0] == "/":
            path = path[1:]

        return f"{self.baseurl}/{path}"

    def send(self, method, path, headers, data=None):
        """Build the URL, handle the response of API calls."""

        url = self._path_strip(path)

        response = requests.request(
            method,
            url,
            headers=headers,
            data=json.dumps(data),
        )
        response.raise_for_status()

        return response.json()

    def get(self):
        """HTTP GET method."""
        return self.send("GET", self.path, self.headers)

    def put(self, path, headers, data=None):
        """HTTP PUT method."""
        return self.send("PUT", path, headers, data)

    def post(self, path, headers, data=None):
        """HTTP POST method."""
        return self.send("POST", path, headers, data)

    def delete(self, path, headers, data=None):
        """HTTP DELETE method."""
        return self.send("DELETE", path, headers, data)

    def template(self, payload, template_file):
        """Template our message to slack."""
        template = env.get_template(template_file)
        message = template.render(data=payload)

        return message
