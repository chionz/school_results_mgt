from fastapi import APIRouter

# This maps and tags our users routes 
router = APIRouter(prefix="/users", tags=["Users"])

# This is an endpoint
@router.get("/user")
def get_users():
    return [{"name": "Alice"}, {"name": "Bob"}]
