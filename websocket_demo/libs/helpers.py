import json
from decimal import Decimal


class DecimalEncoder(json.JSONEncoder):
    """Helper class to convert a DynamoDB item to JSON."""

    def default(self, o):
        if isinstance(o, Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)

        if isinstance(o, set):
            return list(o)

        return super(DecimalEncoder, self).default(o)


def safe_dumps(payload):
    return json.dumps(payload, cls=DecimalEncoder)
