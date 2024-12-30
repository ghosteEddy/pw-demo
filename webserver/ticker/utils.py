import os


def get_env(key: str):
    value = os.environ.get(key)
    if value is None:
        raise KeyError(f"No environment value of: {key}")
    else:
        return value
