# WebViewer - Smart Life Management Web System

<div align="center">

![Version](https://img.shields.io/badge/version-1.2.8-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.11+-orange.svg)

**A unified web platform for three life management tools**

English | [简体中文](README.md)

</div>

---

## 📖 Introduction

WebViewer is an HTTPS web service platform that integrates three life management tools, featuring beautiful card-style interfaces and intelligent message processing capabilities.

### 🎯 Three Core Applications

| App | Name | Purpose | Path |
|------|------|------|----------|
| ✈️ **By Design** | 已读不回 (Read & Ignore) | Pre-trip checklist management | `/bydesign/` |
| 🏠 **Cherry Pick** | 一搬不丢 (Never Lose) | Moving item tracking system | `/cherry-pick/` |
| 📦 **Momhand** | 妈妈的手 (Mom's Hand) | Personal item location manager | `/momhand/` |

---

## 🚀 Quick Start

### Requirements

- Python 3.11+
- OpenSSL (for HTTPS certificate)
- Modern browser (Chrome/Firefox/Safari)

### Installation

```bash
# 1. Clone the repository
git clone git@github.com:Savior2016/webviewer.git
cd webviewer

# 2. Install dependencies (if any)
pip install -r requirements.txt

# 3. Generate self-signed certificate (first run only)
openssl req -x509 -newkey rsa:4096 -keyout selfsigned.key -out selfsigned.crt -days 365 -nodes

# 4. Start the server
python3 server.py
```

### Access the Service

- **Homepage**: `https://localhost/` or `https://<your-ip>/`
- **By Design**: `https://localhost/bydesign/`
- **Cherry Pick**: `https://localhost/cherry-pick/`
- **Momhand**: `https://localhost/momhand/`

> ⚠️ **Note**: When using self-signed certificates, browsers will show a security warning. Click "Continue to site" to proceed.

---

## 📱 Features

### ✈️ By Design - Trip Checklist

**Use Case**: Business trips, vacations, visiting family - any situation where you leave home for several days

**Core Features**:
- ✅ **Universal Checklist**: Recurring tasks for every trip (close windows, power off, lock doors, etc.)
- ✅ **Trip Records**: Special items and one-time tasks for specific trips
- ✅ **Progress Tracking**: Real-time completion percentage
- ✅ **Easy Verification**: Check off items one by one
- ✅ **Template System**: Quickly create standardized checklists

**API Examples**:
```bash
# Create a trip record
curl -X POST https://localhost/bydesign/api/trips \
  -H "Content-Type: application/json" \
  -d '{"name": "Beijing Business Trip", "description": "3-day conference"}'

# Get checklist
curl https://localhost/bydesign/api/checklist

# Add checklist item
curl -X POST https://localhost/bydesign/api/checklist \
  -H "Content-Type: application/json" \
  -d '{"text": "Turn off main power"}'
```

---

### 🏠 Cherry Pick - Moving Item Tracker

**Use Case**: Track all items during relocation

**Core Features**:
- ✅ **Create Moving Events**: Record each moving event
- ✅ **Item Tracking**: Name, original location, new location, packing location
- ✅ **Placement Confirmation**: Mark items as placed in new location
- ✅ **Auto-Sync**: Placed items automatically sync to Momhand system
- ✅ **Status Statistics**: Real-time packing and placement progress

**API Examples**:
```bash
# Create a moving event
curl -X POST https://localhost/cherry-pick/api/moves \
  -H "Content-Type: application/json" \
  -d '{"name": "Move to Wangjing", "description": "2026 Spring Festival move"}'

# Add an item
curl -X POST https://localhost/cherry-pick/api/moves/{moveId}/items \
  -H "Content-Type: application/json" \
  -d '{"name": "Books", "before_location": "Study bookshelf", "after_location": "New home bookshelf"}'
```

---

### 📦 Momhand - Item Location Manager

**Use Case**: Record and find item locations at home

**Core Features**:
- ✅ **Item Registration**: Name, type, location, usage
- ✅ **Quick Search**: Find items by keyword
- ✅ **Category Statistics**: View item distribution by type
- ✅ **Expiration Alerts**: Support expiration dates with advance reminders
- ✅ **Smart Recommendations**: Suggest storage locations based on history

**API Examples**:
```bash
# Add an item
curl -X POST https://localhost/momhand/api/items \
  -H "Content-Type: application/json" \
  -d '{"name": "Cold Medicine", "type": "Medicine", "location": "Living room medicine box", "usage": "Take when having a cold"}'

# Search items
curl "https://localhost/momhand/api/search?q=cold"

# Get statistics
curl https://localhost/momhand/api/stats
```

---

## 🔧 Technical Architecture

### System Architecture

```
┌─────────────────┐
│  Web Browser    │
│  (HTTPS Access) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   server.py     │  ← HTTPS Server (Port 443)
│  (ThreadingMixIn)│
└────────┬────────┘
         │
    ┌────┴────┬────────────┬──────────┐
    ▼         ▼            ▼          ▼
┌────────┐ ┌──────────┐ ┌───────┐ ┌──────────┐
│ByDesign│ │CherryPick│ │Momhand│ │OpenClaw  │
│Manager │ │ Manager  │ │Manager│ │Processor │
└────┬───┘ └────┬─────┘ └───┬───┘ └────┬─────┘
     │          │           │          │
     ▼          ▼           ▼          ▼
┌─────────────────────────────────────────┐
│          data/ (JSON + SQLite)          │
└─────────────────────────────────────────┘
```

### Technology Stack

- **Backend**: Python 3.11+
  - `http.server` + `ThreadingMixIn` - Concurrent HTTP server
  - `ThreadPoolExecutor` - Background task thread pool
  - `sqlite3` - Lightweight database
  - `requests` - HTTP client

- **Frontend**: 
  - HTML5 + CSS3 + JavaScript (vanilla)
  - TailwindCSS - Styling framework
  - Fetch API - Async requests

- **Security**:
  - HTTPS (TLS/SSL)
  - Self-signed certificate
  - Request timeout protection
  - Thread pool resource limits

### Performance Features

- ✅ **Concurrency**: Multi-threaded request handling via ThreadingMixIn
- ✅ **Resource Limits**: Thread pool limits to max 5 concurrent background tasks
- ✅ **Timeout Protection**: 30s HTTP request timeout, 60s background task timeout
- ✅ **Auto Recovery**: Watchdog script auto-detects and restarts stuck services
- ✅ **Stability**: Fixed single-threaded server freeze issue (v1.2.8)

---

## 📂 Project Structure

```
webviewer/
├── server.py                  # HTTPS main server (v1.2.8 fixed)
├── watchdog.sh                # Watchdog monitoring script
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
│
├── # Core Managers
├── bydesign_manager.py        # By Design trip manager
├── cherry_pick_manager.py     # Cherry Pick moving manager
├── momhand_manager_db.py      # Momhand item manager (SQLite)
│
├── # OpenClaw Integration
├── openclaw_agent_processor.py # OpenClaw Agent processor
├── message_engine.py          # Message processing engine
├── message_processor.py       # Message processor
│
├── # Web Interfaces
├── www/
│   ├── index.html             # Homepage - Dummy's Assistant (tool index)
│   ├── bydesign/
│   │   └── index.html         # By Design page
│   ├── cherry-pick/
│   │   └── index.html         # Cherry Pick page
│   ├── momhand/
│   │   └── index.html         # Momhand page
│   └── js/
│       └── agent-chat.js      # Agent chat component
│
├── # Data Storage
├── data/
│   ├── bydesign/              # Trip data
│   │   ├── checklist.json     # Checklists
│   │   ├── trips.json         # Trip records
│   │   └── templates.json     # Templates
│   ├── cherry-pick/           # Moving data
│   │   └── moves.json         # Moving events
│   ├── results/               # Message processing results
│   └── settings.json          # System settings
│
└── # Documentation
├── README.md                  # Chinese documentation
├── README_EN.md               # English documentation (this file)
├── FIX_REPORT.md              # v1.2.8 fix report
├── SYSTEM_ARCHITECTURE.md     # System architecture
├── DESIGN.md                  # Design document
└── VERSION.md                 # Version info
```

---

## 🔐 Security Configuration

### Environment Variables

Sensitive configurations should be set via environment variables, not hardcoded:

```bash
# Copy the template
cp .env.example .env

# Edit .env file (DO NOT commit to Git!)
vim .env
```

### Feishu API Configuration (Optional)

For Feishu message notifications:

```bash
export FEISHU_APP_ID="your_app_id"
export FEISHU_APP_SECRET="your_app_secret"
```

> ⚠️ **Important**: `.env` file is added to `.gitignore` and will NOT be committed to Git.

### SSL Certificate

The project uses self-signed certificates. For production:

1. Use Let's Encrypt free certificates
2. Or use commercial SSL certificates
3. Renew certificates regularly (recommended annually)

Generate new certificate:
```bash
openssl req -x509 -newkey rsa:4096 -keyout server.key -out server.crt -days 365 -nodes
```

---

## 🐛 Troubleshooting

### Service Unreachable

```bash
# 1. Check process
ps aux | grep "python3 server.py"

# 2. Check port
netstat -tlnp | grep 443

# 3. View logs
tail -f /tmp/webviewer.log

# 4. Test connection
curl -sk https://localhost/
```

### Service Frozen/Unresponsive

```bash
# Watchdog will auto-detect and restart
tail -f /tmp/webviewer-watchdog.log

# Manual restart
pkill -9 -f "python3 server.py"
cd /root/.openclaw/workspace/webviewer
nohup python3 server.py > /tmp/webviewer.log 2>&1 &
```

### Certificate Expired

```bash
# Regenerate certificate
openssl req -x509 -newkey rsa:4096 -keyout selfsigned.key -out selfsigned.crt -days 365 -nodes

# Restart service
pkill -9 -f "python3 server.py"
python3 server.py
```

---

## 📊 Version History

### v1.2.8 (2026-03-01) - Stability Fix 🛠️
- 🔧 Use ThreadingMixIn for concurrent HTTP requests
- 🧵 Thread pool limits background tasks (max 5 concurrent)
- ⏱️ Add request timeout protection (30 seconds)
- 🐕 Automatic watchdog monitoring and restart
- 📊 Detailed fix documentation

### v1.2.7 (2026-02-28) - UI Optimization
- Fix floating window affected by background blur layer
- Reduce glass card blur intensity

### v1.2.6 (2026-02-27) - Message System
- Fix message duplication issue
- Optimize blur effects

### v1.0.0 (2026-02-26) - Initial Release 🎉
- WebViewer service officially released
- Three core applications launched
- OpenClaw Agent integration

---

## 🤝 Contributing

Issues and Pull Requests are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

---

## 📞 Contact

- **GitHub**: https://github.com/Savior2016/webviewer
- **Issues**: https://github.com/Savior2016/webviewer/issues

---

<div align="center">

**Made with ❤️ by OpenClaw Community**

[Back to Top](#webviewer---smart-life-management-web-system)

</div>
