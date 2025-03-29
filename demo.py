# demo.py
import asyncio
import sys
from browser import BrowserController
from error_handler import BrowserAutomationError
import logging
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def github_search_demo():
    """
    Demo workflow that:
    1. Logs into GitHub
    2. Performs a search
    3. Interacts with search results
    """
    browser = BrowserController(headless=False)  # Set to true for headless mode
    
    try:
        # Initialize the browser
        await browser.initialize()
        logger.info("Browser initialized")
        
        # Step 1: Navigate to GitHub
        logger.info("Navigating to GitHub...")
        await browser.execute("navigate", {"url": "github.com"})
        
        # Wait for the page to load completely
        await asyncio.sleep(3)
        
        # Debug: Let's find all links on the page to identify the sign-in link
        all_links = await browser.page.query_selector_all('a')
        logger.info(f"Found {len(all_links)} links on the page")
        
        for link in all_links:
            try:
                text = await link.text_content()
                href = await link.get_attribute('href')
                if 'sign in' in text.lower() or '/login' in str(href):
                    logger.info(f"Found potential sign in link: '{text}' with href: {href}")
            except:
                continue
        
        # Try direct JavaScript execution to click the Sign In link
        logger.info("Attempting to click Sign In via JavaScript...")
        await browser.page.evaluate("""
        const signInLink = Array.from(document.querySelectorAll('a')).find(
            a => a.textContent.trim().toLowerCase() === 'sign in' || 
                 a.href.includes('/login')
        );
        if (signInLink) {
            signInLink.click();
            console.log("Sign in link clicked via JavaScript");
        } else {
            console.log("Sign in link not found via JavaScript");
        }
        """)
        
        # Wait for potential navigation
        await asyncio.sleep(3)
        
        # Check if we're on the login page
        current_url = browser.page.url
        logger.info(f"Current URL after sign-in attempt: {current_url}")
        
        # If not on login page, try direct navigation
        if '/login' not in current_url:
            logger.info("Not on login page. Navigating directly to login page...")
            await browser.execute("navigate", {"url": "github.com/login"})
            await asyncio.sleep(2)
        
        # Now we should be on the login page
        logger.info("Checking for login form...")
        login_field = await browser.page.query_selector('#login_field')
        password_field = await browser.page.query_selector('#password')
        
        if not login_field or not password_field:
            logger.error("Login form not found!")
            # Take a screenshot to see what page we're on
            screenshot_result = await browser.execute("screenshot", {})
            import base64
            with open("debug_screenshot.png", "wb") as f:
                f.write(base64.b64decode(screenshot_result["screenshot"]))
            logger.info("Debug screenshot saved to debug_screenshot.png")
            return
        
        # Step 3: Enter username and password
        username = os.getenv("GITHUB_USERNAME")  
        password = os.getenv("GITHUB_PASSWORD")  

        logger.info("Entering username...")
        await browser.page.type("#login_field", username,delay=100)
        
        logger.info("Entering password...")
        await browser.page.type("#password", password,delay=100)
        
        logger.info("Submitting login form...")
        submit_button = await browser.page.query_selector("input[type='submit'][name='commit']")
        if submit_button:
            await submit_button.click()
        else:
            logger.info("Submit button not found, trying JavaScript...")
            await browser.page.evaluate("""
            const submitButton = document.querySelector('input[type="submit"], button[type="submit"]');
            if (submitButton) {
                submitButton.click();
                console.log("Submit button clicked via JavaScript");
            } else {
                console.log("Submit button not found");
            }
            """)
        
        # Wait for login to complete
        await asyncio.sleep(5)
                # Check for OTP/2FA verification
        has_otp = await browser.page.evaluate("""
        (() => {
            const otpFields = document.querySelectorAll('input[type="text"][name*="otp"], input[name*="2fa"], input[placeholder*="verification"]');
            return otpFields.length > 0;
        })()
        """)

        if has_otp:
            logger.info("OTP/2FA verification detected, manual interaction required")
            # Take a screenshot to show the OTP screen
            screenshot_result = await browser.execute("screenshot", {})
            import base64
            with open("reddit_otp_screen.png", "wb") as f:
                f.write(base64.b64decode(screenshot_result["screenshot"]))
            logger.info("OTP screen screenshot saved to reddit_otp_screen.png")
            return  # End demo as manual interaction is needed
        
        
        # Take a screenshot to verify login status
        logger.info("Taking a screenshot to verify login status...")
        screenshot_result = await browser.execute("screenshot", {})
        import base64
        with open("github_login_result.png", "wb") as f:
            f.write(base64.b64decode(screenshot_result["screenshot"]))
        logger.info("Screenshot saved to github_login_result.png")
        
        # Success!
        logger.info("Demo completed!")
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        # Take a screenshot in case of error
        try:
            screenshot_result = await browser.execute("screenshot", {})
            import base64
            with open("error_screenshot.png", "wb") as f:
                f.write(base64.b64decode(screenshot_result["screenshot"]))
            logger.info("Error screenshot saved to error_screenshot.png")
        except:
            pass
    finally:
        # Clean up
        await browser.close()
        logger.info("Browser closed")

