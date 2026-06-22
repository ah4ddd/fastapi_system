from fastapi import FastAPI, Request, BackgroundTasks
# relative import (current package)
from .routers import items, weather, github, crypto, auth
import time
# Built-in CORS middleware class
from fastapi.middleware.cors import CORSMiddleware

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse


"""
When server starts:
    FastAPI
    ↓
    app.main:app
    ↓
    main.py executes
    ↓
    routers imported
    ↓
    database imported
    ↓
    models imported
    ↓
    app object created
    ↓
    routers attached
    ↓
    server starts
"""
tags_metadata = [
    {
        "name": "authentication",
        "description": "JWT authentication and account management."
    },
    {
        "name": "items",
        "description": "Inventory and item management."
    },
    {
        "name": "weather",
        "description": "Weather data using OpenWeather API."
    },
    {
        "name": "crypto",
        "description": "Cryptocurrency market data."
    },
    {
        "name": "github",
        "description": "GitHub repository analytics."
    }
]

app = FastAPI(
    title="FastAPI Learning System",
    description="""
Backend learning playground.

Features:
- JWT Authentication
- PostgreSQL
- SQLAlchemy
- Alembic
- Weather API
- GitHub API
- Crypto API
""",
    version="1.0.0",
    openapi_tags=tags_metadata
)




# Take all routes registered on this router and attach them to the main app
"""
FastAPI App
│
├── Root
│   ├── GET /
│   └── GET /health
│
└── Items Router
    ├── GET /items
    ├── POST /items
    ├── PUT /items/{id}
    └── DELETE /items/{id}
"""
"""
Main app now knows:
    POST /auth/signup
    POST /auth/login
    GET /auth/me
    DELETE /auth/me
    PUT /auth/password

app.include_router(items.router) takes every route defined in items.router
and registers it with the main app.
At startup FastAPI clones all those routes into the main route table.
After this, from FastAPI's perspective,
it's exactly as if you had written all those routes directly in main.py.
The split is just for organization — at runtime it's one unified app.

NOTES: CAN Add Extra Config At Include Time:
    You can override or add to a router's config
    when including it, without touching the router file eg:
        app.include_router(
            admin.router,
            prefix="/admin",       # add prefix the router doesn't have
            tags=["admin"],        # add tags
            dependencies=[Depends(get_token_header)],  # add auth
            responses={418: {"description": "I'm a teapot"}},
        )
"""
# include_router(items.router) = Take router.routes & attach them to app.routes
app.include_router(items.router) # items.router → APIRouter instance
app.include_router(weather.router)
app.include_router(github.router)
app.include_router(crypto.router)
app.include_router(auth.router)


# Root endpoints
@app.get("/health")
async def read_health():
    return {"message": "System is alive"}


"""
Middleware is:
    a global interception layer

It sits BETWEEN:
    incoming request
    your route

and ALSO between:
    your route
    outgoing response
"""
"""
This line:
    response = await call_next(request)

is literally:
    the entire request lifecycle compressed into one line.
    continue processing this request through routing system.

Because inside that ONE line:
    route runs
    dependencies run
    JWT auth runs
    DB queries run
    response gets created
    exceptions may happen
    serialization happens

call_next: This is the PAUSE POINT.
Everything before call_next runs before the endpoint.
Everything after runs after the endpoint.

FastAPI MAY do something like::
    find matching route (eg: @app.get("/users/me"))
    ↓
    run dependencies
    ↓
    run JWT auth
    ↓
    extract token
    ↓
    decode token
    ↓
    verify token
    ↓
    run DB query
    ↓
    execute route
    ↓
    create Response object
    ↓
    return response

ALL of that happens INSIDE:
    await call_next(request) NSIDE THIS ONE LINE.

The Execution Flow Visualized:
    Client sends: GET /items/
            ↓
    MIDDLEWARE STARTS
    start_time = now
            ↓
    call_next(request) ← PAUSE, endpoint runs
            ↓
    endpoint runs: reads DB, builds response
            ↓
    MIDDLEWARE RESUMES with response
    process_time = now - start_time
    response.headers["X-Process-Time"] = "0.043"
            ↓
    return response
            ↓
    Client receives response WITH the extra header
"""
@app.middleware("http") # Register this function as middleware for HTTP requests
# FastAPI later calls this function automatically
# request: Request = Incoming HTTP request object
# call_next = internal continuation function
# the SECOND parameter is expected to be: a callable function object
# Always. That is the middleware contract.
# FastAPI internally guarantees:
# parameter 1 = Request object
# parameter 2 = next callable function
async def log_requests(request: Request, call_next):
    start_time = time.perf_counter() # Stores precise timer
    # Logs incoming request BEFORE route executes
    print(f"Incoming request: {request.method} {request.url}")
    # continue request deeper into FastAPI
    # Before this line: middleware has control
    # After this line: route system has control
    # Then AFTER route finishes: control RETURNS BACK to middleware
    # call_next() returns the route response
    response = await call_next(request) # continue request lifecycle
    process_time = time.perf_counter() - start_time # calculate duration
    print(f"Completed in {process_time:.4f} seconds")
    # Adds custom HTTP header.
    # Response object contains: headers, status code, body, etc.
    # The X- prefix is convention for custom headers
    # it means "this is not a standard HTTP header,
    # it's application-specific
    response.headers["X-Process-Time"] = str(process_time)
    return response # the final response

