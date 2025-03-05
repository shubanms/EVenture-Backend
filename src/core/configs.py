from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def configure_cors(app: FastAPI):
    origins = [
        "http://localhost:5173",
        "localhost:5173",
        "http://localhost:5174",
        "localhost:5174",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def create_app() -> FastAPI:
    app = FastAPI()

    configure_cors(app)

    return app


app = create_app()
