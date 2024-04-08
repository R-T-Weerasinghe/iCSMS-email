from fastapi import APIRouter
from config.database import collection_name
from models.todos import Todo
from schema.schemas import list_serial
from schema.schemas import individual_serial
from bson import ObjectId

router2 = APIrouter()

#GET request method

@router2.get("/")
async def get_todos():
    todos = list_serial(collection_name.find())
    return todos

@router2.post("/")
async def post_todo(todo: Todo):
    collection_name.insert_one(todo.dict())

# PUT request
@router2.put("/{id}")
async def put_todo(id: str, todo: Todo):
    collection_name.find_one_and_update({"_id": ObjectId(id)}, {"$set": dict(todo)})


# DELETE request method
@router2.delete("/{id}")
async def delete_todo(id: str):
    collection_name.find_one_and_delete({"_id": ObjectId(id)})
    
    
# FastAPI endpoint to retrieve a todo by ID
@router2.get("/{todo_id}")
async def read_todo(todo_id: str):
    try:
        # Convert the string to ObjectId for querying MongoDB
        object_id = ObjectId(todo_id)

       
        todo = individual_serial(collection_name.find_one({"_id": object_id}))

        # Check if todo exists
        if todo:
            return todo
        else:
            raise HTTPException(status_code=404, detail="Todo not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    



