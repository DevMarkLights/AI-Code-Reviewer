import httpx
import re
import os
import base64

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

async def fetch_diff(pr_url: str) -> str:
    match = re.match(r"https://github\.com/([^/]+)/([^/]+)/pull/(\d+)", pr_url)
    if not match:
        raise ValueError("Invalid PR URL")
    
    owner, repo, pr_number = match.groups()
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files",
            headers={
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json"
            }
        )
        response.raise_for_status()
        
        files = response.json()
        
        full_diff = ""
        
        # Step 2 — for each file fetch full contents
        for file in files:
            filename = file['filename']
            contents_url = file['contents_url']
            
            contents_response = await client.get(
                contents_url,
                headers={
                    "Authorization": f"Bearer {GITHUB_TOKEN}",
                    "Accept": "application/vnd.github.v3+json"
                }
            )
            contents_response.raise_for_status()
            contents = contents_response.json()
            
            # contents are base64 encoded
            decoded = base64.b64decode(contents['content'].replace('\n', '')).decode('utf-8')
            
            full_diff += f"\n\n### File: {filename}\n"
            full_diff += f"**Changed lines:**\n{file['patch']}\n"  # just the diff
            full_diff += f"**Full file:**\n```\n{decoded}\n```"
            
            # full_diff += f"\n\n### File: {filename}\n```\n{decoded}\n```"
        
        return full_diff
        

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