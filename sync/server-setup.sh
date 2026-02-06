#!/bin/bash
# Server Setup Script
# SCP to new EC2/server instances, then run: bash server-setup.sh

set -e

echo "================================"
echo "  Server Setup Script"
echo "================================"
echo ""

# Update packages
echo "[1/6] Updating packages..."
apt update -y

# Install essentials
echo "[2/6] Installing git, zsh, and essentials..."
apt install -y git zsh curl wget htop ripgrep

# Configure git
echo "[3/6] Configuring git..."
git config --global user.name "marcusshepp"
git config --global user.email "marcusshepdotcom@gmail.com"
git config --global alias.st status
git config --global alias.a add
git config --global alias.ci commit
git config --global alias.ps push
git config --global alias.d diff
git config --global alias.co checkout

echo "Git configured:"
git config --global --list

# Generate SSH key
echo ""
echo "[4/6] Generating SSH key..."
if [ ! -f ~/.ssh/id_ed25519 ]; then
    ssh-keygen -t ed25519 -C "$(hostname)" -f ~/.ssh/id_ed25519 -N ""
else
    echo "SSH key already exists"
fi

# Install starship prompt
echo ""
echo "[5/6] Installing starship prompt..."
curl -sS https://starship.rs/install.sh | sh -s -- -y

# Configure zsh
echo ""
echo "[6/6] Configuring zsh..."
cat > ~/.zshrc << 'ZSHEOF'
eval "$(starship init zsh)"

# -----------------------------------------------------------------------------
# Unix-like Utilities
# -----------------------------------------------------------------------------
alias ll='ls -la'
alias l='ls -la'
alias c='clear'

# -----------------------------------------------------------------------------
# Git Aliases
# -----------------------------------------------------------------------------
alias gs='git status'
alias ga='git add'
alias gc='git commit'
alias gp='git push'
alias gd='git diff'
alias gitbranches='git for-each-ref --sort=committerdate refs/heads/ --format="%(committerdate:iso8601) %(refname:short)"'

# Git helpers - like PowerShell profile
done() {
    git add .
    git commit
    git push origin HEAD
}

donee() {
    if [ -z "$1" ]; then
        echo "Usage: donee 'commit message'"
        return 1
    fi
    git add .
    git commit -m "$1"
    git push
}

# -----------------------------------------------------------------------------
# Claude
# -----------------------------------------------------------------------------
alias cl='claude --dangerously-skip-permissions'

# -----------------------------------------------------------------------------
# AWS Profile
# -----------------------------------------------------------------------------
export AWS_PROFILE='sir-code-alot'
ZSHEOF

mkdir -p ~/.config
cat > ~/.config/starship.toml << 'STAREOF'
format = "🌐 $hostname $directory$git_branch$character"
[hostname]
ssh_only = false
format = "[$hostname]($style) "
style = "green"
[directory]
truncation_length = 2
[character]
success_symbol = "[❯](green)"
error_symbol = "[❯](red)"
[git_branch]
format = "[$branch]($style) "
STAREOF

# Set zsh as default shell
chsh -s $(which zsh)

echo ""
echo "================================"
echo "  SETUP COMPLETE!"
echo "================================"
echo ""
echo ">>> ADD THIS SSH KEY TO GITHUB <<<"
echo ">>> https://github.com/settings/keys <<<"
echo ""
cat ~/.ssh/id_ed25519.pub
echo ""
echo "================================"
echo ""
echo ">>> THEN TEST CONNECTION <<<"
echo ">>> ssh -T git@github.com <<<"
echo ""
echo ">>> THEN RECONNECT TO USE ZSH <<<"
echo ""
