from fastapi import FastAPI, Body, Depends, Query, HTTPException
from pydantic import BaseModel
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Field, Session, SQLModel, create_engine, select


app = FastAPI()

@app.get("/hello/")
async def hello():
    return {"LETS DO IT FROM SCRATCH"}


class AuthUser(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None

# OAuth2 bearer-token extractor
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def fake_decode_token(token):
    return AuthUser(
        username=token + "fakedecoded",
        email="ahad@example.com",
        full_name="Just Ahad"
    )

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = fake_decode_token(token)
    return user

@app.get("/users/me")
async def read_user_me(current_user: Annotated[AuthUser, Depends(get_current_user)]):
    return current_user


@app.post("/items/{item_id}/")
async def items(item_id: str):
    return f"back at yaa!! {item_id}"

class User(BaseModel):
    name: str
    age: int
    country: str | None = None

user_db = {}

@app.post("/user/")
async def user(user: User):
    user_db[user.name.title()] = user.model_dump()
    if user.country:
        return f"Welcom {user.name.title()} from {user.country.title()}"
    return f"welcome {user.name.title()}"

@app.get("/see-users/")
async def users():
    return user_db

@app.delete("/user/")
async def del_user(user: Annotated[str, Body()]):
    username = user.title()
    if username in user_db:
        del user_db[username]
        return {"detail": "User deleted"}
    return {"detail": "User not found"}


class HeroBase(SQLModel):
    name: str = Field(index=True)
    age: int | None = Field(default=None, index=True)


class Hero(HeroBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    secret_name: str


class HeroPublic(HeroBase):
    id: int


class HeroCreate(HeroBase):
    secret_name: str


class HeroUpdate(HeroBase):
    name: str | None = None
    age: int | None = None
    secret_name: str | None = None


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post("/heroes/", response_model=HeroPublic)
def create_hero(hero: HeroCreate, session: SessionDep):
    db_hero = Hero.model_validate(hero)
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero


@app.get("/heroes/", response_model=list[HeroPublic])
def read_heroes(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[Hero]:
    heroes = session.exec(select(Hero).offset(offset).limit(limit)).all()
    return heroes # type: ignore


@app.get("/heroes/{hero_id}", response_model=HeroPublic)
def read_hero(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero


@app.patch("/heroes/{hero_id}", response_model=HeroPublic)
def update_hero(hero_id: int, hero: HeroUpdate, session: SessionDep):
    hero_db = session.get(Hero, hero_id)
    if not hero_db:
        raise HTTPException(status_code=404, detail="Hero not found")
    hero_data = hero.model_dump(exclude_unset=True)
    hero_db.sqlmodel_update(hero_data)
    session.add(hero_db)
    session.commit()
    return hero_db


@app.delete("/heroes/{hero_id}/")
def delete_hero(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    session.delete(hero)
    session.commit()
    return {"ok": True}


@app.post("/addition/")
async def add(a: Annotated[int, Body()], b: Annotated[int, Body()]):
    return a + b

@app.post("/subtraction/")
async def sub(a: Annotated[int, Body()], b: Annotated[int, Body()]):
    return a - b

@app.post("/multiplication/")
async def multiply(a: Annotated[int, Body()], b: Annotated[int, Body()]):
    return a * b

@app.post("/division/")
async def divide(a: Annotated[int, Body()], b: Annotated[int, Body()]):
    return a / b

@app.post("/floordivision/")
async def fd(a: Annotated[int, Body()], b: Annotated[int, Body()]):
    return a // b

@app.post("/modulo/")
async def modular(a: Annotated[int, Body()], b: Annotated[int, Body()]):
    return a % b
