# parser.py
import re
from typing import Tuple, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Define command patterns
COMMAND_PATTERNS = [
    # Navigation
    (r"(?:go to|navigate to|open) (?:the )?(?:website |site |page )?(?:at )?(?:https?://)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/\S*)?)", 
     "navigate", lambda m: {"url": f"https://{m.group(1)}" if not m.group(1).startswith(('http://', 'https://')) else m.group(1)}),
    
    # Clicking
    (r"click(?: on)? (?:the )?(?:button|link|element)(?: (?:with|that says|containing))? ['\"]([^'\"]+)['\"]", 
     "click", lambda m: {"text": m.group(1)}),
    (r"click(?: on)? (?:the )?([a-zA-Z0-9 ]+) (?:button|link|element)", 
     "click", lambda m: {"text": m.group(1)}),
    
    # Form input
    (r"(?:type|enter|input|fill in) ['\"]([^'\"]+)['\"] (?:in(?:to)?|on) (?:the )?([a-zA-Z0-9 ]+)(?: field| input| box)?", 
     "type", lambda m: {"text": m.group(1), "field": m.group(2)}),
    (r"(?:type|enter|input|fill in) ([a-zA-Z0-9 ]+) (?:in(?:to)?|on) (?:the )?([a-zA-Z0-9 ]+)(?: field| input| box)?", 
     "type", lambda m: {"text": m.group(1), "field": m.group(2)}),
    
    # Form submission
    (r"(?:submit|send)(?: the)?(?: form)?", 
     "submit", lambda m: {}),
    
    # Waiting
    (r"wait (?:for )?([\d.]+) seconds?", 
     "wait", lambda m: {"seconds": float(m.group(1))}),
    (r"wait for(?: the)? ([a-zA-Z0-9 ]+)(?: to appear| to load)?", 
     "wait_for_element", lambda m: {"element": m.group(1)}),
    
    # Take screenshot
    (r"(?:take a |capture |grab a )?screenshot", 
     "screenshot", lambda m: {}),
    
    # Login command (special case)
    (r"log(?:in)?(?: to| into) ([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})(?: with username ['\"]([^'\"]+)['\"] and password ['\"]([^'\"]+)['\"])?", 
     "login", lambda m: {
         "website": m.group(1),
         "username": m.group(2) if len(m.groups()) > 1 and m.group(2) else None,
         "password": m.group(3) if len(m.groups()) > 2 and m.group(3) else None
     }),
    
    # Search command (special case)
    (r"search (?:for )?['\"]([^'\"]+)['\"] (?:on|in) ([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", 
     "search", lambda m: {"query": m.group(1), "website": m.group(2)}),
]

def parse_command(command: str) -> Tuple[str, Dict[str, Any]]:
    """
    Parse a natural language command into an action and parameters.
    
    Args:
        command: The natural language command to parse
        
    Returns:
        A tuple of (action, parameters)
        
    Raises:
        ValueError: If the command cannot be parsed
    """
    command = command.strip().lower()
    logger.info(f"Parsing command: {command}")
    
    # Try each pattern until one matches
    for pattern, action, param_extractor in COMMAND_PATTERNS:
        match = re.match(pattern, command, re.IGNORECASE)
        if match:
            params = param_extractor(match)
            logger.info(f"Matched action: {action} with params: {params}")
            return action, params
    
    # If we get here, no pattern matched
    logger.warning(f"No pattern matched for command: {command}")
    raise ValueError(f"Could not understand command: {command}")

# Examples of usage (for testing)
if __name__ == "__main__":
    test_commands = [
        "Go to github.com",
        "Navigate to https://www.google.com",
        "Click on the login button",
        "Click on \"Sign In\"",
        "Type \"hello world\" into the search field",
        "Enter my_username into the username field",
        "Submit the form",
        "Wait 5 seconds",
        "Wait for results to load",
        "Take a screenshot",
        "Login to github.com with username \"myuser\" and password \"mypass\"",
        "Search for \"python automation\" on google.com"
    ]
    
    for cmd in test_commands:
        try:
            action, params = parse_command(cmd)
            print(f"Command: {cmd}")
            print(f"Action: {action}")
            print(f"Params: {params}")
            print("-" * 40)
        except ValueError as e:
            print(f"Error parsing '{cmd}': {e}")
            print("-" * 40)