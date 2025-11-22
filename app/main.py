from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import os

from app.routes import encrypt_routes, decrypt_routes, auth_routes

# ---------------------------
# Create FastAPI app FIRST (very important)
# ---------------------------
app = FastAPI(title="CryptoVault API", version="1.0")

# ---------------------------
# Mount UI folders (NOW app exists — safe to mount)
# ---------------------------
app.mount("/admin", StaticFiles(directory="ui/server_ui"), name="admin")
app.mount("/send", StaticFiles(directory="ui/sender_ui"), name="sender")
app.mount("/receive", StaticFiles(directory="ui/receiver_ui"), name="receiver")

# ---------------------------
# Enable CORS
# ---------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Include API routes
# ---------------------------
app.include_router(encrypt_routes.router, prefix="/encrypt", tags=["Encrypt"])
app.include_router(decrypt_routes.router, prefix="/decrypt", tags=["Decrypt"])
app.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])

# ---------------------------
# Optional static folders (only if they exist)
# ---------------------------
if os.path.exists("ui/server_ui/static"):
    app.mount("/server/static", StaticFiles(directory="ui/server_ui/static"), name="server_static")
if os.path.exists("ui/sender_ui/static"):
    app.mount("/sender/static", StaticFiles(directory="ui/sender_ui/static"), name="sender_static")
if os.path.exists("ui/receiver_ui/static"):
    app.mount("/receiver/static", StaticFiles(directory="ui/receiver_ui/static"), name="receiver_static")

# ---------------------------
# Setup templates
# ---------------------------
server_templates = Jinja2Templates(directory="ui/server_ui")
sender_templates = Jinja2Templates(directory="ui/sender_ui")
receiver_templates = Jinja2Templates(directory="ui/receiver_ui")

# ---------------------------
# UI Routes
# ---------------------------
@app.get("/server", response_class=HTMLResponse)
async def server_home(request: Request):
    return server_templates.TemplateResponse("index.html", {"request": request})

@app.get("/sender", response_class=HTMLResponse)
async def sender_home(request: Request):
    return sender_templates.TemplateResponse("index.html", {"request": request})

@app.get("/receiver", response_class=HTMLResponse)
async def receiver_home(request: Request):
    return receiver_templates.TemplateResponse("index.html", {"request": request})

# Root → admin/dashboard
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return server_templates.TemplateResponse("index.html", {"request": request})
