"""
Database service layer for Blood Test Report Analyser
Handles all database operations and business logic
"""

import json
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_

from database import (
    User, BloodTestReport, BloodMarker, Analysis, 
    AnalysisHistory, UserSession, get_db_session
)

class DatabaseService:
    """Service class for database operations"""
    
    def __init__(self):
        self.db = get_db_session()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()

    # User operations
    def create_user(self, user_data: Dict[str, Any]) -> User:
        """Create a new user"""
        user = User(**user_data)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_user_by_uuid(self, user_uuid: str) -> Optional[User]:
        """Get user by UUID"""
        return self.db.query(User).filter(User.user_uuid == user_uuid).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def update_user(self, user_id: int, user_data: Dict[str, Any]) -> Optional[User]:
        """Update user information"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            for key, value in user_data.items():
                setattr(user, key, value)
            user.updated_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(user)
        return user

    # Blood Test Report operations
    def create_blood_test_report(self, report_data: Dict[str, Any]) -> BloodTestReport:
        """Create a new blood test report"""
        report = BloodTestReport(**report_data)
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report
    
    def get_report_by_uuid(self, report_uuid: str) -> Optional[BloodTestReport]:
        """Get blood test report by UUID"""
        return self.db.query(BloodTestReport).filter(
            BloodTestReport.report_uuid == report_uuid
        ).first()
    
    def get_user_reports(self, user_id: int, limit: int = 10) -> List[BloodTestReport]:
        """Get all reports for a user"""
        return self.db.query(BloodTestReport).filter(
            BloodTestReport.user_id == user_id
        ).order_by(desc(BloodTestReport.created_at)).limit(limit).all()
    
    def update_report_verification(self, report_id: int, is_verified: bool, notes: str = None) -> bool:
        """Update report verification status"""
        report = self.db.query(BloodTestReport).filter(BloodTestReport.id == report_id).first()
        if report:
            report.is_verified = is_verified
            report.verification_notes = notes
            report.updated_at = datetime.now(timezone.utc)
            self.db.commit()
            return True
        return False

    # Blood Marker operations
    def create_blood_markers(self, report_id: int, markers_data: List[Dict[str, Any]]) -> List[BloodMarker]:
        """Create blood markers for a report"""
        markers = []
        for marker_data in markers_data:
            marker_data['report_id'] = report_id
            marker = BloodMarker(**marker_data)
            markers.append(marker)
            self.db.add(marker)
        
        self.db.commit()
        for marker in markers:
            self.db.refresh(marker)
        return markers
    
    def get_report_markers(self, report_id: int) -> List[BloodMarker]:
        """Get all blood markers for a report"""
        return self.db.query(BloodMarker).filter(
            BloodMarker.report_id == report_id
        ).all()
    
    def get_abnormal_markers(self, report_id: int) -> List[BloodMarker]:
        """Get abnormal blood markers for a report"""
        return self.db.query(BloodMarker).filter(
            and_(
                BloodMarker.report_id == report_id,
                BloodMarker.is_normal == False
            )
        ).all()

    # Analysis operations
    def create_analysis(self, analysis_data: Dict[str, Any]) -> Analysis:
        """Create a new analysis"""
        analysis = Analysis(**analysis_data)
        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)
        return analysis
    
    def get_analysis_by_uuid(self, analysis_uuid: str) -> Optional[Analysis]:
        """Get analysis by UUID"""
        return self.db.query(Analysis).filter(
            Analysis.analysis_uuid == analysis_uuid
        ).first()
    
    def get_user_analyses(self, user_id: int, limit: int = 10) -> List[Analysis]:
        """Get all analyses for a user"""
        return self.db.query(Analysis).filter(
            Analysis.user_id == user_id
        ).order_by(desc(Analysis.created_at)).limit(limit).all()
    
    def get_report_analyses(self, report_id: int) -> List[Analysis]:
        """Get all analyses for a specific report"""
        return self.db.query(Analysis).filter(
            Analysis.report_id == report_id
        ).order_by(desc(Analysis.created_at)).all()
    
    def update_analysis(self, analysis_id: int, analysis_data: Dict[str, Any]) -> Optional[Analysis]:
        """Update analysis information"""
        analysis = self.db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if analysis:
            for key, value in analysis_data.items():
                setattr(analysis, key, value)
            analysis.updated_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(analysis)
        return analysis

    # Analysis History operations
    def create_analysis_history(self, history_data: Dict[str, Any]) -> AnalysisHistory:
        """Create analysis history record"""
        history = AnalysisHistory(**history_data)
        self.db.add(history)
        self.db.commit()
        self.db.refresh(history)
        return history
    
    def get_user_analysis_history(self, user_id: int) -> List[AnalysisHistory]:
        """Get analysis history for a user"""
        return self.db.query(AnalysisHistory).filter(
            AnalysisHistory.user_id == user_id
        ).order_by(desc(AnalysisHistory.created_at)).all()

    # User Session operations
    def create_user_session(self, session_data: Dict[str, Any]) -> UserSession:
        """Create a user session record"""
        session = UserSession(**session_data)
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    # Analytics and reporting methods
    def get_user_health_trends(self, user_id: int, marker_name: str) -> List[Dict[str, Any]]:
        """Get health trends for a specific marker over time"""
        results = self.db.query(BloodMarker, BloodTestReport).join(
            BloodTestReport, BloodMarker.report_id == BloodTestReport.id
        ).filter(
            and_(
                BloodTestReport.user_id == user_id,
                BloodMarker.marker_name == marker_name
            )
        ).order_by(BloodTestReport.report_date).all()
        
        trends = []
        for marker, report in results:
            trends.append({
                'date': report.report_date,
                'value': marker.value,
                'unit': marker.unit,
                'is_normal': marker.is_normal,
                'reference_range_min': marker.reference_range_min,
                'reference_range_max': marker.reference_range_max
            })
        
        return trends
    
    def get_most_common_abnormal_markers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most commonly abnormal markers across all users"""
        from sqlalchemy import func
        
        results = self.db.query(
            BloodMarker.marker_name,
            func.count(BloodMarker.id).label('count')
        ).filter(
            BloodMarker.is_normal == False
        ).group_by(
            BloodMarker.marker_name
        ).order_by(
            desc('count')
        ).limit(limit).all()
        
        return [{'marker_name': result[0], 'abnormal_count': result[1]} for result in results]
    
    def get_user_statistics(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive statistics for a user"""
        total_reports = self.db.query(BloodTestReport).filter(
            BloodTestReport.user_id == user_id
        ).count()
        
        total_analyses = self.db.query(Analysis).filter(
            Analysis.user_id == user_id
        ).count()
        
        recent_report = self.db.query(BloodTestReport).filter(
            BloodTestReport.user_id == user_id
        ).order_by(desc(BloodTestReport.created_at)).first()
        
        abnormal_markers_count = 0
        if recent_report:
            abnormal_markers_count = self.db.query(BloodMarker).filter(
                and_(
                    BloodMarker.report_id == recent_report.id,
                    BloodMarker.is_normal == False
                )
            ).count()
        
        return {
            'total_reports': total_reports,
            'total_analyses': total_analyses,
            'recent_report_date': recent_report.created_at if recent_report else None,
            'abnormal_markers_in_recent_report': abnormal_markers_count
        }

    # Utility methods
    def search_reports(self, query: str, user_id: Optional[int] = None) -> List[BloodTestReport]:
        """Search reports by various criteria"""
        search_filter = or_(
            BloodTestReport.lab_name.ilike(f'%{query}%'),
            BloodTestReport.doctor_name.ilike(f'%{query}%'),
            BloodTestReport.test_type.ilike(f'%{query}%')
        )
        
        if user_id:
            search_filter = and_(
                BloodTestReport.user_id == user_id,
                search_filter
            )
        
        return self.db.query(BloodTestReport).filter(search_filter).all()
    
    def cleanup_old_sessions(self, days_old: int = 30) -> int:
        """Clean up old user sessions"""
        from datetime import timedelta
        
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_old)
        deleted_count = self.db.query(UserSession).filter(
            UserSession.created_at < cutoff_date
        ).delete()
        
        self.db.commit()
        return deleted_count

# Utility functions for quick operations
def create_anonymous_user() -> str:
    """Create an anonymous user and return UUID"""
    with DatabaseService() as db_service:
        user = db_service.create_user({
            'full_name': 'Anonymous User',
            'is_active': True
        })
        return user.user_uuid

def store_analysis_result(report_uuid: str, query: str, analysis_result: str, 
                         analysis_type: str = "comprehensive", user_uuid: str = None) -> str:
    """Store analysis result and return analysis UUID"""
    with DatabaseService() as db_service:
        # Get report
        report = db_service.get_report_by_uuid(report_uuid)
        if not report:
            raise ValueError("Report not found")
        
        # Get user if provided
        user_id = None
        if user_uuid:
            user = db_service.get_user_by_uuid(user_uuid)
            if user:
                user_id = user.id
        
        # Create analysis
        analysis_data = {
            'user_id': user_id,
            'report_id': report.id,
            'query': query,
            'analysis_type': analysis_type,
            'medical_summary': analysis_result
        }
        
        analysis = db_service.create_analysis(analysis_data)
        return analysis.analysis_uuid

def get_user_report_history(user_uuid: str) -> List[Dict[str, Any]]:
    """Get user's report history"""
    with DatabaseService() as db_service:
        user = db_service.get_user_by_uuid(user_uuid)
        if not user:
            return []
        
        reports = db_service.get_user_reports(user.id)
        return [
            {
                'uuid': report.report_uuid,
                'filename': report.original_filename,
                'date': report.report_date,
                'created_at': report.created_at,
                'lab_name': report.lab_name,
                'is_verified': report.is_verified
            }
            for report in reports
        ]