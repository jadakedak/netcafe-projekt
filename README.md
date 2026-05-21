# Systemd process guide:

sudo nano /etc/systemd/system/netcafe_cloudbackup.service

[Unit]
Description=creates a backup of netcafé database
After=network.target

[Service]
User=root
WorkingDirectory=/root/projects/cloudbackup_server
ExecStart=/usr/bin/python3 app.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target


sudo systemctl daemon-reload
sudo systemctl enable netcafe_cloudbackup
sudo systemctl start netcafe_cloudbackup
sudo systemctl status netcafe_cloudbackup



HUSK: download visual studio code extension: "SQLite Viewer"