import requests
import telebot
from telebot import types
from mytoken import TelegramConfig

API_BASE_URL = "https://v6.exchangerate-api.com/v6"
REQUEST_TIMEOUT_SEC = 10
DEFAULT_AMOUNT = 100.0

CURRENCIES = [
    "USD",
    "KHR",
    "VND",
]

DISPLAY_CURRENCY = {
    "KHR": "រៀល",
}

DISPLAY_EMOJI = {
    "USD": "🇺🇸",
    "KHR": "🇰🇭",
    "VND": "🇻🇳",
}

bot = telebot.TeleBot(TelegramConfig().get_token())
TOKEN = TelegramConfig().get_exchange_rate_token()
_session = requests.Session()
_pending_pairs = {}


def _welcome_text():
    return (
        "💱 Welcome! This bot converts currency amounts using live exchange rates.\n\n"
        "📝 To convert, send a message in the format:\n"
        "<amount> <from_currency> <to_currency>\n"
        "Example: 100 USD EUR\n\n"
        "👇 Or pick a currency pair below to convert the default amount."
    )


def convert_current(amount, from_currency, to_currency):
    url = f"{API_BASE_URL}/{TOKEN}/latest/{from_currency}"
    response = _session.get(url, timeout=REQUEST_TIMEOUT_SEC)
    response.raise_for_status()
    data = response.json()

    if data.get("result") != "success":
        raise ValueError(data.get("error-type", "unknown API error"))

    rates = data.get("conversion_rates", {})
    if to_currency not in rates:
        raise ValueError(f"unknown currency: {to_currency}")

    converted_rate = rates[to_currency]
    return amount * converted_rate


def _parse_message_text(text):
    parts = text.split()
    if len(parts) != 3:
        raise ValueError("Expected: <amount> <from_currency> <to_currency>")

    amount_str, from_currency, to_currency = parts
    amount = float(amount_str)
    if amount <= 0:
        raise ValueError("Amount must be positive.")

    return amount, from_currency.upper(), to_currency.upper()


def _parse_amount_only(text):
    amount = float(text.strip())
    if amount <= 0:
        raise ValueError("Amount must be positive.")
    return amount

def _build_currency_pairs_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    for from_currency in CURRENCIES:
        for to_currency in CURRENCIES:
            if from_currency == to_currency:
                continue
            from_emoji = DISPLAY_EMOJI.get(from_currency, "")
            to_emoji = DISPLAY_EMOJI.get(to_currency, "")
            label = f"{from_emoji} {from_currency} -> {to_emoji} {to_currency}".strip()
            callback_data = f"pair:{from_currency}:{to_currency}"
            buttons.append(types.InlineKeyboardButton(label, callback_data=callback_data))
    keyboard.add(*buttons)
    return keyboard


@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        _welcome_text(),
        reply_markup=_build_currency_pairs_keyboard(),
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("pair:"))
def handle_pair_selection(call):
    _, from_currency, to_currency = call.data.split(":")
    chat_id = call.message.chat.id
    _pending_pairs[chat_id] = (from_currency, to_currency)
    bot.answer_callback_query(call.id)
    bot.send_message(
        chat_id,
        f"Selected {from_currency} -> {to_currency}. Send the amount to convert.",
    )


@bot.message_handler(func=lambda m: True, content_types=["text"])
def process_conversion(message):
    bot.send_message(
        message.chat.id,
        _welcome_text(),
        reply_markup=_build_currency_pairs_keyboard(),
    )

    chat_id = message.chat.id
    if chat_id in _pending_pairs:
        from_currency, to_currency = _pending_pairs.pop(chat_id)
        try:
            amount = _parse_amount_only(message.text)
            result = convert_current(amount, from_currency, to_currency)
        except (ValueError, requests.RequestException) as exc:
            bot.reply_to(message, f"Error: {exc}")
            return

        bot.reply_to(
            message,
            f"{amount:,.2f} {from_currency} is approximately {result:,.2f} {DISPLAY_CURRENCY.get(to_currency, to_currency)}",
        )
        return

    try:
        amount, from_currency, to_currency = _parse_message_text(message.text)
        result = convert_current(amount, from_currency, to_currency)
    except (ValueError, requests.RequestException) as exc:
        bot.reply_to(message, f"Error: {exc}")
        return

    bot.reply_to(
        message,
        f"{amount:,.2f} {from_currency} is approximately {result:,.2f} {DISPLAY_CURRENCY.get(to_currency, to_currency)}",
    )


def main():
    print("Bot running...")
    bot.infinity_polling(skip_pending=True)


if __name__ == "__main__":
    main()
