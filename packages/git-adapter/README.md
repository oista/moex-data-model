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

## GitHub (read-only)

`GitHubGitProvider` uses GitHub REST (`httpx`) for `get_file` / `resolve_revision` /
`list_revisions`. Writes raise `NotImplementedError`.

Env: `MOEX_GITHUB_TOKEN`, `MOEX_GITHUB_REPO=owner/name`.
