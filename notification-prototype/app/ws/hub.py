import json

from typing import Set
from fastapi import WebSocket

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