#!/bin/bash

# DAO Data AI - Automatic Project Setup Script
# This script creates the complete project structure

echo "🚀 Starting DAO Data AI project setup..."

# Create all directories
echo "📁 Creating directory structure..."
mkdir -p app/api/ingest/proposal
mkdir -p app/api/proposals
mkdir -p "app/api/proposal/[id]"
mkdir -p "app/proposals/[id]"
mkdir -p components
mkdir -p lib
mkdir -p public
mkdir -p supabase/functions/fetch-snapshot-proposals

echo "✅ Directory structure created!"
echo ""
echo "📝 Next steps:"
echo "1. Download all project files from: https://github.com/danvolsky-source/dao-data-ai/releases"
echo "2. Or clone the repo: git clone https://github.com/danvolsky-source/dao-data-ai.git"
echo "3. Run: npm install"
echo "4. Copy .env.example to .env.local and fill in your Supabase credentials"
echo "5. Run: npm run dev"
echo ""
echo "✨ Setup complete!"
