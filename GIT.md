# Git Workflow for Forked Repositories

This document explains the git workflow when working with a forked repository.

## Initial Setup

After forking a repository on GitHub:

```bash
# Clone the original repo (or use your existing clone)
git clone git@github.com:ORIGINAL_OWNER/REPO.git
cd REPO

# Add your fork as a remote
git remote add fork git@github.com:YOUR_USERNAME/REPO.git

# Verify remotes
git remote -v
```

You should see two remotes:
- `origin` → original repository
- `fork` → your fork

## Pushing Changes

```bash
# Make your changes...

# Ensure you're on the main branch (or create a feature branch)
git branch -M main

# Push to your fork
git push -u fork main
```

## Syncing Upstream Changes

When the original repository has updates:

```bash
# Fetch changes from original repo
git fetch origin

# Merge upstream changes into your branch
git merge origin/main

# Push the merged changes to your fork
git push fork main
```

## Remotes Reference

| Remote | Purpose | URL Example |
|--------|---------|-------------|
| `origin` | Original repository (upstream) | `git@github.com:AndyMik90/Auto-Claude.git` |
| `fork` | Your personal fork | `git@github.com:arman-jalili/Auto-Claude.git` |

## Common Commands

```bash
# Check current branch
git branch

# Switch branches
git checkout <branch-name>

# Create and switch to a new branch
git checkout -b <branch-name>

# View remote configuration
git remote -v

# Add a new remote
git remote add <name> <url>

# Remove a remote
git remote remove <name>

# Rename a remote
git remote rename <old-name> <new-name>
```

## Workflow Summary

1. **Fork** the repository on GitHub
2. **Clone** the original repository (or use existing)
3. **Add** your fork as a remote named `fork`
4. **Make** your changes
5. **Push** to `fork` remote
6. **Sync** from `origin` regularly to stay up-to-date
7. **Submit** a pull request from your fork to the original repo (if contributing back)
