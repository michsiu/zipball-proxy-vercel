from flask import Flask, request, send_file, jsonify
import requests
import os
import re
import tempfile
import time

app = Flask(__name__)

def parse_github_url(url):
    """解析 GitHub URL"""
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
        <title>GitHub 下载代理</title>
        <style>
            body { font-family: Arial; max-width: 600px; margin: 50px auto; padding: 20px; }
            input { width: 100%; padding: 10px; margin: 10px 0; }
            button { padding: 10px 20px; background: #0070f3; color: white; border: none; cursor: pointer; }
            .result { margin-top: 20px; padding: 10px; background: #f0f0f0; }
        </style>
    </head>
    <body>
        <h1>📦 GitHub 仓库下载代理</h1>
        <input type="text" id="url" placeholder="https://github.com/owner/repo">
        <button onclick="download()">下载 ZIP</button>
        <div class="result" id="result"></div>
        <script>
            function download() {
                const url = document.getElementById('url').value;
                if (!url) return;
                window.location.href = `/api/download?url=${encodeURIComponent(url)}`;
                document.getElementById('result').innerHTML = '下载中...';
            }
        </script>
    </body>
    </html>
    '''

@app.route('/api/download')
def download():
    """下载 GitHub 仓库"""
    repo_url = request.args.get('url')
    
    if not repo_url:
        return jsonify({'error': '需要 url 参数'}), 400
    
    owner, repo, branch = parse_github_url(repo_url)
    
    if not owner or not repo:
        return jsonify({'error': '无效的 GitHub URL'}), 400
    
    # GitHub API 下载链接
    download_url = f"https://api.github.com/repos/{owner}/{repo}/zipball/{branch}"
    
    # 下载
    response = requests.get(download_url, stream=True)
    
    if response.status_code != 200:
        return jsonify({'error': f'下载失败: HTTP {response.status_code}'}), 500
    
    # 返回文件
    return send_file(
        response.raw,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f"{owner}_{repo}_{branch}.zip"
    )

# Vercel 需要这个
app.debug = False