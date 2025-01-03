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
    """Обработчик события создания пользователя"""
    async with message.process():
        try:
            data = json.loads(message.body.decode())
            logger.info(f"Received user.created event for user {data['email']}")

            session = await anext(get_session())
            try:
                result = await session.execute(
                    select(User).where(User.email == data['email'])
                )
                existing_user = result.scalar_one_or_none()

                if existing_user:
                    logger.warning(f"User {data['email']} already exists in auth service")
                    await message.ack()
                    return

                new_user = User(
                    id=data['id'],
                    email=data['email'],
                    hashed_password=get_password_hash(data['password']),
                    full_name=data['full_name'],
                    role_id=data['role_id'],
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
            await message.reject(requeue=False)

        except Exception as e:
            logger.error(f"Failed to process user.created event: {str(e)}")
            await message.reject(requeue=True)


async def handle_user_updated(message: IncomingMessage):
    """Обработчик события обновления пользователя"""
    async with message.process():
        try:
            data = json.loads(message.body.decode())
            logger.info(f"Received user.updated event for user {data['email']}")

            session = await anext(get_session())
            try:
                result = await session.execute(
                    select(User).where(User.id == data['id'])
                )
                user = result.scalar_one_or_none()

                if not user:
                    logger.error(f"User {data['email']} not found in auth service")
                    await message.reject(requeue=False)
                    return

                # Обновляем поля пользователя
                user.email = data['email']
                user.full_name = data['full_name']
                user.role_id = data['role_id']
                user.is_active = data['is_active']
                user.is_verified = data['is_verified']
                user.updated_at = datetime.fromisoformat(data['updated_at'])

                await session.commit()

                logger.info(f"Successfully updated auth record for user {data['email']}")
                await message.ack()

            except Exception as e:
                logger.error(f"Error processing user update: {str(e)}")
                await session.rollback()
                raise
            finally:
                await session.close()

        except KeyError as e:
            logger.error(f"Invalid message format: {str(e)}")
            await message.reject(requeue=False)

        except Exception as e:
            logger.error(f"Failed to process user.updated event: {str(e)}")
            await message.reject(requeue=True)


async def handle_user_email_updated(message: IncomingMessage):
    """Обработчик события смены email пользователя"""
    async with message.process():
        try:
            data = json.loads(message.body.decode())
            logger.info(f"Received user.email.updated event for user {data['email']}")

            session = await anext(get_session())
            try:
                result = await session.execute(
                    select(User).where(User.id == data['id'])
                )
                user = result.scalar_one_or_none()

                if not user:
                    logger.error(f"User {data['email']} not found in auth service")
                    await message.reject(requeue=False)
                    return

                # Обновляем email и статус верификации
                user.email = data['email']
                user.is_verified = data['is_verified']
                user.updated_at = datetime.fromisoformat(data['updated_at'])

                await session.commit()

                logger.info(f"Successfully updated email for user {data['email']}")
                await message.ack()

            except Exception as e:
                logger.error(f"Error processing email update: {str(e)}")
                await session.rollback()
                raise
            finally:
                await session.close()

        except KeyError as e:
            logger.error(f"Invalid message format: {str(e)}")
            await message.reject(requeue=False)

        except Exception as e:
            logger.error(f"Failed to process user.email.updated event: {str(e)}")
            await message.reject(requeue=True)


async def handle_user_password_updated(message: IncomingMessage):
    """Обработчик события смены пароля пользователя"""
    async with message.process():
        try:
            data = json.loads(message.body.decode())
            logger.info(f"Received user.password.updated event for user {data['email']}")

            session = await anext(get_session())
            try:
                result = await session.execute(
                    select(User).where(User.id == data['id'])
                )
                user = result.scalar_one_or_none()

                if not user:
                    logger.error(f"User {data['email']} not found in auth service")
                    await message.reject(requeue=False)
                    return

                # Обновляем пароль
                user.hashed_password = get_password_hash(data['password'])
                user.updated_at = datetime.fromisoformat(data['updated_at'])

                await session.commit()

                logger.info(f"Successfully updated password for user {data['email']}")
                await message.ack()

            except Exception as e:
                logger.error(f"Error processing password update: {str(e)}")
                await session.rollback()
                raise
            finally:
                await session.close()

        except KeyError as e:
            logger.error(f"Invalid message format: {str(e)}")
            await message.reject(requeue=False)

        except Exception as e:
            logger.error(f"Failed to process user.password.updated event: {str(e)}")
            await message.reject(requeue=True)
