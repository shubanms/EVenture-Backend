from src.core.configs import create_app


from src.core.logger import logger
from src.routes.route_generation import router as route_generation_router
from src.routes.values import route as values_router
from src.routes.assistant import router as assistant_router
from src.routes.attractions import router as attractions_router


app = create_app()


app.include_router(route_generation_router, prefix="/routes", tags=["Routes"])
app.include_router(values_router, prefix="/values", tags=["Values"])
app.include_router(assistant_router, prefix="/assistant", tags=["Assistant"])
app.include_router(attractions_router, prefix="/attractions", tags=["Attractions"])


@app.get("/", tags=["Health Check"])
def health_check():

    logger.info("Application is running")

    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, access_log=False)
