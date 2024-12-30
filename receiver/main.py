import logging
import os

import ylive.ylive as ylive


def _get_env(key: str):
    value = os.environ.get(key)
    if value is None:
        raise KeyError(f"No environment value of: {key}")
    else:
        return value


def _get_ticker_names(key: str):
    value: str = _get_env(key)
    names = value.split(",")
    if 0 == len(names):
        raise ValueError(f"No tickers in env")
    return list(map(lambda n: n.strip(), names))


def main():
    logging.info("Starting Receiver")

    db_config = _get_env("QUESTDB_CONFIG")
    ticker_names = _get_ticker_names("TICKER_NAMES")
    ylive.init_ylive_consumer(ticker_names, db_config)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
