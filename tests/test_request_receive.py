import pytest
from unittest.mock import patch, Mock
from serverless_reverse_proxy.processes import Request_Receive
from serverless_reverse_proxy.processes.Request_Receive import RequestReceive



def test_validate(): 
    mock_reverse_proxy = Mock()

    req_receive = RequestReceive(reverse_proxy=mock_reverse_proxy) #mock to fulfill dependency and test function
    assert req_receive.validate({}) is True

    with pytest.raises(ValueError, match="Invalid payload: must be a dictionary"):
        req_receive.validate("invalid_payload")

def test_run_without_mock():
    mock_reverse_proxy = Mock()
    req_receive = RequestReceive(reverse_proxy=mock_reverse_proxy) #ensure the dependency is correctly mocked
    assert req_receive.reverse_proxy is mock_reverse_proxy

def test_run():
    mock_reverse_proxy = Mock() 
    req_receive = RequestReceive(reverse_proxy=mock_reverse_proxy)

    # Test with a valid payload (a dictionary)
    valid_payload = {"key": "value"}  # This is a valid dictionary payload
    response = req_receive.run(valid_payload)

    # Assert that the returned response is an instance of RequestReceive (self)
    assert isinstance(response, RequestReceive)

    invalid_payload = "Invalid data"
    response = req_receive.run(invalid_payload)

    # Assert that the returned response is a dictionary with an error message
    # Also the payload will be an invalid data type
    assert isinstance(response, dict)
    assert "Error validating request" in response 