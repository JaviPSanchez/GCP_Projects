#!/bin/bash

# Install necessary packages
sudo apt update
sudo apt install -y telnet nginx nano

# Enable nginx to start on boot
sudo systemctl enable nginx

# Set permissions for the web directory
sudo chmod -R 755 /var/www/html

# Create a directory for the application
sudo mkdir -p /var/www/html/app1

# Get the hostname and IP address
HOSTNAME=$(hostname)
IP_ADDRESS=$(hostname -I)

# Create index.html for app1
echo "<!DOCTYPE html>
<html>
<body style='background-color:rgb(250, 210, 210);'>
<h1>Welcome to StackSimplify - WebVM App1</h1>
<p><strong>VM Hostname:</strong> $HOSTNAME</p>
<p><strong>VM IP Address:</strong> $IP_ADDRESS</p>
<p><strong>Application Version:</strong> V1</p>
<p>Google Cloud Platform - Demos</p>
</body>
</html>" | sudo tee /var/www/html/app1/index.html

# Create the main index.html
echo "<!DOCTYPE html>
<html>
<body style='background-color:rgb(250, 210, 210);'>
<h1>Welcome to StackSimplify - WebVM App1</h1>
<p><strong>VM Hostname:</strong> $HOSTNAME</p>
<p><strong>VM IP Address:</strong> $IP_ADDRESS</p>
<p><strong>Application Version:</strong> V1</p>
<p>Google Cloud Platform - Demos</p>
</body>
</html>" | sudo tee /var/www/html/index.html

# Restart nginx to apply changes
sudo systemctl restart nginx
