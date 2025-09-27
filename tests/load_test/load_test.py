import math
import requests
import asyncio
import aiohttp
import os
import pandas as pd
import constants
import helper
from model import User, ChatElement, DockerStats, DockerStatsElement, ApiStats, ApiStatsElement
from aiohttp import ClientTimeout
from urllib.parse import urljoin
from typing import List
from datetime import datetime
from logger import setupLogger

logger = setupLogger(__name__)
USERS = []

def testApplicationLoad(
        userNum: int, 
        isRagUsed: bool, 
        isOneQueryPerChat: bool, 
        outputFilename: str, 
        outputFileWriteMode: str
    ):
    scenario = getScenario(userNum, isRagUsed)
    generateUsers(userNum)
    testResult = asyncio.run(
        testQueriesLoad(scenario, isRagUsed, isOneQueryPerChat)
    )
    outputTestResult(testResult, outputFilename, outputFileWriteMode)

def generateUsers(userNum: int) -> None:
    for i in range(userNum):
        USERS.append(
            authenticateUser(
                f"TEST_USER_{i:0{math.ceil(userNum/10)}d}", 
                f"TEST_PWD_{i:0{math.ceil(userNum/10)}d}"
            )
        )

def authenticateUser(name: str, password:str) -> User:
    user = None
    userRequest = requests.get(
        urljoin(constants.BACKEND_BASE_URL, constants.BACKEND_USER_ENDPOINT), 
        params={"username": name, "password": password}
    )
    if userRequest.status_code == 200:
        user = User(**userRequest.json())
    elif userRequest.status_code == 404:
        user = User(
            username=name, 
            user_password=password
        )
        userPostRequest = requests.post(
            urljoin(constants.BACKEND_BASE_URL, constants.BACKEND_USER_ENDPOINT), 
            data=user.model_dump_json()
        )
        user = User(**userPostRequest.json())
    return user

async def getDockerStats(apiTask: asyncio.Task, clientTimeoutConfig: ClientTimeout = constants.CLIENT_TIMEOUT_CONFIG) -> DockerStats:
    dockerStats = DockerStats()
    session = aiohttp.ClientSession(timeout = clientTimeoutConfig)
    tasks = []
    while not apiTask.done():
        for dockerService in constants.DOCKER_SERVICES:
            tasks.append(
                asyncio.create_task(getDockerStatsOfOneService(dockerStats, dockerService, session))    
            )
        await asyncio.gather(*tasks)
        await asyncio.sleep(0.5)
    await session.close()
    return dockerStats

async def getDockerStatsOfOneService(dockerStats: DockerStats, service: str, session: aiohttp.ClientSession = None) -> None:
    dockerStatsEl = DockerStatsElement(
        request_time = helper.getCurrTimestamp()
    )
    status, response = await helper.sendRequestAsync(
        session=session, 
        method="get", 
        url=urljoin(constants.DOCKER_BASE_URL, constants.DOCKER_CONTAINER_ENDPOINT.format(container=service)), 
        params={"stream": "false"}
    )
    logger.info(f" * Collecting Docker stats ({service})...")
    dockerStatsEl.cpu_cur_container_usage = response["cpu_stats"]["cpu_usage"]["total_usage"]
    dockerStatsEl.cpu_pre_container_usage = response["precpu_stats"]["cpu_usage"]["total_usage"]
    dockerStatsEl.cpu_cur_system_usage = response["cpu_stats"]["system_cpu_usage"]
    dockerStatsEl.cpu_pre_system_usage = response["precpu_stats"]["system_cpu_usage"]
    dockerStatsEl.cpu_num = response["cpu_stats"]["online_cpus"]
    dockerStatsEl.ram_usage = response["memory_stats"]["usage"]
    dockerStatsEl.ram_usage_cache = response["memory_stats"]["stats"].get("cache", 0)
    dockerStatsEl.ram_usage_max = response["memory_stats"]["max_usage"]
    dockerStatsEl.ram_limit = response["memory_stats"]["limit"]
    await dockerStats.put(service, dockerStatsEl)

