import asyncio
import os
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, RPCError
from config import load_config
from Model.Logger.logger import logger

cfg = load_config()
_FORCED_SESSION_PATH: str = None

def get_client() -> TelegramClient:
    """
    Creates and returns an instance of TelegramClient (without automatic connect()).
    """
    # if the path was "forcibly" set, we use it

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
            # Step 1: send the code to the phone
            phone = input("Enter your phone number")
            await client.send_code_request(phone)
            code = input("Enter the code you received in Telegram:")

            try:
                # Step 2: try to log in using the code only
                await client.sign_in(phone=phone, code=code)
            except SessionPasswordNeededError:
                # Step 3 (2FA): If a password is enabled, requesting it
                password = input("Two-factor password is enabled. Enter the password:")
                await client.sign_in(password=password)

        me = await client.get_me()
        print(f"Successfully connected as {me.first_name} (@{me.username}), id={me.id}")
        print("\nIt is not recommended to connect many times. Telegram may block your account.\n")
    except RPCError as e:
        print("\nTelethon RPC error:", e)
    except Exception as e:
        print("\nAnother connection error:", e)
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