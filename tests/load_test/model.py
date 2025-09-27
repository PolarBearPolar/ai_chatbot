import asyncio
from pydantic import BaseModel, ConfigDict
from typing import List, Dict
from datetime import datetime


class User(BaseModel):
    
    model_config = ConfigDict(extra='ignore')

    user_id: str | None = None
    username: str
    user_password: str


class ChatElement(BaseModel):

    chat_id: str | None = None
    chat_role: str
    chat_message: str
    created_at: datetime = None
    user_id: str | None = None


class DockerStats(BaseModel):

    elements: Dict[str, List["DockerStatsElement"]] = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._lock = asyncio.Lock()
     
    async def put(self, key: str, value: "DockerStatsElement"):
        async with self._lock:
            if key in self.elements.keys():
                self.elements.get(key).append(value)
            else:
                self.elements[key] = [value]

    def getStats(self) -> dict:
        stats = dict()
        for key, dockerStatElements in self.elements.items():
            cpuUsages = []
            ramUsages = []
            for dockerStatElement in dockerStatElements:
                cpuUsages.append(dockerStatElement.getCpuUsage())
                ramUsages.append(dockerStatElement.getRamUsage())
            cpuStats = DockerStats.getMinAvgMax(cpuUsages)
            stats[f"{key}_cpu_usage_min"] = cpuStats[0]
            stats[f"{key}_cpu_usage_avg"] = cpuStats[1]
            stats[f"{key}_cpu_usage_max"] = cpuStats[2]
            ramStats = DockerStats.getMinAvgMax(ramUsages)
            stats[f"{key}_ram_usage_min"] = ramStats[0]
            stats[f"{key}_ram_usage_avg"] = ramStats[1]
            stats[f"{key}_ram_usage_max"] = ramStats[2]
        return stats
    
    def getMinAvgMax(l: list):
        if len(l) == 0:
            return (None, None, None)
        else:
            return (min(l), sum(l)/len(l), max(l))


class DockerStatsElement(BaseModel):

    request_time: datetime = None
    cpu_cur_container_usage: int = None
    cpu_pre_container_usage: int = None
    cpu_cur_system_usage: int = None
    cpu_pre_system_usage: int = None
    cpu_num: int = None
    ram_usage: int = None
    ram_usage_cache: int = None
    ram_usage_max: int = None
    ram_limit: int = None

    def getCpuUsage(self):
        try:
            return round((self.cpu_cur_container_usage - self.cpu_pre_container_usage) / (self.cpu_cur_system_usage - self.cpu_pre_system_usage) * self.cpu_num * 100, 2)
        except:
            return 0.0
        
    def getRamUsage(self):
        return self.ram_usage - self.ram_usage_cache


class ApiStats(BaseModel):

    elements: List["ApiStatsElement"] = []
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._lock = asyncio.Lock()

    async def append(self, value: "ApiStatsElement"):
        async with self._lock:
            self.elements.append(value)

    def getStats(self) -> dict:
        totCount = 0
        errCount = 0
        requestDurations = []
        for apiStatElement in self.elements:
            totCount += 1
            if apiStatElement.request_time is not None and apiStatElement.response_time is not None:
                requestDurations.append(
                    (apiStatElement.response_time - apiStatElement.request_time).total_seconds()
                )
            if apiStatElement.status is None or apiStatElement.status == 0 or 400 <= apiStatElement.status < 600:
                errCount += 1
        stats = ApiStats.getMinAvgMax(requestDurations)
        return {
            "requests_total_num": totCount,
            "requests_error_num": errCount,
            "requests_duration_min": stats[0], 
            "requests_duration_avg": stats[1], 
            "requests_duration_max": stats[2]
        }
    
    def getMinAvgMax(l: list):
        if len(l) == 0:
            return (None, None, None)
        else:
            return (min(l), sum(l)/len(l), max(l))


class ApiStatsElement(BaseModel):

    user: str = None
    request_time: datetime = None
    response_time: datetime = None
    status: int = None