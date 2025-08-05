import json
from datetime import datetime
from decimal import Decimal
from typing import Any


class JSONEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)
