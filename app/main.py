from fastapi import FastAPI
from app.routers.user import router as user_router
from app.routers.member import router as member_router
from app.routers.stats import router as stats_router


app = FastAPI()

app.include_router(router=user_router, tags=["User"])
app.include_router(router=member_router, tags=["Organization"])
app.include_router(router=stats_router, tags=["Stats"])
