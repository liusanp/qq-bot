from src.utils.config import get as get_config
import botpy
from src.client.main_client import MainClient


def start():
    intents = botpy.Intents.default()
    client = MainClient(intents=intents, is_sandbox=False)
    client.run(appid=get_config("qqbot.appid"), secret=get_config("qqbot.secret"))


if __name__ == "__main__":
    start()