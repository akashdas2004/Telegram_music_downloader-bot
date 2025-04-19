import os
import asyncio
import nest_asyncio
import time
from yt_dlp import YoutubeDL
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

nest_asyncio.apply()

TOKEN = "YOUR_ACTUAL_BOT_TOKEN_HERE"  # Replace with your actual bot token

user_results = {}

def search_youtube(query, limit=30):
    ydl_opts = {
        'quiet': True,
        'extract_flat': 'in_playlist',
        'force_generic_extractor': True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        results = ydl.extract_info(f"ytsearch{limit}:{query}", download=False)
        return results['entries']

def get_keyboard(results, page, query):
    keyboard = []
    start = page * 10
    end = start + 10
    for i, video in enumerate(results[start:end]):
        keyboard.append([InlineKeyboardButton(video['title'][:50], callback_data=f"select|{start + i}|{query}")])
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅ Previous", callback_data=f"nav|{page-1}|{query}"))
    if end < len(results):
        nav_buttons.append(InlineKeyboardButton("Next ➡", callback_data=f"nav|{page+1}|{query}"))
    if nav_buttons:
        keyboard.append(nav_buttons)
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎵 Use /song <name> to search and download songs.")

async def song(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("❗ Provide a search query.")
        return
    results = search_youtube(query)
    if not results:
        await update.message.reply_text("❌ No results found.")
        return
    user_results[query] = results
    keyboard = get_keyboard(results, 0, query)
    await update.message.reply_text(f"🔍 Results for: {query}", reply_markup=keyboard)

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data.split("|")

    if data[0] == "nav":
        page = int(data[1])
        search_query = data[2]
        results = user_results.get(search_query, [])
        keyboard = get_keyboard(results, page, search_query)
        await query.edit_message_reply_markup(reply_markup=keyboard)

    elif data[0] == "select":
        index = int(data[1])
        search_query = data[2]
        results = user_results.get(search_query, [])

        if index >= len(results):
            await query.message.reply_text("⚠ Invalid selection.")
            return

        video_id = results[index]['id']
        title = results[index]['title']
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        try:
            await query.message.delete()
        except:
            pass

        status_msg = await query.message.chat.send_message("⏬ Downloading...")

        try:
            filename, _ = await download_audio(video_url, status_msg)
            await upload_audio(status_msg, filename, title)
            os.remove(filename)
        except Exception as e:
            print("Download error:", e)
            await status_msg.edit_text("❌ Failed. Might be age-restricted or need cookies.txt.")

async def download_audio(url, status_msg):
    filename = ""

    def progress_hook(d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate') or 1
            downloaded_bytes = d.get('downloaded_bytes', 0)
            percent = downloaded_bytes / total * 100
            speed = d.get('speed')
            speed_str = f"{(speed/1024):.1f} KB/s" if speed else "calculating..."
            text = f"⏬ Downloading: {percent:.1f}% at {speed_str}"
            asyncio.run_coroutine_threadsafe(status_msg.edit_text(text), asyncio.get_event_loop())

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'cookiefile': 'cookies.txt' if os.path.exists("cookies.txt") else None,
        'progress_hooks': [progress_hook],
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info).replace(".webm", ".mp3").replace(".m4a", ".mp3")
    return filename, os.path.getsize(filename)

async def upload_audio(status_msg, filename, title):
    file_size = os.path.getsize(filename)
    chunk_size = 1024 * 512
    sent = 0
    start_time = time.time()

    with open(filename, 'rb') as f:
        while sent < file_size:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            sent += len(chunk)
            elapsed = time.time() - start_time
            speed = (sent / elapsed) if elapsed else 0
            percent = sent / file_size * 100
            speed_str = f"{(speed/1024):.1f} KB/s"
            await status_msg.edit_text(f"⏫ Uploading: {percent:.1f}% at {speed_str}")

    await status_msg.delete()
    await status_msg.chat.send_audio(audio=open(filename, 'rb'), title=title)

async def run_bot():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("song", song))
    app.add_handler(CallbackQueryHandler(handle_buttons))
    print("🤖 Bot is running...")
    await app.run_polling()

await run_bot()
