from datetime import datetime
import json

from django.http import HttpResponse, HttpResponseServerError, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404

from statistic.types import UpdateOneMinRequest
from statistic.models import OneMinBar, Symbol


# Simplify this without using DJR


@csrf_exempt
def update_onemin(request, symbol: str):
    if request.method == "POST":
        _symbol = Symbol.create_symbol(symbol=symbol)
        data: UpdateOneMinRequest = json.loads(request.body)
        result = OneMinBar.update(
            symbol=_symbol,
            data={**data, "bar_time": datetime.fromisoformat(data["bar_time"])},
        )
        if result is None:
            return HttpResponseServerError()
        return HttpResponse(result.id)


@csrf_exempt
def get_onemin(request, symbol: str):
    if request.method == "GET":
        start = request.GET.get("start")
        end = request.GET.get("end")

        if not start or not end:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Start and End parameters are required.",
                },
                status=400,
            )

        try:
            start_dt = datetime.fromisoformat(start)
            end_dt = datetime.fromisoformat(end)
            _symbol = Symbol.objects.get(symbol=symbol)
            bars = OneMinBar.fetch_by_period(_symbol, start_dt, end_dt)
            # Serialize the data to return in the response
            result = [
                {
                    "bar_time": bar.bar_time.isoformat(),
                    "min_price": float(bar.min_price),
                    "max_price": float(bar.max_price),
                    "first_price": float(bar.first_price),
                    "last_price": float(bar.last_price),
                }
                for bar in bars
            ]

            return JsonResponse({"status": "success", "data": result}, safe=False)

        except ValueError:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Please check start and end datetime format",
                },
                status=400,
            )
        except Symbol.DoesNotExist:
            return HttpResponse("Symbol Not Found!!", status=404)
