from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

app = FastAPI()

games = {"ahad": "Metal Gear Solid 2", "siya": "Minecraft"}

# Custom exception for business logic
class GameNotActiveError(Exception):
    def __init__(self, game_name: str):
        self.game_name = game_name

# Handle our custom exception globally
@app.exception_handler(GameNotActiveError)
async def game_not_active_handler(request: Request, exc: GameNotActiveError):
    return JSONResponse(
        status_code=503,
        content={"error": f"{exc.game_name} servers are currently down"}
    )

# Handle validation errors our way
@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"error": "Invalid input", "details": exc.errors()}
    )

@app.get("/games/{game_id}")
async def read_game(game_id: str):
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")

    if game_id == "siya":
        raise GameNotActiveError(game_name=games[game_id])

    return {"your_game": games[game_id]}
