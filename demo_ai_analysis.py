#!/usr/bin/env python3
"""
Enhanced AI Analysis Tools Demo

This script demonstrates the enhanced analysis capabilities powered by Google's GenAI stack.
It showcases AI-powered insights, visualizations, and comprehensive reporting.
"""

import asyncio
import json
import os
import sys
from datetime import datetime, date, timedelta
from dotenv import load_dotenv

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from tools.ai_analysis import (
    initialize_google_genai, analyze_wellness_trends_ai,
    analyze_study_patterns_ai, generate_comprehensive_ai_report,
    save_ai_analysis_results, visual_generator
)


async def demo_ai_analysis():
    """Demonstrate enhanced AI analysis capabilities"""
    
    print("🚀 Enhanced AI Analysis Tools Demo")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Initialize Google GenAI
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID')
    if project_id:
        print(f"🔧 Initializing Google GenAI for project: {project_id}")
        success = initialize_google_genai(project_id)
        if success:
            print("✅ Google GenAI initialized successfully!")
        else:
            print("⚠️  Google GenAI initialization failed - running in basic mode")
    else:
        print("⚠️  GOOGLE_CLOUD_PROJECT_ID not set - running in basic mode")
    
    # Demo user ID
    demo_user_id = "demo_user_123"
    
    print(f"\n📊 Running AI Analysis Demo for user: {demo_user_id}")
    print("-" * 50)
    
    # 1. AI-Powered Wellness Trends Analysis
    print("\n1️⃣ AI-Powered Wellness Trends Analysis")
    print("Analyzing wellness patterns with Google Gemini...")
    
    try:
        wellness_result = await analyze_wellness_trends_ai(demo_user_id, months_back=3)
        
        if wellness_result.get('success'):
            print("✅ Wellness analysis completed!")
            print(f"   📈 Total entries analyzed: {wellness_result.get('total_entries', 0)}")
            print(f"   🎯 Dominant emotion: {wellness_result.get('dominant_emotion', 'N/A')}")
            print(f"   🤖 AI insights generated: {len(wellness_result.get('ai_insights', []))}")
            print(f"   📊 Visualizations created: {len(wellness_result.get('visualizations', []))}")
            
            # Display AI insights
            ai_insights = wellness_result.get('ai_insights', [])
            if ai_insights:
                print("\n   🧠 AI-Generated Insights:")
                for i, insight in enumerate(ai_insights[:2], 1):  # Show first 2 insights
                    print(f"      {i}. {insight.get('title', 'N/A')}")
                    print(f"         Confidence: {insight.get('confidence', 0):.2f}")
                    print(f"         Model: {insight.get('model_used', 'N/A')}")
        else:
            print(f"❌ Wellness analysis failed: {wellness_result.get('message', 'Unknown error')}")
    
    except Exception as e:
        print(f"❌ Error in wellness analysis: {e}")
    
    # 2. AI-Powered Study Patterns Analysis
    print("\n2️⃣ AI-Powered Study Patterns Analysis")
    print("Analyzing study productivity with AI insights...")
    
    try:
        study_result = await analyze_study_patterns_ai(demo_user_id, months_back=2)
        
        if study_result.get('success'):
            print("✅ Study analysis completed!")
            print(f"   📚 Total tasks: {study_result.get('total_tasks', 0)}")
            print(f"   ✅ Completed tasks: {study_result.get('completed_tasks', 0)}")
            print(f"   📊 Completion rate: {study_result.get('completion_rate', 0):.1f}%")
            print(f"   🤖 AI insights generated: {len(study_result.get('ai_insights', []))}")
            print(f"   📊 Visualizations created: {len(study_result.get('visualizations', []))}")
            
            # Display quadrant performance
            quadrant_rates = study_result.get('quadrant_completion_rates', {})
            if quadrant_rates:
                print("\n   📋 Quadrant Performance:")
                for quadrant, rate in quadrant_rates.items():
                    print(f"      {quadrant}: {rate:.1f}% completion")
        else:
            print(f"❌ Study analysis failed: {study_result.get('message', 'Unknown error')}")
    
    except Exception as e:
        print(f"❌ Error in study analysis: {e}")
    
    # 3. Comprehensive AI Report
    print("\n3️⃣ Comprehensive AI Report Generation")
    print("Generating complete wellness and study report with AI...")
    
    try:
        comprehensive_result = await generate_comprehensive_ai_report(demo_user_id, months_back=3)
        
        if comprehensive_result.get('success'):
            print("✅ Comprehensive AI report generated!")
            print(f"   🎯 Overall wellness score: {comprehensive_result.get('wellness_score', 0):.1f}/100")
            print(f"   📝 Executive summary: {comprehensive_result.get('executive_summary', 'N/A')[:100]}...")
            print(f"   🤖 Total AI insights: {len(comprehensive_result.get('all_ai_insights', []))}")
            print(f"   📊 Total visualizations: {len(comprehensive_result.get('all_visualizations', []))}")
            print(f"   💡 AI recommendations: {len(comprehensive_result.get('ai_recommendations', []))}")
            
            # Display AI recommendations
            recommendations = comprehensive_result.get('ai_recommendations', [])
            if recommendations:
                print("\n   💡 AI-Powered Recommendations:")
                for i, rec in enumerate(recommendations[:2], 1):  # Show first 2 categories
                    print(f"      {i}. {rec.get('category', 'N/A')} (Priority: {rec.get('priority', 'N/A')})")
                    print(f"         AI Confidence: {rec.get('ai_confidence', 0):.2f}")
                    rec_list = rec.get('recommendations', [])
                    if rec_list:
                        print(f"         Top recommendation: {rec_list[0]}")
        else:
            print(f"❌ Comprehensive report failed: {comprehensive_result.get('message', 'Unknown error')}")
    
    except Exception as e:
        print(f"❌ Error in comprehensive report: {e}")
    
    # 4. Data Visualization Demo
    print("\n4️⃣ Data Visualization Demo")
    print("Generating sample visualizations...")
    
    try:
        # Sample emotion data
        sample_emotions = {
            "FOCUSED": 25,
            "BALANCED": 18,
            "OVERWHELMED": 8,
            "RELAXED": 12,
            "INTENSE": 15
        }
        
        if visual_generator.available:
            print("✅ Visualization engine available!")
            chart_base64 = visual_generator.generate_emotion_trend_chart(sample_emotions)
            if chart_base64:
                print("✅ Emotion trend chart generated!")
                print(f"   📊 Chart size: {len(chart_base64)} characters (base64)")
                print("   💡 Chart ready for display in web applications")
            else:
                print("❌ Failed to generate emotion chart")
        else:
            print("⚠️  Visualization engine not available")
            print("   Install: pip install matplotlib seaborn pandas numpy")
    
    except Exception as e:
        print(f"❌ Error in visualization demo: {e}")
    
    # 5. Save Results Demo
    print("\n5️⃣ Save AI Analysis Results")
    print("Saving analysis results to Firebase...")
    
    try:
        # Create sample analysis data
        sample_analysis = {
            "analysis_type": "demo_analysis",
            "wellness_score": 78.5,
            "ai_insights": [
                {
                    "title": "Demo AI Insight",
                    "description": "This is a demonstration of AI-powered analysis",
                    "confidence": 0.85,
                    "model_used": "gemini-2.0-flash-exp"
                }
            ],
            "visualizations": [],
            "generated_at": datetime.now().isoformat()
        }
        
        save_result = await save_ai_analysis_results(demo_user_id, sample_analysis)
        
        if save_result.get('success'):
            print("✅ Analysis results saved successfully!")
            print(f"   📄 Document ID: {save_result.get('document_id', 'N/A')}")
            ai_features = save_result.get('ai_features_used', {})
            print(f"   🤖 Google GenAI used: {ai_features.get('google_genai', False)}")
            print(f"   📊 Visualizations included: {ai_features.get('visualizations', False)}")
            print(f"   🧠 AI insights included: {ai_features.get('ai_insights', False)}")
        else:
            print(f"❌ Failed to save results: {save_result.get('message', 'Unknown error')}")
    
    except Exception as e:
        print(f"❌ Error saving results: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print("🎉 Enhanced AI Analysis Demo Complete!")
    print("\n📋 Features Demonstrated:")
    print("   ✅ Google GenAI integration with Gemini 2.0 Flash")
    print("   ✅ AI-powered wellness trend analysis")
    print("   ✅ AI-powered study pattern analysis")
    print("   ✅ Comprehensive AI report generation")
    print("   ✅ Automatic data visualization")
    print("   ✅ Firebase integration with AI metadata")
    print("   ✅ Confidence scoring and model tracking")
    print("   ✅ Personalized AI recommendations")
    
    print("\n🚀 Next Steps:")
    print("   1. Set up Google Cloud project and enable APIs")
    print("   2. Configure environment variables")
    print("   3. Install additional dependencies")
    print("   4. Run the MCP server with enhanced tools")
    print("   5. Integrate with your application")
    
    print("\n📚 Documentation:")
    print("   • Enhanced AI Setup Guide: ENHANCED_AI_SETUP_GUIDE.md")
    print("   • Firebase Integration: FIREBASE_INTEGRATION_README.md")
    print("   • Google Cloud Documentation: https://cloud.google.com/vertex-ai")


if __name__ == "__main__":
    # Run the demo
    asyncio.run(demo_ai_analysis())
