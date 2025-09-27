import uuid
from datetime import datetime, timezone
from aiohttp import ClientError, ClientResponseError, ClientConnectionError, ClientSession
from logger import setupLogger

logger = setupLogger(__name__)

def getCurrTimestamp():
    return datetime.now(timezone.utc)

def generateUuidHex():
    return uuid.uuid4().hex

async def sendRequestAsync(
        session: ClientSession = None, 
        method: str = "get", 
        url: str = None, 
        params: dict = None, 
        body: dict = None, 
        headers: dict = None,
        logRequest = None
    ):
    if logRequest is not None and logRequest:
        logger.debug(f"Sending a request:\n\tmethod - {method}, \n\turl - {url},\n\tparams - {params},\n\tbody - {body},\n\theaders - {headers}")
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
                return response.status, await response.json()
            except ClientResponseError as e:
                logger.debug(f"A ClientResponseError occured when sending a request: {e.message}")
                return e.status, None
            except Exception as e:
                logger.debug(f"An exception occured when sending a request: {str(e)}")
                return 0, None
    except ClientConnectionError as e:
        logger.debug(f"A ClientConnectionError occured when sending a request: {str(e)}")
        return 0, None
    except TimeoutError as e:
        logger.debug(f"A TimeoutError occured when sending a request: {str(e)}")
        return 0, None
    except ClientError as e:
        logger.debug(f"A ClientError occured when sending a request: {str(e)}")
        return 0, None
    except Exception as e:
        logger.debug(f"An exception occured when sending a request: {str(e)}")
        return 0, None