"""
API Retry Utilities
提供 API 請求重試機制，支持指數退避策略
"""

import time
import random
from typing import Callable, Any, Optional, Tuple, Type
from functools import wraps


class RetryConfig:
    """重試配置常量"""
    DEFAULT_MAX_RETRIES = 3
    DEFAULT_BASE_DELAY = 1.0  # 基礎延遲（秒）
    DEFAULT_MAX_DELAY = 60.0  # 最大延遲（秒）
    DEFAULT_EXPONENTIAL_BASE = 2  # 指數底數
    DEFAULT_JITTER = True  # 是否添加隨機抖動


def exponential_backoff(
    max_retries: int = RetryConfig.DEFAULT_MAX_RETRIES,
    base_delay: float = RetryConfig.DEFAULT_BASE_DELAY,
    max_delay: float = RetryConfig.DEFAULT_MAX_DELAY,
    exponential_base: float = RetryConfig.DEFAULT_EXPONENTIAL_BASE,
    jitter: bool = RetryConfig.DEFAULT_JITTER,
    retry_on_exceptions: Tuple[Type[Exception], ...] = (Exception,),
    retry_on_status_codes: Optional[Tuple[int, ...]] = None
):
    """
    指數退避重試裝飾器

    Args:
        max_retries: 最大重試次數
        base_delay: 基礎延遲時間（秒）
        max_delay: 最大延遲時間（秒）
        exponential_base: 指數底數
        jitter: 是否添加隨機抖動（防止雷鳴效應）
        retry_on_exceptions: 需要重試的異常類型元組
        retry_on_status_codes: 需要重試的 HTTP 狀態碼（如 429, 500, 502, 503, 504）

    Returns:
        裝飾器函數

    Example:
        @exponential_backoff(max_retries=3, retry_on_status_codes=(429, 500, 502, 503))
        def call_api():
            response = requests.post(...)
            response.raise_for_status()
            return response.json()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(max_retries + 1):  # +1 因為第一次不算重試
                try:
                    return func(*args, **kwargs)

                except retry_on_exceptions as e:
                    last_exception = e

                    # 檢查是否是 HTTP 錯誤且狀態碼需要重試
                    should_retry = False

                    # 檢查 requests.HTTPError
                    if hasattr(e, 'response') and hasattr(e.response, 'status_code'):
                        status_code = e.response.status_code
                        if retry_on_status_codes and status_code in retry_on_status_codes:
                            should_retry = True
                            print(f"[Retry] HTTP {status_code} error detected, will retry")
                    else:
                        # 對於其他異常，也進行重試（但不超過最大次數）
                        should_retry = True

                    # 如果已經是最後一次嘗試，不再重試
                    if attempt >= max_retries:
                        print(f"[Retry] Max retries ({max_retries}) reached, giving up")
                        raise last_exception

                    if should_retry:
                        # 計算延遲時間（指數退避）
                        delay = min(
                            base_delay * (exponential_base ** attempt),
                            max_delay
                        )

                        # 添加隨機抖動（0.5x - 1.5x）
                        if jitter:
                            delay = delay * (0.5 + random.random())

                        print(f"[Retry] Attempt {attempt + 1}/{max_retries + 1} failed: {str(e)}")
                        print(f"[Retry] Waiting {delay:.2f} seconds before retry...")
                        time.sleep(delay)
                    else:
                        # 不需要重試的錯誤，直接拋出
                        raise e

            # 如果所有重試都失敗，拋出最後一個異常
            if last_exception:
                raise last_exception

        return wrapper
    return decorator


def retry_with_backoff(
    func: Callable,
    max_retries: int = RetryConfig.DEFAULT_MAX_RETRIES,
    base_delay: float = RetryConfig.DEFAULT_BASE_DELAY,
    max_delay: float = RetryConfig.DEFAULT_MAX_DELAY,
    retry_on_status_codes: Optional[Tuple[int, ...]] = (429, 500, 502, 503, 504),
    *args,
    **kwargs
) -> Any:
    """
    函數式重試包裝器（非裝飾器版本）

    用於直接調用重試邏輯而不使用裝飾器

    Args:
        func: 要執行的函數
        max_retries: 最大重試次數
        base_delay: 基礎延遲時間
        max_delay: 最大延遲時間
        retry_on_status_codes: 需要重試的 HTTP 狀態碼
        *args: 傳遞給 func 的位置參數
        **kwargs: 傳遞給 func 的關鍵字參數

    Returns:
        函數執行結果

    Example:
        result = retry_with_backoff(
            requests.post,
            max_retries=3,
            retry_on_status_codes=(429, 500),
            'https://api.example.com',
            headers=headers,
            json=data
        )
    """
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            return func(*args, **kwargs)

        except Exception as e:
            last_exception = e

            # 檢查是否需要重試
            should_retry = False

            if hasattr(e, 'response') and hasattr(e.response, 'status_code'):
                status_code = e.response.status_code
                if retry_on_status_codes and status_code in retry_on_status_codes:
                    should_retry = True
                    print(f"[Retry] HTTP {status_code} error detected, will retry")
            else:
                should_retry = True

            # 最後一次嘗試
            if attempt >= max_retries:
                print(f"[Retry] Max retries ({max_retries}) reached, giving up")
                raise last_exception

            if should_retry:
                # 計算延遲
                delay = min(
                    base_delay * (2 ** attempt),
                    max_delay
                )
                delay = delay * (0.5 + random.random())  # 添加抖動

                print(f"[Retry] Attempt {attempt + 1}/{max_retries + 1} failed: {str(e)}")
                print(f"[Retry] Waiting {delay:.2f} seconds before retry...")
                time.sleep(delay)
            else:
                raise e

    if last_exception:
        raise last_exception


# 預定義的重試配置
OPENAI_RETRY_CONFIG = {
    'max_retries': 5,  # OpenAI 建議最多重試 5 次
    'base_delay': 1.0,
    'max_delay': 60.0,
    'retry_on_status_codes': (429, 500, 502, 503, 504),  # 速率限制和服務器錯誤
}
