"""Compatibility re-export — prefer ``moex_git.github.GitHubGitProvider``."""

from moex_git.github import GitHubGitProvider, GitHubGitProviderStub

__all__ = ["GitHubGitProvider", "GitHubGitProviderStub"]
