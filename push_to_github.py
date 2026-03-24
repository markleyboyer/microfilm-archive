"""
Push the rebuilt archive viewer to GitHub Pages.
Run this after build_viewer.py whenever you want to publish an update.

Usage:
    python push_to_github.py

Requires a GitHub Personal Access Token (classic, repo scope).
Set it as an environment variable to avoid being prompted each time:
    $env:GITHUB_TOKEN = "ghp_..."   (PowerShell)
"""

import base64, json, os, urllib.request, urllib.error, getpass

REPO      = 'markleyboyer/microfilm-archive'
SRC_FILE  = 'archive_viewer.html'
DEST_FILE = 'index.html'
API_BASE  = f'https://api.github.com/repos/{REPO}/contents/{DEST_FILE}'


def get_token():
    token = os.environ.get('GITHUB_TOKEN', '').strip()
    if not token:
        token = getpass.getpass('GitHub PAT (classic, repo scope): ').strip()
    return token


def api_request(url, token, method='GET', payload=None):
    headers = {
        'Authorization':        f'Bearer {token}',
        'Accept':               'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
        'User-Agent':           'microfilm-uploader',
    }
    if payload:
        headers['Content-Type'] = 'application/json'
    req = urllib.request.Request(url, data=payload, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read()), None
    except urllib.error.HTTPError as e:
        return None, f'HTTP {e.code}: {e.read().decode()[:200]}'


def main():
    token = get_token()

    # Read local file
    if not os.path.exists(SRC_FILE):
        print(f'Error: {SRC_FILE} not found. Run build_viewer.py first.')
        return

    with open(SRC_FILE, 'rb') as f:
        content = base64.b64encode(f.read()).decode()

    # Get current SHA (required for updates)
    current, err = api_request(API_BASE, token)
    if err:
        print(f'Could not reach GitHub: {err}')
        return
    sha = current['sha']

    # Push update
    payload = json.dumps({
        'message': 'Update archive viewer',
        'content': content,
        'sha':     sha,
    }).encode()

    result, err = api_request(API_BASE, token, method='PUT', payload=payload)
    if err:
        print(f'Push failed: {err}')
    else:
        print(f'Pushed successfully.')
        print(f'Commit: {result["commit"]["html_url"]}')
        print(f'Live at: https://markleyboyer.github.io/microfilm-archive/ (updates in ~1 min)')


if __name__ == '__main__':
    main()
