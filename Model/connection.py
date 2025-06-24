import asyncio
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, RPCError
from config import load_config

cfg = load_config()

def get_client() -> TelegramClient:
    """
    Creates and returns an instance of TelegramClient (without automatic connect()).
    """
    return TelegramClient(
        cfg['session_name'],
        cfg['api_id'],
        cfg['api_hash']
    )

async def test_connection():
    """
    It connects, logs in (with 2FA enabled), and outputs information about the current user.
    """
    client = get_client()
    try:
        await client.connect()

        if not await client.is_user_authorized():
            # Шаг 1: отправляем код на телефон
            phone = input("Введите ваш номер телефона (в формате +7…): ")
            await client.send_code_request(phone)
            code = input("Введите код, полученный в Telegram: ")

            try:
                # Шаг 2: пробуем войти только по коду
                await client.sign_in(phone=phone, code=code)
            except SessionPasswordNeededError:
                # Шаг 3 (2FA): если включён пароль, запрашиваем его
                password = input("Двухфакторный пароль включён. Введите пароль: ")
                await client.sign_in(password=password)

        me = await client.get_me()
        print(f"Успешно подключились как {me.first_name} (@{me.username}), id={me.id}")
    except RPCError as e:
        print("Ошибка Telethon RPC:", e)
    except Exception as e:
        print("Другая ошибка при соединении:", e)
    finally:
        await client.disconnect()

def run_test():
    """
    Synchronous start of asynchronous verification.
    """
    asyncio.run(test_connection())
