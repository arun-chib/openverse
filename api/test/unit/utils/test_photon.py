from test.factory.models.image import ImageFactory
from unittest import mock
from unittest.mock import MagicMock
from urllib.parse import urlencode

from django.conf import settings
from rest_framework.exceptions import UnsupportedMediaType

import pook
import pytest
import requests

from api.utils.photon import (
    HEADERS,
    UpstreamThumbnailException,
    _get_file_extension_from_url,
    check_image_type,
)
from api.utils.photon import get as photon_get
from api.utils.tallies import get_monthly_timestamp


PHOTON_URL_FOR_TEST_IMAGE = f"{settings.PHOTON_ENDPOINT}subdomain.example.com/path_part1/part2/image_dot_jpg.jpg"
TEST_IMAGE_URL = PHOTON_URL_FOR_TEST_IMAGE.replace(settings.PHOTON_ENDPOINT, "http://")

UA_HEADER = HEADERS["User-Agent"]

# cannot use actual image response because I kept running into some issue with
# requests not being able to decode the content
# I will come back to try to sort it out later but for now
# this will get the tests working.
MOCK_BODY = "mock response body"


@pytest.fixture
def auth_key():
    test_key = "this is a test Photon Key boop boop, let me in"
    settings.PHOTON_AUTH_KEY = test_key

    yield test_key

    settings.PHOTON_AUTH_KEY = None


@pook.on
def test_get_successful_no_auth_key_default_args(mock_image_data):
    mock_get: pook.Mock = (
        pook.get(PHOTON_URL_FOR_TEST_IMAGE)
        .params(
            {
                "w": settings.THUMBNAIL_WIDTH_PX,
                "quality": settings.THUMBNAIL_QUALITY,
            }
        )
        .header("User-Agent", UA_HEADER)
        .header("Accept", "image/*")
        .reply(200)
        .body(MOCK_BODY)
        .mock
    )

    res = photon_get(TEST_IMAGE_URL)

    assert res.content == MOCK_BODY.encode()
    assert res.status_code == 200
    assert mock_get.matched


@pook.on
def test_get_successful_with_auth_key_default_args(mock_image_data, auth_key):
    mock_get: pook.Mock = (
        pook.get(PHOTON_URL_FOR_TEST_IMAGE)
        .params(
            {
                "w": settings.THUMBNAIL_WIDTH_PX,
                "quality": settings.THUMBNAIL_QUALITY,
            }
        )
        .header("User-Agent", UA_HEADER)
        .header("Accept", "image/*")
        .header("X-Photon-Authentication", auth_key)
        .reply(200)
        .body(MOCK_BODY)
        .mock
    )

    res = photon_get(TEST_IMAGE_URL)

    assert res.content == MOCK_BODY.encode()
    assert res.status_code == 200
    assert mock_get.matched


@pook.on
def test_get_successful_no_auth_key_not_compressed(mock_image_data):
    mock_get: pook.Mock = (
        pook.get(PHOTON_URL_FOR_TEST_IMAGE)
        .params(
            {
                "w": settings.THUMBNAIL_WIDTH_PX,
            }
        )
        .header("User-Agent", UA_HEADER)
        .header("Accept", "image/*")
        .reply(200)
        .body(MOCK_BODY)
        .mock
    )

    res = photon_get(TEST_IMAGE_URL, is_compressed=False)

    assert res.content == MOCK_BODY.encode()
    assert res.status_code == 200
    assert mock_get.matched


@pook.on
def test_get_successful_no_auth_key_full_size(mock_image_data):
    mock_get: pook.Mock = (
        pook.get(PHOTON_URL_FOR_TEST_IMAGE)
        .params(
            {
                "quality": settings.THUMBNAIL_QUALITY,
            }
        )
        .header("User-Agent", UA_HEADER)
        .header("Accept", "image/*")
        .reply(200)
        .body(MOCK_BODY)
        .mock
    )

    res = photon_get(TEST_IMAGE_URL, is_full_size=True)

    assert res.content == MOCK_BODY.encode()
    assert res.status_code == 200
    assert mock_get.matched


