# captcha_handler.py
from typing import Optional, List, Tuple
import logging
from playwright.async_api import Page, ElementHandle
import base64
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class CaptchaHandler:
    """
    Handles detection and resolution of CAPTCHAs during browser automation.
    
    This is a basic implementation that:
    1. Detects common types of CAPTCHAs
    2. Provides hooks for integrating with CAPTCHA solving services
    3. Can pause automation for manual intervention when necessary
    """
    
    # Common CAPTCHA selectors and patterns
    CAPTCHA_SELECTORS = [
        # reCAPTCHA
        "iframe[src*='recaptcha']",
        "iframe[title*='recaptcha']",
        ".g-recaptcha",
        "div[data-sitekey]",
        
        # hCaptcha
        "iframe[src*='hcaptcha']",
        ".h-captcha",
        
        # Text-based CAPTCHAs
        "img[alt*='captcha' i]",
        "input[name*='captcha' i]",
        "div[class*='captcha' i]",
        
        # Common captcha terms in various elements
        "label:has-text('I am not a robot')",
        "div:has-text('Verify you are human')"
    ]
    
    # Text patterns that suggest CAPTCHA presence
    CAPTCHA_TEXT_PATTERNS = [
        "captcha",
        "i am not a robot",
        "verify you are human",
        "security check",
        "prove you're human",
        "human verification"
    ]
    
    def __init__(self, page: Page, api_key: Optional[str] = None):
        """
        Initialize the CAPTCHA handler.
        
        Args:
            page: The Playwright page to monitor for CAPTCHAs
            api_key: Optional API key for external CAPTCHA solving service
        """
        self.page = page
        self.api_key = api_key or os.getenv("CAPTCHA_API_KEY")
        
    async def detect_captcha(self) -> Tuple[bool, Optional[str], Optional[ElementHandle]]:
        """
        Detect if a CAPTCHA is present on the current page.
        
        Returns:
            Tuple of (is_captcha_present, captcha_type, captcha_element)
        """
        try:
            # Check for CAPTCHA elements using selectors
            for selector in self.CAPTCHA_SELECTORS:
                element = await self.page.query_selector(selector)
                if element:
                    logger.info(f"CAPTCHA detected via selector: {selector}")
                    
                    # Determine CAPTCHA type
                    captcha_type = "unknown"
                    selector_text = selector.lower()
                    
                    if "recaptcha" in selector_text:
                        captcha_type = "recaptcha"
                    elif "hcaptcha" in selector_text:
                        captcha_type = "hcaptcha"
                    elif "captcha" in selector_text:
                        captcha_type = "text_captcha"
                        
                    return True, captcha_type, element
            
            # Check for CAPTCHA text patterns
            page_text = await self.page.content()
            page_text_lower = page_text.lower()
            
            for pattern in self.CAPTCHA_TEXT_PATTERNS:
                if pattern in page_text_lower:
                    logger.info(f"CAPTCHA detected via text pattern: {pattern}")
                    return True, "unknown", None
            
            return False, None, None
                
        except Exception as e:
            logger.error(f"Error during CAPTCHA detection: {str(e)}")
            return False, None, None
    
    async def solve_captcha(self, captcha_type: str, captcha_element: Optional[ElementHandle] = None) -> bool:
        """
        Attempt to solve a detected CAPTCHA.
        
        Args:
            captcha_type: The type of CAPTCHA detected
            captcha_element: The element containing the CAPTCHA (if available)
            
        Returns:
            True if the CAPTCHA was successfully solved, False otherwise
        """
        logger.info(f"Attempting to solve {captcha_type} CAPTCHA")
        
        if self.api_key:
            # Attempt to solve using an external service
            try:
                if captcha_type == "recaptcha":
                    return await self._solve_recaptcha()
                elif captcha_type == "hcaptcha":
                    return await self._solve_hcaptcha()
                elif captcha_type == "text_captcha":
                    return await self._solve_text_captcha(captcha_element)
                else:
                    logger.warning(f"No automated solution available for {captcha_type} CAPTCHA")
            except Exception as e:
                logger.error(f"Error solving CAPTCHA: {str(e)}")
        
        # If we can't solve automatically, take a screenshot and wait for manual intervention
        return await self._manual_intervention()
    
    async def _solve_recaptcha(self) -> bool:
        """
        Solve a reCAPTCHA.
        This is a placeholder - in a real implementation, you would:
        1. Extract the sitekey from the page
        2. Send it to a CAPTCHA solving service API
        3. Get the response and inject it into the page
        """
        logger.info("Attempting to solve reCAPTCHA")
        
        # Example API integration placeholder
        if not self.api_key:
            return False
            
        # IMPLEMENTATION PENDING
        
        logger.info("This is a placeholder for reCAPTCHA solving")
        return False  # Replace with actual implementation
    
    async def _solve_hcaptcha(self) -> bool:
        """Placeholder for hCaptcha solving"""
        logger.info("hCaptcha solving not yet implemented")
        return False
    
    async def _solve_text_captcha(self, element: Optional[ElementHandle]) -> bool:
        """Placeholder for text-based CAPTCHA solving"""
        logger.info("Text CAPTCHA solving not yet implemented")
        return False
    
    async def _manual_intervention(self) -> bool:
        """
        Request manual intervention to solve a CAPTCHA.
        
        Takes a screenshot, then pauses execution and waits for 
        the CAPTCHA to be solved manually.
        """
        try:
            # Take a screenshot
            screenshot_bytes = await self.page.screenshot()
            with open("captcha_screenshot.png", "wb") as f:
                f.write(screenshot_bytes)
            
            logger.info("CAPTCHA screenshot saved to captcha_screenshot.png")
            logger.info("Waiting for manual CAPTCHA solution...")
            
            # For demo purposes, we'll wait a fixed time for manual intervention
            wait_time = 30  # seconds
            logger.info(f"Waiting {wait_time} seconds for manual CAPTCHA solution...")
            
            for i in range(wait_time):
                # Check every second if we're past the CAPTCHA
                is_captcha_present, _, _ = await self.detect_captcha()
                if not is_captcha_present:
                    logger.info("CAPTCHA appears to be solved")
                    return True
                
                await asyncio.sleep(1)
                if (i + 1) % 5 == 0:
                    logger.info(f"Still waiting... {wait_time - i - 1} seconds remaining")
            
            logger.warning("Timeout waiting for manual CAPTCHA solution")
            return False
            
        except Exception as e:
            logger.error(f"Error during manual intervention: {str(e)}")
            return False