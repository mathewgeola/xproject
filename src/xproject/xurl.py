import os
import re
import sys
from collections.abc import Buffer
from typing import Any, Final, cast
from urllib import parse

import furl
import httpx
import tldextract
from w3lib.url import canonicalize_url

from xproject.xheaders import get_default_headers


def get_furl_obj(url: str) -> furl.furl:
    return furl.furl(url)


def get_origin_path(url: str) -> str:
    """
    >>> get_origin_path("https://passport.jd.com/new/login.aspx?ReturnUrl=https%3A%2F%2Fwww.jd.com%2F")
    'https://passport.jd.com/new/login.aspx'

    :param url:
    :return:
    """
    furl_obj = get_furl_obj(url)
    origin_path = str(furl_obj.origin) + str(furl_obj.path)
    return origin_path


def get_parse_result(url: str) -> parse.ParseResult:
    parse_result = parse.urlparse(url)
    return parse_result


def is_valid(url: str) -> bool:
    """
    >>> is_valid("https://www.baidu.com/")
    True

    :param url:
    :return:
    """
    try:
        parse_result = get_parse_result(url)
        scheme, netloc = parse_result.scheme, parse_result.netloc
        if not scheme:
            return False
        if not netloc:
            return False
        if scheme not in ("http", "https"):
            return False
        return True
    except ValueError:
        return False


def quote(url: str, safe: str = "%;/?:@&=+$,", encoding: str = "utf-8") -> str:
    """
    >>> quote("https://www.baidu.com/s?wd=你好")
    'https://www.baidu.com/s?wd=%E4%BD%A0%E5%A5%BD'

    :param url:
    :param safe:
    :param encoding:
    :return:
    """
    return parse.quote(url, safe=safe, encoding=encoding)


def unquote(url: str, encoding: str = "utf-8") -> str:
    """
    >>> unquote("https://www.baidu.com/s?wd=%E4%BD%A0%E5%A5%BD")
    'https://www.baidu.com/s?wd=你好'

    :param url:
    :param encoding:
    :return:
    """
    return parse.unquote(url, encoding=encoding)


def encode(params: dict[str, Any]) -> str:
    """
    >>> encode({"a": "1", "b": "2"})
    'a=1&b=2'

    :param params:
    :return:
    """
    return parse.urlencode(params)


def decode(url: str) -> dict[str, str]:
    """
    >>> decode("xxx?a=1&b=2")
    {'a': '1', 'b': '2'}

    :param url:
    :return:
    """
    params = dict()

    lst = url.split("?", maxsplit=1)[-1].split("&")
    for i in lst:
        key, value = i.split("=", maxsplit=1)
        params[key] = unquote(value)

    return params


def join_url(base_url: str, url: str) -> str:
    """
    >>> join_url("https://www.baidu.com/", "/s?ie=UTF-8&wd=xspider")
    'https://www.baidu.com/s?ie=UTF-8&wd=xspider'

    :param base_url:
    :param url:
    :return:
    """
    return parse.urljoin(base_url, url)


def join_params(url: str, params: dict[str, Any]) -> str:
    """
    >>> join_params("https://www.baidu.com/s", {"wd": "你好"})
    'https://www.baidu.com/s?wd=%E4%BD%A0%E5%A5%BD'

    :param url:
    :param params:
    :return:
    """
    if not params:
        return url

    params = encode(params)
    separator = "?" if "?" not in url else "&"
    return url + separator + params


def get_params(url: str) -> dict[str, str]:
    """
    >>> get_params("https://www.baidu.com/s?wd=xspider")
    {'wd': 'xspider'}

    :param url:
    :return:
    """
    furl_obj = get_furl_obj(url)
    params = dict(furl_obj.query.params)
    return params


def get_param(url: str, key: str, default: Any | None = None) -> Any:
    """
    >>> get_param("https://www.baidu.com/s?wd=xspider", "wd")
    'xspider'

    :param url:
    :param key:
    :param default:
    :return:
    """
    params = get_params(url)
    param = params.get(key, default)
    return param


def get_url_params(url: str) -> tuple[str, dict[str, str]]:
    """
    >>> get_url_params("https://www.baidu.com/s?wd=xspider")
    ('https://www.baidu.com/s', {'wd': 'xspider'})

    :param url:
    :return:
    """
    root_url = ""
    params = dict()

    if "?" in url:
        root_url = url.split("?", maxsplit=1)[0]
        params = get_params(url)
    else:
        if re.search("[&=]", url) and not re.search("/", url):
            params = get_params(url)
        else:
            root_url = url

    return root_url, params


def get_domain(url: str) -> str:
    """
    >>> get_domain("https://www.baidu.com/s?wd=xspider")
    'baidu'

    :param url:
    :return:
    """
    er = tldextract.extract(url)
    domain = er.domain
    return domain


def get_subdomain(url: str) -> str:
    """
    >>> get_subdomain("https://passport.jd.com/new/login.aspx?ReturnUrl=https%3A%2F%2Fwww.jd.com%2F")
    'passport'

    :param url:
    :return:
    """
    er = tldextract.extract(url)
    subdomain = er.subdomain
    return subdomain


def canonicalize(url: str) -> str:
    """
    >>> canonicalize("https://www.baidu.com/s?wd=xspider")
    'https://www.baidu.com/s?wd=xspider'

    :param url:
    :return:
    """
    return canonicalize_url(url)


def url_to_file_path(
        url: str,
        headers: dict[str, Any] | None = None,
        file_path: str | None = None,
        dir_path: str | None = None,
        file_name: str | None = None,
        file_prefix: str | None = None,
        file_suffix: str | None = None,
        use_cache: bool = True,
) -> str | None:
    if not is_valid(url):
        return None

    if headers is None:
        headers = get_default_headers()

    if file_path is None:
        if dir_path is None:
            sys_argv0 = sys.argv[0]
            if not os.path.isfile(sys_argv0):
                return None
            dir_path = os.path.dirname(sys_argv0)
        if file_name is None:
            if file_prefix is not None and file_suffix is not None:
                file_name = file_prefix + file_suffix
            else:
                if file_prefix is None:
                    file_prefix, _ = os.path.splitext(get_furl_obj(url).path.segments[-1])
                if file_suffix is None:
                    _, file_suffix = os.path.splitext(get_furl_obj(url).path.segments[-1])
                    if file_suffix is None or file_suffix == "":
                        response = httpx.head(url, headers=headers)
                        if (content_type := response.headers.get("content-type")) is not None:
                            # todo：add more content_type
                            content_type_to_file_suffix: Final[dict[str, str]] = {
                                "image/png": "png",
                                "image/gif": "gif",
                                "text/html;charset=utf-8": "html",
                                "text/javascript; charset=utf-8": "js",
                            }
                            file_ext = content_type_to_file_suffix[content_type]
                            file_suffix = "." + file_ext
                file_name = file_prefix + file_suffix
        file_path = os.path.join(dir_path, file_name)

    file_path = os.path.abspath(file_path)

    if use_cache:
        if os.path.exists(file_path):
            return file_path

    dir_path = os.path.dirname(file_path)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    try:
        response = httpx.get(url, headers=headers)
        content = response.content
        data = cast(Buffer, content)
        with open(file_path, "wb") as f:
            f.write(data)
    except Exception:  # noqa
        file_path = None

    return file_path
