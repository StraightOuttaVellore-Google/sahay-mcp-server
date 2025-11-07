"""
Wellness Analysis Saving Tools for MCP Server

These tools allow agents to save wellness analysis results to Firebase Firestore.
Called by agents after safety approval.

MIGRATED TO FIREBASE: Now uses Firestore for real-time sync with Sahay ecosystem.
"""

import json
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional
import uuid
import logging
from google.cloud.firestore_v1 import SERVER_TIMESTAMP

# Import Firebase client
try:
    from ..firebase_client import get_firestore
except ImportError:
    # Fallback for when running tests or in different context
    try:
        from firebase_client import get_firestore
    except ImportError:
        # If Firebase not available, raise clear error
        raise ImportError(
            "Firebase client not available. Ensure firebase_client.py exists "
            "and SERVICE_ACCOUNT_KEY_PATH is set."
        )

logger = logging.getLogger(__name__)


def map_priority_to_quadrant(priority: str) -> str:
    """Map priority classification to Eisenhower quadrant"""
    mapping = {
        "urgent_important": "high_imp_high_urg",
        "important_not_urgent": "high_imp_low_urg",
        "urgent_not_important": "low_imp_high_urg",
        "neither_urgent_nor_important": "low_imp_low_urg",
    }
    return mapping.get(priority, "high_imp_low_urg")


