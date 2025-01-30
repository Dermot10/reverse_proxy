import pytest
from serverless_reverse_proxy.processes.Request_Receive import RequestReceive  # Adjust import based on your project structure


def test_validate_valid_payload():
    receiver = RequestReceive(reverse_proxy=None)
    valid_payload = {"key": "value"}

    assert receiver.validate(valid_payload) is True


def test_validate_invalid_payload():
    receiver = RequestReceive(reverse_proxy=None)

    with pytest.raises(ValueError, match="Invalid payload: must be a dictionary"):
        receiver.validate("invalid_payload")  # Not a dict


@pytest.mark.parametrize("invalid_payload", [None, [], "string", 123, 45.67])
def test_validate_various_invalid_payloads(invalid_payload):
    receiver = RequestReceive(reverse_proxy=None)

    with pytest.raises(ValueError, match="Invalid payload: must be a dictionary"):
        receiver.validate(invalid_payload)


def test_run_valid_payload():
    receiver = RequestReceive(reverse_proxy=None)
    valid_payload = {"key": "value"}

    result = receiver.run(valid_payload)
    assert result == valid_payload
    assert receiver.request_payload == valid_payload


def test_run_invalid_payload():
    receiver = RequestReceive(reverse_proxy=None)
    invalid_payload = "not_a_dict"

    result = receiver.run(invalid_payload)

    assert "Error validating request" in result
    assert isinstance(result["Error validating request"], ValueError)
