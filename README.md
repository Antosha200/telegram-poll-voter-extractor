
# TG_CHOIR — Telegram Poll Voter Extractor

This is a Python-based system that:

- Connects to **Telegram** via the **Telethon** library.
- Extracts the **latest public poll** from the specified chat.
- Retrieves a **list of users** who voted for each answer option.
- Outputs the data in a **human-readable format**.

---

## ✅ Requirements

- Python **3.8+**
- A **Telegram account** with access to the target chat
- (Optional) A **virtual environment**

---

## ⚙️ Configuration

1. **Create a config file** named `config.json` in the root of the project:

```json
{
  "api_id": "your_api_id",
  "api_hash": "your_api_hash_here",
  "chat_username": "https://t.me/your_group_or_channel", 
  "session_name": "Model/poll_session"
}
