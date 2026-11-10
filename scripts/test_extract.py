import urllib.request

boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
body = (
    f'--{boundary}\r\n'
    'Content-Disposition: form-data; name="file"; filename="test.txt"\r\n'
    'Content-Type: text/plain\r\n\r\n'
    'Python, Flask, React, Docker, Kubernetes\r\n'
    f'--{boundary}--\r\n'
).encode('utf-8')

req = urllib.request.Request(
    'http://127.0.0.1:5000/api/extract',
    data=body,
    headers={'Content-Type': f'multipart/form-data; boundary={boundary}'}
)
try:
    with urllib.request.urlopen(req) as resp:
        print('Extract status:', resp.status, resp.read().decode('utf-8')[:200])
except Exception as e:
    print('Extract error:', e)

