# error_handler.py
import logging
import traceback
from typing import Optional

logger = logging.getLogger(__name__)

class BrowserAutomationError(Exception):
    """Base exception for all browser automation errors."""
    
    def __init__(self, message: str, details: Optional[dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)
        
        # Log the error
        logger.error(f"{self.__class__.__name__}: {message}")
        if details:
            logger.error(f"Error details: {details}")

class ElementNotFoundError(BrowserAutomationError):
    """Exception raised when an element is not found."""
    
    def __init__(self, message: str, element_identifier: Optional[str] = None):
        details = {"element_identifier": element_identifier} if element_identifier else {}
        super().__init__(message, details)
        
        # Provide suggestions for recovery
        self.recovery_suggestions = [
            "Check if the element identifier is correct",
            "Try waiting longer for the element to appear",
            "The page structure might have changed"
        ]

class NavigationError(BrowserAutomationError):
    """Exception raised when navigation fails."""
    
    def __init__(self, message: str, url: Optional[str] = None):
        details = {"url": url} if url else {}
        super().__init__(message, details)
        
        # Provide suggestions for recovery
        self.recovery_suggestions = [
            "Check if the URL is correct and accessible",
            "Verify your internet connection",
            "The website might be down or blocking automated access"
        ]

class TimeoutError(BrowserAutomationError):
    """Exception raised when an operation times out."""
    
    def __init__(self, message: str, operation: Optional[str] = None, timeout_ms: Optional[int] = None):
        details = {}
        if operation:
            details["operation"] = operation
        if timeout_ms:
            details["timeout_ms"] = timeout_ms
        super().__init__(message, details)
        
        # Provide suggestions for recovery
        self.recovery_suggestions = [
            "Try increasing the timeout value",
            "Check if the page is loading slowly",
            "The operation might be blocked by the website"
        ]

class AuthenticationError(BrowserAutomationError):
    """Exception raised when authentication fails."""
    
    def __init__(self, message: str, website: Optional[str] = None):
        details = {"website": website} if website else {}
        super().__init__(message, details)
        
        # Provide suggestions for recovery
        self.recovery_suggestions = [
            "Verify your credentials",
            "Check if the website requires two-factor authentication",
            "The website might have anti-bot measures in place"
        ]

class InvalidCommandError(BrowserAutomationError):
    """Exception raised when a command is invalid or cannot be parsed."""
    
    def __init__(self, message: str, command: Optional[str] = None):
        details = {"command": command} if command else {}
        super().__init__(message, details)
        
        # Provide suggestions for recovery
        self.recovery_suggestions = [
            "Check the command syntax",
            "See documentation for supported commands",
            "Try rephrasing the command"
        ]

class BrowserInitializationError(BrowserAutomationError):
    """Exception raised when the browser fails to initialize."""
    
    def __init__(self, message: str, browser_type: Optional[str] = None):
        details = {"browser_type": browser_type} if browser_type else {}
        super().__init__(message, details)
        
        # Provide suggestions for recovery
        self.recovery_suggestions = [
            "Check if the browser is installed and accessible",
            "Verify that no other instances are running that might cause conflicts",
            "Try restarting the application"
        ]

def handle_error(error: Exception) -> dict:
    """
    Convert an exception into a standardized error response format.
    
    Args:
        error: The exception to handle
        
    Returns:
        A dictionary with error details
    """
    if isinstance(error, BrowserAutomationError):
        response = {
            "error_type": error.__class__.__name__,
            "message": error.message,
            "details": error.details
        }
        
        if hasattr(error, "recovery_suggestions"):
            response["recovery_suggestions"] = error.recovery_suggestions
            
        return response
    else:
        # Handle unexpected errors
        return {
            "error_type": "UnexpectedError",
            "message": str(error),
            "details": {
                "traceback": traceback.format_exc()
            }
        }