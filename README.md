# Telegram Music Downloader Bot

This is a Telegram bot built using Python that allows users to search for and download audio from YouTube. The bot uses yt-dlp for downloading the audio and Telegram's python-telegram-bot library for interaction. It supports browsing through multiple search results and downloading the audio in MP3 format.

Features
Search YouTube: Users can search for songs by name using the /song <query> command.

Browse Search Results: Users can browse through multiple search results with "Next" and "Previous" buttons.

Download Audio: Users can select a video to download the audio in MP3 format.

Upload to Telegram: After the download is complete, the bot uploads the MP3 file back to Telegram with the song's title.

Requirements
Python 3.7 or higher

yt-dlp for downloading YouTube content

python-telegram-bot for Telegram bot integration

FFmpeg for audio conversion

Optional: cookies.txt file for bypassing age restrictions or region locks

Setup
1. Install dependencies
You can install the necessary libraries using pip:

bash
Copy
Edit
pip install yt-dlp python-telegram-bot nest_asyncio
2. Create a new Telegram Bot
Open Telegram and search for BotFather.

Use the /newbot command to create a new bot and follow the instructions.

After creation, you will get a bot token. Copy it and replace the YOUR_BOT_TOKEN placeholder in the code with your token.

3. (Optional) Setup Cookies
If you need to bypass age restrictions or region locks, you may need to provide a cookies.txt file. This can be generated using your browser’s developer tools.

4. Run the Bot
bash
Copy
Edit
python song.py
The bot will start running and be accessible on Telegram.

Commands
/start: Displays a welcome message.

/song <name>: Searches for a song or video on YouTube based on the provided query.

Navigation
When you search for a song, the bot will present you with a list of up to 30 search results, and you can navigate between pages using the "Next" and "Previous" buttons.

Download Process
Once you select a song or video, the bot will:

Download the audio in MP3 format.

Upload the MP3 file to the chat.

Display download/upload progress along with the speed.

Collab Testing
The bot has been successfully tested on Google Colab for quick deployment and execution.

License
This project is licensed under the MIT License.
