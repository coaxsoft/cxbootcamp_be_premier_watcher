from django.conf import settings


def construct_url(path: str, token: str) -> str:
    """Create URL to FE site

    :param path: relative path to FE endpoint
    :param token: token to insert
    :return: constructed url
    """
    url = f"{settings.FE_SITE_URL}/{path}"
    url += f"?token={token}"
    return url

