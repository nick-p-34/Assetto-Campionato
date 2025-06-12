from .models import Driver
from sqlmodel import Session


def list_drivers(session: Session):
    return session.query(Driver).all()


def create_driver(session: Session, name: str):
    driver = Driver(name=name)
    session.add(driver)
    session.commit()
    session.refresh(driver)
    return driver