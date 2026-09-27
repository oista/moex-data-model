# moex-git-adapter

Outbound adapter for published Git assets (ADR-002). Application code depends on
`GitProvider`, not GitHub DTOs.

## Local backend

`LocalGitProvider` shells out to `git` in a working tree (no PyGithub).

```python
from moex_git import LocalGitProvider

git = LocalGitProvider(repo_root)
data = git.get_file("HEAD", "README.md")
```
