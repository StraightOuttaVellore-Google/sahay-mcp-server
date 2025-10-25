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
from .firebase_client import initialize_firebase
from .tools.eisenhower import get_all_tasks, save_all_tasks
from .tools.daily_data import get_monthly_data, save_daily_data
from .tools.stats import get_monthly_overview
from .tools.pomodoro import get_pomodoro_analytics, save_pomodoro_session
from .tools.analysis import (
    analyze_wellness_trends, analyze_study_patterns, 
    generate_comprehensive_report, save_analysis_results
)
from .tools.ai_analysis import (
    initialize_google_genai, analyze_wellness_trends_ai, 
    analyze_study_patterns_ai, generate_comprehensive_ai_report,
    save_ai_analysis_results
)
from .tools.wellness_integration import (
    save_wellness_summary, save_study_recommendations,
    get_wellness_history, get_study_recommendations_history,
    create_wellness_insight, sync_wellness_data
)
from .tools.wearable_integration import (
    register_wearable_device, get_user_wearable_devices,
    ingest_wearable_data, get_wearable_data_by_date,
    analyze_wearable_data_ai, get_wearable_insights,
    get_current_recovery_score, generate_mock_wearable_data
)

# Create FastMCP server instance
mcp = FastMCP(name=config.SERVER_NAME)

# Initialize Firebase on startup
initialize_firebase()

# Initialize Google GenAI if available
import os
google_project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID')
if google_project_id:
    initialize_google_genai(google_project_id)

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

# Analysis Tools
@mcp.tool()
async def analyze_wellness_trends(userId: str, months_back: int = 3) -> str:
    """Analyze wellness trends over time"""
    result = await analyze_wellness_trends(userId, months_back)
    return json.dumps(result, indent=2)

@mcp.tool()
async def analyze_study_patterns(userId: str, months_back: int = 2) -> str:
    """Analyze study patterns and productivity"""
    result = await analyze_study_patterns(userId, months_back)
    return json.dumps(result, indent=2)

@mcp.tool()
async def generate_comprehensive_report(userId: str, months_back: int = 3) -> str:
    """Generate comprehensive wellness and study report"""
    result = await generate_comprehensive_report(userId, months_back)
    return json.dumps(result, indent=2)

@mcp.tool()
async def save_analysis_results(userId: str, analysis_data: str) -> str:
    """Save analysis results to Firebase"""
    try:
        data = json.loads(analysis_data)
        result = await save_analysis_results(userId, data)
        return json.dumps(result, indent=2)
    except json.JSONDecodeError as e:
        return json.dumps({
            "success": False,
            "error": f"Invalid JSON format: {str(e)}",
            "message": "Failed to parse analysis data"
        }, indent=2)

# Wellness Integration Tools
@mcp.tool()
async def save_wellness_summary(userId: str, summary_data: str) -> str:
    """Save wellness conversation summary from ADK agents"""
    result = await save_wellness_summary(userId, summary_data)
    return json.dumps(result, indent=2)

@mcp.tool()
async def save_study_recommendations(userId: str, recommendations_data: str) -> str:
    """Save study recommendations from ADK agents as tasks"""
    result = await save_study_recommendations(userId, recommendations_data)
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_wellness_history(userId: str, limit: int = 50) -> str:
    """Get user's wellness conversation history"""
    result = await get_wellness_history(userId, limit)
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_study_recommendations_history(userId: str, limit: int = 20) -> str:
    """Get user's study recommendations history"""
    result = await get_study_recommendations_history(userId, limit)
    return json.dumps(result, indent=2)

@mcp.tool()
async def create_wellness_insight(userId: str, insight_data: str) -> str:
    """Create a wellness insight based on analysis"""
    result = await create_wellness_insight(userId, insight_data)
    return json.dumps(result, indent=2)

