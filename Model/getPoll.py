import asyncio
from telethon.tl.types import MessageMediaPoll
from telethon.tl.functions.messages import GetPollVotesRequest
from connection import get_client, cfg

client = get_client()

async def fetch_last_poll():
    await client.start()
    async for msg in client.iter_messages(cfg['chat_username'], limit=200):
        if isinstance(msg.media, MessageMediaPoll):
            return msg
    return None

async def fetch_voters_for_option(msg, option_bytes: bytes):
    voters = []
    offset = b''
    while True:
        try:
            result = await client(GetPollVotesRequest(
                peer=msg.peer_id,
                id=msg.id,
                option=option_bytes,
                limit=100,
                offset=offset
            ))
        except Exception as e:
            print(f"Error receiving votes: {e}")
            break

        voters.extend(result.users)
        if not result.next_offset:
            break
        offset = result.next_offset

    return voters

async def main():
    msg = await fetch_last_poll()
    if not msg:
        print("No polls found in chat.")
        return

    poll = msg.media.poll
    if not poll.public_voters:
        print("❌ The poll is not public — you cannot get a list of those who voted.")
        return

    print(f"\n{msg.date:%Y-%m-%d %H:%M:%S}")
    question = poll.question.text if hasattr(poll.question, 'text') else poll.question
    print(f"\n{question}\n")

    for answer in poll.answers:
        ans_text = answer.text.text if hasattr(answer.text, 'text') else answer.text
        raw = answer.option
        if isinstance(raw, int):
            option_bytes = bytes([raw])
        else:
            option_bytes = raw

        voters = await fetch_voters_for_option(msg, option_bytes)

        print(f"🔹 {ans_text}: {len(voters)} голос{'ов' if len(voters)%10!=1 or len(voters)%100==11 else ''}")

        for user in voters:
            name = f"{user.first_name or ''} {user.last_name or ''}".strip()
            display = name or (f"@{user.username}" if user.username else f"(ID: {user.id})")
            print(f"   • {display}")
        print()

if __name__ == '__main__':
    asyncio.run(main())
