# @hfidelis

import random
import string
import asyncio

from datetime import datetime

from fastapi import (
    FastAPI,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from ws.hub import hub
from models.base import SimulatePayload
from broker.utils import (
    rabbit_connection,
    setup_rabbitmq,
    consume_and_forward,
    publish_on_exchange,
)

app = FastAPI(title="Protótipo de Notificações")
app.mount("/static", StaticFiles(directory="static", html=True), name="static")


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
    message = {"order_id": order_id, "status": status, "ts": datetime.utcnow().isoformat() + "Z"}
    await publish_on_exchange(message)


@app.get("/", response_class=FileResponse)
async def root():
    return "static/index.html"


@app.post("/simulate")
async def simulate(payload: SimulatePayload):
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

    return {
        "orders": orders,
        "message": f"Simulação iniciada para {len(orders)} pedidos"
    }


@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    await hub.connect(websocket)
    try:
        while True:
              # Mantém conexão viva / keep-alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        hub.disconnect(websocket)
