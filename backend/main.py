from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import users, brands, car_models, suppliers, parts, sales, analogs

Base.metadata.create_all(bind = engine)

app = FastAPI(title = "AutoParts Shop API")

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

app.include_router(users.router)
app.include_router(brands.router)
app.include_router(car_models.router)
app.include_router(suppliers.router)
app.include_router(parts.router)
app.include_router(sales.router)
app.include_router(analogs.router)

@app.get("/")
def root():
    return {"message": "API магазина автозапчастей работает!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host = "127.0.0.1", port = 8000, reload = True)