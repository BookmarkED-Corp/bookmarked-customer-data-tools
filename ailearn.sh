#!/bin/bash

# ailearn.sh - Load Customer Data Tools context for AI assistants
# Tell Claude: "Run ./ailearn.sh" at the start of any session

echo "🤖 Loading Customer Data Tools context for AI assistant..."
echo "================================================================"

# Check if we're in the right directory
if [[ ! -f "CLAUDE.md" ]]; then
    echo "❌ Error: CLAUDE.md not found!"
    echo "   Navigate to project root directory first"
    echo "   Expected: bookmarked-experimental/customer-data-tools/"
    exit 1
fi

echo ""
echo "📋 QUICK CONTEXT:"
echo "=================="
cat .claude/context.md

echo ""
echo "🔍 PROJECT STATUS:"
echo "=================="

# Check if Git is initialized
if [[ -d ".git" ]]; then
    echo "Current branch: $(git branch --show-current)"
    echo ""
    echo "Git remote:"
    git remote -v | head -2
    echo ""
    echo "Recent changes:"
    git status --short | head -20
    echo ""
    echo "Last 10 commits:"
    git log --oneline -10
else
    echo "⚠️  Git repository: NOT INITIALIZED"
    echo "   Recommendation: Initialize Git for version control"
fi

echo ""
echo "⚠️  CRITICAL: GITHUB USER VERIFICATION"
echo "======================================"
echo "BEFORE using any GitHub commands (gh, git push, etc):"
echo ""
echo "1. CHECK current GitHub user:"
echo "   gh auth status"
echo ""
echo "2. VERIFY it matches the correct account for this project:"
echo "   • Expected GitHub Org: bookmarked"
echo "   • Repository: bookmarked-customer-data-tools"
echo "   • Current user should have access to 'bookmarked' org"
echo ""
echo "3. If wrong user, DO NOT PROCEED with git operations"
echo "   • Ask the human user to verify GitHub credentials"
echo "   • DO NOT create repositories under wrong account"
echo "   • DO NOT push to wrong remote"
echo ""
echo "4. Current GitHub authentication status:"
gh auth status 2>&1 || echo "   ⚠️  GitHub CLI not authenticated or not installed"
echo ""

echo ""
echo "📊 KANBAN BOARD STATUS:"
echo "======================="
if [[ -f "kanban/kanban.py" ]]; then
    python3 kanban/kanban.py stats 2>/dev/null || echo "Kanban stats not available"
else
    echo "⚠️  Kanban CLI not found"
fi

echo ""
echo "📁 Documentation Files:"
echo "======================="
echo "Core Documentation:"
ls -1 *.md 2>/dev/null | grep -E '^(PROJECT_REQUIREMENTS|CLAUDE|README|PROJECT_SETUP)' | while read file; do
    size=$(wc -l < "$file" 2>/dev/null)
    echo "• $file ($size lines)"
done

