from fastapi import FastAPI, Request, HTTPException, status
from starlette.responses import RedirectResponse
from starlette.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from schemas.scrape import ScrapeInfo, CsvUrl
from pydantic import BaseModel
from typing import List, Optional, Any

from modules.run import scrape_from_api
from core.config import settings

class FunctionStatus(BaseModel):
    status: bool
    content: Optional[Any] = None
    
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'], # [str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.get("/", tags=['Documentation'])
async def Root():
    return RedirectResponse(app.docs_url)

@app.post(
    "/scrape",
    response_model=CsvUrl
)
def scrape_endpoint(info: ScrapeInfo, request: Request):
    dic_info = {**info.model_dump()}
    status_scrape : FunctionStatus = scrape_from_api(**dic_info)
    if not status_scrape.status: 
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT, 
            detail=status_scrape.content
        ) 
    url = f"{request.base_url}{status_scrape.content}" 
    return {'url': url}
    
if __name__ == '__main__':
    ...