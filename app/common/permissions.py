from app.core.config import settings


async def check_authorization(token: str) -> bool:
    return token == settings.api_key