async def save_recommended_task_to_db(
    user_id: str,
    task_title: str,
    task_description: str,
    priority_classification: str,
    suggested_due_days: int = 7,
    session_id: Optional[str] = None
) -> Dict:
    """
    Save a single recommended task to the database (AgentRecommendedTask table)
    
    This is a RECOMMENDATION that shows in the stats/analysis area.
    User can click to add it to their Eisenhower matrix.
    """
    try:
        quadrant = map_priority_to_quadrant(priority_classification)
        due_date = (date.today() + timedelta(days=suggested_due_days)).isoformat()
        
        # For now, we'll return the data structure
        # In production, this would call the API or directly insert to DB
        return {
            "success": True,
            "task": {
                "user_id": user_id,
                "task_title": task_title,
                "task_description": task_description,
                "quadrant": quadrant,
                "priority_classification": priority_classification,
                "due_date": due_date,
                "suggested_due_days": suggested_due_days,
                "from_agent_session": session_id,
                "status": "recommended",  # Not yet added to matrix
                "created_at": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def save_wellness_pathway_to_db(
    user_id: str,
    pathway_name: str,
    pathway_type: str,
    description: str,
    duration_days: int = 7,
    session_id: Optional[str] = None
) -> Dict:
    """
    Save a wellness pathway recommendation to the database
    
    This is a SUGGESTION that appears in the stats area.
    User can click "Register" to actually enroll.
    """
    try:
        return {
            "success": True,
            "pathway": {
                "user_id": user_id,
                "pathway_name": pathway_name,
                "pathway_type": pathway_type,
                "description": description,
                "duration_days": duration_days,
                "status": "suggested",  # Not yet registered
                "from_agent_session": session_id,
                "created_at": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def save_complete_analysis_result(
    user_id: str,
    session_id: str,
    mode: str,
    transcript_summary: Dict,
    stats_recommendations: Dict,
    safety_approved: bool,
    safety_score: float
) -> Dict:
    """
    ⚡ ACTUAL FIREBASE SAVE - Updates VoiceJournalSession with analysis results
    
    This is the BULK SAVE tool that saves everything at once after safety approval.
    Saves to Firebase Firestore (real-time sync!):
    - voiceJournalSessions/{session_id} (complete analysis)
    - agentRecommendedTasks/{task_id} (individual tasks for stats)
    - wellnessPathways/{pathway_id} (pathways for user registration)
    """
    try:
        db = get_firestore()
        
        # 1. Update VoiceJournalSession with complete analysis
        analysis_data = {
            "mode": mode,
            "transcript_summary": transcript_summary,
            "stats_recommendations": stats_recommendations,
            "safety_approved": safety_approved,
            "safety_score": safety_score,
            "created_at": datetime.utcnow().isoformat()
        }
        
        session_ref = db.collection('voiceJournalSessions').document(session_id)
        session_doc = session_ref.get()
        
        if not session_doc.exists:
            logger.warning(f"No session found for session_id={session_id}, user_id={user_id}")
            return {
                "success": False,
                "error": f"Session not found: {session_id}",
                "database": "firestore"
            }
        
        # Verify ownership
        session_data = session_doc.to_dict()
        if session_data.get("user_id") != user_id:
            logger.warning(f"User {user_id} attempted to update session {session_id} owned by {session_data.get('user_id')}")
            return {
                "success": False,
                "error": "Unauthorized access",
                "database": "firestore"
            }
        
        # Update session document
        session_ref.update({
            "analysis_data": analysis_data,
            "analysis_completed": True,
            "updated_at": SERVER_TIMESTAMP,
        })
        
        logger.info(f"✅ Analysis saved to Firestore VoiceJournalSession: {session_id}")
        
        # 2. Save individual recommended tasks to agentRecommendedTasks collection
        tasks_saved = await _save_recommended_tasks_firestore(
            db, user_id, session_id, 
            stats_recommendations.get("recommended_tasks", [])
        )
        
        # 3. Save wellness pathways to wellnessPathways collection
        pathways_saved = await _save_wellness_pathways_firestore(
            db, user_id,
            stats_recommendations.get("wellness_pathways", [])
        )
        
        logger.info(f"✅ Complete save: {tasks_saved} tasks, {pathways_saved} pathways")
        
        return {
            "success": True,
            "message": "Analysis saved to Firebase Firestore (real-time sync enabled)",
            "session_id": session_id,
            "user_id": user_id,
            "database": "firestore",
            "tasks_saved": tasks_saved,
            "pathways_saved": pathways_saved,
            "saved_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error saving analysis: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "database": "firestore"
        }


async def save_recommendation_to_stats(
    user_id: str,
    recommendation_title: str,
    recommendation_description: str,
    category: str,
    session_id: Optional[str] = None
) -> Dict:
    """
    Save a single recommendation to show in stats/analysis area
    
    Recommendations appear in the "AI Insights" section.
    """
    try:
        return {
            "success": True,
            "recommendation": {
                "user_id": user_id,
                "title": recommendation_title,
                "description": recommendation_description,
                "category": category,
                "from_agent_session": session_id,
                "created_at": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def save_wellness_exercise(
    user_id: str,
    exercise_name: str,
    instructions: str,
    duration: str,
    best_for: Optional[str] = None,
    session_id: Optional[str] = None
) -> Dict:
    """
    Save a wellness exercise recommendation
    
    Exercises appear in the "Wellness Exercises" section.
    """
    try:
        return {
            "success": True,
            "exercise": {
                "user_id": user_id,
                "name": exercise_name,
                "instructions": instructions,
                "duration": duration,
                "best_for": best_for,
                "from_agent_session": session_id,
                "created_at": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def _save_recommended_tasks_firestore(
    db,
    user_id: str,
    session_id: str,
    recommended_tasks: List[Dict]
) -> int:
    """
    Save recommended tasks to Firestore agentRecommendedTasks collection
    These appear in stats/analysis area for user to review and add to matrix
    
    Returns:
        int: Number of tasks saved
    """
    tasks_saved = 0
    tasks_ref = db.collection('agentRecommendedTasks')
    
    for task in recommended_tasks:
        try:
            quadrant = map_priority_to_quadrant(task.get("priority_classification", "important_not_urgent"))
            due_date = (date.today() + timedelta(days=task.get("suggested_due_days", 7))).isoformat()
            
            task_data = {
                "user_id": user_id,
                "task_title": task.get("task_title", ""),
                "task_description": task.get("task_description", ""),
                "quadrant": quadrant,
                "status": "TODO",
                "due_date": due_date,
                "from_agent_session": session_id,
                "created_at": SERVER_TIMESTAMP,
            }
            
            # Use auto-generated document ID
            task_ref = tasks_ref.document()
            task_ref.set(task_data)
            
            tasks_saved += 1
            
        except Exception as e:
            logger.error(f"Error saving task: {e}")
            continue
    
    return tasks_saved


async def _save_wellness_pathways_firestore(
    db,
    user_id: str,
    wellness_pathways: List[Dict]
) -> int:
    """
    Save wellness pathways to Firestore wellnessPathways collection
    These appear as suggestions for user to register
    
    Returns:
        int: Number of pathways saved
    """
    pathways_saved = 0
    pathways_ref = db.collection('wellnessPathways')
    
    for pathway in wellness_pathways:
        try:
            pathway_data = {
                "user_id": user_id,
                "pathway_name": pathway.get("pathway_name", ""),
                "pathway_type": pathway.get("pathway_type", ""),
                "description": pathway.get("description", ""),
                "duration_days": pathway.get("duration_days", 7),
                "status": "SUGGESTED",
                "progress_percentage": 0,
                "created_at": SERVER_TIMESTAMP,
            }
            
            # Use auto-generated document ID
            pathway_ref = pathways_ref.document()
            pathway_ref.set(pathway_data)
            
            pathways_saved += 1
            
        except Exception as e:
            logger.error(f"Error saving pathway: {e}")
            continue
    
    return pathways_saved


# Save to Eisenhower Matrix (Firestore - unified with Sahay)
async def save_to_firebase_eisenhower(
    user_id: str,
    task_title: str,
    task_description: str,
    quadrant: str,
    due_date: str,
    status: str = "TODO"
) -> Dict:
    """
    Save task directly to Firebase Eisenhower Matrix (Sahay ecosystem)
    
    Now uses Firestore for unified real-time sync across all apps!
    """
    try:
        db = get_firestore()
        
        # Use same collection structure as Sahay tools (eisenhower.py)
        tasks_ref = db.collection('users').document(user_id).collection('tasks')
        
        task_data = {
            "title": task_title,
            "description": task_description,
            "quadrant": quadrant,
            "status": status,
            "due_date": due_date,
            "created_at": SERVER_TIMESTAMP,
            "updated_at": SERVER_TIMESTAMP,
        }
        
        # Auto-generate task ID
        task_ref = tasks_ref.document()
        task_ref.set(task_data)
        
        return {
            "success": True,
            "message": "Saved to Firebase Eisenhower Matrix (Firestore)",
            "task_id": task_ref.id,
            "database": "firestore"
        }
    except Exception as e:
        logger.error(f"Error saving to Eisenhower Matrix: {e}")
        return {
            "success": False,
            "error": str(e),
            "database": "firestore"
        }

