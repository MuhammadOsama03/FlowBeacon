from app.redaction import MAX_ATTRIBUTE_STRING, REDACTED, redact_attributes


def test_redacts_sensitive_keys_recursively():
    result = redact_attributes(
        {"authorization": "Bearer hidden", "nested": {"api_key": "hidden"}}
    )

    assert result == {
        "authorization": REDACTED,
        "nested": {"api_key": REDACTED},
    }


def test_redacts_inline_secrets_and_github_tokens():
    result = redact_attributes(
        "token=hidden ghp_abcdefghijklmnopqrstuvwxyz123456"
    )

    assert "hidden" not in result
    assert "ghp_" not in result


def test_bounds_attribute_strings():
    assert len(redact_attributes("x" * 10_000)) == MAX_ATTRIBUTE_STRING


def test_preserves_safe_scalar_values():
    assert redact_attributes({"attempt": 2, "cached": False}) == {
        "attempt": 2,
        "cached": False,
    }

