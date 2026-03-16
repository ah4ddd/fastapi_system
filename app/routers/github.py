from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession # connection to your database
from app.database import get_db # type:ignore
from app.models import GitHubReposResponse, GitHubRepo # type:ignore
from app.db_models import GitHubRepoDB # type:ignore
from app.services.github_api import fetch_user_repos, extract_top_repos # type:ignore
from datetime import datetime

router = APIRouter(prefix="/github", tags=["github"])


@router.get("/repos/{username}", response_model=GitHubReposResponse)
async def get_user_repos(username: str, db: AsyncSession = Depends(get_db)):
    """
    Fetch GitHub user's top repositories by star count.

    - Fetches from GitHub API
    - Stores in database
    - Returns top 10 repos by stars
    """

    # Fetch from GitHub
    repos = await fetch_user_repos(username)

    if repos is None:
        raise HTTPException(
            status_code=404,
            detail=f"Could not fetch repos for {username}"
        )
    # Some users have no public repos. Handle gracefully.
    if len(repos) == 0:
        raise HTTPException(
            status_code=404,
            detail=f"User {username} has no public repositories"
        )

    # Extract top repos
    top_repos = extract_top_repos(repos, limit=10)

    # Current timestamp
    fetched_at = datetime.utcnow().isoformat()

    # Store each repo in database
    # Loop through repos, create DB object for each, commit once at end
    for repo in top_repos:
        db_repo = GitHubRepoDB(
            username=username,
            repo_name=repo["name"],
            description=repo["description"],
            stars=repo["stars"],
            language=repo["language"],
            url=repo["url"],
            updated_at=repo["updated_at"],
            fetched_at=fetched_at
        )
        db.add(db_repo)

    await db.commit()

    # Build response. **repo = unpacks dict into Pydantic model.
    repo_models = [GitHubRepo(**repo) for repo in top_repos]

    return GitHubReposResponse(
        username=username,
        total_repos=len(repos),
        top_repos=repo_models,
        fetched_at=fetched_at
    )
