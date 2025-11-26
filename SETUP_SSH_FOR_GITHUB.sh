#!/bin/bash
# Script to set up SSH keys for GitHub and add the public key

echo "=========================================="
echo "GitHub SSH Key Setup"
echo "=========================================="
echo ""

# Check if SSH key already exists
if [ -f ~/.ssh/id_ed25519.pub ]; then
    echo "✅ SSH key already exists!"
    echo ""
    echo "Your public SSH key:"
    echo "----------------------------------------"
    cat ~/.ssh/id_ed25519.pub
    echo "----------------------------------------"
    echo ""
    echo "📋 Copy the key above and add it to GitHub:"
    echo "   1. Go to: https://github.com/settings/keys"
    echo "   2. Click 'New SSH key'"
    echo "   3. Paste the key above"
    echo "   4. Click 'Add SSH key'"
    echo ""
    read -p "Press Enter after you've added the key to GitHub..."
elif [ -f ~/.ssh/id_rsa.pub ]; then
    echo "✅ SSH key found (RSA format)"
    echo ""
    echo "Your public SSH key:"
    echo "----------------------------------------"
    cat ~/.ssh/id_rsa.pub
    echo "----------------------------------------"
    echo ""
    echo "📋 Copy the key above and add it to GitHub:"
    echo "   1. Go to: https://github.com/settings/keys"
    echo "   2. Click 'New SSH key'"
    echo "   3. Paste the key above"
    echo "   4. Click 'Add SSH key'"
    echo ""
    read -p "Press Enter after you've added the key to GitHub..."
else
    echo "🔑 Generating new SSH key..."
    echo ""
    
    # Generate SSH key
    ssh-keygen -t ed25519 -C "deanwheatley@hotmail.com" -f ~/.ssh/id_ed25519 -N ""
    
    # Start ssh-agent and add key
    eval "$(ssh-agent -s)"
    ssh-add ~/.ssh/id_ed25519
    
    echo ""
    echo "✅ SSH key generated!"
    echo ""
    echo "Your public SSH key:"
    echo "----------------------------------------"
    cat ~/.ssh/id_ed25519.pub
    echo "----------------------------------------"
    echo ""
    echo "📋 Copy the key above and add it to GitHub:"
    echo "   1. Go to: https://github.com/settings/keys"
    echo "   2. Click 'New SSH key'"
    echo "   3. Paste the key above"
    echo "   4. Click 'Add SSH key'"
    echo ""
    read -p "Press Enter after you've added the key to GitHub..."
fi

# Test SSH connection
echo ""
echo "🔍 Testing SSH connection to GitHub..."
if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
    echo "✅ SSH authentication successful!"
    echo ""
    echo "You can now push to GitHub:"
    echo "  git push -u origin main"
else
    echo "⚠️  SSH test completed. If you see 'Hi username!' above, you're good to go!"
    echo ""
    echo "Try pushing now:"
    echo "  git push -u origin main"
fi


