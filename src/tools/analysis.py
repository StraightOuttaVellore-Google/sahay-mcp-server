"""
Enhanced Analysis Tools for Sahay MCP Server

This module provides advanced analysis tools for wellness and study data,
including trend analysis, insights generation, and comprehensive reporting.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, date, timedelta
from enum import Enum
import json
from ..firebase_client import get_firestore
from .eisenhower import get_all_tasks
from .daily_data import get_monthly_data


class AnalysisType(str, Enum):
    """Types of analysis available"""
    WELLNESS_TRENDS = "wellness_trends"
    STUDY_PATTERNS = "study_patterns"
    PRODUCTIVITY_INSIGHTS = "productivity_insights"
    EMOTIONAL_ANALYSIS = "emotional_analysis"
    TASK_PERFORMANCE = "task_performance"
    COMPREHENSIVE_REPORT = "comprehensive_report"


class WellnessInsight:
    """Wellness insight data structure"""
    
    def __init__(self, insight_type: str, title: str, description: str, 
                 confidence: float, recommendations: List[str], 
                 data_points: Dict[str, Any]):
        self.insight_type = insight_type
        self.title = title
        self.description = description
        self.confidence = confidence  # 0.0 to 1.0
        self.recommendations = recommendations
        self.data_points = data_points
        self.generated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'insight_type': self.insight_type,
            'title': self.title,
            'description': self.description,
            'confidence': self.confidence,
            'recommendations': self.recommendations,
            'data_points': self.data_points,
            'generated_at': self.generated_at.isoformat()
        }


async def analyze_wellness_trends(user_id: str, months_back: int = 3) -> Dict[str, Any]:
    """
    Analyze wellness trends over time
    
    Args:
        user_id: User identifier
        months_back: Number of months to analyze
    
    Returns:
        Dictionary containing wellness trend analysis
    """
    try:
        current_date = date.today()
        insights = []
        
        # Get data for the specified period
        monthly_data = {}
        for i in range(months_back):
            target_date = current_date - timedelta(days=30 * i)
            year = target_date.year
            month = target_date.month
            
            data_result = await get_monthly_data(user_id, year, month)
            monthly_data[f"{year}-{month:02d}"] = data_result['data']
        
        # Analyze emotional trends
        emotion_counts = {}
        total_entries = 0
        
        for month_data in monthly_data.values():
            for entry in month_data:
                emotion = entry.get('emoji', 'BALANCED')
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
                total_entries += 1
        
        if total_entries > 0:
            # Calculate dominant emotions
            dominant_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0]
            emotion_percentages = {
                emotion: (count / total_entries) * 100 
                for emotion, count in emotion_counts.items()
            }
            
            # Generate insights
            if emotion_percentages.get('OVERWHELMED', 0) > 30:
                insights.append(WellnessInsight(
                    insight_type="stress_pattern",
                    title="High Stress Periods Detected",
                    description=f"Overwhelmed emotions appear in {emotion_percentages['OVERWHELMED']:.1f}% of entries",
                    confidence=0.8,
                    recommendations=[
                        "Consider implementing stress management techniques",
                        "Take regular breaks during study sessions",
                        "Practice mindfulness or meditation"
                    ],
                    data_points={"overwhelmed_percentage": emotion_percentages['OVERWHELMED']}
                ))
            
            if emotion_percentages.get('FOCUSED', 0) > 40:
                insights.append(WellnessInsight(
                    insight_type="positive_pattern",
                    title="Strong Focus Periods",
                    description=f"Focused state achieved in {emotion_percentages['FOCUSED']:.1f}% of entries",
                    confidence=0.9,
                    recommendations=[
                        "Identify what conditions lead to focused states",
                        "Replicate successful study environments",
                        "Maintain current study strategies"
                    ],
                    data_points={"focused_percentage": emotion_percentages['FOCUSED']}
                ))
        
        return {
            "success": True,
            "analysis_type": "wellness_trends",
            "period_months": months_back,
            "total_entries": total_entries,
            "emotion_distribution": emotion_percentages,
            "dominant_emotion": dominant_emotion,
            "insights": [insight.to_dict() for insight in insights],
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to analyze wellness trends"
        }


async def analyze_study_patterns(user_id: str, months_back: int = 2) -> Dict[str, Any]:
    """
    Analyze study patterns and productivity
    
    Args:
        user_id: User identifier
        months_back: Number of months to analyze
    
    Returns:
        Dictionary containing study pattern analysis
    """
    try:
        current_date = date.today()
        insights = []
        
        # Get tasks data
        tasks_result = await get_all_tasks(user_id)
        tasks = tasks_result['list_of_tasks']
        
        # Analyze task completion patterns
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.get('status') == 'completed'])
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Analyze quadrant performance
        quadrant_performance = {}
        for task in tasks:
            quadrant = task.get('quadrant', 'HUHI')
            if quadrant not in quadrant_performance:
                quadrant_performance[quadrant] = {"completed": 0, "total": 0}
            
            quadrant_performance[quadrant]["total"] += 1
            if task.get('status') == 'completed':
                quadrant_performance[quadrant]["completed"] += 1
        
        # Calculate quadrant completion rates
        quadrant_rates = {}
        for quadrant, data in quadrant_performance.items():
            if data["total"] > 0:
                quadrant_rates[quadrant] = (data["completed"] / data["total"]) * 100
        
        # Generate insights
        if completion_rate < 50:
            insights.append(WellnessInsight(
                insight_type="productivity_challenge",
                title="Low Task Completion Rate",
                description=f"Only {completion_rate:.1f}% of tasks are being completed",
                confidence=0.9,
                recommendations=[
                    "Break down large tasks into smaller, manageable pieces",
                    "Set realistic deadlines and priorities",
                    "Use time-blocking techniques"
                ],
                data_points={"completion_rate": completion_rate}
            ))
        
        if quadrant_rates.get('HUHI', 0) < 70:
            insights.append(WellnessInsight(
                insight_type="priority_management",
                title="High Priority Tasks Need Attention",
                description=f"Only {quadrant_rates.get('HUHI', 0):.1f}% of urgent-important tasks completed",
                confidence=0.8,
                recommendations=[
                    "Focus on urgent-important tasks first",
                    "Eliminate or delegate urgent-unimportant tasks",
                    "Schedule dedicated time for important tasks"
                ],
                data_points={"huhi_completion_rate": quadrant_rates.get('HUHI', 0)}
            ))
        
        return {
            "success": True,
            "analysis_type": "study_patterns",
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "completion_rate": completion_rate,
            "quadrant_performance": quadrant_performance,
            "quadrant_completion_rates": quadrant_rates,
            "insights": [insight.to_dict() for insight in insights],
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to analyze study patterns"
        }


async def generate_comprehensive_report(user_id: str, months_back: int = 3) -> Dict[str, Any]:
    """
    Generate a comprehensive wellness and study report
    
    Args:
        user_id: User identifier
        months_back: Number of months to analyze
    
    Returns:
        Dictionary containing comprehensive analysis report
    """
    try:
        # Get wellness trends
        wellness_analysis = await analyze_wellness_trends(user_id, months_back)
        
        # Get study patterns
        study_analysis = await analyze_study_patterns(user_id, months_back)
        
        # Combine insights
        all_insights = []
        if wellness_analysis.get('success'):
            all_insights.extend(wellness_analysis.get('insights', []))
        if study_analysis.get('success'):
            all_insights.extend(study_analysis.get('insights', []))
        
        # Generate overall wellness score
        wellness_score = calculate_wellness_score(wellness_analysis, study_analysis)
        
        # Generate recommendations
        recommendations = generate_recommendations(all_insights)
        
        return {
            "success": True,
            "analysis_type": "comprehensive_report",
            "period_months": months_back,
            "wellness_score": wellness_score,
            "wellness_trends": wellness_analysis,
            "study_patterns": study_analysis,
            "all_insights": all_insights,
            "recommendations": recommendations,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to generate comprehensive report"
        }


def calculate_wellness_score(wellness_analysis: Dict[str, Any], study_analysis: Dict[str, Any]) -> float:
    """Calculate overall wellness score (0-100)"""
    score = 50.0  # Base score
    
    # Adjust based on wellness trends
    if wellness_analysis.get('success'):
        emotion_dist = wellness_analysis.get('emotion_distribution', {})
        
        # Positive emotions increase score
        positive_emotions = ['FOCUSED', 'BALANCED', 'RELAXED']
        for emotion in positive_emotions:
            score += emotion_dist.get(emotion, 0) * 0.5
        
        # Negative emotions decrease score
        negative_emotions = ['OVERWHELMED', 'BURNT_OUT', 'INTENSE']
        for emotion in negative_emotions:
            score -= emotion_dist.get(emotion, 0) * 0.3
    
    # Adjust based on study patterns
    if study_analysis.get('success'):
        completion_rate = study_analysis.get('completion_rate', 0)
        score += (completion_rate - 50) * 0.2  # Adjust based on completion rate
    
    # Ensure score is between 0 and 100
    return max(0, min(100, score))


def generate_recommendations(insights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate actionable recommendations based on insights"""
    recommendations = []
    
    # Group recommendations by type
    stress_management = []
    productivity = []
    wellness = []
    
    for insight in insights:
        insight_type = insight.get('insight_type', '')
        insight_recommendations = insight.get('recommendations', [])
        
        if 'stress' in insight_type.lower():
            stress_management.extend(insight_recommendations)
        elif 'productivity' in insight_type.lower() or 'task' in insight_type.lower():
            productivity.extend(insight_recommendations)
        else:
            wellness.extend(insight_recommendations)
    
    # Create recommendation categories
    if stress_management:
        recommendations.append({
            "category": "Stress Management",
            "priority": "high",
            "recommendations": list(set(stress_management))[:3]  # Top 3 unique
        })
    
    if productivity:
        recommendations.append({
            "category": "Productivity",
            "priority": "medium",
            "recommendations": list(set(productivity))[:3]
        })
    
    if wellness:
        recommendations.append({
            "category": "General Wellness",
            "priority": "medium",
            "recommendations": list(set(wellness))[:3]
        })
    
    return recommendations


async def save_analysis_results(user_id: str, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
    """Save analysis results to Firebase"""
    try:
        db = get_firestore()
        analysis_ref = db.collection('users').document(user_id).collection('analysis_results')
        
        # Create document with timestamp
        doc_id = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        analysis_ref.document(doc_id).set(analysis_data)
        
        return {
            "success": True,
            "document_id": doc_id,
            "message": "Analysis results saved successfully"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to save analysis results"
        }
