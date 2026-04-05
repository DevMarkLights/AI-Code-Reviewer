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
        MAX_TOTAL_CHARS = 4000

        for file in files:
            if len(full_diff) >= MAX_TOTAL_CHARS:
                break
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
            
            MAX_FILE_CHARS = 1500
            MAX_PATCH_CHARS = 1500

            full_diff += f"### File: {filename}\n"
            full_diff += f"**Changes:**\n{file['patch'][:MAX_PATCH_CHARS]}\n\n"

            if len(decoded) <= MAX_FILE_CHARS:
                full_diff += f"**Full file context:**\n```python\n{decoded}\n```\n\n"
            else:
                full_diff += f"**Note:** File too large, showing diff only.\n\n"
                    
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