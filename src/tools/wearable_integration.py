"""
Wearable Integration Tools for MCP Server

This module provides comprehensive wearable data integration tools including:
- Device management and registration
- Data ingestion from IoT devices
- Google Cloud IoT Core integration
- AI-powered wearable insights
- Mock data generation for development
"""

import asyncio
import json
import random
import uuid
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional
import os

# Firebase imports
from firebase_admin import firestore
from .firebase_client import get_firebase_client

# Google Cloud IoT Core imports
try:
    from google.cloud import iot_v1
    from google.cloud import pubsub_v1
    from google.oauth2 import service_account
    IOT_CORE_AVAILABLE = True
except ImportError:
    IOT_CORE_AVAILABLE = False
    print("Warning: Google Cloud IoT Core not available. Install google-cloud-iot")

# AI Analysis imports
try:
    from .ai_analysis import initialize_google_genai, _get_gemini_model
    AI_ANALYSIS_AVAILABLE = True
except ImportError:
    AI_ANALYSIS_AVAILABLE = False


async def register_wearable_device(user_id: str, device_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Register a new wearable device for a user
    
    Args:
        user_id: User identifier
        device_data: Device information including type, name, device_id
    
    Returns:
        Dict with registration status and device info
    """
    try:
        db = get_firebase_client()
        if not db:
            return {"success": False, "error": "Firebase not available"}
        
        device_id = device_data.get("device_id", str(uuid.uuid4()))
        
        # Check if device already exists
        devices_ref = db.collection("users").document(user_id).collection("wearable_devices")
        existing_devices = devices_ref.where("device_id", "==", device_id).get()
        
        if existing_devices:
            return {
                "success": False,
                "error": "Device already registered",
                "device_id": device_id
            }
        
        # Create device document
        device_doc = {
            "device_id": device_id,
            "device_type": device_data.get("device_type", "smart_watch"),
            "device_name": device_data.get("device_name", "Unknown Device"),
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
            "last_sync": None,
            "iot_registry_id": None,
            "iot_device_id": None
        }
        
        # Register with Google Cloud IoT Core if available
        if IOT_CORE_AVAILABLE and os.getenv("GOOGLE_CLOUD_PROJECT_ID"):
            try:
                iot_registry_id = await register_device_with_iot_core(
                    device_id, 
                    device_data.get("device_type", "smart_watch")
                )
                device_doc["iot_registry_id"] = iot_registry_id
                device_doc["iot_device_id"] = device_id
            except Exception as e:
                print(f"Warning: Failed to register with IoT Core: {e}")
        
        # Save to Firebase
        doc_ref = devices_ref.document()
        doc_ref.set(device_doc)
        
        return {
            "success": True,
            "device_id": doc_ref.id,
            "device_name": device_doc["device_name"],
            "device_type": device_doc["device_type"],
            "iot_registered": device_doc["iot_registry_id"] is not None,
            "status": "registered"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to register device: {str(e)}"
        }


async def get_user_wearable_devices(user_id: str) -> Dict[str, Any]:
    """
    Get all registered wearable devices for a user
    
    Args:
        user_id: User identifier
    
    Returns:
        Dict with list of devices
    """
    try:
        db = get_firebase_client()
        if not db:
            return {"success": False, "error": "Firebase not available"}
        
        devices_ref = db.collection("users").document(user_id).collection("wearable_devices")
        devices = devices_ref.where("is_active", "==", True).get()
        
        device_list = []
        for device in devices:
            device_data = device.to_dict()
            device_list.append({
                "device_id": device.id,
                "device_name": device_data.get("device_name", "Unknown"),
                "device_type": device_data.get("device_type", "unknown"),
                "is_active": device_data.get("is_active", True),
                "last_sync": device_data.get("last_sync"),
                "created_at": device_data.get("created_at"),
                "iot_registered": device_data.get("iot_registry_id") is not None
            })
        
        return {
            "success": True,
            "devices": device_list,
            "count": len(device_list)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get devices: {str(e)}"
        }


async def ingest_wearable_data(user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ingest wearable data from devices/Health Connect
    
    Args:
        user_id: User identifier
        data: Wearable data including device_id, data_date, and metrics
    
    Returns:
        Dict with ingestion status
    """
    try:
        db = get_firebase_client()
        if not db:
            return {"success": False, "error": "Firebase not available"}
        
        device_id = data.get("device_id")
        data_date = data.get("data_date", datetime.now().strftime("%Y-%m-%d"))
        
        # Find the device
        devices_ref = db.collection("users").document(user_id).collection("wearable_devices")
        device_query = devices_ref.where("device_id", "==", device_id).get()
        
        if not device_query:
            return {
                "success": False,
                "error": "Device not found"
            }
        
        device_doc = device_query[0]
        
        # Check if data already exists for this date
        data_ref = db.collection("users").document(user_id).collection("wearable_data")
        existing_data = data_ref.where("data_date", "==", data_date).where("device_id", "==", device_id).get()
        
        if existing_data:
            # Update existing data
            doc_ref = existing_data[0].reference
            doc_ref.update({
                **data,
                "updated_at": datetime.utcnow().isoformat()
            })
            return {
                "success": True,
                "data_id": doc_ref.id,
                "status": "updated"
            }
        
        # Create new data entry
        wearable_data = {
            "device_id": device_id,
            "data_date": data_date,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            **data
        }
        
        doc_ref = data_ref.document()
        doc_ref.set(wearable_data)
        
        # Update device last sync
        device_doc.reference.update({
            "last_sync": datetime.utcnow().isoformat()
        })
        
        return {
            "success": True,
            "data_id": doc_ref.id,
            "data_date": data_date,
            "status": "created"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to ingest data: {str(e)}"
        }


async def get_wearable_data_by_date(user_id: str, date_str: str) -> Dict[str, Any]:
    """
    Get wearable data for a specific date
    
    Args:
        user_id: User identifier
        date_str: Date in YYYY-MM-DD format
    
    Returns:
        Dict with wearable data
    """
    try:
        db = get_firebase_client()
        if not db:
            return {"success": False, "error": "Firebase not available"}
        
        data_ref = db.collection("users").document(user_id).collection("wearable_data")
        data_query = data_ref.where("data_date", "==", date_str).get()
        
        if not data_query:
            return {
                "success": False,
                "error": "No wearable data found for this date"
            }
        
        data_doc = data_query[0].to_dict()
        
        return {
            "success": True,
            "data_id": data_query[0].id,
            "data_date": data_doc["data_date"],
            "sleep": {
                "duration_hours": data_doc.get("sleep_duration_hours"),
                "efficiency": data_doc.get("sleep_efficiency"),
                "deep_sleep_hours": data_doc.get("deep_sleep_hours"),
                "rem_sleep_hours": data_doc.get("rem_sleep_hours"),
                "light_sleep_hours": data_doc.get("light_sleep_hours"),
                "sleep_score": data_doc.get("sleep_score"),
                "bedtime": data_doc.get("bedtime"),
                "wake_time": data_doc.get("wake_time"),
            },
            "heart_rate": {
                "avg_heart_rate": data_doc.get("avg_heart_rate"),
                "resting_heart_rate": data_doc.get("resting_heart_rate"),
                "max_heart_rate": data_doc.get("max_heart_rate"),
                "hrv_rmssd": data_doc.get("hrv_rmssd"),
                "hrv_z_score": data_doc.get("hrv_z_score"),
            },
            "activity": {
                "steps": data_doc.get("steps"),
                "calories_burned": data_doc.get("calories_burned"),
                "active_minutes": data_doc.get("active_minutes"),
                "distance_km": data_doc.get("distance_km"),
                "floors_climbed": data_doc.get("floors_climbed"),
            },
            "stress_recovery": {
                "stress_score": data_doc.get("stress_score"),
                "stress_events": data_doc.get("stress_events"),
                "recovery_score": data_doc.get("recovery_score"),
                "energy_level": data_doc.get("energy_level"),
            },
            "environment": {
                "ambient_temperature": data_doc.get("ambient_temperature"),
                "humidity": data_doc.get("humidity"),
                "noise_level": data_doc.get("noise_level"),
                "light_level": data_doc.get("light_level"),
            },
            "additional": {
                "breathing_rate": data_doc.get("breathing_rate"),
                "blood_oxygen": data_doc.get("blood_oxygen"),
            },
            "created_at": data_doc["created_at"]
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get wearable data: {str(e)}"
        }


async def analyze_wearable_data_ai(user_id: str, data_date: str, analysis_type: str = "comprehensive") -> Dict[str, Any]:
    """
    Analyze wearable data using AI-powered insights
    
    Args:
        user_id: User identifier
        data_date: Date in YYYY-MM-DD format
        analysis_type: Type of analysis (comprehensive, stress_focus, sleep_recovery)
    
    Returns:
        Dict with AI analysis results
    """
    try:
        # Get wearable data
        data_result = await get_wearable_data_by_date(user_id, data_date)
        if not data_result.get("success"):
            return data_result
        
        wearable_data = data_result
        
        if AI_ANALYSIS_AVAILABLE:
            # Use Google GenAI for analysis
            model = _get_gemini_model()
            
            analysis_prompt = f"""
            Analyze the following wearable data for {analysis_type} analysis:
            
            Sleep Data:
            - Duration: {wearable_data['sleep']['duration_hours']} hours
            - Efficiency: {wearable_data['sleep']['efficiency']}
            - Deep Sleep: {wearable_data['sleep']['deep_sleep_hours']} hours
            - REM Sleep: {wearable_data['sleep']['rem_sleep_hours']} hours
            - Sleep Score: {wearable_data['sleep']['sleep_score']}/100
            
            Heart Rate Data:
            - Average HR: {wearable_data['heart_rate']['avg_heart_rate']} BPM
            - Resting HR: {wearable_data['heart_rate']['resting_heart_rate']} BPM
            - HRV RMSSD: {wearable_data['heart_rate']['hrv_rmssd']} ms
            
            Activity Data:
            - Steps: {wearable_data['activity']['steps']}
            - Active Minutes: {wearable_data['activity']['active_minutes']}
            - Calories: {wearable_data['activity']['calories_burned']}
            
            Stress & Recovery:
            - Stress Score: {wearable_data['stress_recovery']['stress_score']}
            - Recovery Score: {wearable_data['stress_recovery']['recovery_score']}
            - Energy Level: {wearable_data['stress_recovery']['energy_level']}
            
            Environment:
            - Temperature: {wearable_data['environment']['ambient_temperature']}°C
            - Humidity: {wearable_data['environment']['humidity']}%
            - Noise Level: {wearable_data['environment']['noise_level']} dB
            - Light Level: {wearable_data['environment']['light_level']}
            
            Provide a comprehensive analysis including:
            1. Overall recovery score (1-100)
            2. Sleep debt assessment
            3. Stress level analysis
            4. Focus recommendation
            5. Detailed insights for each category
            6. Environmental recommendations
            7. Wellness activity suggestions
            8. Confidence score for the analysis
            
            Return as JSON format.
            """
            
            response = model.generate_content(analysis_prompt)
            ai_insights = json.loads(response.text)
        else:
            # Fallback to mock analysis
            ai_insights = generate_mock_ai_insights(wearable_data)
        
        # Calculate recovery score
        recovery_score = calculate_recovery_score(wearable_data)
        
        # Store insights
        db = get_firebase_client()
        if db:
            insights_ref = db.collection("users").document(user_id).collection("wearable_insights")
            insight_doc = {
                "insight_date": data_date,
                "analysis_type": analysis_type,
                "overall_recovery_score": recovery_score,
                "sleep_debt_hours": ai_insights.get("sleep_debt", 0),
                "stress_level": ai_insights.get("stress_level", "medium"),
                "focus_recommendation": ai_insights.get("focus_recommendation", "medium"),
                "ai_insights": ai_insights,
                "confidence_score": ai_insights.get("confidence", 0.8),
                "recommended_focus_duration": ai_insights.get("focus_duration", 25),
                "recommended_break_duration": ai_insights.get("break_duration", 5),
                "recommended_activities": ai_insights.get("activities", {}),
                "created_at": datetime.utcnow().isoformat()
            }
            
            doc_ref = insights_ref.document()
            doc_ref.set(insight_doc)
        
        return {
            "success": True,
            "analysis_type": analysis_type,
            "recovery_score": recovery_score,
            "insights": ai_insights,
            "confidence": ai_insights.get("confidence", 0.8),
            "recommendations": {
                "focus_session_length": ai_insights.get("focus_duration", 25),
                "break_duration": ai_insights.get("break_duration", 5),
                "activities": ai_insights.get("activities", {}),
                "environmental_suggestions": ai_insights.get("environmental", {}),
                "wellness_activities": ai_insights.get("wellness", {})
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to analyze wearable data: {str(e)}"
        }


async def get_wearable_insights(user_id: str, date_str: str) -> Dict[str, Any]:
    """
    Get AI-generated insights for a specific date
    
    Args:
        user_id: User identifier
        date_str: Date in YYYY-MM-DD format
    
    Returns:
        Dict with insights data
    """
    try:
        db = get_firebase_client()
        if not db:
            return {"success": False, "error": "Firebase not available"}
        
        insights_ref = db.collection("users").document(user_id).collection("wearable_insights")
        insights_query = insights_ref.where("insight_date", "==", date_str).get()
        
        if not insights_query:
            return {
                "success": False,
                "error": "No insights found for this date"
            }
        
        insight_doc = insights_query[0].to_dict()
        
        return {
            "success": True,
            "insight_id": insights_query[0].id,
            "insight_date": insight_doc["insight_date"],
            "analysis_type": insight_doc["analysis_type"],
            "overall_recovery_score": insight_doc["overall_recovery_score"],
            "sleep_debt_hours": insight_doc["sleep_debt_hours"],
            "stress_level": insight_doc["stress_level"],
            "focus_recommendation": insight_doc["focus_recommendation"],
            "ai_insights": insight_doc["ai_insights"],
            "confidence_score": insight_doc["confidence_score"],
            "recommendations": {
                "focus_duration": insight_doc["recommended_focus_duration"],
                "break_duration": insight_doc["recommended_break_duration"],
                "activities": insight_doc["recommended_activities"],
            },
            "created_at": insight_doc["created_at"]
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get insights: {str(e)}"
        }


async def get_current_recovery_score(user_id: str) -> Dict[str, Any]:
    """
    Get current recovery score based on latest data
    
    Args:
        user_id: User identifier
    
    Returns:
        Dict with recovery score and recommendation
    """
    try:
        db = get_firebase_client()
        if not db:
            return {"success": False, "error": "Firebase not available"}
        
        # Get latest wearable data
        data_ref = db.collection("users").document(user_id).collection("wearable_data")
        latest_data = data_ref.order_by("data_date", direction=firestore.Query.DESCENDING).limit(1).get()
        
        if not latest_data:
            return {
                "success": False,
                "error": "No wearable data available"
            }
        
        data_doc = latest_data[0].to_dict()
        
        # Calculate recovery score
        recovery_score = calculate_recovery_score_from_dict(data_doc)
        
        return {
            "success": True,
            "recovery_score": recovery_score,
            "data_date": data_doc["data_date"],
            "factors": {
                "sleep_quality": data_doc.get("sleep_score", 0),
                "hrv_score": data_doc.get("hrv_rmssd", 0),
                "stress_level": data_doc.get("stress_score", 0),
                "activity_level": data_doc.get("active_minutes", 0),
            },
            "recommendation": get_recovery_recommendation(recovery_score)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get recovery score: {str(e)}"
        }


async def generate_mock_wearable_data(user_id: str, date_str: str) -> Dict[str, Any]:
    """
    Generate mock wearable data for development/testing
    
    Args:
        user_id: User identifier
        date_str: Date in YYYY-MM-DD format
    
    Returns:
        Dict with mock data creation status
    """
    try:
        # Create mock device if none exists
        devices_result = await get_user_wearable_devices(user_id)
        if not devices_result.get("success") or not devices_result.get("devices"):
            await register_wearable_device(user_id, {
                "device_type": "smart_watch",
                "device_name": "Mock Apple Watch Series 9",
                "device_id": "mock_device_001"
            })
        
        # Generate realistic mock data
        mock_data = {
            "device_id": "mock_device_001",
            "data_date": date_str,
            
            # Sleep Data
            "sleep_duration_hours": round(random.uniform(6.5, 8.5), 1),
            "sleep_efficiency": round(random.uniform(0.75, 0.95), 2),
            "deep_sleep_hours": round(random.uniform(1.5, 2.5), 1),
            "rem_sleep_hours": round(random.uniform(1.0, 2.0), 1),
            "light_sleep_hours": round(random.uniform(3.0, 5.0), 1),
            "sleep_score": random.randint(70, 95),
            
            # Heart Rate Data
            "avg_heart_rate": random.randint(65, 85),
            "resting_heart_rate": random.randint(55, 75),
            "max_heart_rate": random.randint(180, 200),
            "hrv_rmssd": round(random.uniform(25, 45), 1),
            "hrv_z_score": round(random.uniform(-1.5, 1.5), 2),
            
            # Activity Data
            "steps": random.randint(8000, 15000),
            "calories_burned": random.randint(1800, 2500),
            "active_minutes": random.randint(30, 90),
            "distance_km": round(random.uniform(6.0, 12.0), 1),
            "floors_climbed": random.randint(5, 25),
            
            # Stress & Recovery
            "stress_score": round(random.uniform(0.1, 0.8), 2),
            "stress_events": random.randint(0, 5),
            "recovery_score": random.randint(60, 95),
            "energy_level": random.choice(["low", "medium", "high"]),
            
            # Environmental Data
            "ambient_temperature": round(random.uniform(20, 25), 1),
            "humidity": round(random.uniform(40, 60), 1),
            "noise_level": round(random.uniform(30, 70), 1),
            "light_level": random.choice(["low", "medium", "high"]),
            
            # Additional Metrics
            "breathing_rate": round(random.uniform(12, 20), 1),
            "blood_oxygen": round(random.uniform(95, 99), 1),
        }
        
        # Ingest the mock data
        result = await ingest_wearable_data(user_id, mock_data)
        
        if result.get("success"):
            return {
                "success": True,
                "status": "mock_data_created",
                "data_id": result["data_id"],
                "data_date": date_str,
                "device_name": "Mock Apple Watch Series 9",
                "mock_data": mock_data
            }
        else:
            return result
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to generate mock data: {str(e)}"
        }


async def register_device_with_iot_core(device_id: str, device_type: str) -> str:
    """
    Register device with Google Cloud IoT Core
    
    Args:
        device_id: Unique device identifier
        device_type: Type of device
    
    Returns:
        Registry ID for the device
    """
    if not IOT_CORE_AVAILABLE:
        raise Exception("Google Cloud IoT Core not available")
    
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    registry_id = f"wearable-devices-{device_type}"
    
    # Initialize IoT Core client
    client = iot_v1.DeviceManagerClient()
    
    # Create registry if it doesn't exist
    registry_path = client.registry_path(project_id, location, registry_id)
    
    try:
        registry = client.get_registry(request={"name": registry_path})
    except Exception:
        # Create registry
        registry = iot_v1.DeviceRegistry(
            id=registry_id,
            name=registry_path,
            event_notification_configs=[
                iot_v1.EventNotificationConfig(
                    pubsub_topic_name=f"projects/{project_id}/topics/wearable-events"
                )
            ]
        )
        client.create_registry(
            request={
                "parent": f"projects/{project_id}/locations/{location}",
                "device_registry": registry
            }
        )
    
    # Create device
    device_path = client.device_path(project_id, location, registry_id, device_id)
    
    device = iot_v1.Device(
        id=device_id,
        name=device_path,
        metadata={"device_type": device_type, "registered_at": datetime.utcnow().isoformat()}
    )
    
    client.create_device(
        request={
            "parent": registry_path,
            "device": device
        }
    )
    
    return registry_id


# Helper Functions

def calculate_recovery_score(wearable_data: Dict[str, Any]) -> int:
    """Calculate recovery score based on wearable data"""
    score = 50  # Base score
    
    # Sleep quality contribution (30%)
    sleep_score = wearable_data.get("sleep", {}).get("sleep_score", 0)
    if sleep_score:
        score += (sleep_score - 50) * 0.3
    
    # HRV contribution (25%)
    hrv = wearable_data.get("heart_rate", {}).get("hrv_rmssd", 0)
    if hrv:
        if hrv > 35:
            score += 15
        elif hrv > 25:
            score += 5
    
    # Stress level contribution (25%)
    stress_score = wearable_data.get("stress_recovery", {}).get("stress_score", 0)
    if stress_score:
        score -= stress_score * 30
    
    # Activity contribution (20%)
    active_minutes = wearable_data.get("activity", {}).get("active_minutes", 0)
    if active_minutes:
        if active_minutes > 60:
            score += 10
        elif active_minutes > 30:
            score += 5
    
    return max(0, min(100, int(score)))


def calculate_recovery_score_from_dict(data_doc: Dict[str, Any]) -> int:
    """Calculate recovery score from Firebase document"""
    score = 50  # Base score
    
    # Sleep quality contribution (30%)
    sleep_score = data_doc.get("sleep_score", 0)
    if sleep_score:
        score += (sleep_score - 50) * 0.3
    
    # HRV contribution (25%)
    hrv = data_doc.get("hrv_rmssd", 0)
    if hrv:
        if hrv > 35:
            score += 15
        elif hrv > 25:
            score += 5
    
    # Stress level contribution (25%)
    stress_score = data_doc.get("stress_score", 0)
    if stress_score:
        score -= stress_score * 30
    
    # Activity contribution (20%)
    active_minutes = data_doc.get("active_minutes", 0)
    if active_minutes:
        if active_minutes > 60:
            score += 10
        elif active_minutes > 30:
            score += 5
    
    return max(0, min(100, int(score)))


def get_recovery_recommendation(score: int) -> str:
    """Get recommendation based on recovery score"""
    if score >= 80:
        return "Excellent recovery! You're ready for high-intensity tasks."
    elif score >= 60:
        return "Good recovery. Moderate-intensity tasks recommended."
    elif score >= 40:
        return "Fair recovery. Light tasks and extra breaks recommended."
    else:
        return "Poor recovery. Focus on rest and light activities."


def generate_mock_ai_insights(wearable_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate mock AI insights for development"""
    return {
        "recovery_score": random.randint(60, 90),
        "sleep_debt": round(random.uniform(-2, 1), 1),
        "stress_level": random.choice(["low", "medium", "high"]),
        "focus_recommendation": random.choice(["high", "medium", "low"]),
        "confidence": round(random.uniform(0.7, 0.95), 2),
        "focus_duration": random.randint(20, 45),
        "break_duration": random.randint(5, 15),
        "detailed_insights": {
            "sleep_analysis": "Sleep quality is optimal for cognitive performance",
            "stress_indicators": "Stress levels are within normal range",
            "activity_assessment": "Activity levels support good recovery",
            "environmental": {
                "noise_recommendation": "Consider noise-canceling for focus",
                "lighting_suggestion": "Natural lighting optimal for productivity"
            },
            "wellness": {
                "breathing_exercises": "5-minute breathing session recommended",
                "movement_break": "Take a 10-minute walk"
            }
        },
        "activities": {
            "focus_activities": ["Deep work", "Study sessions", "Creative tasks"],
            "break_activities": ["Walking", "Stretching", "Hydration"],
            "wellness_activities": ["Meditation", "Breathing exercises", "Light movement"]
        }
    }
