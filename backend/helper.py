import constants
from aiohttp import ClientError, ClientResponseError, ClientConnectionError, ClientSession

def getLanguage(language: str=None):
    if language == "en":
        return "en"
    elif language == "sr":
        return "sr"
    elif language == "ru":
        return "ru"
    else:
        return constants.API_DEFAULT_LANGUAGE

async def sendRequestAsync(
        session: ClientSession = None, 
        method: str = "get", 
        url: str = None, 
        params: dict = None, 
        body: dict = None, 
        headers: dict = None
    ):
    try:
        requestCoroutine = (
            session.get(url, params=params, headers=headers)
            if method.lower() == "get"
            else session.post(url, params=params, headers=headers, json=body)
        )
        async with requestCoroutine as response:
            try:
                # Raise error if status is 4xx or 5xx
                response.raise_for_status()
                return response.status, await response.json(), None
            except ClientResponseError as e:
                return e.status, None, e.message
            except Exception as e:
                return 0, None, str(e)
    except ClientConnectionError as e:
        return 0, None, str(e)
    except TimeoutError as e:
        return 0, None, str(e)
    except ClientError as e:
        return 0, None, str(e)
    except Exception as e:
        return 0, None, str(e)