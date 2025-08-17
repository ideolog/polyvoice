import hmac
import hashlib
import time
from typing import Mapping
import logging
logger = logging.getLogger(__name__)


def _data_check_string(data: Mapping[str, str]) -> str:
    items = []
    for k in sorted(data.keys()):
        if k in ("hash", "signature"):
            continue
        v = data[k]
        items.append(f"{k}={v}")
    return "\n".join(items)


def validate_login_widget(data: Mapping[str, str], bot_token: str, max_age_sec: int = 3600) -> bool:
    """Validation for Telegram Login Widget (NOT WebApp initData).
    Secret = SHA256(bot_token), then HMAC_SHA256(data_check_string, secret).
    """
    if not bot_token:
        return False

    try:
        auth_date = int(data.get("auth_date", "0"))
    except ValueError:
        auth_date = 0

    # защита по времени
    if not auth_date or (int(time.time()) - auth_date) > max_age_sec:
        return False

    recv_hash = data.get("hash", "")
    dcs = _data_check_string(data)

    secret_key = hashlib.sha256(bot_token.encode("utf-8")).digest()
    calc = hmac.new(secret_key, dcs.encode("utf-8"), hashlib.sha256).hexdigest()
    return hmac.compare_digest(calc, recv_hash)


def validate_miniapp(data: Mapping[str, str], bot_token: str, max_age_sec: int = 3600) -> bool:
    if not bot_token:
        return False

    try:
        auth_date = int(data.get("auth_date", "0"))
    except ValueError:
        auth_date = 0

    if not auth_date or (int(time.time()) - auth_date) > max_age_sec:
        return False

    recv_hash = data.get("hash", "")
    dcs = _data_check_string(data)

    # правильный порядок: key=bot_token, data="WebAppData"
    secret_key = hmac.new(bot_token.encode("utf-8"), b"WebAppData", hashlib.sha256).digest()
    calc = hmac.new(secret_key, dcs.encode("utf-8"), hashlib.sha256).hexdigest()


    logger.debug("MiniApp validation: dcs=%s", dcs)
    logger.debug("recv_hash=%s", recv_hash)
    logger.debug("calc_hash=%s", calc)


    return hmac.compare_digest(calc, recv_hash)

