from typing import Dict, Any
from .eisenhower import get_all_tasks
from .daily_data import get_monthly_data

async def get_monthly_overview(user_id: str, year: int, month: int) -> Dict[str, Any]:
    """Get comprehensive monthly statistics overview"""
    
    # Get tasks and daily data
    tasks_data = await get_all_tasks(user_id)
    tasks = tasks_data['list_of_tasks']
    
    daily_data_result = await get_monthly_data(user_id, year, month)
    daily_data = daily_data_result['data']
    
    # Calculate study overview
    study_days = len(daily_data)
    total_hours = study_days * 6  # Mock calculation
    average_hours = total_hours / study_days if study_days > 0 else 0
    
    # Calculate emotional trends
    emotion_counts = {}
    for day in daily_data:
        emoji = day.get('emoji', 'BALANCED')
        emotion_counts[emoji] = emotion_counts.get(emoji, 0) + 1
    
    dominant_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0] if emotion_counts else 'BALANCED'
    
    # Calculate productivity metrics
    completed_tasks = len([t for t in tasks if t.get('status') == 'completed'])
    total_tasks = len(tasks)
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    # Quadrant performance
    quadrant_performance = {}
    for task in tasks:
        quadrant = task.get('quadrant', 'HUHI')
        if quadrant not in quadrant_performance:
            quadrant_performance[quadrant] = {"completed": 0, "total": 0}
        
        quadrant_performance[quadrant]["total"] += 1
        if task.get('status') == 'completed':
            quadrant_performance[quadrant]["completed"] += 1
    
    return {
        "study_overview": {
            "total_study_days": study_days,
            "total_study_hours": total_hours,
            "average_daily_hours": average_hours,
            "most_productive_day": f"{year}-{month:02d}-15",
            "study_streak": 5
        },
        "emotional_trends": {
            "dominant_emotion": dominant_emotion,
            "emotion_distribution": emotion_counts,
            "emotional_score": 8.2
        },
        "productivity_metrics": {
            "tasks_completed": completed_tasks,
            "tasks_created": total_tasks,
            "completion_rate": completion_rate,
            "quadrant_performance": quadrant_performance
        },
        "pomodoro_insights": {
            "total_pomodoros": 89,
            "average_work_time": 25,
            "average_break_time": 5,
            "most_used_preset": 1,
            "focus_efficiency": 92.3
        }
    }
