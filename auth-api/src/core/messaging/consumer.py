import asyncio
import logging
from typing import Dict, Callable

from core.messaging.rabbitmq import rabbitmq_client
from core.messaging.handlers import handle_user_created

logger = logging.getLogger(__name__)

EVENT_HANDLERS: Dict[str, Callable] = {
    "user.created": handle_user_created
}


async def start_consuming():
    try:
        await rabbitmq_client.connect()

        for routing_key, handler in EVENT_HANDLERS.items():
            await rabbitmq_client.subscribe(
                exchange_name="user_events",
                routing_key=routing_key,
                callback=handler
            )

        while True:
            await asyncio.sleep(15)

    except Exception as e:
        logger.error(f"Error in consumer: {str(e)}")
        raise
    finally:
        await rabbitmq_client.close()


def run_consumer():
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(start_consuming())
    except KeyboardInterrupt:
        logger.info("Shutting down consumer...")
    finally:
        loop.close()
