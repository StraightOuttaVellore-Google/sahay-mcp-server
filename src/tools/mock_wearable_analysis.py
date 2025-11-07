"""
Mock wearable and Sahay ecosystem data analysis tools

Provides mock data for testing agent integration with wearable devices,
pomodoro sessions, study patterns, and wellness metrics.
"""

from typing import Dict, List, Optional
from datetime import datetime, date, timedelta
import random


def generate_mock_wearable_data(userId: str, days: int = 7) -> Dict:
    """
    Generate mock wearable data for analysis
    
    Args:
        userId: User identifier
        days: Number of days of data to generate
        
    Returns:
        Dictionary with mock wearable metrics
    """
    current_date = datetime.now()
    data_points = []
    
    for i in range(days):
        data_date = current_date - timedelta(days=i)
        
        # Generate realistic mock data
        sleep_duration = random.uniform(5.5, 8.5)  # hours
        sleep_efficiency = random.uniform(0.75, 0.95)
        
        data_point = {
            "date": data_date.strftime("%Y-%m-%d"),
            "sleep": {
                "duration_hours": round(sleep_duration, 1),
                "efficiency": round(sleep_efficiency, 2),
                "deep_sleep_hours": round(sleep_duration * 0.25, 1),
                "rem_sleep_hours": round(sleep_duration * 0.20, 1),
                "light_sleep_hours": round(sleep_duration * 0.55, 1),
                "sleep_score": int(sleep_efficiency * 100),
            },
            "heart_rate": {
                "avg": random.randint(65, 85),
                "resting": random.randint(55, 70),
                "max": random.randint(140, 180),
                "hrv_rmssd": random.uniform(25, 65),
            },
            "activity": {
                "steps": random.randint(4000, 12000),
                "calories_burned": random.randint(1800, 2800),
                "active_minutes": random.randint(30, 120),
                "distance_km": round(random.uniform(3, 10), 1),
            },
            "stress": {
                "stress_score": round(random.uniform(0.2, 0.7), 2),
                "stress_events": random.randint(0, 5),
                "recovery_score": random.randint(60, 95),
                "energy_level": random.choice(["medium", "high", "low"]),
            }
        }
        data_points.append(data_point)
    
    return {
        "userId": userId,
        "data_points": data_points,
        "summary": {
            "avg_sleep_hours": round(sum(d["sleep"]["duration_hours"] for d in data_points) / days, 1),
            "avg_steps": int(sum(d["activity"]["steps"] for d in data_points) / days),
            "avg_stress_score": round(sum(d["stress"]["stress_score"] for d in data_points) / days, 2),
            "avg_recovery_score": int(sum(d["stress"]["recovery_score"] for d in data_points) / days),
        }
    }


def analyze_study_patterns(userId: str, days: int = 14) -> Dict:
    """
    Analyze mock study patterns from Sahay ecosystem
    
    Args:
        userId: User identifier
        days: Number of days to analyze
        
    Returns:
        Dictionary with study pattern analysis
    """
    # Mock study sessions
    study_sessions = []
    for i in range(days):
        num_sessions = random.randint(1, 4)
        for _ in range(num_sessions):
            duration = random.randint(25, 120)  # minutes
            focus_score = random.uniform(0.6, 0.95)
            study_sessions.append({
                "duration_minutes": duration,
                "focus_score": round(focus_score, 2),
                "subject": random.choice(["Math", "Science", "Literature", "History", "Programming"]),
                "break_taken": random.choice([True, False]),
            })
    
    total_study_time = sum(s["duration_minutes"] for s in study_sessions)
    avg_focus = sum(s["focus_score"] for s in study_sessions) / len(study_sessions)
    
    return {
        "userId": userId,
        "period_days": days,
        "total_study_minutes": total_study_time,
        "avg_daily_study_minutes": round(total_study_time / days, 1),
        "total_sessions": len(study_sessions),
        "avg_focus_score": round(avg_focus, 2),
        "subjects_studied": list(set(s["subject"] for s in study_sessions)),
        "break_adherence": round(sum(1 for s in study_sessions if s["break_taken"]) / len(study_sessions), 2),
        "insights": {
            "peak_productivity_time": random.choice(["Morning", "Afternoon", "Evening"]),
            "optimal_session_length": random.choice([25, 45, 60]),
            "focus_trend": random.choice(["improving", "stable", "declining"]),
        }
    }


