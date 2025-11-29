#!/bin/bash
# GitHub Setup and Deployment Script
# Run this script to initialize git and push to GitHub

set -e

echo "=========================================="
echo "RAG-Based Legal Advisor Bot"
echo "GitHub Setup & Deployment Script"
echo "=========================================="

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git not found. Please install Git first."
    exit 1
fi

# Initialize git repository
if [ ! -d .git ]; then
    echo "📦 Initializing git repository..."
    git init
    git config user.email "developer@example.com"
    git config user.name "Developer"
fi

# Add all files
echo "📝 Adding files to git..."
git add .

# Create initial commit
echo "💾 Creating initial commit..."
git commit -m "Initial commit: RAG-Based Legal Advisor Bot" || echo "Repository already has commits"

# GitHub instructions
echo ""
echo "=========================================="
echo "⚠️  NEXT STEPS - Push to GitHub"
echo "=========================================="
echo ""
echo "1. Go to GitHub.com and create a new repository:"
echo "   - Repository name: rag-legal-advisor"
echo "   - Description: RAG-Based Legal Advisor Bot"
echo "   - Set to Public (or Private)"
echo "   - Do NOT initialize with README, .gitignore, or license"
echo ""
echo "2. After creating the repository, run these commands:"
echo ""
echo "   git branch -M main"
echo "   git remote add origin https://github.com/YOUR_USERNAME/rag-legal-advisor.git"
echo "   git push -u origin main"
echo ""
echo "=========================================="
echo ""
echo "Git status:"
git status
