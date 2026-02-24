class TelegramConfig:
    def __init__(self):
        self._bot_token = "8338627964:AAE5OBrqHfERvlqd-lv2dXFe_TAb_eOBiNc"
        self._exchange_rate_token = "ea624cd9cb8959181c27c91d"

    def get_token(self) -> str:
        return self._bot_token

    def get_exchange_rate_token(self) -> str:
        return self._exchange_rate_token


if __name__ == "__main__":
    config = TelegramConfig()
    print(config.get_token())
