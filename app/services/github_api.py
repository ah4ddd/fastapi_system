"""
httpx supports:
    async requests
    connection pooling
    timeout control
    modern HTTP features
It's preferred for FastAPI async apps.
"""
import httpx # FastAPI server → GitHub API
from typing import List, Dict # type hinting.


async def fetch_user_repos(username: str) -> List[Dict] | None:
    """
    Fetch all public repositories for a GitHub user.

    Return list of repo dicts or None if request fails.

    Note: GitHub API returns 30 repos per page by default.
    For users with 100+ repos, you'd need pagination logic.
    For now, we fetch first page only.
    """

    url = f"https://api.github.com/users/{username}/repos"

    # GitHub requires User-Agent header
    headers = {
        # Give response formatted for API version 3
        "Accept": "application/vnd.github.v3+json",
        # REQUIRED by GitHub. They reject requests without it
        "User-Agent": "FastAPI-Learning-App"
    }

    # Query Parameters. These become: ?per_page=100&sort=updated
    params = {
        "per_page": 100,  # Max repos per page
        "sort": "updated",  # Sort by most recently updated
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=params, timeout=15.0)

            # Log rate limit info (good practice)
            rate_limit = response.headers.get("X-RateLimit-Remaining", "unknown")
            print(f"GitHub API calls remaining: {rate_limit}")

            if response.status_code == 200:
                # JSON → Python list of dicts
                repos = response.json()
                return repos
            elif response.status_code == 404:
                print(f"User {username} not found")
                return None
            elif response.status_code == 403:
                print("Rate limit exceeded")
                return None
            else:
                print(f"GitHub API error: {response.status_code}")
                return None

        except httpx.TimeoutException:
            print("Request timeout")
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None


def extract_top_repos(repos: List[Dict], limit: int = 10) -> List[Dict]:
    """
    Extract top repos by star count.

    Transforms GitHub's verbose response into clean data.
    """

    # Lambda is a small function that receives each repo dictionary.
    # It extracts the stargazers_count.
    # sorted() uses that value to order the repos.
    # reverse=True makes the order descending.
    # The result is stored in sorted_repos.
    sorted_repos = sorted(repos, key=lambda r: r.get("stargazers_count", 0), reverse=True)

    # Take top N
    top_repos = sorted_repos[:limit]

    # Extract relevant fields
    clean_repos = []
    for repo in top_repos:
        clean_repos.append({
            # Using .get() protects against missing fields.
            "name": repo.get("name", "unknown"),
            "description": repo.get("description", "No description"),
            "stars": repo.get("stargazers_count", 0),
            "language": repo.get("language", "Not specified"),
            "url": repo.get("html_url", ""),
            "updated_at": repo.get("updated_at", "")
        })

    return clean_repos
