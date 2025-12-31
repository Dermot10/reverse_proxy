import pytest
from unittest.mock import patch, Mock, MagicMock
from reverse_proxy.processes.Response_Transform import ResponseTransform
from bs4 import BeautifulSoup

@pytest.fixture
def response_transform():
    mock_reverse_proxy = MagicMock()
    return ResponseTransform(mock_reverse_proxy)

def test_execute_transformation_request_with_valid_text(response_transform):
    response = {'text': '<html><head><title>Test</title></head><body>Hello</body></html>'}
    result = response_transform.execute_transformation_request(response)
    assert result == response['text']

def test_execute_transformation_request_with_bytes(response_transform):
    response = {'text': b'<html><head><title>Test</title></head><body>Hello</body></html>'}
    result = response_transform.execute_transformation_request(response)
    assert result == response['text'].decode('utf-8', errors='replace')

def test_execute_transformation_request_with_no_text(response_transform, caplog):
    response = {}
    with caplog.at_level("WARNING"):
        result = response_transform.execute_transformation_request(response)
        assert result is None
        assert "No text response received." in caplog.text

def test_update_page_title(response_transform):
    html = "<html><head><title>Old Title</title></head><body></body></html>"
    soup = BeautifulSoup(html, 'html.parser')
    updated_soup = response_transform.update_page_title(soup, "New Title")
    assert updated_soup.title.string == "New Title"

def test_replace_text(response_transform):
    html = "<html><body>Hello World</body></html>"
    soup = BeautifulSoup(html, 'html.parser')
    text_replaces = {"Hello": "Hi", "World": "Universe"}
    updated_text = response_transform.replace_text(soup, text_replaces)
    assert updated_text == "<html><body>Hi Universe</body></html>"

def test_text_transformation_with_title_and_replacement(response_transform):
    response_text = "<html><head><title>Old</title></head><body>Hello World</body></html>"
    page_title = "New"
    text_replaces = {"Hello": "Hi", "World": "Universe"}
    result = response_transform.text(response_text, page_title, text_replaces)
    expected_output = "<html><head><title>New</title></head><body>Hi Universe</body></html>"
    assert result['text'] == expected_output

def test_text_with_invalid_response(response_transform, caplog):
    with caplog.at_level("ERROR"):
        result = response_transform.text(None)
        assert result is None
        assert "Response text is not a valid string." in caplog.text
