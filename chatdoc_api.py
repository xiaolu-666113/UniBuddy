import hashlib
import base64
import hmac
import time
import json
import requests

# 星火平台参数（确保已替换为你自己的）
APPID = "bfc279af"
API_SECRET = "MmIxMGY4YzAzMWQ4MmRiYzAxYzk1YWMy"
CHATDOC_UPLOAD_URL = "https://chatdoc.xfyun.cn/openapi/v1/file/upload"
CHATDOC_SPLIT_URL = "https://chatdoc.xfyun.cn/openapi/v1/file/split"
CHATDOC_EMBED_URL = "https://chatdoc.xfyun.cn/openapi/v1/file/embedding"
CHATDOC_QA_WS = "wss://chatdoc.xfyun.cn/openapi/chat"


def gen_signature():
    timestamp = str(int(time.time()))
    raw = APPID + timestamp
    md5 = hashlib.md5()
    md5.update(raw.encode())
    checksum = md5.hexdigest()

    signature = hmac.new(
        API_SECRET.encode(), checksum.encode(), digestmod=hashlib.sha1
    ).digest()
    signature_base64 = base64.b64encode(signature).decode()

    return {
        "appId": APPID,
        "timestamp": timestamp,
        "signature": signature_base64,
    }


def upload_txt_file(file_path, file_name):
    headers = gen_signature()
    with open(file_path, "rb") as f:
        files = {"file": (file_name, f)}
        data = {
            "fileName": file_name,
            "fileType": "wiki",
            "needSummary": False,
            "stepByStep": False,
        }
        resp = requests.post(CHATDOC_UPLOAD_URL, data=data, files=files, headers=headers)
        resp_json = resp.json()
        if resp_json["code"] == 0:
            return resp_json["data"]["fileId"]
        else:
            raise Exception("Upload failed: " + str(resp_json))


def split_file(file_id):
    headers = gen_signature()
    body = {
        "splitType": "wiki",
        "isSplitDefault": False,
        "fileIds": [file_id],
        "wikiSplitExtends": {
            "chunkSeparators": ["DQo="],  # Base64 的换行符（\n）
            "minChunkSize": 100,
            "chunkSize": 2000,
        },
    }
    resp = requests.post(CHATDOC_SPLIT_URL, json=body, headers=headers)
    if resp.json()["code"] != 0:
        raise Exception("Split failed: " + resp.text)


def embed_file(file_id):
    headers = gen_signature()
    body = {"fileIds": [file_id]}
    resp = requests.post(CHATDOC_EMBED_URL, data=body, headers=headers)
    if resp.json()["code"] != 0:
        raise Exception("Embedding failed: " + resp.text)


def ask_question(file_id, question_text):
    import websocket
    import _thread as thread
    import ssl

    headers = gen_signature()
    query_url = CHATDOC_QA_WS + f"?appId={headers['appId']}&timestamp={headers['timestamp']}&signature={headers['signature']}"

    result = {"answer": ""}

    def on_message(ws, message):
        data = json.loads(message)
        if data["code"] != 0:
            ws.close()
            raise Exception("QA Error: " + str(data))

        # ✅ 判断 content 字段是否存在再拼接
        if "content" in data:
            result["answer"] += data["content"]

        if data["status"] == 2:
            ws.close()

    def on_error(ws, error):
        print("WebSocket Error:", error)

    def on_close(ws, *args):
        pass

    def on_open(ws):
        def run(*args):
            body = {
                "chatExtends": {
                    "wikiPromptTpl": "请将以下内容作为已知信息：\n<wikicontent>\n请根据以上内容回答用户的问题。\n问题:<wikiquestion>\n回答:",
                    "wikiFilterScore": 0.83,
                    "temperature": 0.5,
                },
                "fileIds": [file_id],
                "messages": [{"role": "user", "content": question_text}],
            }
            ws.send(json.dumps(body))
        thread.start_new_thread(run, ())

    ws = websocket.WebSocketApp(query_url, on_message=on_message, on_error=on_error, on_close=on_close, on_open=on_open)
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
    return result["answer"]