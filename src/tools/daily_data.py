from typing import List, Dict, Any
from pydantic import BaseModel
from enum import Enum
from ..firebase_client import get_firestore

class StudyEmoji(str, Enum):
    RELAXED = "RELAXED"
    BALANCED = "BALANCED"
    FOCUSED = "FOCUSED"
    INTENSE = "INTENSE"
    OVERWHELMED = "OVERWHELMED"
    BURNT_OUT = "BURNT_OUT"

class DailyData(BaseModel):
    day: int
    month: int
    year: int
    emoji: StudyEmoji
    summary: str

async def get_monthly_data(user_id: str, year: int, month: int) -> Dict[str, List[Dict]]:
    """Get daily data for a specific month"""
    db = get_firestore()
    daily_data_ref = db.collection('users').document(user_id).collection('dailyData')
    
    query = daily_data_ref.where('year', '==', year).where('month', '==', month)
    docs = query.stream()
    
    data = []
    for doc in docs:
        data.append(doc.to_dict())
    
    return {"data": data}

async def save_daily_data(user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Save daily data entry"""
    db = get_firestore()
    doc_id = f"{data['year']}-{data['month']}-{data['day']}"
    daily_data_ref = db.collection('users').document(user_id).collection('dailyData').document(doc_id)
    
    daily_data_ref.set(data)
    
    return {
        "success": True,
        "message": "Daily data saved successfully",
        "data": data
    }