echo ""
echo "Architecture & Guides:"
ls -1 docs/*.{md,html} 2>/dev/null | while read file; do
    echo "• $file"
done

echo ""
echo "💻 PROJECT STRUCTURE:"
echo "====================="

# Check source structure
if [[ -d "src" ]]; then
    echo "✅ Source directory structure:"
    echo "   • src/config/     - Configuration management"
    echo "   • src/auth/       - Authentication"
    echo "   • src/connectors/ - Data source integrations"
    echo "   • src/tools/      - Diagnostic tools"
    echo "   • src/models/     - Data models"
    echo "   • src/routes/     - Flask routes"

    py_files=$(find src -name "*.py" 2>/dev/null | wc -l)
    echo "   Total Python files: $py_files"
else
    echo "⚠️  Source directory structure: NOT YET CREATED"
    echo "   This is expected for new project - will be created during Phase 1"
fi

echo ""

# Check customer integration settings
if [[ -d "customer-integration-settings" ]]; then
    echo "✅ Customer Integration Settings:"
    config_count=$(find customer-integration-settings -name "*.json" ! -name "template.json" 2>/dev/null | wc -l)
    echo "   Customer configs: $config_count"
    if [[ -f "customer-integration-settings/template.json" ]]; then
        echo "   Template available: Yes"
    fi
else
    echo "⚠️  Customer integration settings: NOT FOUND"
fi

echo ""
echo "🧪 DEVELOPMENT ENVIRONMENT:"
echo "==========================="
if [[ -f "requirements.txt" ]]; then
    deps=$(wc -l < requirements.txt)
    echo "Python dependencies: $deps packages"
fi

if [[ -f "package.json" ]]; then
    echo "Node.js: package.json present (for Kanban UI)"
fi

if [[ -f ".env.example" ]]; then
    echo "Environment template: .env.example available"
fi

if [[ -d "venv" ]]; then
    echo "Python venv: ✅ Exists"
else
    echo "Python venv: ⚠️  Not created yet"
fi

echo ""
echo "✅ CONTEXT LOADED! Ready for AI assistance."
echo "============================================"
echo ""
echo "🚀 QUICK START CHECKLIST FOR AI:"
echo "=================================="
echo "• Read .claude/context.md (already displayed above)"
echo "• Read CLAUDE.md (comprehensive AI assistant guide)"
echo "• Read PROJECT_REQUIREMENTS.md (complete requirements)"
echo "• Read docs/ARCHITECTURE.md (system architecture)"
echo "• Check Kanban board: python3 kanban/kanban.py show"
echo ""
echo "📚 For detailed help, ask Claude to read:"
echo "• CLAUDE.md (complete AI assistant guide)"
echo "• PROJECT_REQUIREMENTS.md (functional & technical requirements)"
echo "• docs/ARCHITECTURE.md (system design & deployment)"
echo "• docs/EXECUTIVE_SUMMARY.html (visual overview)"
echo "• customer-integration-settings/README.md (customer config guide)"
echo "• kanban/TASK_SUMMARY.md (all tasks breakdown)"
echo "• kanban/PHASE_OVERVIEW.md (phase visualization)"
echo ""
echo "🧠 AI INITIALIZATION PROCESS:"
echo "=============================="
echo "1. Run this script (./ailearn.sh) ✅"
echo "2. Read the documentation files listed above"
echo "3. Review current Kanban board status"
echo "4. Check git history and recent changes"

if [[ -d ".git" ]]; then
    echo "5. 🔍 MANDATORY: Run git history analysis"
    echo ""
    echo "🔍 GIT HISTORY ANALYSIS REQUIRED!"
    echo "=================================="
    echo "Claude MUST run these commands and DISPLAY results:"
    echo "• git log --oneline --since=\"2 weeks ago\" --no-merges"
    echo "• git log --since=\"1 week ago\" --no-merges --stat | head -100"
    echo "• git status"
    echo ""
    echo "Then provide structured summary of recent work"
else
    echo "5. ⚠️  Git not initialized - skip git history for now"
fi

echo "6. Apply workflow rules and understand project priorities"
echo ""
echo "🔒 CRITICAL BEHAVIORAL RULES:"
echo "============================="
echo "• ⚠️  ALWAYS verify GitHub user BEFORE any git/gh commands!"
echo "• NEVER push to wrong GitHub account/organization"
echo "• NEVER use 'git add .' - always stage files individually"
echo "• NEVER modify production database (read-only access only)"
echo "• ALWAYS use read-only database connections"
echo "• NEVER commit sensitive data (.env files, customer credentials)"
echo "• ALWAYS use Kanban board for task tracking"
echo "• ALWAYS create comprehensive tests for new features"
echo "• NEVER store actual credentials in customer config JSON files"
echo "• ALWAYS reference credentials from .env or AWS Secrets Manager"
echo ""
echo "🔐 GITHUB & GIT RULES:"
echo "======================"
echo "1. BEFORE any git push or gh command:"
echo "   • Run: gh auth status"
echo "   • Verify correct GitHub user"
echo "   • Confirm repository: bookmarked/bookmarked-customer-data-tools"
echo ""
echo "2. If GitHub user is WRONG:"
echo "   • STOP immediately"
echo "   • Ask human user to verify credentials"
echo "   • DO NOT create repos under wrong account"
echo "   • DO NOT push to wrong remote"
echo ""
echo "3. Repository should be under 'bookmarked' organization"
echo "   • NOT under personal accounts"
echo "   • Transfer if created under wrong account"
echo ""
echo "⚠️  MANDATORY SESSION ACKNOWLEDGMENT"
echo "====================================="
echo "After completing initialization, Claude MUST:"
echo "1. Show git history analysis (if git available)"
echo "2. Verify GitHub user with: gh auth status"
echo "3. Acknowledge all critical behavioral rules"
echo "4. Display current Kanban board priorities"
echo "5. Confirm ready to work with current context"
echo ""
echo "📋 PROJECT QUICK REFERENCE:"
echo "==========================="
echo "Purpose: Customer data diagnostic & troubleshooting platform"
echo "Architecture: Flask web application with plugin-based tools"
echo "Database: PostgreSQL (READ-ONLY to Bookmarked staging & production)"
echo "Deployment: AWS Lambda or ECS Fargate"
echo "Version: 1.0.0"
echo "Stage: Foundation Setup Complete - Ready for Phase 1 Development"
echo ""
echo "Diagnostic Tools (4 planned):"
echo "• Student Mismatch Resolver - Incorrect student-parent assignments"
echo "• Missing Data Finder - Missing students/classes/enrollments"
echo "• Parent Email Conflict Detector - Duplicate email overwrites"
echo "• Campus Transfer Validator - Phantom enrollments after transfers"
echo ""
echo "Data Sources:"
echo "• Bookmarked API & Database (staging + production)"
echo "• ClassLink (OAuth2 + API)"
echo "• OneRoster (API + CSV)"
echo "• HubSpot (tickets integration)"
echo "• Customer FTP servers"
echo ""
echo "Current Priorities (Phase 1 - Foundation):"
echo "• TASK-001: Flask application setup"
echo "• TASK-002: Authentication system (Flask-Login)"
echo "• TASK-003: Bookmarked staging DB connector"
echo "• TASK-004: Bookmarked production DB connector"
echo "• TASK-005: Customer integration settings loader"
echo "• TASK-006: Base diagnostic tool class"
echo "• TASK-007: Credential manager"
echo "• TASK-008: Basic dashboard UI"
echo "• TASK-009: Tool selection UI"
echo "• TASK-010: Phase 1 integration tests"
echo ""
echo "🔧 Common Development Commands:"
echo "================================"
echo "# Python Virtual Environment"
echo "python3 -m venv venv"
echo "source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
echo "pip install -r requirements.txt"
echo ""
echo "# Configuration"
echo "cp .env.example .env"
echo "# Edit .env with your credentials"
echo ""
echo "# Flask Development"
echo "export FLASK_APP=src/app.py  # When implemented"
echo "export FLASK_ENV=development"
echo "flask run"
echo ""
echo "# Testing (when implemented)"
echo "pytest"
echo "pytest --cov=src --cov-report=html"
echo ""
echo "# Kanban Board"
echo "python3 kanban/kanban.py show               # Display board"
echo "python3 kanban/kanban.py stats              # Board statistics"
echo "npm install && npm start                    # Web UI (localhost:9001)"
echo "# Then open: http://localhost:9001/kanban_ui.html"
echo ""
echo "# Git & GitHub (VERIFY USER FIRST!)"
echo "gh auth status              # CHECK THIS FIRST!"
echo "git status"
echo "git add <specific-files>    # NEVER use 'git add .'"
echo "git commit -m \"message\""
echo "git push"
echo ""
echo "🎯 SESSION SUCCESS CRITERIA:"
echo "============================"
echo "Claude has successfully initialized when:"
if [[ -d ".git" ]]; then
    echo "✓ Git history analysis shown with structured summary"
    echo "✓ GitHub user verified with gh auth status"
fi
echo "✓ All critical behavioral rules acknowledged"
echo "✓ GitHub verification rules understood"
echo "✓ Current Kanban board priorities displayed"
echo "✓ Ready to work on tasks from backlog"
echo "✓ Understands read-only database access requirement"
echo "✓ Knows to never commit credentials"
echo ""
echo "💡 Claude: Demonstrate your understanding by providing:"
echo "   1. Git history summary (recent work)"
echo "   2. GitHub user verification (gh auth status output)"
echo "   3. Current Kanban board priorities"
echo "   4. Acknowledgment of critical behavioral rules (especially GitHub verification)"
echo "   5. Next steps based on project priorities"
echo ""
echo "🎉 Ready to assist with Customer Data Tools development!"
echo ""
