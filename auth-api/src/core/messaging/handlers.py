import json
import logging
from aio_pika import IncomingMessage
from sqlalchemy import select
from datetime import datetime

from db.database import get_session
from db.models.user import User
from core.utils.password import get_password_hash

logger = logging.getLogger(__name__)


async def handle_user_created(message: IncomingMessage):
    """
    Обработчик события создания пользователя.
    Создает пользователя в auth сервисе на основе данных из users сервиса.
    """
    async with message.process():
        try:
            data = json.loads(message.body.decode())
            logger.info(f"Received user.created event for user {data['email']}")

            session = await anext(get_session())
            try:
                # Проверяем, нет ли уже такого пользователя
                result = await session.execute(
                    select(User).where(User.email == data['email'])
                )
                existing_user = result.scalar_one_or_none()

                if existing_user:
                    logger.warning(f"User {data['email']} already exists in auth service")
                    await message.ack()
                    return

                # Создаем пользователя
                new_user = User(
                    email=data['email'],
                    hashed_password=get_password_hash(data['password']),
                    full_name=data['full_name'],
                    role=data['role'],
                    is_active=data['is_active'],
                    is_verified=data['is_verified'],
                    created_at=datetime.fromisoformat(data['created_at']),
                    updated_at=datetime.fromisoformat(data['updated_at'])
                )

                session.add(new_user)
                await session.commit()

                logger.info(f"Successfully created auth record for user {data['email']}")
                await message.ack()

            except Exception as e:
                logger.error(f"Error processing user creation: {str(e)}")
                await session.rollback()
                raise
            finally:
                await session.close()

        except KeyError as e:
            logger.error(f"Invalid message format: {str(e)}")
            # Если формат сообщения неверный, не пытаемся его переобработать
            await message.reject(requeue=False)

        except Exception as e:
            logger.error(f"Failed to process user.created event: {str(e)}")
            # Другие ошибки - возвращаем в очередь для повторной попытки
            await message.reject(requeue=True)