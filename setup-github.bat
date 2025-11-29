@echo off
REM GitHub Setup and Deployment Script (Windows PowerShell)
REM Run this script to initialize git and push to GitHub

setlocal enabledelayedexpansion

echo.
echo ==========================================
echo RAG-Based Legal Advisor Bot
echo GitHub Setup - Windows Version
echo ==========================================
echo.

REM Check if git is installed
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Git not found. Please install Git first.
    exit /b 1
)

REM Initialize git repository
if not exist .git (
    echo Initializing git repository...
    git init
    git config user.email "developer@example.com"
    git config user.name "Developer"
)

REM Add all files
echo Adding files to git...
git add .

REM Create initial commit
echo Creating initial commit...
git commit -m "Initial commit: RAG-Based Legal Advisor Bot" 2>nul || echo.

REM GitHub instructions
echo.
echo ==========================================
echo NEXT STEPS - Push to GitHub
echo ==========================================
echo.
echo 1. Go to GitHub.com and create a new repository:
echo    - Repository name: rag-legal-advisor
echo    - Description: RAG-Based Legal Advisor Bot
echo    - Set to Public or Private
echo    - DO NOT initialize with README, .gitignore, or license
echo.
echo 2. After creating the repository, run these commands:
echo.
echo    git branch -M main
echo    git remote add origin https://github.com/YOUR_USERNAME/rag-legal-advisor.git
echo    git push -u origin main
echo.
echo ==========================================
echo.
echo Git status:
git status
