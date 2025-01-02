import json
import aio_pika
from typing import Any
import logging

from core.config.settings import settings

logger = logging.getLogger(__name__)


class RabbitMQClient:
    def __init__(self):
        self.connection = None
        self.channel = None

    async def connect(self):
        if not self.connection:
            try:
                self.connection = await aio_pika.connect_robust(
                    f"amqp://{settings.rabbitmq.user}:{settings.rabbitmq.password}@{settings.rabbitmq.host}:{settings.rabbitmq.port}/"
                )
                self.channel = await self.connection.channel()
                logger.info("Successfully connected to RabbitMQ")
            except Exception as e:
                logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
                raise

    async def close(self):
        if self.connection:
            await self.connection.close()
            self.connection = None
            self.channel = None

    async def publish_message(self, exchange_name: str, routing_key: str, message: Any):
        if not self.channel:
            await self.connect()

        try:
            exchange = await self.channel.declare_exchange(
                exchange_name,
                aio_pika.ExchangeType.TOPIC,
                durable=True
            )

            message_body = json.dumps(message).encode()
            await exchange.publish(
                aio_pika.Message(
                    body=message_body,
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                ),
                routing_key=routing_key
            )
            logger.info(f"Published message to {exchange_name} with routing key {routing_key}")
        except Exception as e:
            logger.error(f"Failed to publish message: {str(e)}")
            raise

    async def subscribe(self, exchange_name: str, routing_key: str, callback):
        if not self.channel:
            await self.connect()

        try:
            exchange = await self.channel.declare_exchange(
                exchange_name,
                aio_pika.ExchangeType.TOPIC,
                durable=True
            )

            queue = await self.channel.declare_queue(
                f"{exchange_name}.{routing_key}",
                durable=True
            )

            await queue.bind(exchange, routing_key)

            await queue.consume(callback)
            logger.info(f"Subscribed to {exchange_name} with routing key {routing_key}")
        except Exception as e:
            logger.error(f"Failed to subscribe: {str(e)}")
            raise


rabbitmq_client = RabbitMQClient()
