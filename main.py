from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
import json
from paho.mqtt import client as mqtt_client
from fastapi.staticfiles import StaticFiles

# MQTT 配置
BROKER = "broker.emqx.io"
PORT = 1883
CLIENT_ID = f"fastapi-client-{json.dumps(__import__('random').getrandbits(8))}"
USERNAME = "emqx"
PASSWORD = "public"
TOPIC = "cxg/mqtt"

# FastAPI 实例
app = FastAPI()
app.mount("/html", StaticFiles(directory="templates", html=True), name="static")
# Pydantic 模型
class Command(BaseModel):
    cmd: int
    value: str

# 连接到 MQTT Broker
def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print(f"Failed to connect, return code {rc}")
    
    client = mqtt_client.Client()
    client.username_pw_set(USERNAME, PASSWORD)
    client.on_connect = on_connect
    client.connect(BROKER, PORT)
    return client

mqtt_client = connect_mqtt()
mqtt_client.loop_start()

# 处理 POST 请求
@app.post("/api/cmd")
async def control_device(command: Command):
    try:
        payload = command.dict()
        mqtt_client.publish(TOPIC, json.dumps(payload))
        print(f"Published: {payload} to topic {TOPIC}")
        return {"message": "消息下发成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 提供 HTML 页面
@app.get("/", response_class=HTMLResponse)
async def server():
    html_file = open("templates/index.html", 'r').read()
    return html_file


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)
