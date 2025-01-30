import pytest
from unittest.mock import patch, Mock
from serverless_reverse_proxy.processes.Request_Execute import RequestExecute  # Adjust import based on your project structure


def test_valid_url():
    req_exec = RequestExecute()
    assert req_exec.is_valid_url("https://example.com")
    assert not req_exec.is_valid_url("invalid-url")
    assert not req_exec.is_valid_url("ftp://example.com")  # Only HTTP(S) expected


def test_valid_method():
    req_exec = RequestExecute()
    assert req_exec.is_valid_method("GET")
    assert req_exec.is_valid_method("POST")
    assert not req_exec.is_valid_method("INVALID")


def test_valid_headers():
    req_exec = RequestExecute()
    assert req_exec.is_valid_headers({"User-Agent": "pytest"})
    assert not req_exec.is_valid_headers("invalid")
    assert not req_exec.is_valid_headers({1: "value"})  # Key must be a string


def test_setup_valid():
    req_exec = RequestExecute()
    req_exec.setup("GET", "https://example.com", headers={"User-Agent": "pytest"})
    assert req_exec.method == "GET"
    assert req_exec.url == "https://example.com"
    assert req_exec.headers == {"User-Agent": "pytest"}


def test_setup_invalid_method():
    req_exec = RequestExecute()
    with pytest.raises(ValueError, match="Invalid HTTP method"):
        req_exec.setup("INVALID", "https://example.com")


def test_setup_invalid_url():
    req_exec = RequestExecute()
    with pytest.raises(ValueError, match="Invalid URL"):
        req_exec.setup("GET", "invalid-url")


def test_setup_invalid_headers():
    req_exec = RequestExecute()
    with pytest.raises(ValueError, match="Headers must be a dictionary"):
        req_exec.setup("GET", "https://example.com", headers="invalid")


@patch('requests.request')
def test_run(mock_request):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.text = '{"message": "success"}'
    mock_response.json.return_value = {"message": "success"}

    mock_request.return_value = mock_response

    req_exec = RequestExecute()
    req_exec.setup("GET", "https://example.com")
    req_exec.run()

    assert req_exec.raw_response.status_code == 200
    assert req_exec.raw_response.text == '{"message": "success"}'


@patch('requests.request')
def test_response_json(mock_request):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.text = '{"key": "value"}'
    mock_response.json.return_value = {"key": "value"}

    mock_request.return_value = mock_response

    req_exec = RequestExecute()
    req_exec.run()
    req_exec.raw_response = mock_response  # Manually inject mock response

    response = req_exec.response()

    assert response["status_code"] == 200
    assert response["content_type"] == "application/json"
    assert response["json"] == {"key": "value"}
    assert response["text"] == '{"key": "value"}'


@patch('requests.request')
def test_response_text(mock_request):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.headers = {"Content-Type": "text/html"}
    mock_response.text = "<html>Success</html>"

    mock_request.return_value = mock_response

    req_exec = RequestExecute()
    req_exec.run()
    req_exec.raw_response = mock_response

    response = req_exec.response()

    assert response["status_code"] == 200
    assert response["content_type"] == "text/html"
    assert response["text"] == "<html>Success</html>"


@patch('requests.request')
def test_response_missing_content_type(mock_request):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.headers = {}
    mock_response.text = ""

    mock_request.return_value = mock_response

    req_exec = RequestExecute()
    req_exec.run()
    req_exec.raw_response = mock_response

    response = req_exec.response()

    assert response["status_code"] == 200
    assert response["content_type"] is None
    assert response["text"] == ""
