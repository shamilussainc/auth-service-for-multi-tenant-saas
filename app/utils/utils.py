from app.settings import settings


def generate_invite_link(token: str):
    return f"{settings.BASE_URL}/users/invite?token={token}"
