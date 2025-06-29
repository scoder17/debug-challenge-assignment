from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
import asyncio
import json
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from crewai import Crew, Process
from agents import doctor, verifier, nutritionist, exercise_specialist
from task import help_patients, verification, nutrition_analysis, exercise_planning
from database import get_db, init_database
from database_service import (
    DatabaseService, 
    create_anonymous_user, 
    store_analysis_result,
    get_user_report_history
)
from tools import BloodTestReportTool

# Initialize database on startup
init_database()

app = FastAPI(
    title="Blood Test Report Analyser",
    description="AI-powered blood test analysis with comprehensive health recommendations",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def run_crew(query: str, file_path: str, analysis_type: str = "comprehensive"):
    """Run the medical analysis crew based on analysis type"""
    
    if analysis_type == "verification":
        crew = Crew(
            agents=[verifier],
            tasks=[verification],
            process=Process.sequential,
        )
    elif analysis_type == "nutrition":
        crew = Crew(
            agents=[nutritionist],
            tasks=[nutrition_analysis],
            process=Process.sequential,
        )
    elif analysis_type == "exercise":
        crew = Crew(
            agents=[exercise_specialist],
            tasks=[exercise_planning],
            process=Process.sequential,
        )
    else:  # comprehensive analysis
        crew = Crew(
            agents=[doctor, nutritionist, exercise_specialist],
            tasks=[help_patients, nutrition_analysis, exercise_planning],
            process=Process.sequential,
        )
    
    result = crew.kickoff({'query': query, 'file_path': file_path})
    return result

def extract_blood_markers_from_content(content: str) -> List[Dict[str, Any]]:
    """Extract blood markers from PDF content (simplified implementation)"""
    # This is a basic implementation - you might want to enhance this
    # with more sophisticated parsing logic
    markers = []
    
    # Common blood markers and their typical patterns
    common_markers = {
        'Hemoglobin': ['hemoglobin', 'hgb', 'hb'],
        'White Blood Cells': ['wbc', 'white blood cells', 'leucocytes'],
        'Platelets': ['platelets', 'plt'],
        'Cholesterol': ['cholesterol', 'chol'],
        'HDL': ['hdl'],
        'LDL': ['ldl'],
        'Triglycerides': ['triglycerides', 'tg'],
        'Glucose': ['glucose', 'blood sugar'],
        'Creatinine': ['creatinine'],
        'ALT': ['alt', 'alanine aminotransferase'],
        'AST': ['ast', 'aspartate aminotransferase']
    }
    
    lines = content.lower().split('\n')
    
    for line in lines:
        for marker_name, keywords in common_markers.items():
            if any(keyword in line for keyword in keywords):
                # Try to extract numeric values (this is simplified)
                import re
                numbers = re.findall(r'\d+\.?\d*', line)
                if numbers:
                    try:
                        value = float(numbers[0])
                        # Extract unit if possible
                        unit_match = re.search(r'(\w+/\w+|\w+)', line.split(str(value))[1] if len(line.split(str(value))) > 1 else '')
                        unit = unit_match.group(1) if unit_match else None
                        
                        markers.append({
                            'marker_name': marker_name,
                            'value': value,
                            'unit': unit,
                            'is_normal': None,  # Would need reference ranges to determine
                            'category': 'General'
                        })
                        break
                    except (ValueError, IndexError):
                        continue
    
    return markers

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Blood Test Report Analyser API is running",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.post("/analyze")
async def analyze_blood_report(
    file: UploadFile = File(...),
    query: str = Form(default="Provide a comprehensive analysis of my blood test report"),
    analysis_type: str = Form(default="comprehensive"),  # comprehensive, medical, nutrition, exercise
    user_uuid: Optional[str] = Form(default=None)
):
    """Analyze blood test report and provide comprehensive health recommendations"""
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Validate analysis type
    valid_types = ["comprehensive", "medical", "nutrition", "exercise", "verification"]
    if analysis_type not in valid_types:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid analysis type. Must be one of: {', '.join(valid_types)}"
        )
    
    # Generate unique filename to avoid conflicts
    file_id = str(uuid.uuid4())
    file_path = f"data/blood_test_report_{file_id}.pdf"
    
    try:
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        # Save uploaded file
        file_content = await file.read()
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # Validate query
        if not query or query.strip() == "":
            query = "Provide a comprehensive analysis of my blood test report"
        
        # Create or get user
        with DatabaseService() as db_service:
            user_id = None
            if user_uuid:
                user = db_service.get_user_by_uuid(user_uuid)
                if user:
                    user_id = user.id
            
            if not user_id:
                # Create anonymous user
                user_uuid = create_anonymous_user()
                user = db_service.get_user_by_uuid(user_uuid)
                user_id = user.id
            
            # Extract content using the tool to validate it's readable
            pdf_tool = BloodTestReportTool()
            extracted_content = pdf_tool._run(file_path)
            
            if extracted_content.startswith("Error:"):
                raise HTTPException(status_code=400, detail=extracted_content)
            
            # Create blood test report record
            report_data = {
                'user_id': user_id,
                'original_filename': file.filename,
                'file_path': file_path,
                'file_size': len(file_content),
                'raw_content': extracted_content,
                'created_at': datetime.now(timezone.utc)
            }
            
            report = db_service.create_blood_test_report(report_data)
            
            # Extract and store blood markers
            try:
                markers_data = extract_blood_markers_from_content(extracted_content)
                if markers_data:
                    db_service.create_blood_markers(report.id, markers_data)
            except Exception as e:
                print(f"Warning: Could not extract blood markers: {str(e)}")
            
            # First verify the document if it's not a verification-only request
            verification_result = None
            if analysis_type != "verification":
                try:
                    verification_result = run_crew(
                        query="Verify this blood test report", 
                        file_path=file_path, 
                        analysis_type="verification"
                    )
                    
                    # Update verification status
                    is_verified = "verified" in str(verification_result).lower()
                    db_service.update_report_verification(
                        report.id, 
                        is_verified, 
                        str(verification_result.raw) if hasattr(verification_result, 'raw') else str(verification_result)
                    )
                    
                    if not is_verified:
                        return {
                            "status": "error",
                            "message": "Document verification failed",
                            "verification_result": str(verification_result.raw) if hasattr(verification_result, 'raw') else str(verification_result),
                            "user_uuid": user_uuid,
                            "report_uuid": report.report_uuid
                        }
                except Exception as e:
                    print(f"Warning: Verification failed: {str(e)}")
            
            # Process the blood report with the specified analysis type
            start_time = datetime.now()
            response = run_crew(query=query.strip(), file_path=file_path, analysis_type=analysis_type)
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Store analysis result
            analysis_data = {
                'user_id': user_id,
                'report_id': report.id,
                'query': query,
                'analysis_type': analysis_type,
                'processing_time': processing_time,
                'created_at': datetime.now(timezone.utc)
            }
            
            # Store different types of analysis results
            if analysis_type == "comprehensive":
                analysis_data['medical_summary'] = str(response.raw) if hasattr(response, 'raw') else str(response)
            elif analysis_type == "nutrition":
                analysis_data['nutrition_analysis'] = str(response.raw) if hasattr(response, 'raw') else str(response)
            elif analysis_type == "exercise":
                analysis_data['exercise_recommendations'] = str(response.raw) if hasattr(response, 'raw') else str(response)
            else:
                analysis_data['medical_summary'] = str(response.raw) if hasattr(response, 'raw') else str(response)
            
            analysis = db_service.create_analysis(analysis_data)
            
            # Create user session record
            session_data = {
                'user_id': user_id,
                'activity_type': 'analysis',
                'activity_details': json.dumps({
                    'analysis_type': analysis_type,
                    'query': query,
                    'filename': file.filename
                })
            }
            db_service.create_user_session(session_data)
            
            return {
                "status": "success",
                "message": "Blood test report analyzed successfully",
                "query": query,
                "analysis_type": analysis_type,
                "analysis": str(response.raw) if hasattr(response, 'raw') else str(response),
                "file_processed": file.filename,
                "processing_time_seconds": processing_time,
                "user_uuid": user_uuid,
                "report_uuid": report.report_uuid,
                "analysis_uuid": analysis.analysis_uuid,
                "verification_passed": verification_result is not None
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing blood report: {str(e)}")
    
    finally:
        # Clean up uploaded file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass  # Ignore cleanup errors

@app.get("/user/{user_uuid}/reports")
async def get_user_reports(user_uuid: str):
    """Get all reports for a specific user"""
    try:
        reports = get_user_report_history(user_uuid)
        return {
            "status": "success",
            "user_uuid": user_uuid,
            "reports": reports
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving user reports: {str(e)}")

@app.get("/user/{user_uuid}/analyses")
async def get_user_analyses(user_uuid: str, limit: int = Query(default=10, ge=1, le=50)):
    """Get all analyses for a specific user"""
    try:
        with DatabaseService() as db_service:
            user = db_service.get_user_by_uuid(user_uuid)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            analyses = db_service.get_user_analyses(user.id, limit=limit)
            
            analyses_data = []
            for analysis in analyses:
                analyses_data.append({
                    'uuid': analysis.analysis_uuid,
                    'query': analysis.query,
                    'analysis_type': analysis.analysis_type,
                    'created_at': analysis.created_at,
                    'processing_time': analysis.processing_time,
                    'medical_summary': analysis.medical_summary,
                    'nutrition_analysis': analysis.nutrition_analysis,
                    'exercise_recommendations': analysis.exercise_recommendations
                })
            
            return {
                "status": "success",
                "user_uuid": user_uuid,
                "analyses": analyses_data
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving user analyses: {str(e)}")

@app.get("/analysis/{analysis_uuid}")
async def get_analysis(analysis_uuid: str):
    """Get a specific analysis by UUID"""
    try:
        with DatabaseService() as db_service:
            analysis = db_service.get_analysis_by_uuid(analysis_uuid)
            if not analysis:
                raise HTTPException(status_code=404, detail="Analysis not found")
            
            return {
                "status": "success",
                "analysis": {
                    'uuid': analysis.analysis_uuid,
                    'query': analysis.query,
                    'analysis_type': analysis.analysis_type,
                    'created_at': analysis.created_at,
                    'processing_time': analysis.processing_time,
                    'medical_summary': analysis.medical_summary,
                    'nutrition_analysis': analysis.nutrition_analysis,
                    'exercise_recommendations': analysis.exercise_recommendations,
                    'health_recommendations': analysis.health_recommendations,
                    'supplement_suggestions': analysis.supplement_suggestions,
                    'follow_up_tests': analysis.follow_up_tests
                }
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving analysis: {str(e)}")

@app.get("/report/{report_uuid}")
async def get_report(report_uuid: str):
    """Get a specific blood test report by UUID"""
    try:
        with DatabaseService() as db_service:
            report = db_service.get_report_by_uuid(report_uuid)
            if not report:
                raise HTTPException(status_code=404, detail="Report not found")
            
            # Get associated markers
            markers = db_service.get_report_markers(report.id)
            markers_data = []
            for marker in markers:
                markers_data.append({
                    'name': marker.marker_name,
                    'value': marker.value,
                    'unit': marker.unit,
                    'reference_range_min': marker.reference_range_min,
                    'reference_range_max': marker.reference_range_max,
                    'is_normal': marker.is_normal,
                    'flag': marker.flag,
                    'category': marker.category
                })
            
            return {
                "status": "success",
                "report": {
                    'uuid': report.report_uuid,
                    'filename': report.original_filename,
                    'created_at': report.created_at,
                    'report_date': report.report_date,
                    'lab_name': report.lab_name,
                    'doctor_name': report.doctor_name,
                    'test_type': report.test_type,
                    'is_verified': report.is_verified,
                    'verification_notes': report.verification_notes,
                    'markers': markers_data
                }
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving report: {str(e)}")

@app.get("/user/{user_uuid}/statistics")
async def get_user_statistics(user_uuid: str):
    """Get comprehensive statistics for a user"""
    try:
        with DatabaseService() as db_service:
            user = db_service.get_user_by_uuid(user_uuid)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            stats = db_service.get_user_statistics(user.id)
            
            return {
                "status": "success",
                "user_uuid": user_uuid,
                "statistics": stats
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving user statistics: {str(e)}")

@app.get("/user/{user_uuid}/trends/{marker_name}")
async def get_health_trends(user_uuid: str, marker_name: str):
    """Get health trends for a specific marker over time"""
    try:
        with DatabaseService() as db_service:
            user = db_service.get_user_by_uuid(user_uuid)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            trends = db_service.get_user_health_trends(user.id, marker_name)
            
            return {
                "status": "success",
                "user_uuid": user_uuid,
                "marker_name": marker_name,
                "trends": trends
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving health trends: {str(e)}")

@app.post("/user/create")
async def create_user(user_data: Dict[str, Any]):
    """Create a new user with provided information"""
    try:
        with DatabaseService() as db_service:
            user = db_service.create_user(user_data)
            
            return {
                "status": "success",
                "message": "User created successfully",
                "user_uuid": user.user_uuid
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")

@app.get("/analytics/common-abnormal-markers")
async def get_common_abnormal_markers(limit: int = Query(default=10, ge=1, le=50)):
    """Get most commonly abnormal markers across all users"""
    try:
        with DatabaseService() as db_service:
            markers = db_service.get_most_common_abnormal_markers(limit=limit)
            
            return {
                "status": "success",
                "common_abnormal_markers": markers
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving analytics: {str(e)}")

@app.delete("/cleanup/sessions")
async def cleanup_old_sessions(days_old: int = Query(default=30, ge=1)):
    """Clean up old user sessions"""
    try:
        with DatabaseService() as db_service:
            deleted_count = db_service.cleanup_old_sessions(days_old=days_old)
            
            return {
                "status": "success",
                "message": f"Cleaned up {deleted_count} old sessions"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cleaning up sessions: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)