from fastapi import FastAPI, Request
from .routers import items, weather, github, crypto, auth
import time
# Built-in CORS middleware class
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="FastAPI System",
    description="CRUD API with async support",
    version="1.3.0"
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
# include_router(items.router) = Take router.routes & attach them to app.routes
app.include_router(items.router) # items.router → APIRouter instance
app.include_router(weather.router)
app.include_router(github.router)
app.include_router(crypto.router)
app.include_router(auth.router)


# Root endpoints
@app.get("/")
async def read_root():
    return {"message": "System is alive"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy"
    }


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
        "http://localhost:3000", # React
        "http://localhost:5173", # Vite
        "http://localhost:5500",
        "http://localhost:8080" # anything else
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
