import pytest
import redis


@pytest.fixture(scope="session")
def redis_client():
    r = redis.Redis(host="localhost", port=6379, db=0)
    yield r
    r.close()
