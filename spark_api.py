import time, hashlib, hmac, base64, json
import websocket
from datetime import datetime
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time

# 填入你从讯飞控制台获取的参数
APPID = "bfc279af"
APISecret = "MmIxMGY4YzAzMWQ4MmRiYzAxYzk1YWMy"
APIKey = "a89fac88179e39a0dd41e2bcd909c0a2"
host = "spark-api.xf-yun.com"
path = "/v1/x1"
Spark_url = f"wss://{host}{path}"

# 存储用户上下文
session_context = {}

def create_url():
    now = datetime.now()
    date = format_date_time(time.mktime(now.timetuple()))
    signature_origin = f"host: {host}\ndate: {date}\nGET {path} HTTP/1.1"
    signature_sha = hmac.new(APISecret.encode(), signature_origin.encode(), hashlib.sha256).digest()
    signature = base64.b64encode(signature_sha).decode()
    authorization_origin = f'api_key="{APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature}"'
    authorization = base64.b64encode(authorization_origin.encode()).decode()
    v = {"authorization": authorization, "date": date, "host": host}
    return f"{Spark_url}?{urlencode(v)}"

def ask_spark(question, uid="default_user"):
    history = session_context.get(uid, [])
    history.append({"role": "user", "content": question})
    request_data = {
        "header": {"app_id": APPID, "uid": uid},
        "parameter": {
            "chat": {"domain": "x1", "temperature": 0.5, "max_tokens": 1024}
        },
        "payload": {"message": {"text": history}}
    }

    url = create_url()
    ws = websocket.create_connection(url)
    ws.send(json.dumps(request_data))
    result = ""
    while True:
        msg = ws.recv()
        msg_data = json.loads(msg)
        if msg_data["header"]["code"] != 0:
            break
        choices = msg_data["payload"]["choices"]
        result += choices["text"][0].get("content", "")
        if choices["status"] == 2:
            break
    ws.close()
    history.append({"role": "assistant", "content": result})
    session_context[uid] = history[-10:]  # 最多保留10轮对话
    return result