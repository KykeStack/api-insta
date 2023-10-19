from pydantic import BaseModel, AnyHttpUrl
from typing import List

class ScrapeInfo(BaseModel):
    username: str
    password: str
    profiles: List[str]
    minimun: int
    filter: int

class CsvUrl(BaseModel):
    url: AnyHttpUrl

if __name__ == "__main__":
    ...