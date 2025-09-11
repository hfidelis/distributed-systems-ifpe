import os
import json
import aio_pika

from ws.hub import hub

EXCHANGE_NAME = "orders"
QUEUE_NAME = "order_updates"
ROUTING_KEY = "order.update"
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost/")

rabbit_connection: aio_pika.RobustConnection | None = None
channel: aio_pika.abc.AbstractChannel | None = None
exchange: aio_pika.abc.AbstractExchange | None = None
queue: aio_pika.abc.AbstractQueue | None = None


async def setup_rabbitmq():
    global rabbit_connection, channel, exchange, queue

    rabbit_connection = await aio_pika.connect_robust(RABBITMQ_URL)

    channel = await rabbit_connection.channel()
    await channel.set_qos(prefetch_count=50)

    exchange = await channel.declare_exchange(
        EXCHANGE_NAME,
        aio_pika.ExchangeType.DIRECT,
        durable=True
    )

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


async def publish_on_exchange(message: dict):
    global exchange
    assert exchange is not None

    body = json.dumps(message).encode("utf-8")

    await exchange.publish(
        aio_pika.Message(
            body=body,
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            content_type="application/json"
        ),
        routing_key=ROUTING_KEY,
    )