# Alternative demo workflow for a public site that doesn't require login
async def wikipedia_search_demo():
    """
    Demo workflow that:
    1. Navigates to Wikipedia
    2. Performs a search
    3. Interacts with search results
    """
    browser = BrowserController(headless=False)  # Set to true for headless mode
    
    try:
        # Initialize the browser
        await browser.initialize()
        logger.info("Browser initialized")
        
        # Step 1: Navigate to Wikipedia
        logger.info("Navigating to Wikipedia...")
        await browser.execute("navigate", {"url": "wikipedia.org"})
        
        # Step 2: Perform a search
        search_query = "browser automation"
        logger.info(f"Searching for '{search_query}'...")
        
        # Enter search query
        await browser.execute("type", {"text": search_query, "field": "search"})
        
        # Submit search
        await browser.execute("submit", {})
        
        # Wait for search results to load
        logger.info("Waiting for search results...")
        await asyncio.sleep(2)
        
        # Step 3: Interact with a search result
        logger.info("Clicking on a search result...")
        await browser.execute("click", {"text": "headless browser"})
        
        # Wait for article to load
        await asyncio.sleep(2)
        
        # Take a screenshot
        logger.info("Taking a screenshot...")
        screenshot_result = await browser.execute("screenshot", {})
        
        # Save the screenshot to a file
        import base64
        with open("wikipedia_result.png", "wb") as f:
            f.write(base64.b64decode(screenshot_result["screenshot"]))
            
        logger.info("Screenshot saved to wikipedia_result.png")
        
        # Success!
        logger.info("Demo completed successfully!")
        
    except BrowserAutomationError as e:
        logger.error(f"Demo failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
    finally:
        # Clean up
        await browser.close()
        logger.info("Browser closed")

async def reddit_search_demo():
    """
    Demo workflow that:
    1. Navigates to Reddit
    2. Clicks on the login button
    3. Logs in (prompts for credentials)
    4. Performs a search
    5. Interacts with search results
    """
    browser = BrowserController(headless=False)  # Set to true for headless mode
    
    try:
        # Initialize the browser
        await browser.initialize()
        logger.info("Browser initialized")
        
        # Step 1: Navigate to Reddit
        logger.info("Navigating to Reddit...")
        await browser.execute("navigate", {"url": "reddit.com"})
        
        # Wait for the page to load completely
        await asyncio.sleep(3)
        
        # Click the login button using JavaScript
        logger.info("Clicking login button via JavaScript...")
        await browser.page.evaluate("""
        const loginButton = document.getElementById('login-button');
        if (loginButton) {
            loginButton.click();
            console.log('Login button clicked!');
        } else {
            // Try alternative methods
            const loginLinks = Array.from(document.querySelectorAll('a')).filter(
                a => a.textContent.trim().toLowerCase().includes('log in') || 
                     a.href.includes('/login')
            );
            if (loginLinks.length > 0) {
                loginLinks[0].click();
                console.log('Login link clicked via alternative method');
            } else {
                console.error('Login button not found!');
            }
        }
        """)
        
        # Wait for login form to appear
        await asyncio.sleep(3)
        
        # Check if we're on the login page
        current_url = browser.page.url
        logger.info(f"Current URL after login button click: {current_url}")
        
        # Enter username and password
        username = os.getenv("REDDIT_USERNAME") 
        password = os.getenv("REDDIT_PASSWORD")
        
        logger.info("Entering username...")
        try:
            username_field = await browser.page.wait_for_selector('input[name="username"]', timeout=3000)
            if username_field:
                await username_field.fill(username)
            else:
                logger.warning("Username field not found by name, trying alternative selectors")
                # Try alternative selectors or methods
                await browser.execute("type", {"text": username, "field": "username"})
        except Exception as e:
            logger.error(f"Error entering username: {str(e)}")
            
        logger.info("Entering password...")
        try:
            password_field = await browser.page.wait_for_selector('input[name="password"]', timeout=3000)
            if password_field:
                await password_field.fill(password)
            else:
                logger.warning("Password field not found by name, trying alternative selectors")
                # Try alternative selectors or methods
                await browser.execute("type", {"text": password, "field": "password"})
        except Exception as e:
            logger.error(f"Error entering password: {str(e)}")
        
        logger.info("Clicking login button...")
        try:
            submit_button = await browser.page.query_selector('button.login')
            if submit_button:
                await submit_button.click()
            else:
                logger.info("Submit button not found, trying JavaScript...")
                await browser.page.evaluate("""
                const submitButton = document.querySelector('button[type="submit"], input[type="submit"]');
                if (submitButton) {
                    submitButton.click();
                    console.log("Submit button clicked via JavaScript");
                } else {
                    console.log("Submit button not found");
                }
                """)
        except Exception as e:
            logger.error(f"Error clicking submit button: {str(e)}")
        
        # Wait for login to complete or for 2FA/OTP prompt
        await asyncio.sleep(5)
        
        # Check for OTP/2FA verification
        has_otp = await browser.page.evaluate("""
        (() => {
            const otpFields = document.querySelectorAll('input[type="text"][name*="otp"], input[name*="2fa"], input[placeholder*="verification"]');
            return otpFields.length > 0;
        })()
        """)

        if has_otp:
            logger.info("OTP/2FA verification detected, manual interaction required")
            # Take a screenshot to show the OTP screen
            screenshot_result = await browser.execute("screenshot", {})
            import base64
            with open("github_otp_screen.png", "wb") as f:
                f.write(base64.b64decode(screenshot_result["screenshot"]))
            logger.info("OTP screenshot saved to reddit_otp_screen.png")
            return  # End demo as manual interaction is needed
        
        # Wait for homepage to load after login
        await asyncio.sleep(5)
        
        # Perform a search - FIXED SECTION
        search_query = "python automation"
        logger.info(f"Searching for '{search_query}'...")
        
        # Use JavaScript to find and interact with the search functionality
        # This is more reliable than using selectors that might be hidden
        search_success = await browser.page.evaluate("""
        (query) => {
            // Try multiple approaches to find and use the search functionality
            
            // Approach 1: Try to find the search icon/button and click it
            const searchButtons = Array.from(document.querySelectorAll('button, a, div')).filter(el => {
                const ariaLabel = el.getAttribute('aria-label');
                return ariaLabel && (
                    ariaLabel.toLowerCase().includes('search') || 
                    el.textContent.trim().toLowerCase() === 'search'
                );
            });
            
            if (searchButtons.length > 0) {
                console.log('Found search button, clicking it');
                searchButtons[0].click();
                
                // Wait a moment for search input to appear
                return new Promise(resolve => {
                    setTimeout(() => {
                        // Now try to find the search input
                        const searchInputs = document.querySelectorAll('input[type="text"], input[type="search"], input[name="q"], input[placeholder*="Search"]');
                        if (searchInputs.length > 0) {
                            console.log('Found search input, filling it');
                            searchInputs[0].value = query;
                            
                            // Dispatch events to trigger search
                            searchInputs[0].dispatchEvent(new Event('input', { bubbles: true }));
                            searchInputs[0].dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }));
                            
                            // Also try to find and click a search submit button if available
                            const submitButtons = document.querySelectorAll('button[type="submit"], button[aria-label*="search"], button.search-button');
                            if (submitButtons.length > 0) {
                                console.log('Found submit button, clicking it');
                                submitButtons[0].click();
                            }
                            
                            resolve(true);
                        } else {
                            console.log('Search input not found after clicking search button');
                            resolve(false);
                        }
                    }, 1000);
                });
            }
            
            // Approach 2: Try to directly find the search input
            const searchInputs = document.querySelectorAll('input[type="text"], input[type="search"], input[name="q"], input[placeholder*="Search"]');
            if (searchInputs.length > 0) {
                console.log('Found search input directly, filling it');
                searchInputs[0].focus();
                searchInputs[0].value = query;
                
                // Dispatch events to trigger search
                searchInputs[0].dispatchEvent(new Event('input', { bubbles: true }));
                searchInputs[0].dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }));
                
                return true;
            }
            
            // Approach 3: Try to use the URL based search
            console.log('Direct search methods failed, trying URL-based search');
            window.location.href = 'https://www.reddit.com/search/?q=' + encodeURIComponent(query);
            return true;
        }
        """, search_query)
        
        if search_success:
            logger.info("Search initiated successfully")
        else:
            logger.warning("All search methods failed, trying URL navigation as fallback")
            # Fallback: Navigate directly to search URL
            await browser.execute("navigate", {"url": f"https://www.reddit.com/search/?q={search_query.replace(' ', '+')}"})
        
        # Wait for search results
        logger.info("Waiting for search results...")
        await asyncio.sleep(5)
        
        # Click on the first search result
        logger.info("Clicking on a search result...")
        try:
            # Find all search result links with a more reliable approach
            post_clicked = await browser.page.evaluate("""
            () => {
                // Look for post titles or links that are likely to be search results
                const postSelectors = [
                    'a[data-click-id="body"]', 
                    '.search-result a',
                    'h3 a',
                    'a.title',
                    'a[href^="/r/"]',
                    // Generic selectors that might match post links
                    'div[role="link"] a', 
                    'article a'
                ];
                
                for (const selector of postSelectors) {
                    const links = document.querySelectorAll(selector);
                    if (links.length > 0) {
                        // Filter out navigation links, buttons, etc.
                        const contentLinks = Array.from(links).filter(link => {
                            const href = link.getAttribute('href');
                            const text = link.textContent.trim();
                            return href && 
                                   text.length > 10 && 
                                   !href.includes('/user/') &&
                                   !href.includes('/settings/') &&
                                   !href.includes('/login');
                        });
                        
                        if (contentLinks.length > 0) {
                            console.log('Found post link, clicking it');
                            contentLinks[0].click();
                            return true;
                        }
                    }
                }
                
                return false;
            }
            """)
            
            if post_clicked:
                logger.info("Clicked on a search result")
            else:
                logger.warning("No search results found to click")
        except Exception as e:
            logger.error(f"Error clicking search result: {str(e)}")
        
        # Wait for the post to load
        await asyncio.sleep(3)
        
        # Take a screenshot of the final state
        logger.info("Taking a screenshot...")
        screenshot_result = await browser.execute("screenshot", {})
        import base64
        with open("reddit_result.png", "wb") as f:
            f.write(base64.b64decode(screenshot_result["screenshot"]))
        logger.info("Screenshot saved to reddit_result.png")
        
        logger.info("Reddit demo completed!")
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        # Take a screenshot in case of error
        try:
            screenshot_result = await browser.execute("screenshot", {})
            import base64
            with open("reddit_error.png", "wb") as f:
                f.write(base64.b64decode(screenshot_result["screenshot"]))
            logger.info("Error screenshot saved to reddit_error.png")
        except:
            pass
    finally:
        # Clean up
        await browser.close()
        logger.info("Browser closed")

# Update the main function to include Reddit demo option
async def main():
    # Choose which demo to run
    if len(sys.argv) > 1:
        if sys.argv[1] == "github":
            await github_search_demo()
        elif sys.argv[1] == "reddit":
            await reddit_search_demo()
        else:
            # Default to Wikipedia demo as it doesn't require login
            await wikipedia_search_demo()
    else:
        # Default to Wikipedia demo as it doesn't require login
        await wikipedia_search_demo()

        
# Main function to run the demo
async def main():
    # Choose which demo to run
    if len(sys.argv) > 1 and sys.argv[1] == "github":
        await github_search_demo()
    elif len(sys.argv) > 1 and  sys.argv[1] == "reddit":
        await reddit_search_demo()
    else:
        # Default to Wikipedia demo as it doesn't require login
        await wikipedia_search_demo()

if __name__ == "__main__":
    asyncio.run(main())