import hmac
import hashlib
import time
import base64
import binascii
from typing import Mapping
from nacl.signing import VerifyKey

# Telegram публичный ключ (production)
TELEGRAM_PUBKEY_PROD = "e7bf03a2fa4602af4580703d88dda5bb59f32ed8b02a56c187fe7d34caed242d"


# ==============================================================
#  WIDGET VALIDATION (Telegram Login Widget)
# ==============================================================
def _data_check_string_widget(data: Mapping[str, str]) -> str:
    items = []
    for k in sorted(data.keys()):
        if k in ("hash", "signature"):
            continue
        items.append(f"{k}={data[k]}")
    return "\n".join(items)


def validate_login_widget(data: Mapping[str, str], bot_token: str, max_age_sec: int = 3600) -> bool:
    """Validation for Telegram Login Widget (NOT WebApp initData).
    Secret = SHA256(bot_token), then HMAC_SHA256(data_check_string, secret).
    """
    print("=== validate_login_widget ===")

    if not bot_token:
        print("❌ Missing bot_token")
        return False

    # --- проверка времени ---
    try:
        auth_date = int(data.get("auth_date", "0"))
    except ValueError:
        print("❌ auth_date invalid")
        return False

    if not auth_date or (int(time.time()) - auth_date) > max_age_sec:
        print("❌ auth_date expired/invalid:", auth_date)
        return False

    # --- проверка подписи ---
    recv_hash = data.get("hash", "")
    dcs = _data_check_string_widget(data)

    secret_key = hashlib.sha256(bot_token.encode("utf-8")).digest()
    calc = hmac.new(secret_key, dcs.encode("utf-8"), hashlib.sha256).hexdigest()

    print("Widget validation:")
    print("  data_check_string =", dcs)
    print("  recv_hash         =", recv_hash)
    print("  calc_hash         =", calc)

    result = hmac.compare_digest(calc, recv_hash)
    print("RESULT (widget) =", result)
    return result


# ==============================================================
#  MINIAPP VALIDATION (Telegram WebApp initData)
# ==============================================================
def _data_check_string_miniapp(data: Mapping[str, str], bot_id: str = None) -> str:
    items = []
    for k in sorted(data.keys()):
        if k in ("hash", "signature"):
            continue
        items.append(f"{k}={data[k]}")

    if bot_id:
        return f"{bot_id}:WebAppData\n" + "\n".join(items)
    return "\n".join(items)


def validate_miniapp(data: Mapping[str, str], bot_token: str, max_age_sec: int = 3600) -> bool:
    """Validation for Telegram MiniApp initData (supports both new signature and legacy hash)."""
    print("=== validate_miniapp ===")

    # --- проверка времени ---
    try:
        auth_date = int(data.get("auth_date", "0"))
    except ValueError:
        print("❌ auth_date invalid")
        return False

    if not auth_date or (int(time.time()) - auth_date) > max_age_sec:
        print("❌ auth_date expired/invalid:", auth_date)
        return False

    # --- Вариант 1: новая схема (Ed25519 signature) ---
    signature = data.get("signature")
    if signature:
        print("→ Using Ed25519 signature validation")
        bot_id = bot_token.split(":")[0]
        dcs = _data_check_string_miniapp(data, bot_id)
        print("  data_check_string =", dcs)

        try:
            sig_bytes = base64.urlsafe_b64decode(signature + "==")
            verify_key = VerifyKey(binascii.unhexlify(TELEGRAM_PUBKEY_PROD))
            verify_key.verify(dcs.encode("utf-8"), sig_bytes)
            print("✅ MiniApp Ed25519 signature valid")
            return True
        except Exception as e:
            print("❌ MiniApp signature check failed:", e)
            return False

    # --- Вариант 2: fallback (старый HMAC) ---
    recv_hash = data.get("hash", "")
    if recv_hash:
        print("→ Using fallback HMAC validation")
        dcs = _data_check_string_miniapp(data)
        print("  data_check_string =", dcs)

        secret_key = hmac.new(
            key=bot_token.encode("utf-8"),
            msg=b"WebAppData",
            digestmod=hashlib.sha256
        ).digest()
        calc = hmac.new(secret_key, dcs.encode("utf-8"), hashlib.sha256).hexdigest()

        print("  recv_hash =", recv_hash)
        print("  calc_hash =", calc)

        result = hmac.compare_digest(calc, recv_hash)
        print("RESULT (miniapp HMAC) =", result)
        return result

    print("❌ No signature/hash found in data")
    return False
