# Architecture Overview:


## Repository Structure

```
aichoir/
├── components/               # Existing landing page components (untouched)
├── pages/
│   └── CourtSearchPage.tsx   # New Court Search page (React)
├── CourtSearch/              # Existing Python scraper package (untouched)
│   ├── scrapers/
│   ├── court_lookup.py
│   └── requirements.txt
├── backend/
│   ├── app.py                # Flask app (new)
│   └── requirements.txt      # Flask + all CourtSearch deps combined (new)
├── App.tsx                   # Add routing / page switching
├── index.tsx
├── index.html
├── vite.config.ts            # Add /api proxy for dev
├── package.json              # Add react-router-dom
├── tsconfig.json
├── CLAUDE.md
└── architectureplan.md
```

---

## Production Deployment (VPS + Domain)

### Infrastructure

| Component | Detail |
|---|---|
| VPS | Hetzner, 4GB RAM, Ubuntu |
| Domain | aichoir.xyz (registered on Namecheap) |
| Reverse proxy | Nginx |
| SSL | Let's Encrypt via Certbot (auto-renews) |
| Process manager | systemd |

### How It All Fits Together

```
Browser → https://www.aichoir.xyz
    │
    ▼
Nginx (port 80/443)
    │  SSL termination + reverse proxy
    │  Proxies ALL requests to Flask
    ▼
Flask (127.0.0.1:5001)
    ├── /api/*        → API routes (search, status, results)
    └── /*            → Serves dist/index.html + static assets
```

Nginx does NOT serve static files directly. Flask handles everything — both the built React frontend (`dist/`) and the API routes. Nginx just terminates SSL and proxies.

### DNS (Namecheap → Advanced DNS)

| Type | Host | Value |
|---|---|---|
| A Record | @ | VPS IP |
| A Record | www | VPS IP |

### Nginx Config

Location: `/etc/nginx/sites-available/aichoir`
Symlinked to: `/etc/nginx/sites-enabled/aichoir`

```nginx
server {
    listen 80;
    server_name aichoir.xyz www.aichoir.xyz;

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
    }
}
```

Certbot added the SSL (443) server block automatically. The `proxy_read_timeout 300s` is critical — court searches take 1-3 minutes, and the default 60s timeout would kill them.

### systemd Service

Location: `/etc/systemd/system/aichoir.service`

```ini
[Unit]
Description=AI Choir Flask App
After=network.target

[Service]
User=root
WorkingDirectory=/root/aichoir
Environment="FLASK_ENV=production"
Environment="PORT=5001"
ExecStart=/usr/bin/python3 backend/app.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Key details:
- `WorkingDirectory=/root/aichoir` (NOT `/root/aichoir/backend` — Flask resolves `dist/` and `CourtSearch/` relative to this)
- `ExecStart` uses `backend/app.py` (relative to WorkingDirectory)
- `Restart=always` — auto-restarts on crash or VPS reboot

### Common Commands (on VPS)

```bash
# Check if app is running
sudo systemctl status aichoir

# View logs
sudo journalctl -u aichoir -n 50 --no-pager

# Restart after code changes
sudo systemctl restart aichoir

# Rebuild frontend after React changes
cd ~/aichoir && npm run build && sudo systemctl restart aichoir

# Test Nginx config after editing
sudo nginx -t && sudo systemctl reload nginx

# Renew SSL (usually auto, but manual if needed)
sudo certbot renew
```
