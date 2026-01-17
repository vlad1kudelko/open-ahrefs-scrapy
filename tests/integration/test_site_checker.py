import json
import time

import pytest


@pytest.fixture(scope="function")
def redis_del(redis_client):
    redis_client.delete("crawler:dupefilter")
    redis_client.delete("crawler:items")
    redis_client.delete("crawler:start_urls")
    yield
    time.sleep(2)


def wait_list(redis_client, key):
    for _ in range(10):
        if redis_client.llen(key) > 0:
            break
        time.sleep(1)
    else:
        raise ValueError("Результат пуст")


def test_site_checker_200(redis_client, redis_del):
    redis_client.rpush("crawler:start_urls", "https://example.com/")
    wait_list(redis_client, "crawler:items")
    first = json.loads(redis_client.lpop("crawler:items"))
    assert json.dumps(first) == json.dumps(
        {
            "url": "https://example.com/",
            "status": 200,
            "title": "Example Domain",
            "redirect_times": 0,
            "redirect_urls": [],
            "referer": "",
        }
    )


def test_site_checker_404(redis_client, redis_del):
    redis_client.rpush("crawler:start_urls", "https://vlad1kudelko.github.io/404")
    wait_list(redis_client, "crawler:items")
    first = json.loads(redis_client.lpop("crawler:items"))
    print(first)
    #  assert json.dumps(first) == json.dumps(
    #  {
    #  "url": "https://example.com/",
    #  "status": 200,
    #  "title": "Example Domain",
    #  "redirect_times": 0,
    #  "redirect_urls": [],
    #  "referer": "",
    #  }
    #  )
