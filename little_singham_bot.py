import os
import asyncio
import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from config import 5856009289, 8191916199:AAE-ezyhTkdta-0p8I-lVSsDn8l7UdjhhY0, 100372627111,


# ---------------- Owner-only decorator ----------------
def owner_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        chat = update.effective_chat

        if chat.type == "private" and user.id != OWNER_ID:
            await update.message.reply_text(
                f"👋 Hi {user.first_name}, I only work in our official group.\n"
                f"👉 Please join: https://t.me/joinchat/{OFFICIAL_GROUP_ID}"
            )
            return
        if chat.type in ["group", "supergroup"] and chat.id != OFFICIAL_GROUP_ID:
            await update.message.reply_text("❌ I only work in the official group.")
            return

        return await func(update, context)
    return wrapper

# ---------------- /record command ----------------
@owner_only
async def record(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 3:
        await update.message.reply_text(
            "Usage:\n/record <start_time> <end_time> <M3U8_LINK>\n"
            "Optional: Bottom.Black.Bars, Audio.rename.tracks"
        )
        return

    start_time, end_time, link = context.args[0], context.args[1], context.args[2]
    bottom_black = "Bottom.Black.Bars" in context.args
    rename_audio = "Audio.rename.tracks" in context.args

    # Temporary filename
    filename = "temp_record.mp4"

    await update.message.reply_text(f"📥 Recording started...\nFilename: {filename}")

    vf = "scale=-2:480"
    if bottom_black:
        vf += ",pad=854:480:(854-iw)/2:0:black,drawtext=text='Anime-cartoon.kesug.com':fontcolor=white:fontsize=22:x=w-tw-40:y=35"

    audio_map = ["-map", "0:a:0"] if not rename_audio else ["-map", "0:a"]
    metadata_args = []
    if rename_audio:
        languages = ["Hindi","English","Tamil","Telugu","Kannada","Malayalam","Bengali"]
        for idx, lang in enumerate(languages):
            metadata_args += ["-metadata:s:a:%d" % idx, f"title=[Anime-Cartoon.kesug.com] {lang}"]

    ffmpeg_cmd = [
        "ffmpeg", "-y", "-i", link, "-t", "00:02:00",
        "-map", "0:v", *audio_map,
        "-vf", vf, "-c:v", "libx264", "-preset", "slow", "-b:v", "700k",
        "-c:a", "aac", "-b:a", "64k",
        *metadata_args,
        "-movflags", "+faststart",
        filename
    ]

    process = await asyncio.create_subprocess_exec(*ffmpeg_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

    msg = await update.message.reply_text("⏳ Downloading...")
    import re, time
    pattern = re.compile(r"time=(\d+):(\d+):(\d+\.\d+)")
    duration_sec = 120
    while True:
        line = await process.stderr.readline()
        if not line:
            break
        text = line.decode("utf-8")
        match = pattern.search(text)
        if match:
            h, m, s = match.groups()
            elapsed_sec = int(h)*3600 + int(m)*60 + int(float(s))
            percent = min(100, (elapsed_sec / duration_sec) * 100)
            eta = max(0, int(duration_sec - elapsed_sec))
            await msg.edit_text(f"📥 Download: {percent:.1f}% | ETA: {eta}s")

    await process.wait()
    await msg.edit_text("📤 Uploading video to Telegram...")

    # Send file to Telegram and delete local temp
    with open(filename, "rb") as f:
        await context.bot.send_video(chat_id=OWNER_ID, video=f, caption="✅ Recording Completed!")

    os.remove(filename)
    await msg.edit_text("✅ Download + Upload Completed!")
