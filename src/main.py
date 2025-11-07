#!/usr/bin/env python3
"""
Study MCP Server - Fixed for MCP Inspector

This server implements the Model Context Protocol (MCP) for study data management.
It provides tools for interacting with Eisenhower Matrix, daily data tracking,
statistics, and Pomodoro sessions through Firebase Firestore.

@module study-mcp-server
"""

import json
from mcp.server.fastmcp import FastMCP
from .config import config
from .auth import get_auth
try:
    from .firebase_client import initialize_firebase
    FIREBASE_AVAILABLE = True
except:
    FIREBASE_AVAILABLE = False
from .tools.eisenhower import get_all_tasks, save_all_tasks
from .tools.daily_data import get_monthly_data, save_daily_data
from .tools.stats import get_monthly_overview
from .tools.pomodoro import get_pomodoro_analytics, save_pomodoro_session
from .tools.mock_wearable_analysis import (
    generate_mock_wearable_data,
    analyze_study_patterns,
    get_wellness_recommendations_context,
    get_eisenhower_analysis,
    get_pomodoro_effectiveness
)
from .tools.wellness_saving import (
    save_recommended_task_to_db,
    save_wellness_pathway_to_db,
    save_complete_analysis_result,
    save_recommendation_to_stats,
    save_wellness_exercise,
    save_to_firebase_eisenhower
)

# Create FastMCP server instance
mcp = FastMCP(name=config.SERVER_NAME)

# Initialize Firebase on startup (optional, only if available)
if FIREBASE_AVAILABLE:
    try:
        initialize_firebase()
    except:
        print("Firebase initialization skipped - using PostgreSQL only")

@mcp.tool()
async def eisenhower_get_tasks(userId: str) -> str:
    """Get all tasks from Eisenhower Matrix"""
    result = await get_all_tasks(userId)
    return json.dumps(result, indent=2)

@mcp.tool()
async def eisenhower_save_tasks(userId: str, tasks: list) -> str:
    """Save all tasks to Eisenhower Matrix"""
    result = await save_all_tasks(userId, tasks)
    return json.dumps(result, indent=2)

@mcp.tool()
async def daily_data_get_monthly(userId: str, year: int, month: int) -> str:
    """Get daily data for a specific month"""
    result = await get_monthly_data(userId, year, month)
    return json.dumps(result, indent=2)

@mcp.tool()
async def daily_data_save(userId: str, day: int, month: int, year: int, emoji: str, summary: str) -> str:
    """Save daily data entry"""
    data = {
        "day": day,
        "month": month,
        "year": year,
        "emoji": emoji,
        "summary": summary
    }
    result = await save_daily_data(userId, data)
    return json.dumps(result, indent=2)

@mcp.tool()
async def stats_monthly_overview(userId: str, year: int, month: int) -> str:
    """Get comprehensive monthly statistics overview"""
    result = await get_monthly_overview(userId, year, month)
    return json.dumps(result, indent=2)

@mcp.tool()
async def pomodoro_get_analytics(userId: str, year: int, month: int) -> str:
    """Get pomodoro analytics for a specific month"""
    result = await get_pomodoro_analytics(userId, year, month)
    return json.dumps(result, indent=2)

@mcp.tool()
async def pomodoro_save_session(userId: str, work_duration: int, break_duration: int, preset_id: int, completed: bool) -> str:
    """Save a pomodoro session"""
    session_data = {
        "work_duration": work_duration,
        "break_duration": break_duration,
        "preset_id": preset_id,
        "completed": completed
    }
    result = await save_pomodoro_session(userId, session_data)
    return json.dumps(result, indent=2)

# Mock Analysis Tools for Wellness Agents
@mcp.tool()
async def get_mock_wearable_data(userId: str, days: int = 7) -> str:
    """
    Get mock wearable data for wellness analysis.
    Provides sleep, heart rate, activity, and stress metrics.
    """
    result = generate_mock_wearable_data(userId, days)
    return json.dumps(result, indent=2)

@mcp.tool()
async def analyze_user_study_patterns(userId: str, days: int = 14) -> str:
    """
    Analyze study patterns and productivity metrics.
    Provides insights on study duration, focus, and optimal times.
    """
    result = analyze_study_patterns(userId, days)
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_wellness_context(userId: str) -> str:
    """
    Get comprehensive wellness context for personalized recommendations.
    Combines wearable data, study patterns, and provides actionable insights.
    """
    result = get_wellness_recommendations_context(userId)
    return json.dumps(result, indent=2)

@mcp.tool()
async def analyze_task_distribution(userId: str) -> str:
    """
    Analyze Eisenhower matrix task distribution and time management.
    Provides insights on task prioritization and planning effectiveness.
    """
    result = get_eisenhower_analysis(userId)
    return json.dumps(result, indent=2)

@mcp.tool()
async def analyze_pomodoro_effectiveness(userId: str, days: int = 7) -> str:
    """
    Analyze pomodoro technique effectiveness and completion rates.
    Provides insights on optimal session duration and environment.
    """
    result = get_pomodoro_effectiveness(userId, days)
    return json.dumps(result, indent=2)

