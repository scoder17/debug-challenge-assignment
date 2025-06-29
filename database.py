"""
Database models and configuration for Blood Test Report Analyser
"""

import os
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, JSON
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./blood_test_analyzer.db")

# Create engine
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()

# Database Models
class User(Base):
    """User model for storing user information"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=True)
    full_name = Column(String(255), nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String(10), nullable=True)
    phone = Column(String(20), nullable=True)
    emergency_contact = Column(String(255), nullable=True)
    medical_conditions = Column(Text, nullable=True)  # JSON string of conditions
    medications = Column(Text, nullable=True)  # JSON string of medications
    allergies = Column(Text, nullable=True)  # JSON string of allergies
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    is_active = Column(Boolean, default=True)
    
    # Relationships
    reports = relationship("BloodTestReport", back_populates="user", cascade="all, delete-orphan")
    analyses = relationship("Analysis", back_populates="user", cascade="all, delete-orphan")

class BloodTestReport(Base):
    """Model for storing blood test report information"""
    __tablename__ = "blood_test_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    report_uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=True)  # For temporary storage
    file_size = Column(Integer, nullable=True)
    report_date = Column(DateTime, nullable=True)  # Date when blood test was taken
    lab_name = Column(String(255), nullable=True)
    doctor_name = Column(String(255), nullable=True)
    test_type = Column(String(100), nullable=True)  # Complete Blood Count, Lipid Panel, etc.
    raw_content = Column(Text, nullable=True)  # Extracted PDF content
    processed_content = Column(Text, nullable=True)  # Cleaned and structured content
    blood_markers = Column(Text, nullable=True)  # JSON string of extracted markers
    is_verified = Column(Boolean, default=False)
    verification_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="reports")
    analyses = relationship("Analysis", back_populates="report", cascade="all, delete-orphan")
    markers = relationship("BloodMarker", back_populates="report", cascade="all, delete-orphan")

class BloodMarker(Base):
    """Model for storing individual blood marker values"""
    __tablename__ = "blood_markers"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("blood_test_reports.id"), nullable=False)
    marker_name = Column(String(100), nullable=False)  # e.g., "Hemoglobin", "Cholesterol"
    value = Column(Float, nullable=True)
    unit = Column(String(20), nullable=True)  # e.g., "mg/dL", "g/dL"
    reference_range_min = Column(Float, nullable=True)
    reference_range_max = Column(Float, nullable=True)
    reference_range_text = Column(String(100), nullable=True)  # For non-numeric ranges
    is_normal = Column(Boolean, nullable=True)
    flag = Column(String(10), nullable=True)  # "H" for high, "L" for low, "N" for normal
    category = Column(String(50), nullable=True)  # "Lipids", "CBC", "Liver Function", etc.
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    report = relationship("BloodTestReport", back_populates="markers")

class Analysis(Base):
    """Model for storing analysis results"""
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    report_id = Column(Integer, ForeignKey("blood_test_reports.id"), nullable=False)
    query = Column(Text, nullable=False)  # User's original query
    analysis_type = Column(String(50), nullable=False)  # "medical", "nutrition", "exercise", "comprehensive"
    
    # Analysis results
    medical_summary = Column(Text, nullable=True)
    abnormal_findings = Column(Text, nullable=True)  # JSON string
    health_recommendations = Column(Text, nullable=True)
    nutrition_analysis = Column(Text, nullable=True)
    dietary_recommendations = Column(Text, nullable=True)
    exercise_recommendations = Column(Text, nullable=True)
    supplement_suggestions = Column(Text, nullable=True)  # JSON string
    follow_up_tests = Column(Text, nullable=True)  # JSON string
    risk_factors = Column(Text, nullable=True)  # JSON string
    
    # Metadata
    processing_time = Column(Float, nullable=True)  # Time taken to process in seconds
    confidence_score = Column(Float, nullable=True)  # AI confidence in analysis (0-1)
    reviewed_by_human = Column(Boolean, default=False)
    reviewer_notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="analyses")
    report = relationship("BloodTestReport", back_populates="analyses")

class AnalysisHistory(Base):
    """Model for tracking analysis history and comparisons"""
    __tablename__ = "analysis_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False)
    previous_analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=True)
    comparison_notes = Column(Text, nullable=True)
    trend_analysis = Column(Text, nullable=True)  # JSON string of trends
    improvement_areas = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class UserSession(Base):
    """Model for tracking user sessions and activities"""
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    activity_type = Column(String(50), nullable=False)  # "upload", "analysis", "view_history"
    activity_details = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

# Database utility functions
def create_database():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_session() -> Session:
    """Get database session for direct use"""
    return SessionLocal()

# Database initialization
def init_database():
    """Initialize database with tables"""
    create_database()
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_database()