async def sendQuery(apiStats: ApiStats, user: User, questions: List[str], isOneQueryPerChat: bool = True, session: aiohttp.ClientSession = None):
    chatId = None if isOneQueryPerChat else helper.generateUuidHex()
    for question in questions:
        logger.info(f" * {user.username}: Sending query '{question}'...")
        apiStatsEl = ApiStatsElement(
            request_time = helper.getCurrTimestamp(),
            user = user.username
        )
        chatElement = ChatElement(
            chat_id=chatId,
            chat_role=constants.ROLE_USER,
            chat_message=question,
            user_id=user.user_id
        )
        status, response = await helper.sendRequestAsync(
            session=session, 
            method="post", 
            url=urljoin(constants.BACKEND_BASE_URL, constants.BACKEND_QUERY_ENDPOINT), 
            headers={constants.BACKEND_HEADER_LANGUAGE: "en"},
            body=chatElement.model_dump(),
            logRequest=True
        )
        apiStatsEl.response_time = helper.getCurrTimestamp()
        apiStatsEl.status = status
        await apiStats.append(apiStatsEl)
        logger.debug(f" * {user.username}: Got answer for '{question}' - '{None if response is None else response}'...") #ChatElement(**response).chat_message

async def sendQueries(questions: List[str], isOneQueryPerChat: bool = True, clientTimeoutConfig: ClientTimeout = constants.CLIENT_TIMEOUT_CONFIG):
    apiStats = ApiStats()
    session = aiohttp.ClientSession(timeout = clientTimeoutConfig)
    queryTasks = []
    for user in USERS:
        queryTasks.append(
            asyncio.create_task(sendQuery(apiStats, user, questions, isOneQueryPerChat, session))
        )
    await asyncio.gather(*queryTasks)
    await session.close()
    return apiStats

def getQuestionList(isRagUsed: bool = True):
    if isRagUsed:
        return constants.QUESTIONS_RAG
    else:
        return constants.QUESTIONS_OTHER

def getScenario(userNum: int = 0, isRagUsed: bool = True):
    return f"{userNum} user(s), {'RAG' if isRagUsed else 'no RAG'}"

async def testQueriesLoad(
        scenario: str = None,
        isRagUsed: bool = True, 
        isOneQueryPerChat: bool = True
    ):
    startDatetime = helper.getCurrTimestamp()
    apiTask = asyncio.create_task(sendQueries(getQuestionList(isRagUsed), isOneQueryPerChat))
    dockerTask = asyncio.create_task(getDockerStats(apiTask))

    apiStats, dockerStats = await asyncio.gather(apiTask, dockerTask)
    endDatetime = helper.getCurrTimestamp()
    return calculateStats(scenario, startDatetime, endDatetime, apiStats, dockerStats)

def calculateStats(scenario: str, startDatetime: datetime, endDatetime: datetime, apiStats: ApiStats, dockerStats: DockerStats) -> None:
    aStats = apiStats.getStats()
    dStats = dockerStats.getStats()
    result = {
        "scenario": scenario,
        "test_start": startDatetime,
        "test_end": endDatetime,
        "test_duration": (endDatetime - startDatetime).total_seconds(), # if endDatetime is not None and startDatetime is not None else None
        "requests_per_second_num": aStats["requests_total_num"]/(endDatetime - startDatetime).total_seconds(),
        **aStats,
        **dStats
    }
    return result

def outputTestResult(stats: dict, outputFilename: str=constants.DEFAULT_OUTPUT_FILENAME, mode: str="w") -> None:
    df = pd.DataFrame([stats], columns=[
            "scenario",
            "test_start",
            "test_end",
            "test_duration",
            "requests_per_second_num",
            "requests_total_num",
            "requests_error_num",
            "requests_duration_min",
            "requests_duration_avg",
            "requests_duration_max",
            "vector_database_cpu_usage_min",
            "vector_database_cpu_usage_avg",
            "vector_database_cpu_usage_max",
            "vector_database_ram_usage_min",
            "vector_database_ram_usage_avg",
            "vector_database_ram_usage_max",
            "backend_cpu_usage_min",
            "backend_cpu_usage_avg",
            "backend_cpu_usage_max",
            "backend_ram_usage_min",
            "backend_ram_usage_avg",
            "backend_ram_usage_max",
            "database_cpu_usage_min",
            "database_cpu_usage_avg",
            "database_cpu_usage_max",
            "database_ram_usage_min",
            "database_ram_usage_avg",
            "database_ram_usage_max",
            "chatbot_cpu_usage_min",
            "chatbot_cpu_usage_avg",
            "chatbot_cpu_usage_max",
            "chatbot_ram_usage_min",
            "chatbot_ram_usage_avg",
            "chatbot_ram_usage_max"
    ])
    outputFilepath = os.path.join(os.path.dirname(__file__), outputFilename)
    if os.path.exists(outputFilepath) and mode == "a":
        df.to_csv(outputFilepath, mode="a", sep="\t", index=False, header=False)
    else:
        df.to_csv(outputFilepath, mode="w", sep="\t", index=False, header=True)