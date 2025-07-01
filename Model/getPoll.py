import asyncio
import re
import argparse
import os
import sys
from telethon.tl.types import MessageMediaPoll
from telethon.tl.functions.messages import GetPollVotesRequest, SendVoteRequest

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from Model.Saver.saver import PollSaver
from Model.Logger.logger import logger
from connection import get_client, cfg

client = get_client()

def sanitize_key(key: str) -> str:
    """
    Converts the text of the response option to a secure key for JSON
    :param key: Text of the response option
    :return: Secure key
    """
    sanitized = re.sub(r'[^\w]', '_', key)
    sanitized = re.sub(r'_+', '_', sanitized)
    return sanitized.strip('_')

async def fetch_last_poll():
    await client.start()
    async for msg in client.iter_messages(cfg['chat_username'], limit=200):
        if isinstance(msg.media, MessageMediaPoll):
            return msg
    return None
"""
async def fetch_poll_by_id(msg_id: int):
    
    Receives a survey based on the specified message ID
    :param msg_id: ID of the polling message
    :return: Message object or None
    
    await client.start()
    try:
        msg = await client.get_messages(
            entity=cfg['chat_username'],
            ids=msg_id,
        )
        if msg and isinstance(msg.media, MessageMediaPoll):
            return msg
        logger.error(f"Message with ID {msg_id} is not a poll or not found")
        return None
    except Exception as e:
        logger.error(f"Error fetching message by ID: {e}")
        return None
"""
async def fetch_poll_by_poll_id(poll_id: int):
    """
   Gets a poll by a unique poll_id instead of message_id 
   :param poll_id: Poll ID (poll.id field in MessageMediaPoll) 
   :return: Message object or None
    """
    await client.start()
    try:
        async for msg in client.iter_messages(
                entity=cfg['chat_username'],
                limit=200  # Ограничение на количество проверяемых сообщений
        ):
            if (
                    isinstance(msg.media, MessageMediaPoll) and
                    msg.media.poll.id == poll_id
            ):
                return msg
        logger.warning(f"Poll with ID {poll_id} not found in the last 200 messages")
        return None
    except Exception as e:
        logger.error(f"Error fetching poll by ID: {e}")
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
            logger.error(f"Error receiving votes: {e}")
            break

        voters.extend(result.users)
        if not result.next_offset:
            break
        offset = result.next_offset
    return voters

async def has_user_voted(msg, user_id: int) -> bool:
    """Check if user has already voted in the poll"""
    try:
        # Checking first option to see if user has voted
        first_option = msg.media.poll.answers[0].option
        if isinstance(first_option, int):
            first_option_bytes = bytes([first_option])
        else:
            first_option_bytes = first_option

        voters = await fetch_voters_for_option(msg, first_option_bytes)
        if any(voter.id == user_id for voter in voters):
            return True

        # Check other options if needed
        for answer in msg.media.poll.answers[1:]:
            raw = answer.option
            option_bytes = bytes([raw]) if isinstance(raw, int) else raw
            voters = await fetch_voters_for_option(msg, option_bytes)
            if any(voter.id == user_id for voter in voters):
                return True

        return False
    except Exception as e:
        logger.error(f"Error checking user vote: {e}")
        return False

async def main():
    # Command line argument parsing
    parser = argparse.ArgumentParser(description='Fetch Telegram polls')
    parser.add_argument('--poll_id', type=int, help='ID of the poll in message to fetch')
    args = parser.parse_args()

    if args.poll_id:
        poll_msg = await fetch_poll_by_poll_id(args.poll_id)
    else:
        poll_msg = await fetch_last_poll()

    if not poll_msg:
        logger.error("No polls found in chat.")
        return

    poll = poll_msg.media.poll
    if not poll.public_voters:
        logger.error("The poll is not public — you cannot get a list of those who voted.")
        return

    poll_date = poll_msg.date
    question = poll.question.text if hasattr(poll.question, 'text') else poll.question

    me = await client.get_me()
    need_to_vote = not await has_user_voted(poll_msg, me.id)

    # Voting logic
    if need_to_vote:
        first_option = poll.answers[0].option
        if isinstance(first_option, int):
            first_option_bytes = bytes([first_option])
        else:
            first_option_bytes = first_option

        await client(SendVoteRequest(
            peer=poll_msg.peer_id,
            msg_id=poll_msg.id,
            options=[first_option_bytes]
        ))
        logger.info("Temporarily voted to access poll results")
        await asyncio.sleep(1)

    poll_data = {
        "date": poll_date.isoformat(),
        "question": question,
    }

    for answer in poll.answers:
        ans_text = answer.text.text if hasattr(answer.text, 'text') else answer.text
        raw = answer.option
        if isinstance(raw, int):
            option_bytes = bytes([raw])
        else:
            option_bytes = raw

        voters = await fetch_voters_for_option(poll_msg, option_bytes)
        filtered_voters = [user for user in voters if user.id != me.id or not need_to_vote]

        voter_names = []
        for u in filtered_voters:
            name = f"{u.first_name or ''} {u.last_name or ''}".strip()
            display = name or (f"@{u.username}" if u.username else f"(ID: {u.id})")
            voter_names.append(display)

        option_key = sanitize_key(ans_text)

        poll_data[option_key] = {
            "voter_counts": len(filtered_voters),
            "voter_names": voter_names
        }

    if need_to_vote:
        await client(SendVoteRequest(
            peer=poll_msg.peer_id,
            msg_id=poll_msg.id,
            options=[]
        ))
        logger.info("Temporary vote removed")

    saver = PollSaver()
    saved_path = saver.save_as_json(poll_date, poll_data, subfolder="Polls")
    logger.info(f"Poll results saved to: {saved_path}")

    # Выводим ID сообщения перед результатами
    print(f"\nPoll message ID: {poll_msg.id}")
    print(f"{poll_date:%Y-%m-%d %H:%M:%S}")
    print(f"\n{question}\n")

    for option_key, data in poll_data.items():
        if option_key in ["date", "question"]:
            continue

        vote_count = data["voter_counts"]
        if vote_count % 10 == 1 and vote_count % 100 != 11:
            vote_text = "голос"
        elif 2 <= vote_count % 10 <= 4 and not (12 <= vote_count % 100 <= 14):
            vote_text = "голоса"
        else:
            vote_text = "голосов"

        original_text = next(
            (ans.text.text if hasattr(ans.text, 'text') else ans.text
             for ans in poll.answers
             if sanitize_key(ans.text.text if hasattr(ans.text, 'text') else ans.text) == option_key),
            option_key  # fallback
        )

        print(f"🔹 {original_text}: {vote_count} {vote_text}")
        for name in data["voter_names"]:
            print(f"   • {name}")
        print()

if __name__ == '__main__':
    asyncio.run(main())