# CORS (cross origin resource sharing)
# CORS is a browser-enforced permission system that allows
# a frontend running on one origin e.g. localhost:3000
# to communicate with a backend running on another origin e.g. localhost:8000
"""
Why is CORS middleware?
Because the backend must answer that request for EVERY route.

middleware lesson:
    @app.middleware("http")
        gets:
            request
            ↓
            route
            ↓
            response

CORS needs exactly that.
Because it must intercept requests.

Visualize:
    Browser
    ↓
    Request
    ↓
    CORSMiddleware
    ↓
    Route
    ↓
    Response
    ↓
    CORSMiddleware
    ↓
    Browser

Why?

Because Before route. CORS needs to Inspect:
    Origin: localhost:3000

And after route. Add Access-Control-Allow-Origin:
    http://localhost:3000
to response headers.

That's literally middleware behavior:
    before route
    after route

which is why CORS is implemented as middleware.
Because it:
    Intercepts every request and response
    specifically to tell browsers
    which frontend origins are trusted.
"""
# That's it. This middleware intercepts every OPTIONS preflight
# and every request, checks if the origin is in your allowed list,
# and adds the right headers automatically.
# Order matters. CORS middleware should be added
# before your custom logging middleware.
# CORS is outermost, runs first on requests.
app.add_middleware( # Attach middleware to application.
    CORSMiddleware,
    # which frontends are allowed to talk to your API
    # Origins are addresses (protocol + domain + port)
    allow_origins=[
        # Trusted frontends
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:8080",
    ],
    # This one matters for auth.
    allow_credentials=True,
    # Allow GET, POST, PUT, DELETE, PATCH, OPTIONS, HEAD.
    allow_methods=["*"],
    # Allow any request header.
    allow_headers=["*"],
    # Include custom header
    # (By default the browser hides custom headers from JavaScript)
    expose_headers=["X-Process-Time"]
)

"""
Background Task

Normal request:
    Request
    ↓
    Endpoint
    ↓
    Work
    ↓
    Response

Background task:
    Request
    ↓
    Endpoint
    ↓
    Schedule task
    ↓
    Response immediately
    ↓
    Task executes afterwards

Used for:
    - emails
    - logging
    - analytics
    - notifications

Not for:
    - AI training
    - heavy computation
    - long jobs

Those use Celery/Redis workers.
"""
def write_log(message: str):
    with open("background.log", "a") as log:
        log.write(f"{message}\n")


@app.post("/test-background")
async def test_background(
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(
        write_log,
        "Hello from Background Task!"
    )
    return{"message": "Task scheduled"}

"""
Browser asks:
    /static/style.css
        ↓
FastAPI looks inside:
    frontend/style.css
"""
app.mount(
    "/static",
    StaticFiles(directory="frontend"),
    name="static"
)


# Open file: frontend/index.html
# Read contents
# Send contents
# Browser receives HTML
@app.get("/")
async def homepage():
    return FileResponse("frontend/index.html")

"""
Full lifecycle (what FastAPI actually does)

When the server starts:

Step 1
Python imports modules
    `main.py imports items module`

Step 2
items.py executes
    `router object created
     routes registered`

Step 3
Main app registers router
    `app.include_router(items.router)`

Step 4
FastAPI merges routes
    `app.routes += router.routes`

Step 5
Server starts listening.
"""

# requests → router → endpoint → validation → business logic → database → response
