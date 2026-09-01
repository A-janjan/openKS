import redis
import json
import os
from dotenv import load_dotenv

_ = load_dotenv()


redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6380)),
    decode_responses=True,
)


def get_cache(key: str):
    data = redis_client.get(key)
    if data:
        return json.loads(data)
    return None


def set_cache(key: str, value, ttl: int = 3600):
    redis_client.setex(key, ttl, json.dumps(value))
