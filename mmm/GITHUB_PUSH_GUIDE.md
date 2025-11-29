# GitHub Push Instructions

## 📝 Step-by-Step Guide to Push to GitHub

### Step 1: Create a GitHub Repository

1. Go to [GitHub.com](https://github.com) and sign in
2. Click the **+** icon (top right) → **New repository**
3. Fill in:
   - **Repository name**: `rag-legal-advisor`
   - **Description**: `RAG-Based Legal Advisor Bot - Production Ready`
   - **Visibility**: Public (or Private if you prefer)
4. ⚠️ **DO NOT** initialize with:
   - README (we have one)
   - .gitignore (we have one)
   - License (we have one)
5. Click **Create repository**

### Step 2: Link Local Repository to GitHub

After creating the repository, GitHub will show you the push commands. Copy/paste these (or use the ones below with YOUR_USERNAME):

```bash
cd "c:\Users\yash pandey\Desktop\RAG Based legal chatbot"

# Set upstream branch
git branch -M main

# Add remote repository
git remote add origin https://github.com/YOUR_USERNAME/rag-legal-advisor.git

# Push to GitHub
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

### Step 3: Verify Push

```bash
# Check remote
git remote -v

# Check branch
git branch -a

# View commits
git log --oneline
```

## 🔐 Authentication

### Option A: HTTPS (Recommended for beginners)
```bash
# First time, GitHub will prompt for credentials
# OR generate a Personal Access Token:
# 1. GitHub Settings → Developer settings → Personal access tokens
# 2. Generate new token (check 'repo' scope)
# 3. Copy token
# 4. Paste when prompted

git push -u origin main
# When prompted for password, use your token
```

### Option B: SSH (More secure)
```bash
# Generate SSH key (if you don't have one)
ssh-keygen -t ed25519 -C "your_email@example.com"

# Add to GitHub:
# Settings → SSH and GPG keys → New SSH key
# Paste content of ~/.ssh/id_ed25519.pub

# Clone with SSH
git remote set-url origin git@github.com:YOUR_USERNAME/rag-legal-advisor.git
git push -u origin main
```

## ✅ Verification Checklist

After push, verify:

```bash
# 1. Check remote tracking
git remote -v
# Output should show:
# origin  https://github.com/YOUR_USERNAME/rag-legal-advisor.git (fetch)
# origin  https://github.com/YOUR_USERNAME/rag-legal-advisor.git (push)

# 2. Check branch
git branch -a
# Output should show:
# * main
#   remotes/origin/main

# 3. View commit
git log -1 --format="%H %s"
```

## 🌐 GitHub Repository Features

After push, configure these on GitHub:

### 1. Settings Tab
```
Repository Settings → General
- Set main branch as default
- Enable "Automatically delete head branches"
- Enable "Require pull request reviews" (optional)
```

### 2. Add Repository Topics
```
Add tags: python, ai, rag, legal, nlp, faiss, streamlit, docker
```

### 3. Enable GitHub Pages (Optional)
```
Settings → Pages
- Source: main branch /docs folder
- Creates automatic documentation site
```

### 4. Add GitHub Actions (CI/CD)
Create `.github/workflows/tests.yml`:
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest -v
      - run: flake8 src/
```

Then commit and push:
```bash
git add .github/
git commit -m "Add GitHub Actions CI/CD"
git push origin main
```

## 🚀 Next Steps After Push

### 1. Update README Links
In `README.md`, update these lines with your actual username:
```markdown
git clone https://github.com/YOUR_USERNAME/rag-legal-advisor.git
```

### 2. Create Release
```bash
git tag -a v1.0.0 -m "Version 1.0.0 - Initial Release"
git push origin v1.0.0
```

Then on GitHub:
- Go to Releases
- Click "Create a release"
- Select tag v1.0.0
- Add description
- Click "Publish release"

### 3. Add Collaborators (if team project)
```
Settings → Collaborators → Add collaborators
```

### 4. Set Up Issue Templates
Create `.github/ISSUE_TEMPLATE/bug_report.md`:
```markdown
---
name: Bug report
about: Create a report to help us improve
---

**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce...

**Expected behavior**
What you expected to happen.

**Environment**
- OS: [e.g. Windows, Linux]
- Python: [e.g. 3.11]
```

## 🔄 Updating Repository After Push

### Add New Files
```bash
git add path/to/new/file.py
git commit -m "Add new feature description"
git push origin main
```

### Create Feature Branch
```bash
git checkout -b feature/my-feature
# Make changes
git add .
git commit -m "Add my feature"
git push origin feature/my-feature

# Then open Pull Request on GitHub
```

### Keep Local in Sync
```bash
git fetch origin
git merge origin/main
# or
git pull origin main
```

## 🐛 Troubleshooting

### "fatal: remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/rag-legal-advisor.git
git push -u origin main
```

### "fatal: 'origin' does not appear to be a 'git' repository"
```bash
git remote add origin https://github.com/YOUR_USERNAME/rag-legal-advisor.git
git push -u origin main
```

### "Permission denied (publickey)"
- Use HTTPS instead of SSH
- Or add SSH key to GitHub (see Option B above)

### "Updates were rejected because the tip of your current branch is behind"
```bash
git pull origin main
git push origin main
```

## 📊 View Repository Status

After pushing, you can view:

```
https://github.com/YOUR_USERNAME/rag-legal-advisor
├── Code tab - Source code
├── Issues tab - Feature requests & bugs
├── Pull Requests tab - Code reviews
├── Projects tab - Project board
├── Wiki tab - Documentation (optional)
└── Insights tab - Stats & graphs
```

## 🎯 Common Commands Reference

```bash
# Check status
git status

# View recent commits
git log --oneline -10

# View changes
git diff

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1

# Switch branch
git checkout branch-name

# View all branches
git branch -a

# Sync with remote
git fetch origin
git merge origin/main

# Push current branch
git push origin branch-name

# Delete local branch
git branch -d branch-name

# Delete remote branch
git push origin --delete branch-name
```

---

✅ **Your code is now ready for GitHub!**

Once pushed, your repository will be visible at:
```
https://github.com/YOUR_USERNAME/rag-legal-advisor
```

Happy coding! 🚀
