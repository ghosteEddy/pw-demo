import argparse
from datetime import datetime, timedelta
import json
import os
import urllib.parse
import requests
from typing import TypedDict, NamedTuple

import urllib


# printing because we capture stdout to log
class StatsData(NamedTuple):
    bar_time: str
    symbol: str
    min_price: float
    max_price: float
    first_price: float
    last_price: float


class QueryResult(TypedDict):
    query: str
    columns: list
    timestamp: int
    dataset: list[list]


class UpdateOneMinRequest(TypedDict):
    min_price: str
    max_price: str
    first_price: str
    last_price: str
    bar_time: str


def update_data(symbol: str, data: UpdateOneMinRequest):
    host = os.environ.get("TICKER_STATS_HOST")
    payload = json.dumps(data)
    headers = {"Content-Type": "application/json"}
    res = requests.post(
        f"{host}/stats/{symbol}/update_onemin", headers=headers, data=payload
    )
    return res.status_code


def fetch_data(from_time: datetime, to_time: datetime):
    print("Fetching data ....")
    host = os.environ.get("QUESTDB_HOST")
    _from_time = from_time.strftime("%Y-%m-%dT%H:%M:%S")
    _to_time = to_time.strftime("%Y-%m-%dT%H:%M:%S")
    query = f"SELECT timestamp as bar_time, id as symbol, MIN(price) as min_price, MAX(price) as max_price, FIRST(PRICE) as first_price, LAST(PRICE) as last_price FROM ticker WHERE '{_from_time}' <= received_on AND '{_to_time}' >= received_on SAMPLE BY 1m GROUP BY id"
    # fetching as csv would be more efficient but we are using json for now
    res = requests.get(f"{host}/exec?query={urllib.parse.quote(query)}")
    data: QueryResult = res.json()
    dataset = data["dataset"]

    return dataset


def main(start: datetime, end: datetime):
    dataset = fetch_data(start, end)
    # actually data set is list of list not tuple we will sacrifice to work with named tuple
    for raw_data in dataset:
        data: StatsData = StatsData(
            bar_time=raw_data[0],
            symbol=raw_data[1],
            min_price=raw_data[2],
            max_price=raw_data[3],
            first_price=raw_data[4],
            last_price=raw_data[5],
        )
        symbol = data.symbol
        payload: UpdateOneMinRequest = {
            "bar_time": data.bar_time,
            "first_price": data.first_price,
            "last_price": data.last_price,
            "max_price": data.max_price,
            "min_price": data.min_price,
        }
        result_code = update_data(symbol=symbol, data=payload)
        print(f"Code {result_code} : {symbol} {data.bar_time}")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process data within a date range.")
    parser.add_argument(
        "start",
        type=str,
        help="Start datetime in ISO format (e.g., 2024-12-29T11:25:00Z)",
    )
    parser.add_argument(
        "end", type=str, help="End datetime in ISO format (e.g., 2024-12-30T11:25:00Z)"
    )

    args = parser.parse_args()

    start_time = datetime.fromisoformat(args.start)
    end_time = datetime.fromisoformat(args.end)

    print(f"Job start from: {start_time} to: {end_time}")
    try:
        result = main(start_time, end_time)
    except Exception as e:
        print("ERROR!!")
        print(e)
    print(f"Job Done with code: {result}")
