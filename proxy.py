from flask import Flask, request, Response
import requests
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)

# Replace https://IP:1935 -> http://IP:1935 inside m3u8 manifests
IP_1935_RE = re.compile(r'https://(\d{1,3}(?:\.\d{1,3}){3}):1935', flags=re.IGNORECASE)

@app.get('/proxy')
def proxy():
    url = request.args.get('url')
    if not url:
        return 'Missing url param', 400
    try:
        # follow redirects; stream=False so we can rewrite small manifest bodies
        r = requests.get(url, timeout=15, allow_redirects=True)
    except Exception as e:
        return (f'Upstream fetch failed: {e}', 502)

    content_type = r.headers.get('Content-Type','')
    headers = {k:v for k,v in r.headers.items() if k.lower() not in ('content-encoding','transfer-encoding','connection')}

    # If this looks like an HLS/M3U8 manifest, rewrite https IP:1935 -> http
    if 'mpegurl' in content_type.lower() or url.lower().endswith('.m3u8'):
        text = r.text
        # rewrite https://IP:1935 to http://IP:1935
        new_text = IP_1935_RE.sub(r'http://\1:1935', text)
        # Also rewrite any https://...:1935 occurrences more broadly
        new_text = re.sub(r'https://(\d+\.\d+\.\d+\.\d+):([0-9]+)', lambda m: f'http://{m.group(1)}:{m.group(2)}' if m.group(2)=='1935' else m.group(0), new_text)
        return Response(new_text, status=r.status_code, headers={**headers, 'Access-Control-Allow-Origin': '*'})

    # Otherwise stream back the raw bytes and preserve headers, with CORS
    return Response(r.content, status=r.status_code, headers={**headers, 'Access-Control-Allow-Origin': '*'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
