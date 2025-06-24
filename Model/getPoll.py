import asyncio
import os
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPoll
from telethon.tl.functions.messages import GetPollVotesRequest
from Model.config import load_config

cfg = load_config()
SESSION_PATH = os.path.join(os.path.dirname(__file__), cfg['session_name'])
client = TelegramClient(SESSION_PATH, cfg['api_id'], cfg['api_hash'])

async def fetch_last_poll():
    await client.start()
    async for msg in client.iter_messages(cfg['chat_username'], limit=200):
        if isinstance(msg.media, MessageMediaPoll):
            return msg
    return None

async def fetch_voters_for_option(msg, option_bytes: bytes):
    voters = []
    while True:
        try:
            result = await client(GetPollVotesRequest(
                peer=msg.peer_id,
                id=msg.id,
                option=option_bytes,
                limit=100
            ))
        except Exception as e:
            print(f"Ошибка при получении голосующих: {e}")
            break

        voters.extend(result.users)

        # если нет следующего оффсета — выходим
        if not result.next_offset:
            break

    return voters

async def main():
    msg = await fetch_last_poll()
    if not msg:
        print("В чате не найдено ни одного опроса.")
        return

    poll = msg.media.poll
    results = msg.media.results

    if not poll.public_voters:
        print("❌ Опрос не является публичным — нельзя получить имена голосовавших.")
        return

    question = getattr(poll.question, 'text', str(poll.question))
    print(f"\n{msg.date:%Y-%m-%d %H:%M:%S}")
    print(f"\n {question}\n")

    for answer, poll_result in zip(poll.answers, results.results):
        ans_text = getattr(answer.text, 'text', str(answer.text))
        raw_opt  = answer.option

        # Упаковываем в "сырые" байты только если это int
        if isinstance(raw_opt, int):
            option_bytes = bytes([raw_opt])
        elif isinstance(raw_opt, (bytes, bytearray)):
            option_bytes = raw_opt
        else:
            raise TypeError(f"Неподдерживаемый тип answer.option: {type(raw_opt)}")

        # Демонстрируем, что действительно передаём правильные байты
        print(f"🔹 {ans_text}")

        voters = await fetch_voters_for_option(msg, option_bytes)
        if not voters:
            print("")
            continue

        for user in voters:
            name = f"{user.first_name or ''} {user.last_name or ''}".strip()
            display = name or (f"@{user.username}" if user.username else f"(ID: {user.id})")
            print(f"   • {display}")
        print()

if __name__ == '__main__':
    asyncio.run(main())
