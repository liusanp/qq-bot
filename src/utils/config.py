from botpy.ext.cog_yaml import read


config_data = read("config.yaml")


def get(key: str) -> str:
    print(config_data)
    if key and key in config_data.keys():
        return config_data[key]
    else:
        return ""