import hmac, hashlib
from urllib.parse import parse_qsl

BOT_TOKEN = "8363201760:AAE0-9WQx7WRnDLwKcg_WTV7G6QCerDfLxw"

RAW = "query_id=AAFM0LoVAAAAAEzQuhVIinX2&user=%7B%22id%22%3A364564556%2C%22first_name%22%3A%22Pavel%22%2C%22last_name%22%3A%22D.%22%2C%22username%22%3A%22crowdprophet%22%2C%22language_code%22%3A%22en%22%2C%22is_premium%22%3Atrue%2C%22allows_write_to_pm%22%3Atrue%2C%22photo_url%22%3A%22https%3A%5C%2F%5C%2Ft.me%5C%2Fi%5C%2Fuserpic%5C%2F320%5C%2FCTDTmmBSnrgguY0bEXBu0OB7pGNxDTiEYY-586jQdCQ.svg%22%7D&auth_date=1755643062&signature=wpnFhGOCGSmRF-SaBsB6JHRLjK5-7BZcGklVIBXMzPbgKfsxnaza3LMd_IF8RdKaBL5B_8pD47FkCmQAJPyVAg&hash=c39b27134e9d20c54e963a43ae4034900d1210d0b50010593b6ad47cbf21401b"

def _data_check_string(data_items):
    items = []
    for k, v in sorted(data_items):
        if k in ("hash", "signature"):
            continue
        items.append(f"{k}={v}")
    return "\n".join(items)

def validate_miniapp(raw, bot_token):
    # работаем напрямую со строкой, без json.loads/unquote
    data_items = parse_qsl(raw, keep_blank_values=True, strict_parsing=False)
    dcs = _data_check_string(data_items)

    recv_hash = dict(data_items).get("hash", "")

    secret_key = hmac.new(
        key=bot_token.encode("utf-8"),
        msg=b"WebAppData",
        digestmod=hashlib.sha256
    ).digest()

    calc = hmac.new(secret_key, dcs.encode("utf-8"), hashlib.sha256).hexdigest()

    print("data_check_string:\n", dcs)
    print("recv_hash:", recv_hash)
    print("calc_hash:", calc)

    return hmac.compare_digest(calc, recv_hash)

print("VALID:", validate_miniapp(RAW, BOT_TOKEN))
