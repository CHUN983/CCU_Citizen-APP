"""
Category API routes
"""

from fastapi import APIRouter, HTTPException
from utils.database import get_db_cursor

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("")
async def get_categories():
    """Get all categories"""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT id as category_id, name, description, created_at
            FROM categories
            ORDER BY name
        """)

        categories = cursor.fetchall()

        return {
            "categories": categories,
            "total": len(categories)
        }


@router.get("/{category_id}")
async def get_category(category_id: int):
    """Get category by ID"""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT id as category_id, name, description, created_at
            FROM categories
            WHERE id = %s
        """, (category_id,))

        category = cursor.fetchone()

        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        return category
