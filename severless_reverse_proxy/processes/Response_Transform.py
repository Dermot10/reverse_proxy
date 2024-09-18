import logging
from bs4 import BeautifulSoup


class ResponseTransform:

    def __init__(self, reverse_proxy):
        self.reverse_proxy = reverse_proxy
        self.logger = logging.getLogger(__name__)  # Setup logger

    def execute_request(self) -> str:
        """Execute the request and get the response text"""
        response = self.reverse_proxy.request_execute.response()
        text_response = response.get('text') if response else None
        if not text_response:
            self.logger.warning("No text response received.")
        return text_response

    def update_page_title(self, soup, page_title):
        """Update the page title in the HTML response if present"""
        if page_title and soup.title:
            soup.title.string = page_title
            self.logger.info(f"Page title updated to: {page_title}")
        return soup

    def replace_text(self, soup, text_replaces):
        """Replace text in the response based on the provided dictionary"""
        response_text = str(soup)
        if isinstance(text_replaces, dict):
            for key, value in text_replaces.items():
                response_text = response_text.replace(key, value)
                self.logger.info(f"Replaced '{key}' with '{value}'")
        return response_text

    def text(self, response_text, page_title=None, text_replaces=None):
        """Main function to handle HTML text transformation"""
        if not isinstance(response_text, str):
            self.logger.error("Response text is not a valid string.")
            return None

        try:
            soup = BeautifulSoup(response_text, 'html.parser')
            self.logger.info("Successfully parsed response text with BeautifulSoup.")

            # Update the page title
            soup = self.update_page_title(soup, page_title)

            # Replace text if required
            updated_text = self.replace_text(soup, text_replaces)

            return dict(text=updated_text)

        except Exception as error:
            self.logger.error(f"Error in text transformation: {error}")
            return None
