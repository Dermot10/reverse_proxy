# Serverless Reverse Proxy

This project is a modular and scalable serverless reverse proxy built with Python. It includes key features such as request validation, response transformation, and routing logic. The reverse proxy is designed to handle incoming HTTP requests, forward them to the appropriate destinations, and transform the responses before sending them back to the client.

---

## Features

### Core Functionalities

1. **Request Validation**:
   - Validates HTTP methods, URLs, headers, and payloads.
2. **Routing Logic**:
   - Routes requests to target endpoints based on extracted data.
3. **Response Transformation**:
   - Modifies response content using BeautifulSoup to handle custom transformations like updating HTML titles or replacing text dynamically.

### Framework Integration

- **Flask Integration**:
  - The reverse proxy is integrated with Flask to handle HTTP requests and responses.

---

## Code Structure

### Key Modules

#### 1. `RequestExecute`

Handles HTTP request execution.

- Validates input parameters like method, URL, and headers.
- Executes the request and extracts response metadata such as status code, headers, and content.

#### 2. `RequestReceive`

Validates and processes incoming payloads.

- Ensures payload compliance with required formats.
- Acts as an intermediary between incoming requests and the proxy logic.

#### 3. `ResponseTransform`

Transforms the HTTP response content.

- Parses and updates HTML responses using BeautifulSoup.
- Handles title updates and text replacements for dynamic customization.

#### 4. `ReverseProxy`

Handles routing and integrates the `RequestExecute`, `RequestReceive`, and `ResponseTransform` modules for end-to-end functionality.

### Flask Entry Point

The `app.py` file serves as the entry point for the Flask application, exposing a `/proxy/<path>` route to process and proxy incoming HTTP requests.

---

## Flask API

### Endpoint: `/proxy/<path>`

#### Methods Supported

- `GET`
- `POST`
- `PUT`
- `DELETE`

#### Request Format

```json
{
  "httpMethod": "<HTTP_METHOD>",
  "path": "<REQUEST_PATH>",
  "body": "<REQUEST_BODY>",
  "headers": {
    "<HEADER_KEY>": "<HEADER_VALUE>"
  }
}
```

#### Example Usage

```bash
curl -X GET "http://localhost:5001/proxy/example/path"
```

#### Response Format

```json
{
    "content_type": "<CONTENT_TYPE>",
    "status_code": <STATUS_CODE>,
    "content": "<RESPONSE_CONTENT>",
    "json": { "<JSON_BODY>" },
    "headers": {
        "<HEADER_KEY>": "<HEADER_VALUE>"
    }
}
```

---

## Setup and Installation

### Prerequisites

- Python 3.8+
- Flask
- Requests
- BeautifulSoup (from `bs4`)

### Installation Steps

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Flask application:
   ```bash
   python app.py
   ```

---

## Design Highlights

### Modular Design

- Independent modules for request handling, routing, and response transformation.
- Promotes separation of concerns and testability.

### Scalable and Serverless

- Designed for deployment in serverless environments, ensuring scalability and cost efficiency.

### Extendability

- Easily add new features like advanced request filtering or caching mechanisms.

---

## Example Workflow

1. **Incoming Request**:
   - An HTTP request is sent to the `/proxy/<path>` endpoint.
2. **Request Handling**:
   - `RequestReceive` validates and processes the payload.
3. **Routing**:
   - `ReverseProxy` determines the appropriate target endpoint.
4. **Request Execution**:
   - `RequestExecute` sends the request to the target and retrieves the response.
5. **Response Transformation**:
   - `ResponseTransform` updates the response (e.g., replaces text or updates HTML titles).
6. **Return to Client**:
   - The transformed response is sent back to the client.

---

## Future Enhancements

- Add caching mechanisms for frequently requested endpoints.
- Implement authentication and authorization for enhanced security.
- Introduce asynchronous request handling for improved performance.

---

## License

This project is licensed under the MIT License.
