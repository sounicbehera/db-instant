from secrets import token_urlsafe


def generate_username() -> str:
    return f"dev_{token_urlsafe(4)}"


def generate_password() -> str:
    return token_urlsafe(16)