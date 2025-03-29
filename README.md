# Browser Automation Agent

A simple browser automation agent that accepts natural language commands to control browser actions.

## DEMO
https://www.loom.com/share/f5c4d07de179429ca4d35a94d00232f4?sid=5189c56e-f243-4019-8d69-9bfa30c90046 

## Features

- Natural language interface for controlling web browsers
- Easy to use REST API
- Support for common browser actions:
  - Navigation
  - Clicking
  - Typing
  - Form submission
  - Waiting
  - Screenshots
  - Login automation
  - Search automation

## Installation

1. Clone this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:

```bash
python -m playwright install
```

## Usage

### Starting the API Server

```bash
python app.py
```

This will start the FastAPI server at `http://localhost:8000`.

### Running the Demo Workflow

```bash
# Run the Wikipedia search demo (no login required)
python demo.py

# Run the GitHub search demo (requires login credentials)
python demo.py github

# Run the Reddit search demo (requires login credentials)
python demo.py reddit
```


Note: For the Github demo, you'll need to set the following environment variables in a .env file:

GITHUBS_USERNAME: Your Github username
GITHUBS_PASSWORD: Your Github password

Note: For the Reddit demo, you'll need to set the following environment variables in a .env file:

REDDIT_USERNAME: Your Reddit username
REDDIT_PASSWORD: Your Reddit password

## API Endpoints

### Interact API

`POST /interact`

Accepts natural language commands to control browser actions.

Example request:
```json
{
  "command": "go to github.com",
  "options": {}
}
```

Example response:
```json
{
  "success": true,
  "message": "Successfully executed: go to github.com",
  "data": {
    "url": "https://github.com/",
    "title": "GitHub: Let's build from here · GitHub"
  }
}
```

### Status API

`GET /status`

Returns the current status of the browser.

Example response:
```json
{
  "status": "ready",
  "browser_info": {
    "status": "ready",
    "current_url": "https://github.com/",
    "title": "GitHub: Let's build from here · GitHub"
  }
}
```

## Example Commands

- "Go to github.com"
- "Click on the login button"
- "Type 'hello world' into the search field"
- "Submit the form"
- "Wait 5 seconds"
- "Wait for results to load"
- "Take a screenshot"
- "Login to github.com with username 'myuser' and password 'mypass'"
- "Search for 'python automation' on google.com"


## Advanced Features

### CAPTCHA Handling

The browser automation agent now includes:
- CAPTCHA detection capabilities
- Support for different CAPTCHA types (reCAPTCHA, hCaptcha, text-based)
- Fallback to manual intervention when automated solving fails

### Enhanced Error Handling

The BrowserAutomationError class provides:
- Custom exception handling for browser automation errors
- Structured error responses with detailed information
- Automatic screenshot capture for debugging purposes

### JavaScript-Based Interactions

The demo includes advanced JavaScript-based interaction techniques:
- DOM manipulation for finding and clicking elements
- Event dispatching for form submissions
- Multiple fallback approaches for handling dynamic web elements

### Two-Factor Authentication Detection

The agent can:
- Detect when 2FA/OTP verification is required
- Capture screenshots of verification screens
- Provide clear logging about authentication status

## Demo Workflows

The project now includes three demonstration workflows:

1. **Wikipedia Search Demo** (default)
   - Navigate to Wikipedia
   - Perform a search with specified keywords
   - Interact with search results

2. **GitHub Search Demo**
   - Log into GitHub (requires credentials)
   - Navigate the GitHub interface
   - Handle potential login challenges

3. **Reddit Search Demo**
   - Navigate to Reddit
   - Log in with provided credentials
   - Perform search operations
   - Handle dynamic content loading
   - Interact with search results

  ## Contact Information

  You can reach me at:
  - Email: manojk030303@gmail.com
  - Twitter: [manojkumark_cpy](https://x.com/manojkumark_cpy)
