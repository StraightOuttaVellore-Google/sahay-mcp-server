"""
Enhanced Analysis Tools with Google GenAI Stack Integration

This module provides advanced analysis tools powered by Google's GenAI technologies
including Vertex AI, Gemini models, and Looker Studio for comprehensive wellness
and study data analysis with AI-powered insights and visualizations.
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, date, timedelta
from enum import Enum
import json
import os
import base64
import io
from dataclasses import dataclass
import asyncio

# Google Cloud imports
try:
    import vertexai
    from vertexai.generative_models import GenerativeModel, Part
    from vertexai.preview.language_models import TextGenerationModel
    from google.cloud import aiplatform
    from google.cloud import storage
    VERTEX_AI_AVAILABLE = True
except ImportError:
    VERTEX_AI_AVAILABLE = False

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    import pandas as pd
    import numpy as np
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False

from ..firebase_client import get_firestore
from .eisenhower import get_all_tasks
from .daily_data import get_monthly_data


class AnalysisType(str, Enum):
    """Enhanced analysis types with AI capabilities"""
    AI_WELLNESS_INSIGHTS = "ai_wellness_insights"
    PREDICTIVE_ANALYSIS = "predictive_analysis"
    EMOTIONAL_INTELLIGENCE = "emotional_intelligence"
    STUDY_OPTIMIZATION = "study_optimization"
    PERSONALIZED_RECOMMENDATIONS = "personalized_recommendations"
    VISUAL_ANALYTICS = "visual_analytics"
    COMPREHENSIVE_AI_REPORT = "comprehensive_ai_report"


@dataclass
class AIInsight:
    """Enhanced AI-powered insight"""
    insight_type: str
    title: str
    description: str
    confidence: float
    ai_generated: bool
    recommendations: List[str]
    data_points: Dict[str, Any]
    visualizations: List[str]  # Base64 encoded charts
    generated_at: datetime
    model_used: str


class GoogleGenAIAnalyzer:
    """Google GenAI-powered analysis engine"""
    
    def __init__(self, project_id: str, location: str = "us-central1"):
        self.project_id = project_id
        self.location = location
        self.model = None
        self.text_model = None
        
        if VERTEX_AI_AVAILABLE:
            self._initialize_vertex_ai()
    
    def _initialize_vertex_ai(self):
        """Initialize Vertex AI with Gemini models"""
        try:
            vertexai.init(project=self.project_id, location=self.location)
            
            # Initialize Gemini 2.0 Flash for advanced analysis
            self.model = GenerativeModel("gemini-2.0-flash-exp")
            
            # Initialize text generation model for summaries
            self.text_model = TextGenerationModel.from_pretrained("gemini-2")
            
            print(f"✅ Vertex AI initialized successfully for project: {self.project_id}")
        except Exception as e:
            print(f"❌ Failed to initialize Vertex AI: {e}")
            self.model = None
            self.text_model = None
    
    async def generate_ai_insights(self, data: Dict[str, Any], analysis_type: str) -> List[AIInsight]:
        """Generate AI-powered insights using Gemini models"""
        if not self.model:
            return []
        
        try:
            # Prepare context for AI analysis
            context = self._prepare_analysis_context(data, analysis_type)
            
            # Generate insights using Gemini
            prompt = f"""
            As an expert wellness and study analytics AI, analyze the following data and provide insights:
            
            Data: {json.dumps(data, indent=2)}
            Analysis Type: {analysis_type}
            
            Please provide:
            1. Key insights with confidence scores (0-1)
            2. Specific recommendations
            3. Data patterns identified
            4. Predictive trends
            
            Format as JSON with this structure:
            {{
                "insights": [
                    {{
                        "title": "Insight title",
                        "description": "Detailed description",
                        "confidence": 0.85,
                        "recommendations": ["rec1", "rec2"],
                        "data_patterns": {{"pattern": "value"}}
                    }}
                ]
            }}
            """
            
            response = self.model.generate_content(prompt)
            insights_data = json.loads(response.text)
            
            # Convert to AIInsight objects
            ai_insights = []
            for insight_data in insights_data.get("insights", []):
                ai_insight = AIInsight(
                    insight_type=analysis_type,
                    title=insight_data.get("title", ""),
                    description=insight_data.get("description", ""),
                    confidence=insight_data.get("confidence", 0.5),
                    ai_generated=True,
                    recommendations=insight_data.get("recommendations", []),
                    data_points=insight_data.get("data_patterns", {}),
                    visualizations=[],
                    generated_at=datetime.now(),
                    model_used="gemini-2.0-flash-exp"
                )
                ai_insights.append(ai_insight)
            
            return ai_insights
            
        except Exception as e:
            print(f"Error generating AI insights: {e}")
            return []
    
    def _prepare_analysis_context(self, data: Dict[str, Any], analysis_type: str) -> str:
        """Prepare context for AI analysis"""
        context_parts = []
        
        if "emotion_distribution" in data:
            context_parts.append(f"Emotional patterns: {data['emotion_distribution']}")
        
        if "completion_rate" in data:
            context_parts.append(f"Task completion rate: {data['completion_rate']}%")
        
        if "wellness_score" in data:
            context_parts.append(f"Overall wellness score: {data['wellness_score']}")
        
        return " | ".join(context_parts)


class VisualAnalyticsGenerator:
    """Generate visual analytics using matplotlib and seaborn"""
    
    def __init__(self):
        self.available = PLOTTING_AVAILABLE
    
    def generate_emotion_trend_chart(self, emotion_data: Dict[str, int]) -> str:
        """Generate emotion trend visualization"""
        if not self.available:
            return ""
        
        try:
            plt.style.use('seaborn-v0_8')
            fig, ax = plt.subplots(figsize=(10, 6))
            
            emotions = list(emotion_data.keys())
            counts = list(emotion_data.values())
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
            
            bars = ax.bar(emotions, counts, color=colors[:len(emotions)])
            ax.set_title('Emotional State Distribution', fontsize=16, fontweight='bold')
            ax.set_xlabel('Emotional States', fontsize=12)
            ax.set_ylabel('Frequency', fontsize=12)
            
            # Add value labels on bars
            for bar, count in zip(bars, counts):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                       str(count), ha='center', va='bottom', fontweight='bold')
            
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return image_base64
            
        except Exception as e:
            print(f"Error generating emotion chart: {e}")
            return ""
    
    def generate_productivity_trend_chart(self, productivity_data: Dict[str, Any]) -> str:
        """Generate productivity trend visualization"""
        if not self.available:
            return ""
        
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # Task completion by quadrant
            quadrants = list(productivity_data.get('quadrant_performance', {}).keys())
            completion_rates = []
            
            for quadrant in quadrants:
                data = productivity_data['quadrant_performance'][quadrant]
                rate = (data['completed'] / data['total'] * 100) if data['total'] > 0 else 0
                completion_rates.append(rate)
            
            bars1 = ax1.bar(quadrants, completion_rates, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])
            ax1.set_title('Task Completion by Quadrant', fontsize=14, fontweight='bold')
            ax1.set_ylabel('Completion Rate (%)', fontsize=12)
            ax1.set_ylim(0, 100)
            
            # Add value labels
            for bar, rate in zip(bars1, completion_rates):
                ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                        f'{rate:.1f}%', ha='center', va='bottom', fontweight='bold')
            
            # Overall productivity trend
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
            productivity_scores = [65, 72, 68, 75, 80, 78]  # Mock data
            
            ax2.plot(months, productivity_scores, marker='o', linewidth=3, markersize=8, color='#2E86AB')
            ax2.set_title('Productivity Trend', fontsize=14, fontweight='bold')
            ax2.set_ylabel('Productivity Score', fontsize=12)
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return image_base64
            
        except Exception as e:
            print(f"Error generating productivity chart: {e}")
            return ""


# Global instances
genai_analyzer = None
visual_generator = VisualAnalyticsGenerator()


def initialize_google_genai(project_id: str, location: str = "us-central1") -> bool:
    """Initialize Google GenAI services"""
    global genai_analyzer
    
    if not VERTEX_AI_AVAILABLE:
        print("❌ Vertex AI not available. Install: pip install google-cloud-aiplatform")
        return False
    
    try:
        genai_analyzer = GoogleGenAIAnalyzer(project_id, location)
        return genai_analyzer.model is not None
    except Exception as e:
        print(f"❌ Failed to initialize Google GenAI: {e}")
        return False


async def analyze_wellness_trends_ai(user_id: str, months_back: int = 3) -> Dict[str, Any]:
    """
    Enhanced wellness trends analysis with AI insights
    """
    try:
        current_date = date.today()
        insights = []
        visualizations = []
        
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
            emotion_percentages = {
                emotion: (count / total_entries) * 100 
                for emotion, count in emotion_counts.items()
            }
            
            dominant_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0]
            
            # Generate AI insights if available
            if genai_analyzer:
                ai_insights = await genai_analyzer.generate_ai_insights(
                    {
                        "emotion_distribution": emotion_percentages,
                        "total_entries": total_entries,
                        "months_analyzed": months_back
                    },
                    "ai_wellness_insights"
                )
                insights.extend(ai_insights)
            
            # Generate visualizations
            if visual_generator.available:
                emotion_chart = visual_generator.generate_emotion_trend_chart(emotion_counts)
                if emotion_chart:
                    visualizations.append({
                        "type": "emotion_distribution",
                        "title": "Emotional State Distribution",
                        "data": emotion_chart
                    })
        
        return {
            "success": True,
            "analysis_type": "ai_wellness_trends",
            "period_months": months_back,
            "total_entries": total_entries,
            "emotion_distribution": emotion_percentages,
            "dominant_emotion": dominant_emotion,
            "ai_insights": [insight.__dict__ for insight in insights],
            "visualizations": visualizations,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to analyze wellness trends with AI"
        }


async def analyze_study_patterns_ai(user_id: str, months_back: int = 2) -> Dict[str, Any]:
    """
    Enhanced study patterns analysis with AI insights
    """
    try:
        insights = []
        visualizations = []
        
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
        
        # Generate AI insights if available
        if genai_analyzer:
            ai_insights = await genai_analyzer.generate_ai_insights(
                {
                    "completion_rate": completion_rate,
                    "quadrant_performance": quadrant_performance,
                    "total_tasks": total_tasks,
                    "completed_tasks": completed_tasks
                },
                "study_optimization"
            )
            insights.extend(ai_insights)
        
        # Generate visualizations
        if visual_generator.available:
            productivity_chart = visual_generator.generate_productivity_trend_chart({
                "quadrant_performance": quadrant_performance
            })
            if productivity_chart:
                visualizations.append({
                    "type": "productivity_analysis",
                    "title": "Productivity Analysis",
                    "data": productivity_chart
                })
        
        return {
            "success": True,
            "analysis_type": "ai_study_patterns",
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "completion_rate": completion_rate,
            "quadrant_performance": quadrant_performance,
            "quadrant_completion_rates": quadrant_rates,
            "ai_insights": [insight.__dict__ for insight in insights],
            "visualizations": visualizations,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to analyze study patterns with AI"
        }


async def generate_comprehensive_ai_report(user_id: str, months_back: int = 3) -> Dict[str, Any]:
    """
    Generate comprehensive AI-powered wellness and study report
    """
    try:
        # Get wellness trends
        wellness_analysis = await analyze_wellness_trends_ai(user_id, months_back)
        
        # Get study patterns
        study_analysis = await analyze_study_patterns_ai(user_id, months_back)
        
        # Combine insights
        all_insights = []
        all_visualizations = []
        
        if wellness_analysis.get('success'):
            all_insights.extend(wellness_analysis.get('ai_insights', []))
            all_visualizations.extend(wellness_analysis.get('visualizations', []))
        
        if study_analysis.get('success'):
            all_insights.extend(study_analysis.get('ai_insights', []))
            all_visualizations.extend(study_analysis.get('visualizations', []))
        
        # Generate overall wellness score
        wellness_score = calculate_ai_wellness_score(wellness_analysis, study_analysis)
        
        # Generate AI-powered recommendations
        recommendations = await generate_ai_recommendations(all_insights)
        
        # Generate executive summary using AI
        executive_summary = await generate_executive_summary(
            wellness_analysis, study_analysis, wellness_score
        )
        
        return {
            "success": True,
            "analysis_type": "comprehensive_ai_report",
            "period_months": months_back,
            "wellness_score": wellness_score,
            "executive_summary": executive_summary,
            "wellness_trends": wellness_analysis,
            "study_patterns": study_analysis,
            "all_ai_insights": all_insights,
            "all_visualizations": all_visualizations,
            "ai_recommendations": recommendations,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to generate comprehensive AI report"
        }


def calculate_ai_wellness_score(wellness_analysis: Dict[str, Any], study_analysis: Dict[str, Any]) -> float:
    """Calculate AI-enhanced wellness score"""
    score = 50.0  # Base score
    
    # Adjust based on wellness trends
    if wellness_analysis.get('success'):
        emotion_dist = wellness_analysis.get('emotion_distribution', {})
        
        # AI-weighted scoring
        positive_emotions = ['FOCUSED', 'BALANCED', 'RELAXED']
        for emotion in positive_emotions:
            score += emotion_dist.get(emotion, 0) * 0.6
        
        negative_emotions = ['OVERWHELMED', 'BURNT_OUT', 'INTENSE']
        for emotion in negative_emotions:
            score -= emotion_dist.get(emotion, 0) * 0.4
    
    # Adjust based on study patterns
    if study_analysis.get('success'):
        completion_rate = study_analysis.get('completion_rate', 0)
        score += (completion_rate - 50) * 0.3
    
    # AI confidence adjustment
    ai_insights = wellness_analysis.get('ai_insights', []) + study_analysis.get('ai_insights', [])
    if ai_insights:
        avg_confidence = sum(insight.get('confidence', 0.5) for insight in ai_insights) / len(ai_insights)
        score *= (0.8 + avg_confidence * 0.4)  # Boost score based on AI confidence
    
    return max(0, min(100, score))


async def generate_ai_recommendations(insights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate AI-powered recommendations"""
    recommendations = []
    
    # Group recommendations by type
    stress_management = []
    productivity = []
    wellness = []
    
    for insight in insights:
        insight_type = insight.get('insight_type', '')
        insight_recommendations = insight.get('recommendations', [])
        
        if 'stress' in insight_type.lower() or 'wellness' in insight_type.lower():
            stress_management.extend(insight_recommendations)
        elif 'productivity' in insight_type.lower() or 'study' in insight_type.lower():
            productivity.extend(insight_recommendations)
        else:
            wellness.extend(insight_recommendations)
    
    # Create recommendation categories with AI enhancement
    if stress_management:
        recommendations.append({
            "category": "AI-Enhanced Stress Management",
            "priority": "high",
            "recommendations": list(set(stress_management))[:3],
            "ai_confidence": 0.9
        })
    
    if productivity:
        recommendations.append({
            "category": "AI-Optimized Productivity",
            "priority": "medium",
            "recommendations": list(set(productivity))[:3],
            "ai_confidence": 0.85
        })
    
    if wellness:
        recommendations.append({
            "category": "AI-Personalized Wellness",
            "priority": "medium",
            "recommendations": list(set(wellness))[:3],
            "ai_confidence": 0.8
        })
    
    return recommendations


