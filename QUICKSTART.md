# Quick Reference Guide

## 🚀 Getting Started (5 minutes)

### 1. Install
```bash
git clone https://github.com/jrutkarss/server_utils.git
cd server_utils
pip install -r requirements.txt
```

### 2. Setup
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 3. Run
```bash
# Terminal 1 - Django Server
python manage.py runserver

# Terminal 2 - Local Agent
python agents/agent.py

# Terminal 3 - Network Agent
export NETWORK_GATEWAY=192.168.1.1
export NETWORK_SUBNET=192.168.1.0/24
python agents/network_agent.py
```

### 4. Access
- Dashboard: http://localhost:8000/admin/
- API: http://localhost:8000/api/network-devices/

---

## 📊 What You Can Monitor

### Local Machine (Automatic)
- CPU usage & model
- RAM usage & capacity
- Disk usage & capacity
- CPU temperature
- Battery level (laptops)
- Active Directory status (Windows)
- Device role (server vs laptop)

### Network Devices (Automatic Discovery)
- All connected devices on network
- IP addresses & MAC addresses
- Hostnames (reverse DNS)
- Device types & vendors
- Online/offline status
- Ping latency
- CPU & memory (via SNMP)
- Network throughput

---

## 🔧 Configuration

### Environment Variables

```bash
# Required
DJANGO_SECRET_KEY=your-secret-here
CENTRAL_API_URL=http://localhost:8000/api/

# Network Settings
NETWORK_GATEWAY=192.168.1.1           # Your router IP
NETWORK_SUBNET=192.168.1.0/24         # Your network range
SNMP_COMMUNITY=public                 # SNMP community string

# Optional
DEBUG=False                            # Set to True for development
ALLOWED_HOSTS=localhost,127.0.0.1     # Allowed domains
POLL_INTERVAL=1800                    # Scan interval in seconds
```

### Network Configuration

**Find your network info:**
```bash
# Windows
ipconfig

# Linux/macOS
ifconfig
```

**Example:**
- Router IP: 192.168.1.1 → Set `NETWORK_GATEWAY=192.168.1.1`
- Subnet: 192.168.1.0/24 → Set `NETWORK_SUBNET=192.168.1.0/24`

---

## 🌐 API Endpoints

### Get All Network Devices
```bash
curl http://localhost:8000/api/network-devices/
```

### Get All Local Machines
```bash
curl http://localhost:8000/api/
```

### View Specific Device Metrics
```bash
curl "http://localhost:8000/admin/MainWebApp/networkdevice/?ip_address=192.168.1.100"
```

---

## 📈 Common Tasks

### Check if agent is running
```bash
# Look for python processes
ps aux | grep agent.py

# Windows
tasklist | findstr python
```

### View database data
```bash
python manage.py shell
>>> from MainWebApp.models import NetworkDevice
>>> NetworkDevice.objects.all()
>>> device = NetworkDevice.objects.get(ip_address='192.168.1.100')
>>> device.metrics.all()
```

### Force a rescan
Simply restart the network agent:
```bash
# Stop with Ctrl+C, then restart
python agents/network_agent.py
```

### Export metrics
```bash
# Via API
curl http://localhost:8000/api/network-devices/ > devices.json

# Via Django shell
python manage.py dumpdata MainWebApp > backup.json
```

---

## ⚠️ Troubleshooting

### Agent won't start
```bash
# Check Python version
python --version  # Should be 3.9+

# Check dependencies
pip install -r requirements.txt

# Try running with verbose output
python -u agents/agent.py
```

### No devices discovered
```bash
# Verify network configuration
ping 192.168.1.1

# Check environment variables
echo $NETWORK_GATEWAY
echo $NETWORK_SUBNET

# Run network agent with debug
python agents/network_agent.py 2>&1 | head -50
```

### Database error
```bash
# Reset database
python manage.py migrate
python manage.py createsuperuser
```

### API not responding
```bash
# Check if server is running
curl http://localhost:8000/

# Check logs
python manage.py runserver 2>&1 | grep -i error
```

---

## 🔐 Security Tips

1. **Change SECRET_KEY** - Use environment variable, not hardcoded
2. **Set DEBUG=False** - In production
3. **SNMP Community** - Change from "public" in production
4. **Database** - Use PostgreSQL instead of SQLite for production
5. **API Auth** - Consider adding token authentication
6. **Firewall** - Restrict agent access to authorized networks

---

## 📂 File Locations

```
Key Files:
├── agents/agent.py              → Local system monitoring
├── agents/network_agent.py       → Network device discovery
├── MainWebApp/models.py          → Database models
├── MainWebApp/views.py           → API endpoints
├── server_utils/settings.py      → Django configuration
├── manage.py                     → Django CLI
├── requirements.txt              → Python dependencies
└── README.md                     → Full documentation
```

---

## 🎯 Example Workflows

### Monitor Your Home Network

```bash
# Set your home network
export NETWORK_GATEWAY=192.168.0.1
export NETWORK_SUBNET=192.168.0.0/24
export POLL_INTERVAL=600  # Check every 10 minutes

# Run agents
python manage.py runserver &
python agents/network_agent.py &

# Check dashboard
# http://localhost:8000/admin/MainWebApp/networkdevice/
```

### Monitor Office Network

```bash
# Set office network
export NETWORK_GATEWAY=10.0.0.1
export NETWORK_SUBNET=10.0.0.0/24
export POLL_INTERVAL=1800  # Check every 30 minutes
export SNMP_COMMUNITY=office-snmp-key

# Deploy to server
python manage.py runserver 0.0.0.0:8000 &
nohup python agents/network_agent.py > logs/network-agent.log 2>&1 &

# Access from other machines
# http://server-ip:8000/api/network-devices/
```

### Monitor Multiple Networks

```bash
# Run multiple instances of network agent
# Agent 1: Home network
NETWORK_GATEWAY=192.168.1.1 python agents/network_agent.py &

# Agent 2: Office network
NETWORK_GATEWAY=10.0.0.1 python agents/network_agent.py &

# Both report to same Django instance
```

---

## 📚 Additional Resources

- **Full README**: See [README.md](./README.md)
- **Network Agent Guide**: See [NETWORK_AGENT_GUIDE.md](./NETWORK_AGENT_GUIDE.md)
- **Implementation Details**: See [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md)
- **Django Docs**: https://docs.djangoproject.com/
- **psutil Docs**: https://psutil.readthedocs.io/

---

## ❓ FAQ

**Q: How often does monitoring happen?**  
A: Every 30 minutes by default (configurable via `POLL_INTERVAL`)

**Q: Can I monitor devices without SNMP?**  
A: Yes! ARP scanning and ping work without SNMP. Set `SNMP_COMMUNITY=""`

**Q: What OS does this run on?**  
A: Windows, Linux, macOS. Both agents are cross-platform.

**Q: Can I use PostgreSQL instead of SQLite?**  
A: Yes! Update `DATABASES` in `server_utils/settings.py`

**Q: How do I backup my data?**  
A: Use `python manage.py dumpdata > backup.json`

**Q: Can I run this on a Raspberry Pi?**  
A: Yes! Python 3.9+ and ~100MB disk space required

**Q: How many devices can I monitor?**  
A: Tested with 100+ devices. Database indexing optimizes queries.

**Q: Can I modify the scan interval?**  
A: Yes: `export POLL_INTERVAL=3600` for 1 hour scans

**Q: What if a device is offline?**  
A: Shows as `online: false` with last known metrics

---

**Need Help?** Check the full README.md or create an issue on GitHub!
