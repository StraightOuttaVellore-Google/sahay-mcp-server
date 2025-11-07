from typing import List, Dict, Any
from pydantic import BaseModel
from enum import Enum
from ..firebase_client import get_firestore
import uuid
from datetime import datetime

class TaskQuadrant(str, Enum):
    HUHI = "HUHI"
    LUHI = "LUHI" 
    HULI = "HULI"
    LULI = "LULI"

class TaskStatus(str, Enum):
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class Task(BaseModel):
    id: str
    title: str
    description: str
    quadrant: TaskQuadrant
    status: TaskStatus
    created_at: str
    updated_at: str

async def get_all_tasks(user_id: str) -> Dict[str, List[Task]]:
    """Get all tasks for a user from Firestore"""
    db = get_firestore()
    tasks_ref = db.collection('users').document(user_id).collection('tasks')
    docs = tasks_ref.stream()
    
    tasks = []
    for doc in docs:
        task_data = doc.to_dict()
        task_data['id'] = doc.id
        tasks.append(Task(**task_data))
    
    return {"list_of_tasks": [task.dict() for task in tasks]}

async def save_all_tasks(user_id: str, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Save all tasks for a user to Firestore"""
    db = get_firestore()
    batch = db.batch()
    tasks_ref = db.collection('users').document(user_id).collection('tasks')
    
    # Delete existing tasks
    existing_docs = tasks_ref.stream()
    for doc in existing_docs:
        batch.delete(doc.reference)
    
    # Add new tasks
    for task_data in tasks:
        task_id = task_data.get('id', str(uuid.uuid4()))
        task_data['updated_at'] = datetime.now().isoformat()
        doc_ref = tasks_ref.document(task_id)
        batch.set(doc_ref, task_data)
    
    batch.commit()
    
    return {
        "success": True,
        "message": "Tasks saved successfully",
        "tasks_count": len(tasks)
    }