@mcp.tool()
async def sync_wellness_data(userId: str) -> str:
    """Sync wellness data between different collections"""
    result = await sync_wellness_data(userId)
    return json.dumps(result, indent=2)

# Enhanced AI Analysis Tools
@mcp.tool()
async def analyze_wellness_trends_ai(userId: str, months_back: int = 3) -> str:
    """Analyze wellness trends with AI-powered insights using Google GenAI"""
    result = await analyze_wellness_trends_ai(userId, months_back)
    return json.dumps(result, indent=2)

@mcp.tool()
async def analyze_study_patterns_ai(userId: str, months_back: int = 2) -> str:
    """Analyze study patterns with AI-powered insights using Google GenAI"""
    result = await analyze_study_patterns_ai(userId, months_back)
    return json.dumps(result, indent=2)

@mcp.tool()
async def generate_comprehensive_ai_report(userId: str, months_back: int = 3) -> str:
    """Generate comprehensive AI-powered wellness and study report with visualizations"""
    result = await generate_comprehensive_ai_report(userId, months_back)
    return json.dumps(result, indent=2)

@mcp.tool()
async def save_ai_analysis_results(userId: str, analysis_data: str) -> str:
    """Save AI analysis results to Firebase with enhanced metadata"""
    try:
        data = json.loads(analysis_data)
        result = await save_ai_analysis_results(userId, data)
        return json.dumps(result, indent=2)
    except json.JSONDecodeError as e:
        return json.dumps({
            "success": False,
            "error": f"Invalid JSON format: {str(e)}",
            "message": "Failed to parse AI analysis data"
        }, indent=2)

# Wearable Integration Tools
@mcp.tool()
async def register_wearable_device(userId: str, deviceData: str) -> str:
    """Register a new wearable device for a user"""
    try:
        data = json.loads(deviceData)
        result = await register_wearable_device(userId, data)
        return json.dumps(result, indent=2)
    except json.JSONDecodeError as e:
        return json.dumps({
            "success": False,
            "error": f"Invalid JSON format: {str(e)}",
            "message": "Failed to parse device data"
        }, indent=2)

@mcp.tool()
async def get_user_wearable_devices(userId: str) -> str:
    """Get all registered wearable devices for a user"""
    result = await get_user_wearable_devices(userId)
    return json.dumps(result, indent=2)

@mcp.tool()
async def ingest_wearable_data(userId: str, data: str) -> str:
    """Ingest wearable data from devices/Health Connect"""
    try:
        data_dict = json.loads(data)
        result = await ingest_wearable_data(userId, data_dict)
        return json.dumps(result, indent=2)
    except json.JSONDecodeError as e:
        return json.dumps({
            "success": False,
            "error": f"Invalid JSON format: {str(e)}",
            "message": "Failed to parse wearable data"
        }, indent=2)

@mcp.tool()
async def get_wearable_data_by_date(userId: str, dateStr: str) -> str:
    """Get wearable data for a specific date"""
    result = await get_wearable_data_by_date(userId, dateStr)
    return json.dumps(result, indent=2)

@mcp.tool()
async def analyze_wearable_data_ai(userId: str, dataDate: str, analysisType: str = "comprehensive") -> str:
    """Analyze wearable data using AI-powered insights"""
    result = await analyze_wearable_data_ai(userId, dataDate, analysisType)
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_wearable_insights(userId: str, dateStr: str) -> str:
    """Get AI-generated insights for a specific date"""
    result = await get_wearable_insights(userId, dateStr)
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_current_recovery_score(userId: str) -> str:
    """Get current recovery score based on latest data"""
    result = await get_current_recovery_score(userId)
    return json.dumps(result, indent=2)

@mcp.tool()
async def generate_mock_wearable_data(userId: str, dateStr: str) -> str:
    """Generate mock wearable data for development/testing"""
    result = await generate_mock_wearable_data(userId, dateStr)
    return json.dumps(result, indent=2)

if __name__ == "__main__":
    mcp.run()
