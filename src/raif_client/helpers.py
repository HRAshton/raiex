from argon2.low_level import Type as Argon2Type, hash_secret_raw

_ARGON_SETTINGS = {
    "argon2Type": 1,
    "argon2Time": 3,
    "argon2Mem": 4096,
    "argon2HashLen": 32,
    "argon2Version": 19,
}


def strip_bom(text: str) -> str:
    return text[1:] if text and ord(text[0]) == 0xFEFF else text


def argon2_hash_hex(password: str, username: str) -> str:
    salt_txt = username.lower()
    if len(salt_txt) < 8:
        salt_txt = salt_txt + ("\x00" * (8 - len(salt_txt)))
    salt_bytes = salt_txt.encode("utf-8")

    raw = hash_secret_raw(
        secret=password.encode("utf-8"),
        salt=salt_bytes,
        time_cost=int(_ARGON_SETTINGS["argon2Time"]),
        memory_cost=int(_ARGON_SETTINGS["argon2Mem"]),
        parallelism=1,
        hash_len=int(_ARGON_SETTINGS["argon2HashLen"]),
        type=_argon2_type(int(_ARGON_SETTINGS["argon2Type"])),
        version=int(_ARGON_SETTINGS["argon2Version"])
    )
    return raw.hex()


def _argon2_type(t: int) -> Argon2Type:
    if t == 0:
        return Argon2Type.D
    if t == 1:
        return Argon2Type.I
    return Argon2Type.ID
