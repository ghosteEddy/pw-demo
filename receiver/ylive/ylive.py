import datetime
import logging
import yliveticker
import functools

from typing import TypedDict
from questdb.ingress import Sender, TimestampNanos


class _Payload(TypedDict):
    id: str
    exchange: str
    quoteType: str
    price: float
    timestamp: int
    marketHours: int
    changePercent: float
    dayVolume: int
    change: float
    priceHint: int


def ylive_handler(config, ws, msg: _Payload):
    try:
        logging.info(
            f"Receive {msg['id']} {msg['exchange']} {msg['price']} {msg['timestamp']} {msg['change']}"
        )
        logging.info(msg)
        with Sender.from_conf(config) as sender:
            sender.row(
                "ticker",
                symbols={"id": msg["id"], "exchange": msg["exchange"]},
                columns={"price": msg["price"], "received_on": datetime.datetime.now()},
                at=TimestampNanos(msg["timestamp"] * 1_000_000),
            )
            sender.flush()
    except Exception as e:
        logging.error("Error: {}".format(e))


def _validate_ticker_names(names: list[str]) -> bool:
    if len(names) < 1:
        return False

    predicates: list[callable[[str], bool]] = [
        functools.partial(ensure_type, str),
        is_not_empty_string,
    ]

    for name in names:
        if not all(pred(name) for pred in predicates):
            return False
    return True


def ensure_type(
    expect: any,
    input: any,
) -> bool:
    return isinstance(input, expect)


def is_not_empty_string(txt: str) -> bool:
    return 1 <= len(txt)


def init_ylive_consumer(ticker_names: list[str], db_config: str):
    if not _validate_ticker_names(ticker_names):
        raise ValueError("Invalid ticker names")

    logging.info("Connecting to DB")
    yliveticker.YLiveTicker(
        on_ticker=functools.partial(ylive_handler, db_config), ticker_names=ticker_names
    )
