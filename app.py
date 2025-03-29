from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import uvicorn
from pydantic import BaseModel
import asyncio
from typing import Dict, Any, Optional
import logging

from browser import BrowserController
from error_handler import BrowserAutomationError, handle_error

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="Browser Automation Agent API")

class CommandRequest(BaseModel):
    command: str
    options: Optional[Dict[str, Any]] = None

class CommandResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

# Global browser controller instance
browser_controller = None

@app.on_event("startup")
async def startup_event():
    global browser_controller
    browser_controller = BrowserController()
    await browser_controller.initialize()
    logger.info("Browser controller initialized")

@app.on_event("shutdown")
async def shutdown_event():
    global browser_controller
    if browser_controller:
        await browser_controller.close()
        logger.info("Browser controller shut down")

@app.post("/interact", response_model=CommandResponse)
async def interact(request: CommandRequest):
    global browser_controller
    
    if not browser_controller:
        raise HTTPException(status_code=500, detail="Browser controller not initialized")
    
    try:
        # Parse the natural language command
        # Note: You mentioned you already have the parser implemented
        from parser import parse_command
        action, parameters = parse_command(request.command)
        
        # Apply any additional options provided in the request
        if request.options:
            parameters.update(request.options)
        
        # Execute the command
        result = await browser_controller.execute(action, parameters)
        
        return CommandResponse(
            success=True,
            message=f"Successfully executed: {request.command}",
            data=result
        )
        
    except BrowserAutomationError as e:
        logger.error(f"Browser automation error: {str(e)}")
        error_response = handle_error(e)
        return CommandResponse(
            success=False,
            message=str(e),
            data=error_response
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.exception_handler(BrowserAutomationError)
async def browser_error_handler(request: Request, exc: BrowserAutomationError):
    error_response = handle_error(exc)
    return JSONResponse(
        status_code=400,
        content={"success": False, "message": str(exc), "data": error_response}
    )

@app.get("/status")
async def get_status():
    global browser_controller
    if not browser_controller:
        return {"status": "not_initialized"}
    
    try:
        browser_status = await browser_controller.get_status()
        return {
            "status": "ready",
            "browser_info": browser_status
        }
    except Exception as e:
        logger.error(f"Error getting browser status: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy"}

@app.post("/reset")
async def reset_browser():
    """Reset the browser controller (close and reinitialize)."""
    global browser_controller
    try:
        if browser_controller:
            await browser_controller.close()
            logger.info("Browser controller closed")
        
        browser_controller = BrowserController()
        await browser_controller.initialize()
        logger.info("Browser controller reinitialized")
        
        return {"status": "success", "message": "Browser reset successfully"}
    except Exception as e:
        logger.error(f"Error resetting browser: {str(e)}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)