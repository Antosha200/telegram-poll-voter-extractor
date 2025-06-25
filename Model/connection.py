import asyncio
import os
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, RPCError
from config import load_config

cfg = load_config()
_FORCED_SESSION_PATH: str = None

def get_client() -> TelegramClient:
    """
    Creates and returns an instance of TelegramClient (without automatic connect()).
    """
    # если путь был "принудительно" установлен — используем его

    if _FORCED_SESSION_PATH:
            session_fp = _FORCED_SESSION_PATH
    else:
            here = os.path.dirname(os.path.abspath(__file__))
            root_dir = os.path.normpath(os.path.join(here, '..'))
            session_dir = os.path.join(root_dir, 'Session')
            session_fp = os.path.join(session_dir, f"{cfg['session_name']}.session")

    return TelegramClient(
        session_fp,
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
            phone = input("Введите ваш номер телефона")
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
        print("Не рекомендуется подключаться много раз. Телеграмм может заблокировать аккаунт.")
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

def set_session_path(path: str):
    global _FORCED_SESSION_PATH
    _FORCED_SESSION_PATH = path