# agents/network_agent.py
"""
Network Machine Usage Agent - Monitors devices connected to the switch via IP address
Provides SNMP querying, ARP scanning, and network performance metrics
"""

import os
import socket
import subprocess
import json
import re
import time
import logging
import requests
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

# Try importing optional network libraries
try:
    from pysnmp.hlapi import *
    SNMP_AVAILABLE = True
except ImportError:
    SNMP_AVAILABLE = False

try:
    import nmap
    NMAP_AVAILABLE = True
except ImportError:
    NMAP_AVAILABLE = False

logger = logging.getLogger(__name__)

# =========================================================================
# 🔀 NETWORK CONFIGURATION
# =========================================================================
CENTRAL_API_URL = os.environ.get('CENTRAL_API_URL', 'http://localhost:8000/api/network-devices/')
NETWORK_GATEWAY = os.environ.get('NETWORK_GATEWAY', '192.168.1.1')
NETWORK_SUBNET = os.environ.get('NETWORK_SUBNET', '192.168.1.0/24')
SNMP_COMMUNITY = os.environ.get('SNMP_COMMUNITY', 'public')
POLL_INTERVAL = int(os.environ.get('POLL_INTERVAL', 1800))  # 30 minutes
# =========================================================================

@dataclass
class NetworkDevice:
    """Represents a network device discovered on the switch"""
    ip_address: str
    mac_address: str
    hostname: Optional[str] = None
    device_type: Optional[str] = None  # router, printer, computer, etc.
    vendor: Optional[str] = None
    last_seen: str = None
    online: bool = True

