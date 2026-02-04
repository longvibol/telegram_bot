class TelegramConfig:
    def __init__(self):
        self._bot_token = "8338627964:AAE5OBrqHfERvlqd-lv2dXFe_TAb_eOBiNc"

    def get_token(self) -> str:
        return self._bot_token


if __name__ == "__main__":
    config = TelegramConfig()
    print(config.get_token())