"""
Wellness Data Integration Tools for Sahay MCP Server

This module provides tools for integrating wellness data from ADK agents
with the study management system, creating a unified data ecosystem.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, date
import json
from ..firebase_client import get_firestore
from .daily_data import save_daily_data, StudyEmoji
from .eisenhower import save_all_tasks, TaskQuadrant, TaskStatus


async def save_wellness_summary(user_id: str, summary_data: str) -> Dict[str, Any]:
    """
    Save wellness conversation summary from ADK agents
    
    Args:
        user_id: User identifier
        summary_data: JSON string containing wellness summary data
    
    Returns:
        Dictionary with success status and details
    """
    try:
        data = json.loads(summary_data)
        
        # Extract key information
        summary = data.get('summary', '')
        emotions = data.get('emotions', [])
        focus_areas = data.get('focus_areas', [])
        tags = data.get('tags', [])
        stress_level = data.get('stress_level', 'moderate')
        
        # Map stress level to emoji
        stress_to_emoji = {
            'low': StudyEmoji.RELAXED,
            'moderate': StudyEmoji.BALANCED,
            'high': StudyEmoji.OVERWHELMED
        }
        
        emoji = stress_to_emoji.get(stress_level.lower(), StudyEmoji.BALANCED)
        
        # Save as daily entry
        today = date.today()
        daily_entry = {
            "day": today.day,
            "month": today.month,
            "year": today.year,
            "emoji": emoji.value,
            "summary": summary,
            "wellness_data": {
                "emotions": emotions,
                "focus_areas": focus_areas,
                "tags": tags,
                "stress_level": stress_level,
                "source": "adk_wellness_agent"
            }
        }
        
        result = await save_daily_data(user_id, daily_entry)
        
        # Also save to wellness summaries collection
        db = get_firestore()
        wellness_ref = db.collection('users').document(user_id).collection('wellness_summaries')
        
        wellness_doc = {
            "summary": summary,
            "emotions": emotions,
            "focus_areas": focus_areas,
            "tags": tags,
            "stress_level": stress_level,
            "timestamp": datetime.now().isoformat(),
            "source": "adk_wellness_agent"
        }
        
        wellness_ref.add(wellness_doc)
        
        return {
            "success": True,
            "message": "Wellness summary saved successfully",
            "daily_entry_saved": result.get('success', False),
            "wellness_summary_saved": True
        }
        
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"Invalid JSON format: {str(e)}",
            "message": "Failed to parse wellness summary data"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to save wellness summary"
        }


async def save_study_recommendations(user_id: str, recommendations_data: str) -> Dict[str, Any]:
    """
    Save study recommendations from ADK study agents as tasks
    
    Args:
        user_id: User identifier
        recommendations_data: JSON string containing study recommendations
    
    Returns:
        Dictionary with success status and details
    """
    try:
        data = json.loads(recommendations_data)
        
        # Extract recommended tasks
        recommended_tasks = data.get('recommended_tasks', [])
        
        if not recommended_tasks:
            return {
                "success": True,
                "message": "No tasks to save",
                "tasks_saved": 0
            }
        
        # Convert recommendations to tasks
        tasks = []
        for task_data in recommended_tasks:
            # Map priority classification to quadrant
            priority_map = {
                'urgent_important': TaskQuadrant.HUHI,
                'important_not_urgent': TaskQuadrant.HULI,
                'urgent_not_important': TaskQuadrant.LUHI,
                'neither_urgent_nor_important': TaskQuadrant.LULI
            }
            
            priority = task_data.get('priority_classification', 'important_not_urgent')
            quadrant = priority_map.get(priority, TaskQuadrant.HULI)
            
            task = {
                "title": task_data.get('task_title', ''),
                "description": task_data.get('task_description', ''),
                "quadrant": quadrant.value,
                "status": TaskStatus.CREATED.value,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "source": "adk_study_agent",
                "priority_classification": priority
            }
            tasks.append(task)
        
        # Save tasks
        result = await save_all_tasks(user_id, tasks)
        
        # Also save recommendations to separate collection
        db = get_firestore()
        recommendations_ref = db.collection('users').document(user_id).collection('study_recommendations')
        
        recommendations_doc = {
            "recommendations": data.get('recommendations', []),
            "wellness_exercises": data.get('wellness_exercises', []),
            "resources": data.get('resources', []),
            "study_focus_tips": data.get('study_focus_tips', []),
            "tone": data.get('tone', 'supportive'),
            "timestamp": datetime.now().isoformat(),
            "source": "adk_study_agent"
        }
        
        recommendations_ref.add(recommendations_doc)
        
        return {
            "success": True,
            "message": "Study recommendations saved successfully",
            "tasks_saved": result.get('tasks_count', 0),
            "recommendations_saved": True
        }
        
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"Invalid JSON format: {str(e)}",
            "message": "Failed to parse recommendations data"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to save study recommendations"
        }


async def get_wellness_history(user_id: str, limit: int = 50) -> Dict[str, Any]:
    """
    Get user's wellness conversation history
    
    Args:
        user_id: User identifier
        limit: Maximum number of entries to retrieve
    
    Returns:
        Dictionary containing wellness history
    """
    try:
        db = get_firestore()
        wellness_ref = db.collection('users').document(user_id).collection('wellness_summaries')
        
        # Query recent entries
        query = wellness_ref.order_by('timestamp', direction='DESCENDING').limit(limit)
        docs = query.stream()
        
        wellness_history = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            wellness_history.append(data)
        
        return {
            "success": True,
            "wellness_history": wellness_history,
            "count": len(wellness_history)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve wellness history"
        }


async def get_study_recommendations_history(user_id: str, limit: int = 20) -> Dict[str, Any]:
    """
    Get user's study recommendations history
    
    Args:
        user_id: User identifier
        limit: Maximum number of entries to retrieve
    
    Returns:
        Dictionary containing study recommendations history
    """
    try:
        db = get_firestore()
        recommendations_ref = db.collection('users').document(user_id).collection('study_recommendations')
        
        # Query recent entries
        query = recommendations_ref.order_by('timestamp', direction='DESCENDING').limit(limit)
        docs = query.stream()
        
        recommendations_history = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            recommendations_history.append(data)
        
        return {
            "success": True,
            "recommendations_history": recommendations_history,
            "count": len(recommendations_history)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve study recommendations history"
        }


async def create_wellness_insight(user_id: str, insight_data: str) -> Dict[str, Any]:
    """
    Create a wellness insight based on analysis
    
    Args:
        user_id: User identifier
        insight_data: JSON string containing insight data
    
    Returns:
        Dictionary with success status and details
    """
    try:
        data = json.loads(insight_data)
        
        # Create insight document
        insight_doc = {
            "insight_type": data.get('insight_type', 'general'),
            "title": data.get('title', ''),
            "description": data.get('description', ''),
            "confidence": data.get('confidence', 0.5),
            "recommendations": data.get('recommendations', []),
            "data_points": data.get('data_points', {}),
            "generated_at": datetime.now().isoformat(),
            "source": "analysis_tool"
        }
        
        # Save to Firebase
        db = get_firestore()
        insights_ref = db.collection('users').document(user_id).collection('wellness_insights')
        insights_ref.add(insight_doc)
        
        return {
            "success": True,
            "message": "Wellness insight created successfully",
            "insight": insight_doc
        }
        
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"Invalid JSON format: {str(e)}",
            "message": "Failed to parse insight data"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to create wellness insight"
        }


async def sync_wellness_data(user_id: str) -> Dict[str, Any]:
    """
    Sync wellness data between different collections
    
    Args:
        user_id: User identifier
    
    Returns:
        Dictionary with sync status and details
    """
    try:
        db = get_firestore()
        
        # Get wellness summaries
        wellness_ref = db.collection('users').document(user_id).collection('wellness_summaries')
        wellness_docs = wellness_ref.stream()
        
        # Get daily data
        daily_ref = db.collection('users').document(user_id).collection('dailyData')
        daily_docs = daily_ref.stream()
        
        # Count documents
        wellness_count = len(list(wellness_docs))
        daily_count = len(list(daily_docs))
        
        return {
            "success": True,
            "message": "Wellness data sync completed",
            "wellness_summaries": wellness_count,
            "daily_entries": daily_count,
            "sync_timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to sync wellness data"
        }
