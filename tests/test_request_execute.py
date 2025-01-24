from sqlite3 import paramstyle
import pytest
from unittest.mock import patch, Mock
from serverless_reverse_proxy.processes.Request_Execute import RequestExecute


def test_is_valid_url():
    req_executor = RequestExecute()
    assert req_executor.is_valid_url("https://google.com") is True 
    assert req_executor.is_valid_url("https://youtube.com") is True
    assert req_executor.is_valid_url("hello") is False


def test_is_valid_method(): 
    req_executor = RequestExecute()
    assert req_executor.is_valid_method("GET") is True 
    assert req_executor.is_valid_method("POST") is True 
    assert req_executor.is_valid_method("INVALID") is False

def test_is_valid_headers(): 
    req_executor = RequestExecute()
    assert req_executor.is_valid_headers({"test_key":"test_value"}) == True
    assert req_executor.is_valid_headers({}) == True
    assert req_executor.is_valid_headers({1: "test_value"}) == False
    assert req_executor.is_valid_headers({"test_key": 1}) == False
    assert req_executor.is_valid_headers({None:None}) == False

    
def test_setup_valid_request():
    req_executor = RequestExecute()
    req_executor.setup("GET", "http://google.com", params={"q":"test"})
    assert req_executor.method == ("GET")
    assert req_executor.url == ("http://google.com")
    assert req_executor.params == {"q":"test"}

def test_setup_invalid_url(): 
    req_executor = RequestExecute()
    with pytest.raises(ValueError, match="Invalid URL"):
        req_executor.setup("GET", "INVALID URL")


@patch('requests.request') # sim mock http requests, used to utilise mock inside func instead
def test_run(mock_request): 
    mock_response = Mock()
    mock_response.status_code = 200 
    mock_response.text = "Success"
    mock_response.json.return_value = {"key": "value"}

    mock_request.return_value = mock_response #set return value of mock request 

    req_executor = RequestExecute()
    req_executor.setup("GET", "http://google.com", params={"q":"test"})
    req_executor.run()

    mock_request.assert_called_once_with(method=req_executor.method,
                                        url = req_executor.url,
                                        params = req_executor.params,
                                        data = req_executor.data, 
                                        headers = req_executor.headers)

    assert req_executor.raw_response.status_code == 200
    assert req_executor.raw_response.text == "Success"


@patch('requests.request')
def test_response(mock_request): 
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.headers = {"content_type": "application/json"}
    mock_response.text = '{"key": "value"}'
    
    mock_request.return_value = mock_response

    req_executor = RequestExecute()
    req_executor.setup("GET", "http://google.com", params={"q":"test"})
    req_executor.run()
    
    response = req_executor.response()
    assert response["status_code"] == 200
    assert response["headers"]["content_type"] == "application/json"
    assert response["text"] == '{"key": "value"}'
    

@patch('requests.request')
def test_response_with_non_json(mock_request): 
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.headers = {"content_type": "text/html"}
    mock_response.text = "<html><body>Success</body></html>"
    mock_response.json.side_effect = ValueError("No JSON content")

    mock_request.return_value = mock_response

    req_executor = RequestExecute()
    req_executor.raw_response = mock_response

    result = req_executor.response()

    assert result["status_code"] == 200
    assert result["json"] is None
    assert result["headers"]["content_type"] == "text/html"
    assert result["text"] == "<html><body>Success</body></html>"


@patch('requests.request')
def test_response_with_missing_content_type(mock_request):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.headers = {}  # No Content-Type header
    mock_response.text = "Success"
    mock_response.json.side_effect = ValueError("No JSON content")

    mock_request.return_value = mock_response

    req_executor = RequestExecute()
    req_executor.raw_response = mock_response

    result = req_executor.response()

    assert result["status_code"] == 200
    assert result["content_type"] is None
    assert result["json"] is None
    assert result["text"] == "Success"
    assert result['headers'] == {}


def test_response_with_no_raw_response():
    req_executor = RequestExecute()
    req_executor.raw_response = None

    result = req_executor.response()

    assert result == {}
