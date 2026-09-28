# moex-git-adapter

Outbound adapter for published Git assets (ADR-002). Application code depends on
`GitProvider`, not GitHub DTOs.

## Factory

```python
from moex_git import make_git_provider

# MOEX_GIT_PROVIDER=local|github (default local)
git = make_git_provider(repo_root=".")
```

## Local backend

`LocalGitProvider` shells out to `git` in a working tree.

```python
from moex_git import LocalGitProvider

git = LocalGitProvider(repo_root)
data = git.get_file("HEAD", "README.md")
```

## GitHub

`GitHubGitProvider` uses GitHub REST (`httpx`) for read and write:

- read: `get_file` / `resolve_revision` / `list_revisions`
- write: `create_branch` / `commit_files` / `create_review` (opens PR)

Env: `MOEX_GITHUB_TOKEN`, `MOEX_GITHUB_REPO=owner/name`, `MOEX_GITHUB_BASE=main`.
