import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from controller.crm_router import router as crm_router
from controller.sequence_router import router as sequence_router

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

if __name__ == "__main__":
    uvicorn.run("main:apps", host="0.0.0.0", port=1802, reload=True)