
# Telegram Poll Voter Extractor

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
**Create a config file** named `config.json` in the root of the project:

```json
{
  "api_id": "your_api_id",
  "api_hash": "your_api_hash_here",
  "chat_username": "https://t.me/your_group_or_channel", 
  "session_name": "Model/poll_session"
}
```

---

## 🔑 Where to Get API Credentials?
You can obtain your api_id and api_hash from my.telegram.org:

 - Go to https://my.telegram.org

 - Log in with your Telegram account (phone number and verification code)

 - Navigate to API development tools

 - Click Create new application

 - Fill in the required fields (e.g., app title, short name)

 - After creation, copy your api_id and api_hash from the page

---

## 🧭 What is `chat_username`?
This should be the public or private invite link to the chat (group/channel) where the poll is posted.

Examples:

Public group: https://t.me/mychatgroup

Private group (invite-only): https://t.me/+HoysWf3C7BU3ZjZk

You must be a member of the group and have permission to read messages in it.

## 📎 Useful Links

- [🔑 my.telegram.org — Get API ID and Hash](https://my.telegram.org)
- [📘 Telethon Documentation](https://docs.telethon.dev/)
- [💬 Example Telegram Chat (Public)](https://t.me/mychatgroup)
- [🔒 Example Telegram Invite Link (Private)](https://t.me/+HoysWf3C7BU3ZjZk)

## 👾 How to run with console?
At the moment, there are two launch options:
1. Running without setting parameters. It will return the last poll in the chat.
```bash
cd Action
```
```bash
python start.py
```
2. Running with the `msg_id` parameter. Will return the poll that has actual message id
```bash
cd Action
```
```bash
python start.py --msg_id 789012
```
Find which id to use you can from Telegram web URL
```bash
https://web.telegram.org/k/#-1234567890
```

## 🎯 Where to find the results?
All results you can find in `Documents/Results` folder in JSON format.
You also can find logs in `Logs` folder
