from src.utils.short_code import generate_short_code
from src.utils.password import hash_password, verify_password


def test_short_code_generation():
    code = generate_short_code()
    assert isinstance(code, str)
    assert len(code) >= 6


def test_short_code_uniqueness():
    codes = {generate_short_code() for _ in range(25)}
    assert len(codes) == 25


def test_password_hash_and_verify():
    password = "secure-password"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong-password", hashed)
