# Auto Message Selfbot

A Discord selfbot for automatically sending messages to specified channels at set intervals.

## Features
- Schedule automatic messages to any channel
- List and remove scheduled auto-messages
- Simple command interface

## Setup
1. **Install Python 3.10**
2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
3. **Update `config.json`** in the project folder:
   ```json
   {
     "token": "YOUR_TOKEN_HERE",
     "prefix": "."
   }
   ```

## Commands
- `.startam <channel_id> <interval_minutes> <message>` — Start auto-messaging a channel
- `.stopam <channel_id>` — Stop auto-messaging a channel
- `.amlist` — List all active auto-messages

## Disclaimer
- **Selfbots are against Discord's Terms of Service and can result in account termination.**
- This project is for educational purposes only. Use at your own risk.
