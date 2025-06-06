#!/bin/sh

set -e

echo "Starting Alpine VM setup..."

echo "Creating user 'foo'..."
adduser foo

echo "Installing OpenSSH..."
apk add openssh

echo "Generating SSH host keys..."
ssh-keygen -A

echo "Starting SSH service..."
rc-service sshd start

echo "Enabling SSH to start on boot..."
rc-update add sshd default

echo "Installing doas for sudo functionality..."
apk add doas

echo "Configuring doas for user 'foo'..."
mkdir -p /etc/doas.d
echo "permit foo as root" > /etc/doas.d/doas.conf

echo "Bringing up network interface..."
ip link set eth0 up
udhcpc -i eth0

echo "Enabling community repository for Docker..."
echo "https://dl-cdn.alpinelinux.org/alpine/v$(cat /etc/alpine-release | cut -d'.' -f1,2)/main" > /etc/apk/repositories
echo "https://dl-cdn.alpinelinux.org/alpine/v$(cat /etc/alpine-release | cut -d'.' -f1,2)/community" >> /etc/apk/repositories

echo "Updating package index..."
apk update

echo "Installing Docker..."
apk add docker docker-compose

echo "Adding user 'foo' to docker group..."
addgroup foo docker

echo "Starting Docker service..."
rc-service docker start --nodeps

echo "Enabling Docker to start on boot..."
rc-update add docker default

echo "Creating basic network interfaces file..."
cat > /etc/network/interfaces << EOF
auto lo
iface lo inet loopback

auto eth0
iface eth0 inet dhcp
EOF

echo "Enabling networking service..."
rc-update add networking default

echo "Getting current IP address..."
IP=$(ip route get 1 | awk '{print $7}' | head -1)
echo "Setup complete! You can now SSH to this machine at: $IP"
echo "Username: foo"