async def generate_executive_summary(wellness_analysis: Dict[str, Any], 
                                   study_analysis: Dict[str, Any], 
                                   wellness_score: float) -> str:
    """Generate AI-powered executive summary"""
    if not genai_analyzer or not genai_analyzer.text_model:
        return f"Overall wellness score: {wellness_score:.1f}/100"
    
    try:
        prompt = f"""
        Generate a concise executive summary for a wellness and study analytics report:
        
        Wellness Score: {wellness_score:.1f}/100
        Wellness Trends: {wellness_analysis.get('emotion_distribution', {})}
        Study Performance: {study_analysis.get('completion_rate', 0):.1f}% completion rate
        
        Provide a 2-3 sentence summary highlighting key insights and recommendations.
        """
        
        response = genai_analyzer.text_model.predict(prompt)
        return response.text
        
    except Exception as e:
        return f"Overall wellness score: {wellness_score:.1f}/100. AI summary generation failed: {e}"


async def save_ai_analysis_results(user_id: str, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
    """Save AI analysis results to Firebase with enhanced metadata"""
    try:
        db = get_firestore()
        analysis_ref = db.collection('users').document(user_id).collection('ai_analysis_results')
        
        # Add AI metadata
        analysis_data['ai_enhanced'] = True
        analysis_data['google_genai_used'] = genai_analyzer is not None
        analysis_data['visualizations_included'] = len(analysis_data.get('visualizations', [])) > 0
        
        # Create document with timestamp
        doc_id = f"ai_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        analysis_ref.document(doc_id).set(analysis_data)
        
        return {
            "success": True,
            "document_id": doc_id,
            "message": "AI analysis results saved successfully",
            "ai_features_used": {
                "google_genai": genai_analyzer is not None,
                "visualizations": len(analysis_data.get('visualizations', [])) > 0,
                "ai_insights": len(analysis_data.get('ai_insights', [])) > 0
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to save AI analysis results"
        }
