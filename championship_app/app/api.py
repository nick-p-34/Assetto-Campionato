from fastapi import FastAPI, Depends
from .db import get_session
from .services import list_drivers, create_driver


def register_routes(app: FastAPI):
    @app.get("/drivers")
    def api_list_drivers(session=Depends(get_session)):
        return list_drivers(session)

    @app.post("/drivers")
    def api_create_driver(name: str, session=Depends(get_session)):
        return create_driver(session, name)