# ========== WELLNESS ANALYSIS SAVING TOOLS ==========
# These tools are called by agents AFTER safety approval to save results

@mcp.tool()
async def save_task_recommendation(
    userId: str,
    task_title: str,
    task_description: str,
    priority_classification: str,
    suggested_due_days: int = 7,
    session_id: str = None
) -> str:
    """
    Save a recommended task to database for user to review in stats area.
    User can then click to add it to their Eisenhower matrix.
    
    Priority classifications: urgent_important, important_not_urgent, urgent_not_important, neither_urgent_nor_important
    """
    result = await save_recommended_task_to_db(
        userId, task_title, task_description, priority_classification, 
        suggested_due_days, session_id
    )
    return json.dumps(result, indent=2)

@mcp.tool()
async def save_pathway_suggestion(
    userId: str,
    pathway_name: str,
    pathway_type: str,
    description: str,
    duration_days: int = 7,
    session_id: str = None
) -> str:
    """
    Save a wellness pathway suggestion for user to review and register.
    Appears in stats area as a clickable suggestion.
    
    Pathway types: mindfulness, stress_management, study_technique, focus_enhancement, self_care, etc.
    """
    result = await save_wellness_pathway_to_db(
        userId, pathway_name, pathway_type, description, duration_days, session_id
    )
    return json.dumps(result, indent=2)

@mcp.tool()
async def save_insight_recommendation(
    userId: str,
    title: str,
    description: str,
    category: str,
    session_id: str = None
) -> str:
    """
    Save a single recommendation/insight to show in AI stats area.
    These appear as actionable insights for the user.
    
    Categories: stress_relief, time_management, self_care, study_strategy, wellness_tip, etc.
    """
    result = await save_recommendation_to_stats(
        userId, title, description, category, session_id
    )
    return json.dumps(result, indent=2)

@mcp.tool()
async def save_exercise_recommendation(
    userId: str,
    exercise_name: str,
    instructions: str,
    duration: str,
    best_for: str = None,
    session_id: str = None
) -> str:
    """
    Save a wellness exercise recommendation to show in stats area.
    User can view and practice these exercises.
    """
    result = await save_wellness_exercise(
        userId, exercise_name, instructions, duration, best_for, session_id
    )
    return json.dumps(result, indent=2)

@mcp.tool()
async def mcp_login(username: str, password: str) -> str:
    """
    🔐 LOGIN FOR EXTERNAL MCP CLIENTS (Cursor, Claude Code, etc.)
    
    Authenticate with username/email and password to get user_id.
    After login, use the returned user_id for all subsequent tool calls.
    
    **REAL-TIME SYNC:** All data is saved to Firebase Firestore, so changes
    sync instantly across all devices and clients!
    
    Example usage in Cursor/Claude:
    1. Call mcp_login("your_username", "your_password")
    2. Get user_id from response
    3. Use user_id in all other tools (eisenhower_get_tasks, etc.)
    
    Args:
        username: Your username or email address
        password: Your password
    
    Returns:
        JSON string with:
        - success: bool
        - user_id: str (use this for all other tools)
        - username: str
        - email: str
        - session_token: str (optional, for future API key mode)
        - message: str
    """
    auth = get_auth()
    result = auth.login_with_credentials(username, password)
    return json.dumps(result, indent=2)


@mcp.tool()
async def save_complete_wellness_analysis(
    userId: str,
    session_id: str,
    mode: str,
    transcript_summary: dict,
    stats_recommendations: dict,
    safety_approved: bool,
    safety_score: float,
    api_key: str = None
) -> str:
    """
    **BULK SAVE TOOL** - Save complete analysis result after safety approval.
    
    This is the MAIN SAVE tool that agents should call after passing safety review.
    It saves everything at once: summary, recommendations, tasks, pathways, exercises, resources.
    
    Use this tool ONLY after receiving "SAFETY_APPROVED" from safety reviewer.
    
    Authentication:
    - If called from ADK agents (backend context): userId is authenticated, no api_key needed
    - If called from Claude/external LLM: provide api_key for authentication
    
    Args:
        userId: User ID to save data for
        session_id: Voice journal session ID
        mode: 'study' or 'wellness'
        transcript_summary: Summary dict with emotions, focus areas, etc.
        stats_recommendations: Recommendations dict with tasks, pathways, etc.
        safety_approved: Safety approval status
        safety_score: Safety score (0.0-1.0)
        api_key: Optional API key for external LLM authentication
    
    Returns:
        JSON string with save result
    """
    # Validate authentication
    auth = get_auth()
    if not auth.validate_user_access(userId, api_key):
        return json.dumps({
            "success": False,
            "error": "Authentication failed - invalid user_id or api_key",
            "hint": "For external LLM use, provide valid api_key. For backend use, ensure user_id is authenticated."
        }, indent=2)
    
    # Proceed with save
    result = await save_complete_analysis_result(
        userId, session_id, mode, transcript_summary,
        stats_recommendations, safety_approved, safety_score
    )
    return json.dumps(result, indent=2)

if __name__ == "__main__":
    mcp.run()
