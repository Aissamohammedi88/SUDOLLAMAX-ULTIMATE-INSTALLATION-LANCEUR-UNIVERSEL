#!/bin/bash
# ============================================================
# GITHUB AUTH FORCE — WEB + TERMINAL
# Auteur : Aissa Mohammedi
# Version : 1.0.0
# Description : Force l'authentification GitHub.
# ============================================================

set -e

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; BLUE='\033[0;34m'; NC='\033[0m'
info()  { echo -e "${GREEN}[OK]${NC} $1"; }
warn()  { echo -e "${YELLOW}[ATTENTION]${NC} $1"; }
fail()  { echo -e "${RED}[ERREUR]${NC} $1"; }
section() { echo -e "\n${BLUE}===== $1 =====${NC}"; }

EMAIL="nodepy6@proton.me"
USERNAME="Aissa Mohammedi"
GITHUB_ENTERPRISE_URL="https://github.your-company.com"

# ─── 1. GÉNÉRATION DE LA CLÉ SSH ─────────────────────────────────

section "1. GÉNÉRATION DE LA CLÉ SSH"

ssh-keygen -t ed25519 -C "$EMAIL" -f ~/.ssh/id_ed25519 -N "" -q
PUB_KEY=$(cat ~/.ssh/id_ed25519.pub)
info "Clé SSH générée"

# ─── 2. CONFIGURATION GIT ────────────────────────────────────────

section "2. CONFIGURATION GIT"

git config --global user.name "$USERNAME"
git config --global user.email "$EMAIL"
git config --global core.sshCommand "ssh -i ~/.ssh/id_ed25519 -o IdentitiesOnly=yes"
info "Git configuré"

# ─── 3. GÉNÉRATION D'UN TOKEN (via API GitHub) ──────────────────

section "3. GÉNÉRATION D'UN TOKEN"

# Note : nécessite un token admin pour créer un token via API
# Sinon, guide l'utilisateur vers l'interface web
echo "🔑 Pour générer un token manuellement :"
echo "   → https://github.com/settings/tokens"
echo "   → Sélectionne 'repo' et 'workflow'"
echo ""
echo "📌 Token recommandé pour le web :"

# Création d'un fichier de token
cat > ~/.github_token.txt << EOF
# GitHub Token — À copier dans l'interface web
# URL : https://github.com/settings/tokens
# Scopes : repo, workflow, admin:org
# Email : $EMAIL
GITHUB_TOKEN="ton_token_personnel"
EOF

info "Fichier ~/.github_token.txt créé"

# ─── 4. CONFIGURATION DE L'AUTHENTIFICATION WEB ──────────────────

section "4. AUTHENTIFICATION WEB"

# Création du fichier de configuration GitHub Desktop
mkdir -p ~/.config/GitHub\ Desktop
cat > ~/.config/GitHub\ Desktop/GitHubDesktop.config << EOF
{
    "sso": {
        "url": "$GITHUB_ENTERPRISE_URL",
        "autoLogin": true
    },
    "auth": {
        "method": "token",
        "tokenFile": "~/.github_token.txt"
    },
    "git": {
        "path": "C:\\Program Files\\Git\\bin\\git.exe"
    }
}
EOF

info "Configuration web prête"

# ─── 5. TEST DE CONNEXION ─────────────────────────────────────────

section "5. TEST DE CONNEXION"

ssh -T git@github.com 2>&1 | grep -q "successfully authenticated" && \
    info "✅ Authentification SSH réussie" || \
    warn "⚠️ Ajoute manuellement la clé : https://github.com/settings/keys"

# ─── 6. AFFICHAGE DES INSTRUCTIONS ───────────────────────────────

section "6. INSTRUCTIONS FINALES"

echo "📌 POUR LE TERMINAL :"
echo "   ssh -T git@github.com"
echo ""
echo "📌 POUR LE WEB :"
echo "   1. Va sur https://github.com/settings/tokens"
echo "   2. Copie le token dans ~/.github_token.txt"
echo "   3. Relance GitHub Desktop"
echo ""
echo "📌 POUR LE DÉPLOIEMENT MSI :"
echo "   msiexec /i GitHubDesktop.msi /quiet"
echo "   copie le fichier GitHubDesktop.config dans %APPDATA%\\GitHub Desktop\\"
echo ""
echo "✅ Authentification forcée configurée"
