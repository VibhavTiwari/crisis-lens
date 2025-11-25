app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock Data Store
MOCK_ITEMS = [
    {
        "id": "item1",
        "title": "Breaking: Floods in Mumbai",
        "text": "Reports of water logging in Bandra.",
        "risk_score": 0.85,
        "status": "pending_review",
        "claims": [
            {"id": "c1", "text": "Floods caused by cloudburst", "veracity": 0.4, "risk": 0.8}
        ]
    },
    {
        "id": "item2",
        "title": "Alien spaceship in Delhi",
        "text": "Viral video shows UFO.",
        "risk_score": 0.1,
        "status": "verified_false",
        "claims": [
            {"id": "c2", "text": "Aliens landed", "veracity": 0.0, "risk": 0.1}
        ]
    }
]

class Item(BaseModel):
    id: str
    title: str
    text: str
    risk_score: float
    status: str
    claims: List[dict]

@app.get("/api/items", response_model=List[Item])
async def get_items():
    return MOCK_ITEMS

@app.get("/api/items/{item_id}", response_model=Item)
async def get_item(item_id: str):
    for item in MOCK_ITEMS:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")

@app.post("/api/items/{item_id}/verify")
async def verify_item(item_id: str, status: str):
    for item in MOCK_ITEMS:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock Data Store
MOCK_ITEMS = [
    {
        "id": "item1",
        "title": "Breaking: Floods in Mumbai",
        "text": "Reports of water logging in Bandra.",
        "risk_score": 0.85,
        "status": "pending_review",
        "claims": [
            {"id": "c1", "text": "Floods caused by cloudburst", "veracity": 0.4, "risk": 0.8}
        ]
    },
    {
        "id": "item2",
        "title": "Alien spaceship in Delhi",
        "text": "Viral video shows UFO.",
        "risk_score": 0.1,
        "status": "verified_false",
        "claims": [
            {"id": "c2", "text": "Aliens landed", "veracity": 0.0, "risk": 0.1}
        ]
    }
]

class Item(BaseModel):
    id: str
    title: str
    text: str
    risk_score: float
    status: str
    claims: List[dict]

@app.get("/api/items", response_model=List[Item])
async def get_items():
    return MOCK_ITEMS

@app.get("/api/items/{item_id}", response_model=Item)
async def get_item(item_id: str):
    for item in MOCK_ITEMS:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")

@app.post("/api/items/{item_id}/verify")
async def verify_item(item_id: str, status: str):
    for item in MOCK_ITEMS:
        if item["id"] == item_id:
            item["status"] = status
            return {"message": f"Item {item_id} marked as {status}"}
    raise HTTPException(status_code=404, detail="Item not found")

from apps.api.routers import items, claims
from apps.api.routers.auth import router as auth_router
from apps.api.routers.workflows import router as workflows_router

app.include_router(auth_router)
app.include_router(workflows_router)
app.include_router(items.router)
app.include_router(claims.router)

# Serve Frontend
# In a real app, we might serve this separately or use a proper build
# For this demo, we serve static files from apps/frontend
if os.path.exists("apps/frontend"):
    app.mount("/", StaticFiles(directory="apps/frontend", html=True), name="frontend")
