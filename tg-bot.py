from src.utils.config import get as get_config
from src.client.tg_client import TgClient


if __name__ == "__main__":
    tgClient = TgClient(get_config('tg.token'))
    tgClient.run()