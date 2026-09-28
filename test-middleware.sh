#!/bin/bash
# Script de test du middleware /admin
# Usage: ./test-middleware.sh [URL]
# Par défaut teste sur http://localhost:3000

URL="${1:-http://localhost:3000}"

echo "🔒 Test du middleware Edge /admin"
echo "URL de base : $URL"
echo ""

# Fonction pour afficher un résultat de test
test_result() {
    local name="$1"
    local expected="$2"
    local actual="$3"
    
    if [[ "$actual" == *"$expected"* ]]; then
        echo "✅ $name : OK ($actual)"
    else
        echo "❌ $name : ÉCHEC (attendu: $expected, reçu: $actual)"
    fi
}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 TEST 1 : Pages admin SANS authentification"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test 1.1 - /admin/ sans auth
echo "1.1 - GET $URL/admin/ (sans auth)"
response=$(curl -s -I "$URL/admin/" | head -1)
test_result "/admin/ sans auth" "401" "$response"
echo ""

# Test 1.2 - /admin/corpus.html sans auth
echo "1.2 - GET $URL/admin/corpus.html (sans auth)"
response=$(curl -s -I "$URL/admin/corpus.html" | head -1)
test_result "/admin/corpus.html sans auth" "401" "$response"
echo ""

# Test 1.3 - /admin/paiements.html sans auth
echo "1.3 - GET $URL/admin/paiements.html (sans auth)"
response=$(curl -s -I "$URL/admin/paiements.html" | head -1)
test_result "/admin/paiements.html sans auth" "401" "$response"
echo ""

# Vérifier l'en-tête WWW-Authenticate
echo "1.4 - Vérification de l'en-tête WWW-Authenticate"
auth_header=$(curl -s -I "$URL/admin/" | grep -i "www-authenticate")
test_result "WWW-Authenticate présent" "Basic realm" "$auth_header"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔑 TEST 2 : Pages admin AVEC authentification"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Note : ce test nécessite que ADMIN_PASSWORD soit défini
if [ -n "$ADMIN_PASSWORD" ]; then
    echo "2.1 - GET $URL/admin/ (avec bon mot de passe)"
    response=$(curl -s -I -u "admin:$ADMIN_PASSWORD" "$URL/admin/" | head -1)
    test_result "/admin/ avec auth valide" "200" "$response"
    echo ""
    
    echo "2.2 - GET $URL/admin/corpus.html (avec bon mot de passe)"
    response=$(curl -s -I -u "admin:$ADMIN_PASSWORD" "$URL/admin/corpus.html" | head -1)
    test_result "/admin/corpus.html avec auth valide" "200" "$response"
    echo ""
else
    echo "⚠️  ADMIN_PASSWORD non défini - tests avec authentification sautés"
    echo "    Définir : export ADMIN_PASSWORD='votre_secret'"
    echo ""
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ TEST 3 : Pages publiques (ne doivent PAS être affectées)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test 3.1 - Page d'accueil
echo "3.1 - GET $URL/ (page d'accueil)"
response=$(curl -s -I "$URL/" | head -1)
test_result "Page d'accueil accessible" "200" "$response"
echo ""

# Test 3.2 - /chat
echo "3.2 - GET $URL/chat"
response=$(curl -s -I "$URL/chat" | head -1)
test_result "/chat accessible" "200\|302" "$response"
echo ""

# Test 3.3 - /oh/242/
echo "3.3 - GET $URL/oh/242/"
response=$(curl -s -I "$URL/oh/242/" | head -1)
test_result "/oh/242/ accessible" "200\|302" "$response"
echo ""

# Test 3.4 - /faq
echo "3.4 - GET $URL/faq"
response=$(curl -s -I "$URL/faq" | head -1)
test_result "/faq accessible" "200\|302" "$response"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 TEST 4 : API publiques (ne doivent PAS être affectées)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test 4.1 - /api/progress
echo "4.1 - GET $URL/api/progress"
response=$(curl -s -I "$URL/api/progress" | head -1)
test_result "/api/progress accessible" "200" "$response"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Résumé"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ Si tous les tests passent, le middleware fonctionne correctement :"
echo "   - /admin/* est protégé par Basic Auth (401 sans credentials)"
echo "   - Les pages publiques restent accessibles (200)"
echo "   - Le middleware ne touche PAS aux routes en dehors de /admin"
echo ""
echo "⚠️  Pour tester avec authentification, définir :"
echo "    export ADMIN_PASSWORD='votre_secret_admin'"
echo ""
