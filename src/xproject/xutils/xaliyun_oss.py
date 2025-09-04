from __future__ import annotations

import os
import random
import time
from dataclasses import dataclass
from functools import wraps
from typing import Callable, TypeVar, ParamSpec, Any, overload

import oss2


@dataclass
class OSSConfig:
    endpoint: str
    bucket_name: str
    access_key_id: str
    access_key_secret: str
    security_token: str | None = None

    @classmethod
    def from_env(cls) -> OSSConfig:
        return cls(
            endpoint=os.environ.get("ALIYUN_OSS_ENDPOINT", ""),
            bucket_name=os.environ.get("ALIYUN_OSS_BUCKET_NAME", ""),
            access_key_id=os.environ.get("ALIYUN_OSS_ACCESS_KEY_ID", ""),
            access_key_secret=os.environ.get("ALIYUN_OSS_ACCESS_KEY_SECRET", ""),
            security_token=os.environ.get("ALIYUN_OSS_SECURITY_TOKEN"),
        )


def _is_retryable(exception: Exception) -> bool:
    if isinstance(exception, oss2.exceptions.RequestError):
        return True
    return False


P = ParamSpec("P")
R = TypeVar("R")

Decorator = Callable[[Callable[P, R]], Callable[P, R]]


@overload
def retry(
        func: None = ...,
        *,
        max_retries: int = ...,
        delay: float = ...,
        backoff: float = ...,
        jitter: float = ...,
) -> Decorator:
    ...


@overload
def retry(
        func: Callable[P, R],
        *,
        max_retries: int = ...,
        delay: float = ...,
        backoff: float = ...,
        jitter: float = ...,
) -> Callable[P, R]:
    ...


def retry(
        func: Callable[P, R] | None = None,
        *,
        max_retries: int = 3,
        delay: float = 0.5,
        backoff: float = 2.0,
        jitter: float = 0.1,
) -> Any:
    def decorator(fn: Callable[P, R]) -> Callable[P, R]:
        @wraps(fn)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            delay_ = max(0.0, delay)
            last_exception: Exception | None = None

            for retries in range(1, max(1, max_retries) + 1):
                try:
                    return fn(*args, **kwargs)
                except Exception as exception:
                    last_exception = exception
                    if not _is_retryable(exception) or retries >= max_retries:
                        raise
                    time.sleep(delay_ + random.uniform(0.0, jitter))
                    delay_ *= max(1.0, backoff)

            raise last_exception.with_traceback(last_exception.__traceback__)

        return wrapper

    if func is None:
        return decorator

    return decorator(func)


class AliyunOSS:
    def __init__(self, bucket: oss2.Bucket):
        self._bucket = bucket

    @classmethod
    def from_config(cls, config: OSSConfig) -> AliyunOSS:
        auth = (
            oss2.Auth(config.access_key_id, config.access_key_secret)
            if not config.security_token
            else oss2.StsAuth(config.access_key_id, config.access_key_secret, config.security_token)
        )
        bucket = oss2.Bucket(auth, config.endpoint, config.bucket_name)
        return cls(bucket)

    @classmethod
    def from_params(
            cls,
            endpoint: str,
            bucket_name: str,
            access_key_id: str,
            access_key_secret: str,
            security_token: str | None = None,
    ) -> AliyunOSS:
        return cls.from_config(OSSConfig(endpoint, bucket_name, access_key_id, access_key_secret, security_token))

    # ========== upload ==========
    @retry
    def put_content(
            self,
            key: str,
            content: bytes,
            *,
            headers: dict[str, str] | oss2.CaseInsensitiveDict | None = None,
            progress_callback: Callable[[int, int | None], None] | None = None
    ) -> oss2.models.PutObjectResult:
        return self._bucket.put_object(key, content, headers=headers, progress_callback=progress_callback)

    @retry
    def put_text(
            self,
            key: str,
            text: str,
            *,
            encoding: str = "utf-8",
            headers: dict[str, str] | oss2.CaseInsensitiveDict | None = None,
            progress_callback: Callable[[int, int | None], None] | None = None
    ) -> oss2.models.PutObjectResult:
        data = text.encode(encoding)
        return self._bucket.put_object(key, data, headers=headers, progress_callback=progress_callback)

    @retry
    def put_object_from_file(
            self,
            key: str,
            filename: str,
            *,
            headers: dict[str, str] | oss2.CaseInsensitiveDict | None = None,
            progress_callback: Callable[[int, int | None], None] | None = None
    ) -> oss2.models.PutObjectResult:
        return self._bucket.put_object_from_file(key, filename, headers=headers, progress_callback=progress_callback)

    # ========== download ==========
    @retry
    def get_bytes(
            self,
            key: str,
            *,
            byte_range: tuple[int | None, int | None] | None = None,
            headers: dict[str, str] | oss2.CaseInsensitiveDict | None = None,
            progress_callback: Callable[[int, int | None], None] | None = None,
            process: str | None = None,
            params: dict[str, str] | None = None
    ) -> bytes:
        response = self._bucket.get_object(
            key,
            byte_range=byte_range,
            headers=headers,
            progress_callback=progress_callback,
            process=process,
            params=params
        )
        try:
            return response.read()
        finally:
            response.close()

    @retry
    def get_text(
            self,
            key: str,
            *,
            encoding: str = "utf-8",
            byte_range: tuple[int | None, int | None] | None = None,
            headers: dict[str, str] | oss2.CaseInsensitiveDict | None = None,
            progress_callback: Callable[[int, int | None], None] | None = None,
            process: str | None = None,
            params: dict[str, str] | None = None
    ) -> str:
        response = self._bucket.get_object(
            key,
            byte_range=byte_range,
            headers=headers,
            progress_callback=progress_callback,
            process=process,
            params=params
        )
        try:
            return response.read().decode(encoding)
        finally:
            response.close()

    # ========== manage ==========
    @retry
    def object_exists(
            self,
            key: str,
            *,
            headers: dict[str, str] | oss2.CaseInsensitiveDict | None = None
    ) -> bool:
        return self._bucket.object_exists(key, headers=headers)

    @retry
    def head_object(
            self,
            key: str,
            *,
            headers: dict[str, str] | oss2.CaseInsensitiveDict | None = None,
            params: dict[str, str] | oss2.CaseInsensitiveDict | None = None
    ) -> oss2.models.HeadObjectResult:
        return self._bucket.head_object(key, headers=headers, params=params)

    @retry
    def delete_object(
            self,
            key: str,
            *,
            params: dict[str, str] | None = None,
            headers: dict[str, str] | oss2.CaseInsensitiveDict | None = None
    ) -> oss2.models.RequestResult:
        return self._bucket.delete_object(key, params=params, headers=headers)

    @retry
    def batch_delete_objects(
            self,
            key_list: list[str],
            *,
            headers: dict[str, str] | oss2.CaseInsensitiveDict | None = None
    ) -> oss2.models.BatchDeleteObjectsResult | None:
        if not key_list:
            return None
        return self._bucket.batch_delete_objects(key_list, headers=headers)
