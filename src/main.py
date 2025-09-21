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

# Create FastMCP server instance
mcp = FastMCP(name=config.SERVER_NAME)

# Initialize Firebase on startup
initialize_firebase()

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

if __name__ == "__main__":
    mcp.run()
