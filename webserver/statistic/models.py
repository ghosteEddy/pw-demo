from datetime import datetime, timedelta
from typing import Optional, TypedDict
from django.db import models


class Symbol(models.Model):
    id = models.AutoField(primary_key=True)
    symbol = models.CharField(max_length=32, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @staticmethod
    def create_symbol(symbol: str) -> "Symbol":
        """Wrapper of get_or_create and return only object"""
        # TODO: validate result
        symbol_instance = Symbol.objects.get_or_create(symbol=symbol)
        return symbol_instance[0]


class BaseStat(models.Model):
    symbol = models.ForeignKey(Symbol, on_delete=models.RESTRICT)
    min_price = models.DecimalField(max_digits=24, decimal_places=10)
    max_price = models.DecimalField(max_digits=24, decimal_places=10)
    first_price = models.DecimalField(max_digits=24, decimal_places=10)
    last_price = models.DecimalField(max_digits=24, decimal_places=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class OneMinBar(BaseStat):
    bar_time = models.DateTimeField()

    class _UpdateOneMinInterface(TypedDict):
        min_price: str
        max_price: str
        first_price: str
        last_price: str
        bar_time: datetime

    @staticmethod
    def find_exist(symbol: Symbol, datetime: datetime) -> Optional["OneMinBar"]:
        try:
            return OneMinBar.objects.get(symbol=symbol.id, bar_time=datetime)
        except OneMinBar.DoesNotExist:
            return None

    @staticmethod
    def create(symbol: Symbol, data: _UpdateOneMinInterface) -> Optional["OneMinBar"]:
        bar = OneMinBar.objects.create(
            symbol=symbol,
            min_price=data["min_price"],
            max_price=data["max_price"],
            first_price=data["first_price"],
            last_price=data["last_price"],
            bar_time=data["bar_time"],
        )
        return bar

    @staticmethod
    def update(symbol: Symbol, data: _UpdateOneMinInterface):
        exist: OneMinBar | None = OneMinBar.find_exist(
            symbol=symbol, datetime=data["bar_time"]
        )
        if exist is None:
            result = OneMinBar.create(symbol, data)
            return result
        else:
            # TODO: do stats adjustment here such as adjust min max
            # stubs by returning old exist data for now
            return exist

    @staticmethod
    def fetch_by_period(
        symbol: Symbol, start: datetime, end: datetime
    ) -> list[Optional["OneMinBar"]]:
        # verify if start and end period is longer than 4 hours
        period_duration = end - start
        if period_duration > timedelta(hours=4):
            raise ValueError("The specified period cannot exceed 4 hours.")

        # query list of data
        bars = list(
            OneMinBar.objects.filter(
                symbol=symbol,
                bar_time__gte=start,
                bar_time__lte=end,
            ).order_by("bar_time")
        )

        # fillin the minuets with no data with the same amount of value the same as last value of minute before
        # TODO: in case of no first data, we will just set it as None for simplicity

        result = []
        current_time = start
        last_bar = None

        while current_time <= end:
            # Find a bar for the current time
            matching_bars = [bar for bar in bars if bar.bar_time == current_time]

            if matching_bars:
                # Add the matching bar to the filled list
                last_bar = matching_bars[0]
                result.append(last_bar)
            elif last_bar:
                # If no matching bar, duplicate the last bar with the current time
                result.append(
                    OneMinBar(
                        symbol=last_bar.symbol,
                        min_price=last_bar.min_price,
                        max_price=last_bar.max_price,
                        first_price=last_bar.last_price,
                        last_price=last_bar.last_price,
                        bar_time=current_time,
                    )
                )

            # Move to the next minute
            current_time += timedelta(minutes=1)

        return result