@pook.on
def test_get_successful_no_auth_key_full_size_not_compressed(mock_image_data):
    mock_get: pook.Mock = (
        pook.get(PHOTON_URL_FOR_TEST_IMAGE)
        .header("User-Agent", UA_HEADER)
        .header("Accept", "image/*")
        .reply(200)
        .body(MOCK_BODY)
        .mock
    )

    res = photon_get(TEST_IMAGE_URL, is_full_size=True, is_compressed=False)

    assert res.content == MOCK_BODY.encode()
    assert res.status_code == 200
    assert mock_get.matched


@pook.on
def test_get_successful_no_auth_key_png_only(mock_image_data):
    mock_get: pook.Mock = (
        pook.get(PHOTON_URL_FOR_TEST_IMAGE)
        .params(
            {
                "w": settings.THUMBNAIL_WIDTH_PX,
                "quality": settings.THUMBNAIL_QUALITY,
            }
        )
        .header("User-Agent", UA_HEADER)
        .header("Accept", "image/png")
        .reply(200)
        .body(MOCK_BODY)
        .mock
    )

    res = photon_get(TEST_IMAGE_URL, accept_header="image/png")

    assert res.content == MOCK_BODY.encode()
    assert res.status_code == 200
    assert mock_get.matched


@pook.on
def test_get_successful_forward_query_params(mock_image_data):
    params = urlencode({"hello": "world", 1: 2, "beep": "boop"})
    mock_get: pook.Mock = (
        pook.get(PHOTON_URL_FOR_TEST_IMAGE)
        .params(
            {
                "w": settings.THUMBNAIL_WIDTH_PX,
                "quality": settings.THUMBNAIL_QUALITY,
                "q": params,
            }
        )
        .header("User-Agent", UA_HEADER)
        .header("Accept", "image/*")
        .reply(200)
        .body(MOCK_BODY)
        .mock
    )

    url_with_params = f"{TEST_IMAGE_URL}?{params}"

    res = photon_get(url_with_params)

    assert res.content == MOCK_BODY.encode()
    assert res.status_code == 200
    assert mock_get.matched


@pytest.fixture
def setup_requests_get_exception(monkeypatch):
    def do(exc):
        def raise_exc(*args, **kwargs):
            raise exc

        monkeypatch.setattr("requests.get", raise_exc)

    yield do


@pook.on
def test_get_successful_records_response_code(mock_image_data, redis):
    (
        pook.get(PHOTON_URL_FOR_TEST_IMAGE)
        .params(
            {
                "w": settings.THUMBNAIL_WIDTH_PX,
                "quality": settings.THUMBNAIL_QUALITY,
            }
        )
        .header("User-Agent", UA_HEADER)
        .header("Accept", "image/*")
        .reply(200)
        .body(MOCK_BODY)
        .mock
    )

    photon_get(TEST_IMAGE_URL)
    month = get_monthly_timestamp()
    assert redis.get(f"thumbnail_response_code:{month}:200") == b"1"
    assert (
        redis.get(
            f"thumbnail_response_code_by_domain:subdomain.example.com:{month}:200"
        )
        == b"1"
    )


alert_count_params = pytest.mark.parametrize(
    "count_start, should_alert",
    [
        (0, True),
        (1, True),
        (50, True),
        (99, True),
        (100, False),
        (999, True),
        (1000, False),
        (1500, False),
        (1999, True),
    ],
)


@pytest.mark.parametrize(
    "exc, exc_name",
    [
        (ValueError("whoops"), "builtins.ValueError"),
        (requests.ConnectionError("whoops"), "requests.exceptions.ConnectionError"),
        (requests.ConnectTimeout("whoops"), "requests.exceptions.ConnectTimeout"),
        (requests.ReadTimeout("whoops"), "requests.exceptions.ReadTimeout"),
        (requests.Timeout("whoops"), "requests.exceptions.Timeout"),
        (requests.exceptions.SSLError("whoops"), "requests.exceptions.SSLError"),
        (OSError("whoops"), "builtins.OSError"),
    ],
)
@alert_count_params
def test_get_exception_handles_error(
    exc,
    exc_name,
    count_start,
    should_alert,
    capture_exception,
    setup_requests_get_exception,
    redis,
):
    setup_requests_get_exception(exc)
    month = get_monthly_timestamp()
    key = f"thumbnail_error:{exc_name}:subdomain.example.com:{month}"
    redis.set(key, count_start)

    with pytest.raises(UpstreamThumbnailException):
        photon_get(TEST_IMAGE_URL)

    assert_func = (
        capture_exception.assert_called_once
        if should_alert
        else capture_exception.assert_not_called
    )
    assert_func()
    assert redis.get(key) == str(count_start + 1).encode()


