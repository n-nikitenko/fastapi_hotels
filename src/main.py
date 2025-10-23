from fastapi import FastAPI
from api import hotels_routers

app = FastAPI()
app.include_router(hotels_routers)

if __name__=="__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        reload=True
    )