def get_wellness_recommendations_context(userId: str) -> Dict:
    """
    Get contextual wellness data for personalized recommendations
    
    Args:
        userId: User identifier
        
    Returns:
        Dictionary with wellness context
    """
    wearable_data = generate_mock_wearable_data(userId, days=3)
    study_patterns = analyze_study_patterns(userId, days=7)
    
    # Calculate wellness metrics
    avg_sleep = wearable_data["summary"]["avg_sleep_hours"]
    avg_stress = wearable_data["summary"]["avg_stress_score"]
    avg_recovery = wearable_data["summary"]["avg_recovery_score"]
    avg_focus = study_patterns["avg_focus_score"]
    
    # Determine wellness state
    sleep_adequate = avg_sleep >= 7.0
    stress_high = avg_stress > 0.6
    recovery_good = avg_recovery > 70
    focus_good = avg_focus > 0.75
    
    return {
        "userId": userId,
        "current_wellness_state": {
            "sleep_adequate": sleep_adequate,
            "stress_level": "high" if stress_high else "moderate" if avg_stress > 0.4 else "low",
            "recovery_status": "good" if recovery_good else "needs_attention",
            "focus_capacity": "high" if focus_good else "moderate" if avg_focus > 0.65 else "low",
        },
        "recent_metrics": {
            "avg_sleep_hours": avg_sleep,
            "avg_stress_score": avg_stress,
            "avg_recovery_score": avg_recovery,
            "avg_study_minutes_per_day": study_patterns["avg_daily_study_minutes"],
            "avg_focus_score": avg_focus,
        },
        "recommendations_context": {
            "needs_sleep_improvement": not sleep_adequate,
            "needs_stress_management": stress_high,
            "can_handle_intense_study": recovery_good and focus_good,
            "suggested_study_duration": 45 if recovery_good else 30,
            "suggested_break_frequency": "every 25min" if stress_high else "every 45min",
        }
    }


def get_eisenhower_analysis(userId: str) -> Dict:
    """
    Analyze task distribution in Eisenhower matrix
    
    Args:
        userId: User identifier
        
    Returns:
        Dictionary with task distribution analysis
    """
    # Mock task distribution
    quadrants = {
        "urgent_important": random.randint(2, 5),
        "important_not_urgent": random.randint(5, 10),
        "urgent_not_important": random.randint(1, 4),
        "neither_urgent_nor_important": random.randint(0, 3),
    }
    
    total_tasks = sum(quadrants.values())
    
    return {
        "userId": userId,
        "task_distribution": quadrants,
        "total_tasks": total_tasks,
        "analysis": {
            "time_management_score": round((quadrants["important_not_urgent"] / total_tasks) * 100, 1) if total_tasks > 0 else 0,
            "urgency_overload": quadrants["urgent_important"] + quadrants["urgent_not_important"] > total_tasks * 0.5,
            "proactive_planning": quadrants["important_not_urgent"] > quadrants["urgent_important"],
            "recommendations": [
                "Focus more on Quadrant 2 (Important but not Urgent) tasks" if quadrants["important_not_urgent"] < 5 else "Good balance in Quadrant 2",
                "Reduce Quadrant 3 (Urgent but not Important) tasks" if quadrants["urgent_not_important"] > 3 else "Good control of Quadrant 3",
                "Eliminate Quadrant 4 tasks" if quadrants["neither_urgent_nor_important"] > 2 else "Minimal time wasters",
            ]
        }
    }


def get_pomodoro_effectiveness(userId: str, days: int = 7) -> Dict:
    """
    Analyze pomodoro session effectiveness
    
    Args:
        userId: User identifier
        days: Number of days to analyze
        
    Returns:
        Dictionary with pomodoro effectiveness metrics
    """
    sessions = []
    for _ in range(days * random.randint(2, 5)):
        completed = random.choice([True, True, True, False])  # 75% completion rate
        sessions.append({
            "work_duration": random.choice([25, 45, 60]),
            "break_duration": random.choice([5, 10, 15]),
            "completed": completed,
            "interruptions": random.randint(0, 3) if completed else random.randint(2, 5),
        })
    
    total_sessions = len(sessions)
    completed_sessions = sum(1 for s in sessions if s["completed"])
    completion_rate = completed_sessions / total_sessions if total_sessions > 0 else 0
    
    return {
        "userId": userId,
        "period_days": days,
        "total_sessions": total_sessions,
        "completed_sessions": completed_sessions,
        "completion_rate": round(completion_rate, 2),
        "avg_work_duration": round(sum(s["work_duration"] for s in sessions) / total_sessions, 1),
        "avg_interruptions": round(sum(s["interruptions"] for s in sessions) / total_sessions, 1),
        "effectiveness_score": round(completion_rate * 100 * (1 - sum(s["interruptions"] for s in sessions) / (total_sessions * 5)), 1),
        "insights": {
            "optimal_duration": 25 if completion_rate > 0.8 else 45,
            "needs_environment_optimization": sum(s["interruptions"] for s in sessions) / total_sessions > 2,
            "consistency": "high" if total_sessions / days > 3 else "moderate" if total_sessions / days > 1.5 else "low",
        }
    }


