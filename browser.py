#browser.py
from playwright.async_api import async_playwright, Page, Browser, ElementHandle
import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
import base64
from error_handler import (
    BrowserAutomationError, 
    ElementNotFoundError, 
    NavigationError,
    TimeoutError
)

logger = logging.getLogger(__name__)

class BrowserController:
    def __init__(self, headless: bool = False, slow_mo: int = 50):
        """
        Initialize the browser controller.
        
        Args:
            headless: Whether to run the browser in headless mode
            slow_mo: Slow down operations by this many milliseconds
        """
        self.headless = headless
        self.slow_mo = slow_mo
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize the browser."""
        if self.initialized:
            return
        
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                slow_mo=self.slow_mo
            )
            self.context = await self.browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
            )
            self.page = await self.context.new_page()
            self.initialized = True
            logger.info("Browser initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize browser: {str(e)}")
            await self.close()
            raise BrowserAutomationError(f"Browser initialization failed: {str(e)}")
    
    async def close(self):
        """Close the browser and all resources."""
        try:
            if self.page:
                await self.page.close()
                self.page = None
            
            if self.context:
                await self.context.close()
                self.context = None
            
            if self.browser:
                await self.browser.close()
                self.browser = None
            
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
            
            self.initialized = False
            logger.info("Browser closed successfully")
        except Exception as e:
            logger.error(f"Error during browser close: {str(e)}")
    
    async def get_status(self) -> Dict[str, Any]:
        """Get the current status of the browser."""
        if not self.initialized:
            return {"status": "not_initialized"}
        
        try:
            current_url = await self.page.url()
            return {
                "status": "ready",
                "current_url": current_url,
                "title": await self.page.title()
            }
        except Exception as e:
            logger.error(f"Error getting browser status: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def execute(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a browser action.
        
        Args:
            action: The action to execute
            parameters: The parameters for the action
            
        Returns:
            A dictionary with the result of the action
            
        Raises:
            BrowserAutomationError: If the action fails
        """
        if not self.initialized:
            await self.initialize()
        
        # Map actions to methods
        action_map = {
            "navigate": self._navigate,
            "click": self._click,
            "type": self._type,
            "submit": self._submit,
            "wait": self._wait,
            "wait_for_element": self._wait_for_element,
            "screenshot": self._screenshot,
            "login": self._login,
            "search": self._search
        }
        
        if action not in action_map:
            raise BrowserAutomationError(f"Unknown action: {action}")
        
        try:
            result = await action_map[action](**parameters)
            return result
        except BrowserAutomationError:
            # Re-raise specific browser errors
            raise
        except Exception as e:
            logger.error(f"Error executing action {action}: {str(e)}", exc_info=True)
            raise BrowserAutomationError(f"Failed to execute {action}: {str(e)}")
    
    async def _navigate(self, url: str) -> Dict[str, Any]:
        """Navigate to a URL."""
        try:
            # Add protocol if not present
            if not url.startswith(('http://', 'https://')):
                url = f"https://{url}"
            
            logger.info(f"Navigating to: {url}")
            # Fix: Use proper wait_until value
            # await self.page.goto(url, wait_until="networkidle")
            # Alternative approach if the above doesn't work:
            await self.page.goto(url)
            await self.page.wait_for_load_state("networkidle")
            return {
                "url":  self.page.url,
                "title": await self.page.title()
            }
        except Exception as e:
            logger.error(f"Navigation error to {url}: {str(e)}")
            raise NavigationError(f"Failed to navigate to {url}: {str(e)}")
    async def _find_element(self, identifier, timeout=5000) -> ElementHandle:
        """
        Find an element using various strategies.
        
        Args:
            identifier: Text, selector, or field name to find
            timeout: Timeout in milliseconds
            
        Returns:
            ElementHandle if found
            
        Raises:
            ElementNotFoundError: If the element is not found
        """
        try:
            # Try by text
            try:
                element = await self.page.wait_for_selector(
                    f"text='{identifier}'",
                    timeout=timeout
                )
                if element:
                    return element
            except:
                pass
            
            # Try by placeholder
            try:
                element = await self.page.wait_for_selector(
                    f"[placeholder*='{identifier}' i]",
                    timeout=timeout
                )
                if element:
                    return element
            except:
                pass
            
            # Try by label
            try:
                element = await self.page.wait_for_selector(
                    f"label:has-text('{identifier}')",
                    timeout=timeout
                )
                if element:
                    # Find the input associated with this label
                    label_for = await element.get_attribute('for')
                    if label_for:
                        input_element = await self.page.wait_for_selector(
                            f"#{label_for}",
                            timeout=1000
                        )
                        if input_element:
                            return input_element
                    # Try finding input inside the label
                    input_inside = await element.query_selector('input')
                    if input_inside:
                        return input_inside
                    return element
            except:
                pass
            
            # Try common selectors for input fields
            common_selectors = [
                f"input[name*='{identifier}' i]",
                f"input[id*='{identifier}' i]",
                f"input[aria-label*='{identifier}' i]",
                f"textarea[name*='{identifier}' i]",
                f"textarea[id*='{identifier}' i]",
                f"textarea[aria-label*='{identifier}' i]",
                f"button:has-text('{identifier}')",
                f"a:has-text('{identifier}')"
            ]
            
            for selector in common_selectors:
                try:
                    element = await self.page.wait_for_selector(selector, timeout=1000)
                    if element:
                        return element
                except:
                    continue
            
            # If all strategies fail, raise an error
            raise ElementNotFoundError(f"Could not find element: {identifier}")
        except ElementNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error finding element '{identifier}': {str(e)}")
            raise ElementNotFoundError(f"Error finding element '{identifier}': {str(e)}")
    
    async def _click(self, text: str) -> Dict[str, Any]:
        """Click on an element containing the specified text."""
        try:
            element = await self._find_element(text)
            await element.click()
            return {"clicked": text}
        except ElementNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Click error on '{text}': {str(e)}")
            raise BrowserAutomationError(f"Failed to click on '{text}': {str(e)}")
    
    async def _type(self, text: str, field: str) -> Dict[str, Any]:
        """Type text into a field."""
        try:
            element = await self._find_element(field)
            # Clear the field first
            await element.fill("")
            await element.type(text, delay=50)  # Type with a slight delay for realism
            return {"field": field, "typed": text}
        except ElementNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Type error in field '{field}': {str(e)}")
            raise BrowserAutomationError(f"Failed to type in field '{field}': {str(e)}")
    
    async def _submit(self) -> Dict[str, Any]:
        """Submit the current form."""
        try:
            # Try to find a submit button first
            submit_selectors = [
                "input[type='submit']",
                "button[type='submit']",
                "button:has-text('Submit')",
                "button:has-text('Login')",
                "button:has-text('Sign in')",
                "button:has-text('Search')",
                "button:has-text('Send')"
            ]
            
            for selector in submit_selectors:
                try:
                    submit_button = await self.page.wait_for_selector(selector, timeout=1000)
                    if submit_button:
                        await submit_button.click()
                        await self.page.wait_for_load_state("networkidle")
                        return {"submitted": True}
                except:
                    continue
            
            # If no submit button found, try pressing Enter on a form element
            form = await self.page.query_selector("form")
            if form:
                await form.press("Enter")
                await self.page.wait_for_load_state("networkidle")
                return {"submitted": True}
            
            # If still not successful, try pressing Enter on the active element
            await self.page.keyboard.press("Enter")
            await self.page.wait_for_load_state("networkidle")
            return {"submitted": True}
        except Exception as e:
            logger.error(f"Form submission error: {str(e)}")
            raise BrowserAutomationError(f"Failed to submit form: {str(e)}")
    
    async def _wait(self, seconds: float) -> Dict[str, Any]:
        """Wait for a specified number of seconds."""
        try:
            await asyncio.sleep(seconds)
            return {"waited": seconds}
        except Exception as e:
            logger.error(f"Wait error: {str(e)}")
            raise BrowserAutomationError(f"Failed to wait: {str(e)}")
    
    async def _wait_for_element(self, element: str, timeout: int = 30000) -> Dict[str, Any]:
        """Wait for an element to appear on the page."""
        try:
            await self._find_element(element, timeout=timeout)
            return {"waited_for": element}
        except ElementNotFoundError:
            raise TimeoutError(f"Timed out waiting for element: {element}")
        except Exception as e:
            logger.error(f"Wait for element error: {str(e)}")
            raise BrowserAutomationError(f"Failed to wait for element: {str(e)}")
    
    async def _screenshot(self) -> Dict[str, Any]:
        """Take a screenshot of the current page."""
        try:
            screenshot_bytes = await self.page.screenshot()
            screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
            return {
                "screenshot": screenshot_base64,
                "format": "base64"
            }
        except Exception as e:
            logger.error(f"Screenshot error: {str(e)}")
            raise BrowserAutomationError(f"Failed to take screenshot: {str(e)}")
    
    async def _login(self, website: str, username: Optional[str] = None, password: Optional[str] = None) -> Dict[str, Any]:
        """Log in to a website."""
        try:
            # Navigate to the website
            await self._navigate(website)
            
            # Look for login, sign in, or account links
            login_buttons = [
                "Log in", "Login", "Sign in", "Signin", "Sign In", 
                "Account", "My Account"
            ]
            
            # Try to find and click a login button
            for button_text in login_buttons:
                try:
                    login_button = await self.page.wait_for_selector(
                        f"text='{button_text}'",
                        timeout=2000
                    )
                    if login_button:
                        await login_button.click()
                        # Wait for the page to settle
                        await self.page.wait_for_load_state("networkidle")
                        break
                except:
                    continue
            
            # If username and password are provided, try to fill the login form
            if username and password:
                # Common username field identifiers
                username_fields = ["username", "email", "user", "login"]
                password_fields = ["password", "pass"]
                
                # Try to find and fill username field
                username_filled = False
                for field in username_fields:
                    try:
                        await self._type(username, field)
                        username_filled = True
                        break
                    except:
                        continue
                
                if not username_filled:
                    raise ElementNotFoundError("Could not find username field")
                
                # Try to find and fill password field
                password_filled = False
                for field in password_fields:
                    try:
                        await self._type(password, field)
                        password_filled = True
                        break
                    except:
                        continue
                
                if not password_filled:
                    raise ElementNotFoundError("Could not find password field")
                
                # Submit the form
                await self._submit()
            
            return {
                "logged_in": username is not None and password is not None,
                "website": website,
                "current_url": await self.page.url()
            }
        except Exception as e:
            logger.error(f"Login error for {website}: {str(e)}")
            raise BrowserAutomationError(f"Failed to login to {website}: {str(e)}")
    
    async def _search(self, query: str, website: str) -> Dict[str, Any]:
        """Search for a query on a website."""
        try:
            # Navigate to the website
            await self._navigate(website)
            
            # Common search field identifiers
            search_fields = ["search", "q", "query", "find"]
            
            # Try to find and fill search field
            search_filled = False
            for field in search_fields:
                try:
                    await self._type(query, field)
                    search_filled = True
                    break
                except:
                    continue
            
            if not search_filled:
                # Try to find any visible search box
                search_box = await self.page.wait_for_selector(
                    "input[type='search'], input[placeholder*='search' i], input[aria-label*='search' i]",
                    timeout=5000
                )
                if search_box:
                    await search_box.fill("")
                    await search_box.type(query, delay=50)
                    search_filled = True
            
            if not search_filled:
                raise ElementNotFoundError("Could not find search field")
            
            # Submit the search
            await self._submit()
            
            # Wait for search results to load
            await self.page.wait_for_load_state("networkidle")
            
            return {
                "search_query": query,
                "website": website,
                "current_url": await self.page.url()
            }
        except Exception as e:
            logger.error(f"Search error for '{query}' on {website}: {str(e)}")
            raise BrowserAutomationError(f"Failed to search for '{query}' on {website}: {str(e)}")