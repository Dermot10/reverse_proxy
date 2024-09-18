class RequestReceive:
    def __init__(self, reverse_proxy):
        self.reverse_proxy = reverse_proxy
        self.request_payload = None

    def validate(self, payload) -> bool:
        if not isinstance(payload, dict):
            raise ValueError("Invalid payload: must be a dictionary")
        # You can add more validation logic here (e.g., required fields, format checks)
        return True

    def run(self, request_payload):
        try:
            self.validate(request_payload)
            self.request_payload = request_payload
        except Exception as error:
            return {"Error validating request": error}
        return self
