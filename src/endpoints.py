import time
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sbase import BaseCase

from src.consts import CHALLENGE_TITLES
from src.models import (
    LinkRequest,
    LinkResponse,
    Solution,
)

from .utils import get_sb, logger, save_screenshot

router = APIRouter()

SeleniumDep = Annotated[BaseCase, Depends(get_sb)]


@router.get("/", include_in_schema=False)
def read_root():
    """Redirect to /docs."""
    logger.debug("Redirecting to /docs")
    return RedirectResponse(url="/docs", status_code=301)


@router.get("/health")
def health_check(sb: SeleniumDep):
    """Health check endpoint."""
    health_check_request = read_item(
        LinkRequest.model_construct(url="https://google.com"),
        sb,
    )

    if health_check_request.solution.status != HTTPStatus.OK:
        raise HTTPException(
            status_code=500,
            detail="Health check failed",
        )

    return {"status": "ok"}


@router.post("/old/v1")
def read_item(request: LinkRequest, sb: SeleniumDep) -> LinkResponse:
    """Handle POST requests."""
    start_time = int(time.time() * 1000)
    sb.uc_open_with_reconnect(request.url)
    logger.debug(f"Got webpage: {request.url}")
    source_bs = sb.get_beautiful_soup()
    title_tag = source_bs.title
    if title_tag and title_tag.string in CHALLENGE_TITLES:
        logger.debug("Challenge detected")
        sb.uc_gui_click_captcha()
        logger.info("Clicked captcha")

    source_bs = sb.get_beautiful_soup()
    title_tag = source_bs.title

    if title_tag and title_tag.string in CHALLENGE_TITLES:
        save_screenshot(sb)
        raise HTTPException(status_code=500, detail="Could not bypass challenge")

    return LinkResponse(
        message="Success",
        solution=Solution(
            userAgent=sb.get_user_agent(),
            url=sb.get_current_url(),
            status=200,
            cookies=sb.get_cookies(),
            headers={},
            response=str(source_bs),
        ),
        start_timestamp=start_time,
    )

@router.post("/v1")
def bypass(request: LinkRequest, sb: SeleniumDep) -> LinkResponse:
    """Handle POST requests."""
    start_time = int(time.time() * 1000)
    sb.uc_open_with_reconnect(request.url)
    logger.debug(f"Got webpage: {request.url}")
    source_bs = sb.get_beautiful_soup()
    title_tag = source_bs.title
    if title_tag and title_tag.string in CHALLENGE_TITLES:
        logger.debug("Challenge detected")
        sb.uc_gui_click_captcha()
    
        try:
            verify_success(sb)
        except Exception:
            if sb.is_element_visible('input[value*="Verify"]'):
                sb.uc_click('input[value*="Verify"]')
            else:
                sb.uc_gui_click_captcha()
            try:
                verify_success(sb)
            except Exception:
                save_screenshot(sb)
                raise HTTPException(status_code=500, detail=f"Could not bypass challenge: {Exception}")
            
        return LinkResponse(
            message="Success",
            solution=Solution(
                userAgent=sb.get_user_agent(),
                url=sb.get_current_url(),
                status=200,
                cookies=sb.get_cookies(),
                headers={},
                response=str(source_bs),
            ),
            start_timestamp=start_time,
        )
    else:
        try:
            verify_success(sb)
        except Exception:
            if sb.is_element_visible('input[value*="Verify"]'):
                sb.uc_click('input[value*="Verify"]')
            else:
                sb.uc_gui_click_captcha()
            try:
                verify_success(sb)
            except Exception:
                save_screenshot(sb)
                raise HTTPException(status_code=500, detail=f"Could not bypass challenge: {Exception}")
            
        return LinkResponse(
            message="Success",
            solution=Solution(
                userAgent=sb.get_user_agent(),
                url=sb.get_current_url(),
                status=200,
                cookies=sb.get_cookies(),
                headers={},
                response=str(source_bs),
            ),
            start_timestamp=start_time,
        )

def verify_success(sb):
    sb.assert_element('img[alt="logo"]', timeout=4)
    sb.sleep(3)