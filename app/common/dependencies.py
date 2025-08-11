from typing import Annotated, Literal

from fastapi import HTTPException, status, Security
from fastapi.security import APIKeyHeader

from .permissions import check_authorization


access_token = APIKeyHeader(name="API-Key")


class AuthorizationRequired:
    def __init__(self):
        pass

    async def __call__(
        self,
        token: Annotated[str, Security(access_token)],
    ) -> Literal[True]:
        allowed = await check_authorization(token)
        if allowed:
            return True

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API Key")