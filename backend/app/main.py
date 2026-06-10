from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, plans, activities, wellness, n8n_proxy

app = FastAPI(
    title="Bibi Cycling Training Platform API",
    description="Backend API and ML Core for the Bibi AI autonomous cycling coach.",
    version="2.0.0"
)

# Set CORS origins (allow localhost React development and reverse proxy production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to server domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(plans.router)
app.include_router(activities.router)
app.include_router(wellness.router)
app.include_router(n8n_proxy.router)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "app": "Bibi Cycling API",
        "version": "2.0.0"
    }

@app.get("/health")
def health_check():
    # Simple endpoint for Docker / reverse proxy healthchecks
    return {"health": "OK"}
