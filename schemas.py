"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Add your own schemas here:
# --------------------------------------------------

class Note(BaseModel):
    """
    Notes collection schema for engineering students
    Collection name: "note"
    """
    title: str = Field(..., min_length=3, max_length=120, description="Note title")
    subject: str = Field(..., min_length=2, max_length=80, description="Subject or course name")
    branch: Optional[str] = Field(None, description="Engineering branch e.g., CSE, ECE, ME, CE")
    semester: Optional[str] = Field(None, description="Semester or year e.g., 1st, 2nd, 3rd, 4th")
    description: Optional[str] = Field(None, max_length=500, description="Short description of the note")
    content: Optional[str] = Field(None, description="Text/markdown content of the note")
    file_url: Optional[str] = Field(None, description="Public URL to a file (PDF, DOC, etc.)")
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags for quick search")
    uploader_name: Optional[str] = Field(None, description="Name of the uploader")
    uploader_email: Optional[EmailStr] = Field(None, description="Email of the uploader")
    likes: int = Field(0, ge=0, description="Number of likes")

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