@alert_count_params
@pytest.mark.parametrize(
    "status_code, text",
    [
        (400, "Bad Request"),
        (401, "Unauthorized"),
        (403, "Forbidden"),
        (500, "Internal Server Error"),
    ],
)
def test_get_http_exception_handles_error(
    status_code,
    text,
    count_start,
    should_alert,
    capture_exception,
    setup_requests_get_exception,
    redis,
):
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = status_code
    mock_response.text = text
    exc = requests.HTTPError(response=mock_response)
    setup_requests_get_exception(exc)

    month = get_monthly_timestamp()
    key = f"thumbnail_error:requests.exceptions.HTTPError:subdomain.example.com:{month}"
    redis.set(key, count_start)

    with pytest.raises(UpstreamThumbnailException):
        photon_get(TEST_IMAGE_URL)

    assert_func = (
        capture_exception.assert_called_once
        if should_alert
        else capture_exception.assert_not_called
    )
    assert_func()
    assert redis.get(key) == str(count_start + 1).encode()

    # Assertions about the HTTP error specific message
    assert (
        redis.get(
            f"thumbnail_http_error:subdomain.example.com:{month}:{status_code}:{text}"
        )
        == b"1"
    )


@pook.on
def test_get_successful_https_image_url_sends_ssl_parameter(mock_image_data):
    https_url = TEST_IMAGE_URL.replace("http://", "https://")
    mock_get: pook.Mock = (
        pook.get(PHOTON_URL_FOR_TEST_IMAGE)
        .params(
            {
                "w": settings.THUMBNAIL_WIDTH_PX,
                "quality": settings.THUMBNAIL_QUALITY,
                "ssl": "true",
            }
        )
        .header("User-Agent", UA_HEADER)
        .header("Accept", "image/*")
        .reply(200)
        .body(MOCK_BODY)
        .mock
    )

    res = photon_get(https_url)

    assert res.content == MOCK_BODY.encode()
    assert res.status_code == 200
    assert mock_get.matched


@pook.on
def test_get_unsuccessful_request_raises_custom_exception():
    mock_get: pook.Mock = pook.get(PHOTON_URL_FOR_TEST_IMAGE).reply(404).mock

    with pytest.raises(
        UpstreamThumbnailException, match=r"Failed to render thumbnail."
    ):
        photon_get(TEST_IMAGE_URL)

    assert mock_get.matched


@pytest.mark.parametrize(
    "image_url, expected_ext",
    [
        ("example.com/image.jpg", "jpg"),
        ("www.example.com/image.JPG", "jpg"),
        ("http://example.com/image.jpeg", "jpeg"),
        ("https://subdomain.example.com/image.svg", "svg"),
        ("https://example.com/image.png?foo=1&bar=2#fragment", "png"),
        ("https://example.com/possibleimagewithoutext", ""),
        (
            "https://iip.smk.dk/iiif/jp2/kksgb22133.tif.jp2/full/!400,/0/default.jpg",
            "jpg",
        ),
    ],
)
def test__get_extension_from_url(image_url, expected_ext):
    assert _get_file_extension_from_url(image_url) == expected_ext


@pytest.mark.django_db
@pytest.mark.parametrize("image_type", ["apng", "svg", "bmp"])
def test_check_image_type_raises_by_not_allowed_types(image_type):
    image_url = TEST_IMAGE_URL.replace(".jpg", f".{image_type}")
    image = ImageFactory.create(url=image_url)

    with pytest.raises(UnsupportedMediaType):
        check_image_type(image_url, image)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "headers, expected_cache_val",
    [
        ({"Content-Type": "image/svg+xml"}, b"svg+xml"),
        (None, b"unknown"),
    ],
)
def test_check_image_type_saves_image_type_to_cache(redis, headers, expected_cache_val):
    image_url = TEST_IMAGE_URL.replace(".jpg", "")
    image = ImageFactory.create(url=image_url)

    with mock.patch("requests.head") as mock_head, pytest.raises(UnsupportedMediaType):
        mock_head.return_value.headers = headers
        check_image_type(image_url, image)

    key = f"media:{image.identifier}:thumb_type"
    assert redis.get(key) == expected_cache_val
