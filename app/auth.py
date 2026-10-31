import os
from fastapi import Header, HTTPException

API_KEY = os.getenv("API_KEY")


def verify_api_key(authorization: str | None = Header(default=None)):
    if not API_KEY:
        raise HTTPException(
            status_code=500,
            detail="API key is not configured"
        )

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Missing Authorization header"
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid Authorization header"
        )

    provided_key = authorization.replace("Bearer ", "", 1)

    if provided_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )

    return True