import httpx
import re
import os

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

async def fetch_diff(pr_url: str) -> str:
    match = re.match(r"https://github\.com/([^/]+)/([^/]+)/pull/(\d+)", pr_url)
    if not match:
        raise ValueError("Invalid PR URL")
    
    owner, repo, pr_number = match.groups()
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}",
            headers={
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3.diff"
            }
        )
        response.raise_for_status()
        return response.text

async def postComment(url:str, comment:str):
    
    match = re.match(r"https://github\.com/([^/]+)/([^/]+)/pull/(\d+)", url)
    if not match:
        raise ValueError("Invalid PR URL")
    
    owner, repo, pr_number = match.groups()
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments",
            headers={
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json"
            },
            json={"body": comment}
        )
        response.raise_for_status()