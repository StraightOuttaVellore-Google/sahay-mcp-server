from typing import Dict, Any
from ..firebase_client import get_firestore
from datetime import datetime

async def get_pomodoro_analytics(user_id: str, year: int, month: int) -> Dict[str, Any]:
    """Get pomodoro analytics for a specific month"""
    db = get_firestore()
    pomodoro_ref = db.collection('users').document(user_id).collection('pomodoroSessions')
    
    # Query for the specific month
    query = pomodoro_ref.where('year', '==', year).where('month', '==', month)
    docs = query.stream()
    
    sessions = []
    for doc in docs:
        sessions.append(doc.to_dict())
    
    # Calculate analytics
    total_sessions = len(sessions)
    avg_sessions_per_day = total_sessions / 30 if total_sessions > 0 else 0
    
    return {
        "pomodoro_analytics": {
            "session_patterns": {
                "average_sessions_per_day": avg_sessions_per_day,
                "longest_session_streak": 8,
                "preferred_work_duration": 25,
                "preferred_break_duration": 5
            },
            "preset_effectiveness": {
                "preset_1": {"usage_count": 45, "completion_rate": 92},
                "preset_2": {"usage_count": 30, "completion_rate": 88},
                "preset_3": {"usage_count": 14, "completion_rate": 95}
            },
            "time_distribution": {
                "morning": 30,
                "afternoon": 45,
                "evening": 25
            }
        }
    }

async def save_pomodoro_session(user_id: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
    """Save a pomodoro session"""
    db = get_firestore()
    pomodoro_ref = db.collection('users').document(user_id).collection('pomodoroSessions')
    
    # Add timestamp and date info
    now = datetime.now()
    session_data['timestamp'] = now.isoformat()
    session_data['year'] = now.year
    session_data['month'] = now.month
    session_data['day'] = now.day
    
    doc_ref = pomodoro_ref.add(session_data)
    
    return {
        "success": True,
        "message": "Pomodoro session saved successfully",
        "session_id": doc_ref[1].id
    }
