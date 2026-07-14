import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from controllers.crm_router import router as crm_router
from controllers.sequence_router import router as sequence_router
from controllers.contactUs_router import router as contact_us_router
from controllers.auth_router import router as authentication_router
from controllers.news_router import router as tech_news_router
from controllers.email_transcript_router import router as email_transcript_router
from controllers.helper_routers import router as helper_routers

apps = FastAPI()

apps.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include all routers
apps.include_router(crm_router)
apps.include_router(sequence_router)
apps.include_router(contact_us_router)
apps.include_router(authentication_router)
apps.include_router(tech_news_router)
apps.include_router(email_transcript_router)
apps.include_router(helper_routers)



if __name__ == "__main__":
    uvicorn.run("main:apps", host="0.0.0.0", port=1802, reload=True)