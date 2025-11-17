import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import db, create_document, get_documents
from schemas import Note

app = FastAPI(title="EngiNotes API", description="Backend for engineering notes sharing platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "EngiNotes backend is running"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from EngiNotes API!"}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            
            # Try to list collections to verify connectivity
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]  # Show first 10 collections
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    # Check environment variables
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response

# -----------------------------
# Notes Endpoints (Database)
# -----------------------------

class NoteCreate(BaseModel):
    title: str
    subject: str
    branch: Optional[str] = None
    semester: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    file_url: Optional[str] = None
    tags: Optional[List[str]] = []
    uploader_name: Optional[str] = None
    uploader_email: Optional[str] = None

@app.post("/api/notes")
def create_note(note: NoteCreate):
    note_model = Note(**note.model_dump())
    note_id = create_document("note", note_model)
    return {"id": note_id, "message": "Note created"}

@app.get("/api/notes")
def list_notes(subject: Optional[str] = None, branch: Optional[str] = None, semester: Optional[str] = None, q: Optional[str] = None):
    filter_dict = {}
    if subject:
        filter_dict["subject"] = subject
    if branch:
        filter_dict["branch"] = branch
    if semester:
        filter_dict["semester"] = semester
    if q:
        # naive search across title/description/tags
        filter_dict["$or"] = [
            {"title": {"$regex": q, "$options": "i"}},
            {"description": {"$regex": q, "$options": "i"}},
            {"tags": {"$elemMatch": {"$regex": q, "$options": "i"}}}
        ]
    docs = get_documents("note", filter_dict)
    # Convert ObjectId to string for _id
    for d in docs:
        d["id"] = str(d.get("_id"))
        d.pop("_id", None)
    return {"items": docs}

@app.get("/api/notes/{note_id}")
def get_note(note_id: str):
    from bson import ObjectId
    try:
        doc = db.note.find_one({"_id": ObjectId(note_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Note not found")
        doc["id"] = str(doc.get("_id"))
        doc.pop("_id", None)
        return doc
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid id")

@app.post("/api/notes/{note_id}/like")
def like_note(note_id: str):
    from bson import ObjectId
    result = db.note.update_one({"_id": ObjectId(note_id)}, {"$inc": {"likes": 1}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"message": "Liked"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
