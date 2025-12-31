# Reverse Proxy - Functional Design

A lightweight, modular reverse proxy built with Python using functional programming principles. The proxy validates requests, routes them to target endpoints, executes HTTP calls, and optionally transforms responses before returning them to clients.

---

## Features

### Core Functionalities

1. **Request Validation**

   - Validates HTTP methods, paths, headers, and request structure
   - Ensures proper data types and required fields

2. **Smart Routing**

   - Maps request paths to target URLs using configurable route mappings
   - Supports multiple target endpoints

3. **Request Execution**

   - Executes HTTP requests with proper headers and data formatting
   - Handles JSON and text/HTML content types
   - Automatic request body preparation based on content type

4. **Response Transformation** (Optional)

   - HTML manipulation using BeautifulSoup
   - Dynamic page title updates
   - Text replacement for custom content modification

5. **Flask Integration**
   - RESTful API endpoint for proxying requests
   - Health check and route listing endpoints
   - Proper error handling and logging

---

## Architecture

### Functional Design Principles

This reverse proxy follows a **functional/compositional** design pattern:

- **Pure functions** - No classes or instance state, just data transformations
- **Function composition** - Small, focused functions that combine into pipelines
- **Explicit dependencies** - All data passed as function arguments
- **Immutability focus** - Functions don't mutate data, they return new values

### Component Architecture

sequenceDiagram
Note over Client,Transform: Local Flask simulates AWS Lambda<br/>Pipeline is environment-agnostic
participant Client
participant Flask as Flask Handler<br/>(Adapter)
participant PipelineProxy as proxy_request()<br/>(Orchestrator)
participant Validate as validate_event()
participant Route as route_to_target()
participant Execute as execute_request()
participant Parse as parse_response()
participant Transform as transform_response()

    Client->>Flask: HTTP Request<br/>(GET/POST/PUT/DELETE)

    Note over Flask: Adapter Layer<br/>Format Translation
    Flask->>Flask: Extract headers, body, params
    Flask->>Flask: Remove problematic headers<br/>(Host, Content-Length, etc.)
    Flask->>Flask: Build standard event format

    Flask->>PipelineProxy: proxy_request(event, transform_options?)

    Note over PipelineProxy: Orchestration Layer<br/>Business Logic Pipeline

    PipelineProxy->>Validate: validate_event(event)
    Validate-->>PipelineProxy: validated_event / error
    PipelineProxy->>Route: route_to_target(path, route_config)
    Route-->>PipelineProxy: target_url / error

    PipelineProxy->>Execute: execute_request(method, url, params, data, headers)
    Execute-->>Execute: Validate URL format
    Execute-->>Execute: Prepare request body<br/>(stringify JSON if needed)
    Execute-->>Execute: Add User-Agent if missing
    Execute->>Execute: HTTP Request to target
    Note right of Execute: External HTTP call<br/>timeout=30s
    Execute-->>PipelineProxy: raw_response (requests.Response)

    PipelineProxy->>Parse: parse_response(raw_response)
    Parse-->>Parse: Extract status, headers
    Parse-->>Parse: Detect content type
    alt JSON Response
        Parse-->>Parse: Parse JSON
    else HTML/Text Response
        Parse-->>Parse: Extract text
    end
    Parse-->>PipelineProxy: response dict

    alt transform_options provided
        PipelineProxy->>Transform: transform_response(response, options)
        Transform-->>Transform: Parse HTML (BeautifulSoup)

        alt page_title specified
            Transform-->>Transform: Update <title> tag
        end

        alt text_replaces specified
            Transform-->>Transform: Replace text content
        end

        Transform-->>PipelineProxy: transformed_response
    end

    PipelineProxy-->>Flask: final_response dict

    Note over Flask: Format Response<br/>for HTTP
    Flask->>Flask: Extract content
    Flask->>Flask: Convert to bytes if needed
    Flask->>Flask: Set Content-Type header

    Flask-->>Client: HTTP Response<br/>(status, headers, body)

    Note over Client,Flask: Error Handling:<br/>Any exception returns<br/>500 with error JSON

```
Flask Handler (Adapter Layer)
    ├─ Translates HTTP requests → standard event format
    ├─ Calls proxy_request() orchestrator
    └─ Translates response → HTTP format

proxy_request() (Orchestrator)
    ├─ validate_event()
    ├─ route_to_target()
    ├─ execute_request()
    ├─ parse_response()
    └─ transform_response()
```

---

## API Reference

### Flask Endpoints

#### `GET/POST/PUT/DELETE /proxy/<path>`

Proxy requests to configured target endpoints.

**Example: Simple GET**

