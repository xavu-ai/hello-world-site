"""GitHub API client with retry logic and error handling."""
import os
from typing import Any

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)


class GitHubAPIError(Exception):
    """GitHub API error exception."""

    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        self.message = message
        super().__init__(f"GitHub API error ({status_code}): {message}")


class GitHubRateLimitError(GitHubAPIError):
    """GitHub API rate limit exceeded error."""

    def __init__(self, message: str, retry_after: int | None = None) -> None:
        self.retry_after = retry_after
        super().__init__(status_code=429, message=message)


class GitHubClient:
    """GitHub API client with authentication and retry logic."""

    BASE_URL = "https://api.github.com"

    def __init__(self, token: str | None = None) -> None:
        """Initialize GitHub client.

        Args:
            token: GitHub personal access token. If not provided,
                   reads from GITHUB_TOKEN env variable.
        """
        self.token = token or os.environ.get("GITHUB_TOKEN")
        if not self.token:
            raise ValueError("GitHub token is required. Set GITHUB_TOKEN environment variable.")

    def _get_headers(self) -> dict[str, str]:
        """Get headers for API requests."""
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    @retry(
        retry=retry_if_exception_type(GitHubRateLimitError),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        stop=stop_after_attempt(5),
    )
    async def _request(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> dict[str, Any] | list[Any]:
        """Make HTTP request with retry logic.

        Args:
            method: HTTP method
            url: Request URL
            **kwargs: Additional arguments for httpx request

        Returns:
            Response JSON data

        Raises:
            GitHubAPIError: On API error
            GitHubRateLimitError: On rate limit error
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self._get_headers(),
                    **kwargs,
                )

                if response.status_code == 429:
                    retry_after = response.headers.get("Retry-After")
                    raise GitHubRateLimitError(
                        message="GitHub API rate limit exceeded",
                        retry_after=int(retry_after) if retry_after else None,
                    )

                if response.status_code >= 400:
                    error_data = response.json() if response.content else {}
                    message = error_data.get("message", response.text)
                    raise GitHubAPIError(status_code=response.status_code, message=message)

                return response.json()

            except httpx.HTTPError as e:
                raise GitHubAPIError(
                    status_code=0,
                    message=f"HTTP error occurred: {str(e)}",
                )

    async def create_project(
        self,
        name: str,
        description: str | None = None,
        owner: str | None = None,
        include_issues: bool = True,
        include_wiki: bool = False,
    ) -> dict[str, Any]:
        """Create a new GitHub project.

        Args:
            name: Project name
            description: Project description
            owner: Owner/organization (uses authenticated user if not provided)
            include_issues: Enable issue tracking
            include_wiki: Enable wiki

        Returns:
            Created project data
        """
        if owner:
            url = f"{self.BASE_URL}/orgs/{owner}/projects"
        else:
            url = f"{self.BASE_URL}/user/projects"

        data: dict[str, Any] = {
            "name": name,
            "body": description,
            "include_issues": include_issues,
            "include_wiki": include_wiki,
        }

        return await self._request("POST", url, json=data)

    async def get_project(self, project_id: int) -> dict[str, Any]:
        """Get a GitHub project by ID.

        Args:
            project_id: GitHub project ID

        Returns:
            Project data
        """
        url = f"{self.BASE_URL}/projects/{project_id}"
        return await self._request("GET", url)

    async def update_project(
        self,
        project_id: int,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Update a GitHub project.

        Args:
            project_id: GitHub project ID
            **kwargs: Fields to update

        Returns:
            Updated project data
        """
        url = f"{self.BASE_URL}/projects/{project_id}"
        return await self._request("PATCH", url, json=kwargs)

    async def delete_project(self, project_id: int) -> None:
        """Delete a GitHub project.

        Args:
            project_id: GitHub project ID
        """
        url = f"{self.BASE_URL}/projects/{project_id}"
        await self._request("DELETE", url)


def get_github_client() -> GitHubClient:
    """Factory function to get GitHub client instance.

    Returns:
        GitHubClient instance
    """
    return GitHubClient()