@dataclass
class NetworkMetrics:
    """Network performance metrics for a device"""
    ip_address: str
    device_name: str
    cpu_usage_pct: float = -1.0
    memory_usage_pct: float = -1.0
    disk_usage_pct: float = -1.0
    network_in_mbps: float = -1.0
    network_out_mbps: float = -1.0
    ping_ms: float = -1.0
    timestamp: str = None

    def to_dict(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
        return asdict(self)


class NetworkScanner:
    """Scans network for connected devices and retrieves metrics"""
    
    def __init__(self, gateway: str = None, subnet: str = None):
        self.gateway = gateway or NETWORK_GATEWAY
        self.subnet = subnet or NETWORK_SUBNET
        self.devices: Dict[str, NetworkDevice] = {}
    
    def arp_scan(self) -> List[NetworkDevice]:
        """Perform ARP scan to discover devices on the network"""
        devices = []
        
        try:
            if os.name == 'nt':  # Windows
                result = subprocess.run(
                    ['arp', '-a'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                lines = result.stdout.split('\n')
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 2 and self._is_valid_ip(parts[0]):
                        device = NetworkDevice(
                            ip_address=parts[0],
                            mac_address=parts[1] if len(parts) > 1 else 'unknown',
                            last_seen=datetime.now().isoformat()
                        )
                        devices.append(device)
            else:  # Linux/macOS
                result = subprocess.run(
                    ['arp', '-a'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                pattern = r'\((\d+\.\d+\.\d+\.\d+)\).*?([\da-f:]{17})'
                for match in re.finditer(pattern, result.stdout):
                    device = NetworkDevice(
                        ip_address=match.group(1),
                        mac_address=match.group(2),
                        last_seen=datetime.now().isoformat()
                    )
                    devices.append(device)
        except Exception as e:
            logger.error(f"ARP scan failed: {e}")
        
        return devices
    
    @staticmethod
    def _is_valid_ip(ip: str) -> bool:
        """Validate IP address format"""
        try:
            socket.inet_aton(ip)
            return True
        except socket.error:
            return False
    
    def resolve_hostname(self, ip: str) -> Optional[str]:
        """Attempt reverse DNS lookup for IP address"""
        try:
            return socket.gethostbyaddr(ip)[0]
        except Exception:
            return None
    
    def ping_device(self, ip: str) -> float:
        """Ping device and return response time in ms"""
        try:
            if os.name == 'nt':
                result = subprocess.run(
                    ['ping', '-n', '1', ip],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                match = re.search(r'time[<=](\d+)ms', result.stdout)
                if match:
                    return float(match.group(1))
            else:
                result = subprocess.run(
                    ['ping', '-c', '1', ip],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                match = re.search(r'time=(\d+(?:\.\d+)?)\s*ms', result.stdout)
                if match:
                    return float(match.group(1))
        except Exception as e:
            logger.debug(f"Ping failed for {ip}: {e}")
        
        return -1.0
    
    def snmp_query(self, ip: str) -> Optional[NetworkMetrics]:
        """Query device via SNMP for system metrics"""
        if not SNMP_AVAILABLE:
            return None
        
        try:
            metrics = NetworkMetrics(
                ip_address=ip,
                device_name=self.resolve_hostname(ip) or ip,
                timestamp=datetime.now().isoformat()
            )
            
            # OID for system uptime
            errorIndication, errorStatus, errorIndex, varBinds = next(
                getCmd(SnmpEngine(),
                       CommunityData(SNMP_COMMUNITY),
                       UdpTransportTarget((ip, 161), timeout=3, retries=1),
                       ContextData(),
                       ObjectType(ObjectIdentity('1.3.6.1.2.1.1.1.0')))
            )
            
            if not errorIndication:
                metrics.ping_ms = 0  # If SNMP works, device is up
                return metrics
        except Exception as e:
            logger.debug(f"SNMP query failed for {ip}: {e}")
        
        return None
    
    def scan_and_collect_metrics(self) -> Tuple[List[NetworkDevice], List[NetworkMetrics]]:
        """Main scanning routine - discovers devices and collects metrics"""
        print(f"\n{'='*60}")
        print(f"🌐 NETWORK SCAN STARTED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        devices = self.arp_scan()
        metrics_list = []
        
        for device in devices:
            print(f"🔍 Scanning {device.ip_address}...", end=' ')
            
            # Enrich device info
            device.hostname = self.resolve_hostname(device.ip_address)
            ping_time = self.ping_device(device.ip_address)
            
            if ping_time >= 0:
                print(f"✅ Online ({ping_time:.1f}ms)")
                device.online = True
                
                # Create metrics entry
                metrics = NetworkMetrics(
                    ip_address=device.ip_address,
                    device_name=device.hostname or device.ip_address,
                    ping_ms=ping_time,
                    timestamp=datetime.now().isoformat()
                )
                
                # Try SNMP query
                snmp_metrics = self.snmp_query(device.ip_address)
                if snmp_metrics:
                    metrics.cpu_usage_pct = snmp_metrics.cpu_usage_pct
                    metrics.memory_usage_pct = snmp_metrics.memory_usage_pct
                
                metrics_list.append(metrics)
            else:
                print(f"❌ Offline")
                device.online = False
            
            time.sleep(0.5)  # Rate limiting
        
        print(f"\n{'='*60}")
        print(f"📊 SCAN COMPLETE: Found {len(devices)} devices")
        print(f"{'='*60}\n")
        
        return devices, metrics_list


class NetworkReporter:
    """Reports network scan results to central API"""
    
    def __init__(self, api_url: str = None):
        self.api_url = api_url or CENTRAL_API_URL
    
    def send_devices(self, devices: List[NetworkDevice]) -> bool:
        """Send discovered devices to central API"""
        try:
            payload = {
                "devices": [asdict(d) for d in devices],
                "timestamp": datetime.now().isoformat(),
                "scan_type": "arp"
            }
            
            response = requests.post(
                f"{self.api_url}discover/",
                json=payload,
                timeout=15
            )
            
            print(f"[{datetime.now().strftime('%X')}] Sent {len(devices)} devices. Status: {response.status_code}")
            return response.status_code == 201
        except Exception as e:
            logger.error(f"Failed to send devices: {e}")
            return False
    
    def send_metrics(self, metrics_list: List[NetworkMetrics]) -> bool:
        """Send metrics to central API"""
        try:
            payload = {
                "metrics": [m.to_dict() for m in metrics_list],
                "timestamp": datetime.now().isoformat()
            }
            
            response = requests.post(
                f"{self.api_url}metrics/",
                json=payload,
                timeout=15
            )
            
            print(f"[{datetime.now().strftime('%X')}] Sent {len(metrics_list)} metric entries. Status: {response.status_code}")
            return response.status_code == 201
        except Exception as e:
            logger.error(f"Failed to send metrics: {e}")
            return False


def process_and_report():
    """Main execution routine"""
    scanner = NetworkScanner()
    reporter = NetworkReporter()
    
    devices, metrics = scanner.scan_and_collect_metrics()
    
    # Display results
    print("\n📋 DISCOVERED DEVICES:")
    for device in devices:
        print(f"  • {device.ip_address:15} | {device.mac_address:17} | {device.hostname or 'Unknown':20} | {'🟢' if device.online else '🔴'}")
    
    if metrics:
        print("\n📊 COLLECTED METRICS:")
        for m in metrics:
            print(f"  • {m.device_name:15} | Ping: {m.ping_ms:6.1f}ms")
    
    # Send to API
    reporter.send_devices(devices)
    if metrics:
        reporter.send_metrics(metrics)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("🚀 Starting Network Machine Usage Agent...")
    
    process_and_report()
    
    while True:
        print(f"\n⏰ Next scan in {POLL_INTERVAL}s...")
        time.sleep(POLL_INTERVAL)
        process_and_report()
