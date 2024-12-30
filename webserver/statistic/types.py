from datetime import datetime
from typing import TypedDict


class UpdateOneMinRequest(TypedDict):
    min_price: str
    max_price: str
    first_price: str
    last_price: str
    bar_time: str
