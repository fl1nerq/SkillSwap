from fastapi import FastAPI
from src.api.auth import router as auth_router
from src.api.users import router as users_router
from src.api.categories import router as categories_router
from src.api.ads import router as ads_router
from src.api.deals import router as deals_router
from src.api.chat import router as chat_router


app = FastAPI(title="SkillSwapper")

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(categories_router)
app.include_router(ads_router)
app.include_router(deals_router)
app.include_router(chat_router)

@app.get('/')
async def root():
    return {"message": "SkillSwap API is running!", "status": "Active"}


@app.get("/about")
async def about():
    return {"author": "Zakhar", "level": "Novice to Pro"}
