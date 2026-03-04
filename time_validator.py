async def record(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != OWNER_ID:
        return

    if len(context.args) < 2:
        await update.message.reply_text(
            "Usage:\n"
            "/record LINK 00:10:00\n"
            "OR\n"
            "/record LINK 10:50AM 12:15PM 01/02/2026"
        )
        return

    link = context.args[0]

    # ==========================
    # MODE 1 → Duration
    # ==========================
    if len(context.args) == 2:
        duration = context.args[1]

        valid, result = check_recording_time(duration)
        if not valid:
            await update.message.reply_text(result)
            return

        now = datetime.now()
        filename = f"AnimeCartoon.[{now.strftime('%d-%m-%Y')}].[{now.strftime('%I-%M%p')}].480p.WEB-DL.MultiAudio.H264.mp4"

        await run_ffmpeg(update, link, duration, filename)

    # ==========================
    # MODE 2 → Start End Date
    # ==========================
    elif len(context.args) == 4:
        start_time = context.args[1]
        end_time = context.args[2]
        date_str = context.args[3]

        valid, result = check_recording_time(start_time, end_time, date_str)
        if not valid:
            await update.message.reply_text(result)
            return

        duration_seconds = result
        duration = str(datetime.utcfromtimestamp(duration_seconds).strftime("%H:%M:%S"))

        filename = (
            f"AnimeCartoon.[{date_str.replace('/','-')}]."
            f"[{start_time}-{end_time}]."
            "480p.WEB-DL.MultiAudio.H264.mp4"
        )

        await run_ffmpeg(update, link, duration, filename)

    else:
        await update.message.reply_text("❌ Invalid format.")