```bash
curl http://localhost:5001/proxy/google
```

**Example: POST with JSON**

```bash
curl -X POST http://localhost:5001/proxy/jsonplaceholder \
  -H "Content-Type: application/json" \
  -d '{"title": "foo", "body": "bar", "userId": 1}'
```

**Example: GET with Transformation**

```bash
curl "http://localhost:5001/proxy/google?page_title=Custom%20Title"
```

---

#### `GET /health`

Health check endpoint.

**Response:**

```json
{
  "status": "healthy",
  "service": "reverse-proxy",
  "routes": ["/google", "/youtube", ...]
}
```

---

#### `GET /routes`

List available proxy routes.

**Response:**

```json
{
  "available_routes": {
    "/google": "https://www.google.com",
    "/youtube": "https://www.youtube.com",
    ...
  }
}
```

---

## Setup and Installation

### Prerequisites

- Python 3.8+
- pip

### Installation

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```

2. **Create virtual environment (recommended):**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Flask server:**

   ```bash
   python app.py
   ```

   Server starts at `http://localhost:5001`

---

## Configuration

### Route Configuration

Edit `ROUTE_CONFIG` in your main module:

```python
ROUTE_CONFIG = {
    "/google": "https://www.google.com",
    "/youtube": "https://www.youtube.com",
    "/api": "https://api.example.com",
    "/custom": "https://custom-target.com"
}
```

---

## Usage Examples

### Direct Usage (Without Flask)

```python
from reverse_proxy import proxy_request

# Simple GET request
event = {
    'method': 'GET',
    'path': '/google',
    'headers': {'Accept': 'text/html'}
}

response = proxy_request(event)
print(f"Status: {response['status_code']}")
print(f"Content: {response['content'][:100]}...")
```

### With Transformation

```python
event = {
    'method': 'GET',
    'path': '/google',
    'headers': {'Accept': 'text/html'}
}

transform_options = {
    'page_title': 'My Custom Search Engine',
    'text_replaces': {
        'Google': 'MySearch',
        'Search': 'Find'
    }
}

response = proxy_request(event, transform_options)
```

### Via Flask API

```bash
# Simple GET
curl http://localhost:5001/proxy/google

# POST with JSON body
curl -X POST http://localhost:5001/proxy/api \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'

# With transformation
curl "http://localhost:5001/proxy/google?page_title=Custom%20Title"
```

---

## Testing

### Manual Testing with cURL

```bash
# Health check
curl http://localhost:5001/health

# List routes
curl http://localhost:5001/routes

# Simple proxy
curl http://localhost:5001/proxy/google

# Save response to file
curl http://localhost:5001/proxy/google -o output.html
```

### Python Test Script

```python
import requests

BASE_URL = "http://localhost:5001"

# Test health
response = requests.get(f"{BASE_URL}/health")
print(response.json())

# Test proxy
response = requests.get(f"{BASE_URL}/proxy/google")
print(f"Status: {response.status_code}")
print(f"Content length: {len(response.text)}")

# Test POST
response = requests.post(
    f"{BASE_URL}/proxy/api",
    json={"test": "data"}
)
print(response.json())
```

---

## Design Choices

### Separation of Concerns

- **Flask Handler** - HTTP adapter (Dev Server) (format translation only)
- **proxy_request()** - Business logic orchestrator
- **Pure functions** - Domain logic (validation, routing, execution, transformation)

### Benefits

- **Simple** - Easy to understand and modify
- **Testable** - Pure functions are easy to test
- **Maintainable** - Clear separation of concerns
- **Reusable** - Functions can be used in different contexts (Flask, Lambda, CLI)

---

## Deployment Options

### Local Development

```bash
python app.py
```

### Docker

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

---

## Future Enhancements

- [ ] Add caching layer (Redis/Memcached)
- [ ] Implement rate limiting
- [ ] Add request/response logging middleware
- [ ] Support for authentication/authorization
- [ ] Async request handling (aiohttp)
- [ ] Response streaming for large files
- [ ] Metrics and monitoring integration
- [ ] Custom middleware pipeline

---

## Troubleshooting

### Common Issues

**Issue: "Invalid chunk size" error**

- **Cause:** Large responses with chunked encoding
- **Fix:** Use `make_response()` or set explicit `Content-Length` header

**Issue: "403 Forbidden" errors**

- **Cause:** Missing or incorrect headers
- **Fix:** Ensure `User-Agent` header is set (automatically added)

**Issue: Timeout errors**

- **Cause:** Target server is slow or blocking requests
- **Fix:** Adjust timeout in `execute_request()` or try different target

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

## License

This project is licensed under the MIT License. See LICENSE file for details.
