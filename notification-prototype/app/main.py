# @hfidelis

import asyncio
import json
import os
import random
import string
from datetime import datetime
from typing import Set

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import aio_pika

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost/")
EXCHANGE_NAME = "orders"
QUEUE_NAME = "order_updates"
ROUTING_KEY = "order.update"

app = FastAPI(title="Protótipo de Notificações")
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

class Hub:
    def __init__(self):
        self.connections: Set[WebSocket] = set()

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.connections.add(ws)

    def disconnect(self, ws: WebSocket):
        self.connections.discard(ws)

    async def broadcast(self, message: dict):
        text = json.dumps(message, ensure_ascii=False)
        to_remove = []
        for ws in list(self.connections):
            try:
                await ws.send_text(text)
            except:
                to_remove.append(ws)
        for ws in to_remove:
            self.disconnect(ws)


hub = Hub()


rabbit_connection: aio_pika.RobustConnection | None = None
channel: aio_pika.abc.AbstractChannel | None = None
exchange: aio_pika.abc.AbstractExchange | None = None
queue: aio_pika.abc.AbstractQueue | None = None


async def setup_rabbitmq():
    global rabbit_connection, channel, exchange, queue
    rabbit_connection = await aio_pika.connect_robust(RABBITMQ_URL)
    channel = await rabbit_connection.channel()
    await channel.set_qos(prefetch_count=50)
    exchange = await channel.declare_exchange(EXCHANGE_NAME, aio_pika.ExchangeType.DIRECT, durable=True)
    queue = await channel.declare_queue(QUEUE_NAME, durable=True)
    await queue.bind(exchange, routing_key=ROUTING_KEY)


async def consume_and_forward():
    global queue
    assert queue is not None
    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process(requeue=False):
                try:
                    payload = json.loads(message.body.decode("utf-8"))
                    await hub.broadcast(payload)
                except Exception:
                    continue


@app.on_event("startup")
async def startup_event():
    await setup_rabbitmq()
    asyncio.create_task(consume_and_forward())


@app.on_event("shutdown")
async def shutdown_event():
    if rabbit_connection:
        await rabbit_connection.close()


STATUSES = ["prepared", "shipped", "delivered"]


def new_order_id() -> str:
    return "ORD-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))


async def publish_status(order_id: str, status: str):
    assert exchange is not None
    message = {"order_id": order_id, "status": status, "ts": datetime.utcnow().isoformat() + "Z"}
    body = json.dumps(message).encode("utf-8")
    await exchange.publish(
        aio_pika.Message(body=body, delivery_mode=aio_pika.DeliveryMode.PERSISTENT, content_type="application/json"),
        routing_key=ROUTING_KEY,
    )


class SimulateIn(BaseModel):
    n_orders: int = Field(gt=0, le=5000)
    min_delay_ms: int = Field(default=300, ge=0)
    max_delay_ms: int = Field(default=1200, ge=0)


@app.get("/", response_class=FileResponse)
async def root():
    return "static/index.html"


@app.post("/simulate")
async def simulate(payload: SimulateIn):
    orders = [new_order_id() for _ in range(payload.n_orders)]

    async def simulate_order(order_id: str):
        delays = [
            random.randint(payload.min_delay_ms, payload.max_delay_ms) / 1000,
            random.randint(payload.min_delay_ms, payload.max_delay_ms) / 1000,
        ]
        await publish_status(order_id, "prepared")
        await asyncio.sleep(delays[0])
        await publish_status(order_id, "shipped")
        await asyncio.sleep(delays[1])
        await publish_status(order_id, "delivered")

    for oid in orders:
        asyncio.create_task(simulate_order(oid))

    return {"orders": orders, "message": f"Simulação iniciada para {len(orders)} pedidos"}


@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    await hub.connect(websocket)
    try:
        while True:
              # Mantém conexão viva / keep-alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        hub.disconnect(websocket)
