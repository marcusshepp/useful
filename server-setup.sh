#!/bin/bash
# Server Setup Script
# SCP to new EC2/server instances, then run: bash server-setup.sh

set -e

echo "================================"
echo "  Server Setup Script"
echo "================================"
echo ""

# Update packages
echo "[1/11] Updating packages..."
apt update -y

# Install essentials (only if not installed)
echo "[2/11] Installing essentials..."
for pkg in git zsh curl wget htop ripgrep neovim unzip; do
    if command -v $pkg &> /dev/null; then
        echo "  ✓ $pkg already installed"
    else
        echo "  Installing $pkg..."
        apt install -y $pkg
    fi
done

# Install Node.js 20 (only if not installed or wrong version)
echo ""
echo "[3/11] Checking Node.js..."
if command -v node &> /dev/null && [[ $(node -v) == v20* ]]; then
    echo "  ✓ Node.js 20 already installed"
else
    echo "  Installing Node.js 20..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt install -y nodejs
    echo "  ✓ Node.js $(node -v) installed"
fi

# Install pnpm (only if not installed)
echo ""
echo "[4/11] Checking pnpm..."
if command -v pnpm &> /dev/null; then
    echo "  ✓ pnpm already installed"
else
    echo "  Installing pnpm..."
    npm install -g pnpm
    echo "  ✓ pnpm installed"
fi

# Install Claude Code (only if not installed)
echo ""
echo "[5/11] Checking Claude Code..."
if command -v claude &> /dev/null; then
    echo "  ✓ Claude Code already installed"
else
    echo "  Installing Claude Code..."
    curl -fsSL https://claude.ai/install.sh | sh
    echo "  ✓ Claude Code installed"
fi

# Install Playwright (only if not installed)
echo ""
echo "[6/11] Checking Playwright..."
if npm list -g @playwright/test &> /dev/null; then
    echo "  ✓ Playwright already installed"
else
    echo "  Installing Playwright..."
    npm install -g playwright
    npx playwright install --with-deps chromium
    echo "  ✓ Playwright installed"
fi

# Install Playwright MCP (only if not installed)
echo ""
echo "[7/11] Checking Playwright MCP..."
if npm list -g @anthropic-ai/mcp-server-playwright &> /dev/null 2>&1 || npm list -g @playwright/mcp &> /dev/null 2>&1; then
    echo "  ✓ Playwright MCP already installed"
else
    echo "  Installing Playwright MCP..."
    npm install -g @playwright/mcp
    echo "  ✓ Playwright MCP installed"
fi

# Install AWS CLI (only if not installed)
echo ""
echo "[8/11] Checking AWS CLI..."
if command -v aws &> /dev/null; then
    echo "  ✓ AWS CLI already installed"
else
    echo "  Installing AWS CLI..."
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "/tmp/awscliv2.zip"
    unzip -q /tmp/awscliv2.zip -d /tmp
    /tmp/aws/install
    rm -rf /tmp/awscliv2.zip /tmp/aws
    echo "  ✓ AWS CLI installed"
fi

# Configure git (only if not configured)
echo ""
echo "[9/11] Configuring git..."
if [ -z "$(git config --global user.name)" ]; then
    git config --global user.name "marcusshepp"
    git config --global user.email "marcusshepdotcom@gmail.com"
    git config --global alias.st status
    git config --global alias.a add
    git config --global alias.ci commit
    git config --global alias.ps push
    git config --global alias.d diff
    git config --global alias.co checkout
    echo "  ✓ Git configured"
else
    echo "  ✓ Git already configured"
fi

# Generate SSH key (only if not exists)
echo ""
echo "[10/11] Checking SSH key..."
if [ -f ~/.ssh/id_ed25519 ]; then
    echo "  ✓ SSH key already exists"
else
    echo "  Generating SSH key..."
    mkdir -p ~/.ssh
    ssh-keygen -t ed25519 -C "$(hostname)" -f ~/.ssh/id_ed25519 -N ""
    echo "  ✓ SSH key generated"
fi

# Install starship prompt (only if not installed)
echo ""
echo "[11/11] Setting up shell..."
if command -v starship &> /dev/null; then
    echo "  ✓ Starship already installed"
else
    echo "  Installing starship..."
    curl -sS https://starship.rs/install.sh | sh -s -- -y
    echo "  ✓ Starship installed"
fi

# Configure zsh (only if not configured)
if [ -f ~/.zshrc ] && grep -q "starship init" ~/.zshrc; then
    echo "  ✓ Zsh already configured"
else
    cat > ~/.zshrc << 'ZSHEOF'
eval "$(starship init zsh)"

# -----------------------------------------------------------------------------
# Unix-like Utilities
# -----------------------------------------------------------------------------
alias ll='ls -la'
alias l='ls -la'
alias c='clear'
alias v='nvim'
alias vim='nvim'

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

# -----------------------------------------------------------------------------
# Path
# -----------------------------------------------------------------------------
export PATH="$HOME/.claude/bin:$HOME/.local/bin:$PATH"
ZSHEOF
    echo "  ✓ Zsh configured"
fi

# Configure starship (only if not configured)
if [ -f ~/.config/starship.toml ]; then
    echo "  ✓ Starship config already exists"
else
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
    echo "  ✓ Starship config created"
fi

# Set zsh as default shell (only if not already)
if [ "$SHELL" = "$(which zsh)" ]; then
    echo "  ✓ Zsh already default shell"
else
    chsh -s $(which zsh)
    echo "  ✓ Zsh set as default shell"
fi

echo ""
echo "================================"
echo "  SETUP COMPLETE!"
echo "================================"
echo ""
echo "Installed:"
echo "  - git, zsh, curl, wget, htop, ripgrep, neovim"
echo "  - Node.js 20, pnpm"
echo "  - Claude Code"
echo "  - Playwright + Playwright MCP"
echo "  - AWS CLI"
echo "  - Starship prompt"
echo ""
echo "================================"
echo ""
echo ">>> ADD THIS SSH KEY TO GITHUB <<<"
echo ">>> https://github.com/settings/keys <<<"
echo ""
cat ~/.ssh/id_ed25519.pub
echo ""
echo "================================"
echo ""
echo ">>> NEXT STEPS <<<"
echo "1. ssh -T git@github.com"
echo "2. aws configure (if needed)"
echo "3. claude (to authenticate)"
echo "4. Reconnect to use zsh"
echo ""
