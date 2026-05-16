from flask import Flask, request, send_file, jsonify
import requests
import re

app = Flask(__name__)

def parse_github_url(url):
    """Parse GitHub URL"""
    pattern = r'github\.com/([^/]+)/([^/]+)'
    match = re.search(pattern, url)
    if match:
        owner = match.group(1)
        repo = match.group(2)
        branch = 'main'
        if '/tree/' in url:
            branch = url.split('/tree/')[1].split('/')[0]
        return owner, repo, branch
    return None, None, None

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>GitHub Download Proxy</title>
        <style>
            body { font-family: Arial; max-width: 600px; margin: 50px auto; padding: 20px; }
            input { width: 100%; padding: 10px; margin: 10px 0; box-sizing: border-box; }
            button { padding: 10px 20px; background: #0070f3; color: white; border: none; cursor: pointer; }
            .result { margin-top: 20px; padding: 10px; background: #f0f0f0; }
        </style>
    </head>
    <body>
        <h1>📦 GitHub Repository Download Proxy</h1>
        <input type="text" id="url" placeholder="https://github.com/owner/repo">
        <button onclick="download()">Download ZIP</button>
        <div id="result" class="result"></div>
        <script>
            function download() {
                const url = document.getElementById('url').value;
                if (!url) return;
                window.location.href = '/api/download?url=' + encodeURIComponent(url);
                document.getElementById('result').innerHTML = 'Downloading...';
            }
        </script>
    </body>
    </html>
    '''

@app.route('/api/download')
def download():
    """Download GitHub repository"""
    repo_url = request.args.get('url')

    if not repo_url:
        return jsonify({'error': 'url parameter required'}), 400

    owner, repo, branch = parse_github_url(repo_url)

    if not owner or not repo:
        return jsonify({'error': 'Invalid GitHub URL'}), 400

    download_url = f"https://api.github.com/repos/{owner}/{repo}/zipball/{branch}"

    response = requests.get(download_url, stream=True)

    if response.status_code != 200:
        return jsonify({'error': f'Download failed: HTTP {response.status_code}'}), 500

    return send_file(
        response.raw,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f"{owner}_{repo}_{branch}.zip"
    )