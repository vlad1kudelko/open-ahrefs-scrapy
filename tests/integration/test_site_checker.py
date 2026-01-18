import json
import time

import pytest


@pytest.fixture(scope="function")
def redis_del(redis_client):
    redis_client.delete("crawler:start_urls")
    redis_client.delete("crawler:dupefilter")
    redis_client.delete("crawler:requests")
    redis_client.delete("crawler:items")
    yield
    time.sleep(3)


def wait_list(redis_client, key):
    for _ in range(20):
        if redis_client.llen(key) > 0:
            break
        time.sleep(1)
    else:
        raise ValueError("Результат пуст")
    return json.loads(redis_client.lpop(key))


def test_site_checker_200(redis_client, redis_del):
    redis_client.rpush("crawler:start_urls", "https://example.com/")
    first = wait_list(redis_client, "crawler:items")
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
    second = wait_list(redis_client, "crawler:items")
    assert json.dumps(second) == json.dumps(
        {
            "url": "http://www.iana.org/help/example-domains",
            "status": 200,
            "title": "Example Domains",
            "redirect_times": 2,
            "redirect_urls": [
                "https://iana.org/domains/example",
                "https://www.iana.org/domains/example",
            ],
            "referer": "https://example.com/",
        }
    )


def test_site_checker_404(redis_client, redis_del):
    redis_client.rpush("crawler:start_urls", "https://ifconfig.me/404")
    first = wait_list(redis_client, "crawler:items")
    assert json.dumps(first) == json.dumps(
        {
            "url": "https://ifconfig.me/404",
            "status": 404,
            "title": None,
            "redirect_times": 0,
            "redirect_urls": [],
            "referer": "",
        }
    )


def test_site_checker_302_count1(redis_client, redis_del):
    redis_client.rpush("crawler:start_urls", "http://hb.opencpu.org/redirect/1")
    first = wait_list(redis_client, "crawler:items")
    assert json.dumps(first) == json.dumps(
        {
            "url": "http://hb.opencpu.org/get",
            "status": 200,
            "title": None,
            "redirect_times": 1,
            "redirect_urls": ["http://hb.opencpu.org/redirect/1"],
            "referer": "",
        }
    )


def test_site_checker_302_count3(redis_client, redis_del):
    redis_client.rpush("crawler:start_urls", "http://hb.opencpu.org/redirect/3")
    first = wait_list(redis_client, "crawler:items")
    assert json.dumps(first) == json.dumps(
        {
            "url": "http://hb.opencpu.org/get",
            "status": 200,
            "title": None,
            "redirect_times": 3,
            "redirect_urls": [
                "http://hb.opencpu.org/redirect/3",
                "http://hb.opencpu.org/relative-redirect/2",
                "http://hb.opencpu.org/relative-redirect/1",
            ],
            "referer": "",
        }
    )
