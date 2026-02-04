import logging
import re
from io import BytesIO

import requests
import telebot

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "8338627964:AAE5OBrqHfERvlqd-lv2dXFe_TAb_eOBiNc"
bot = telebot.TeleBot(BOT_TOKEN)


def extract_drive_file_id(url: str) -> str | None:
    """
    Supports links like:
    - https://drive.google.com/file/d/<ID>/view?...
    - https://drive.google.com/open?id=<ID>
    - https://drive.google.com/uc?id=<ID>&export=download
    - https://drive.google.com/drive/folders/<ID>  (folders won't work for a single file)
    """
    patterns = [
        r"/file/d/([a-zA-Z0-9_-]+)",
        r"[?&]id=([a-zA-Z0-9_-]+)",
        r"/uc\?export=download&id=([a-zA-Z0-9_-]+)",
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None


def download_from_google_drive(file_id: str, timeout: int = 30) -> bytes:
    """
    Downloads bytes from Google Drive file ID.
    Handles the "confirm download" token Google uses for large/flagged files.
    Requires the file to be shared publicly or at least accessible without login.
    """
    session = requests.Session()

    # First request
    url = "https://drive.google.com/drive/home?dmr=1&ec=wgc-drive-hero-goto"
    resp = session.get(url, params={"id": file_id}, stream=True, timeout=timeout)
    resp.raise_for_status()

    # Sometimes Google asks for a confirmation token (virus scan warning)
    confirm_token = None
    for k, v in resp.cookies.items():
        if k.startswith("download_warning"):
            confirm_token = v
            break

    if confirm_token:
        resp = session.get(
            url,
            params={"id": file_id, "confirm": confirm_token},
            stream=True,
            timeout=timeout,
        )
        resp.raise_for_status()

    # If not an image, Telegram may reject. We'll still download and attempt send.
    data = resp.content

    # Basic check for Drive HTML error page (permissions/not found)
    if data[:200].lower().find(b"<html") != -1:
        raise RuntimeError(
            "Google Drive returned an HTML page (likely permission issue or not a direct file). "
            "Make sure the file is shared as 'Anyone with the link can view'."
        )

    return data


@bot.message_handler(commands=["photo"])
def send_photo_from_drive(message):
    """
    Usage:
    /photo <google drive share link>
    """
    chat_id = message.chat.id
    parts = message.text.split(maxsplit=1)

    if len(parts) < 2:
        bot.send_message(chat_id, "Usage:\n/photo <google drive image link>")
        return

    drive_link = parts[1].strip()
    file_id = extract_drive_file_id(drive_link)

    if not file_id:
        bot.send_message(chat_id, "I couldn't find a Google Drive file ID in that link.")
        return

    try:
        img_bytes = download_from_google_drive(file_id)
        bio = BytesIO(img_bytes)
        bio.name = "photo.jpg"  # helps Telegram treat it as an image
        bio.seek(0)

        bot.send_photo(chat_id, bio, caption="Photo from Google Drive ✅")

    except Exception as e:
        bot.send_message(chat_id, f"Failed to send photo.\nError: {e}")


@bot.message_handler(func=lambda m: True)
def help_text(message):
    bot.send_message(
        message.chat.id,
        "Send:\n/photo <google drive image link>\n\nExample:\n/photo https://drive.google.com/file/d/FILE_ID/view"
    )


print("Bot running...")
bot.infinity_polling()
