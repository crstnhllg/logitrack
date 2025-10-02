from fastapi import FastAPI
from app.database import engine
from app.models import Base
from app.routers import auth, vehicles, users, orders


app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(vehicles.router)
app.include_router(orders.router)

