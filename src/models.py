from __future__ import annotations

import time
from http import HTTPStatus
from typing import Annotated, Any

from fastapi import Body
from pydantic import BaseModel

from src import consts


class LinkRequest(BaseModel):
    cmd: Annotated[
        str,
        Body(
            default="request.get",
            description="Type of request, currently only supports GET requests. This string is purely for compatibility with FlareSolverr.",
        ),
    ]
    url: Annotated[str, Body(pattern=r"^https?://", default="https://")]
    max_timeout: Annotated[int, Body(default=60)]


class Solution(BaseModel):
    url: str
    status: int
    cookies: list
    userAgent: str  # noqa: N815 # Ignore to preserve compatibility
    headers: dict[str, Any]
    response: str

    @classmethod
    def invalid(cls, url: str):
        """
        Return an empty Solution with default values.

        Useful for returning an error response.
        """
        return cls(
            url=url,
            status=HTTPStatus.INTERNAL_SERVER_ERROR,
            cookies=[],
            userAgent="",
            headers={},
            response="",
        )


class LinkResponse(BaseModel):
    status: str = "ok"
    message: str
    solution: Solution
    start_timestamp: Annotated[int, Body(alias="startTimestamp")] = int(
        time.time() * 1000
    )
    end_timestamp: Annotated[int, Body(alias="endTimestamp")] = int(time.time() * 1000)
    version: str = consts.VERSION

    @classmethod
    def invalid(cls, url: str):
        """
        Return an invalid LinkResponse with default error values.

        This method is used to generate a response indicating an invalid request.
        """
        return cls(
            status="error",
            message="Invalid request",
            solution=Solution.invalid(url),
            start_timestamp=int(time.time() * 1000),
            end_timestamp=int(time.time() * 1000),
        )