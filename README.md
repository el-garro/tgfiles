# TGFiles

Simple web and API to use a private Telegram channel as a small file storage

# Instructions
1. Create a private channel in Telegram, copy the chat id (you can get the chat id by copying the url of any message in the channel, getting the first big number in the url and prepending -100 to it, ie: https://t.me/c/1234567890/888 = -1001234567890 ).
2. Create a Telegram Bot in @BotFather, copy the bot token.
3. Add your newly created bot to your newly created channel.
4. Configure your env vars TG_BOT_TOKEN (self-explanatory), TG_CHANNEL_ID (self-explanatory), URL (the base url of your app, ie: https://www.example.com).
5. Run that thing, you're ready to go.
