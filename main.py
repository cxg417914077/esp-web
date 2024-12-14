from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
import json
from paho.mqtt import client as mqtt_client

# MQTT 配置
BROKER = "broker.emqx.io"
PORT = 1883
CLIENT_ID = f"fastapi-client-{json.dumps(__import__('random').getrandbits(8))}"
USERNAME = "emqx"
PASSWORD = "public"
TOPIC = "cxg/mqtt"

# FastAPI 实例
app = FastAPI()

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
        return {"message": "MQTT message sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 提供 HTML 页面
@app.get("/led", response_class=HTMLResponse)
async def server():
    html_file = open("index.html", 'r').read()
    return html_file


@app.get("/lcd", response_class=HTMLResponse)
async def server():
    html_file = open("light_control_text_input.html", 'r').read()
    return html_file


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)
