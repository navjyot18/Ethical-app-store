"""
SQLAlchemy models for apps and analysis results
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, CheckConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class App(Base):
    """App metadata"""
    __tablename__ = 'apps'
    
    id = Column(Integer, primary_key=True)
    package_name = Column(String(255), unique=True, nullable=False)
    app_name = Column(String(255), nullable=False)
    developer = Column(String(255))
    category = Column(String(100))
    platform = Column(String(20))
    icon_url = Column(Text)
    privacy_policy_url = Column(Text)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to analysis results
    analyses = relationship("AnalysisResult", back_populates="app", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint("platform IN ('android', 'ios', 'both')"),
    )
    
    def __repr__(self):
        return f"<App(id={self.id}, name='{self.app_name}', package='{self.package_name}')>"


class AnalysisResult(Base):
    """Analysis result for an app"""
    __tablename__ = 'analysis_results'
    
    id = Column(Integer, primary_key=True)
    app_id = Column(Integer, ForeignKey('apps.id', ondelete='CASCADE'), nullable=False)
    app_version = Column(String(50))
    analyzed_at = Column(DateTime, default=datetime.utcnow)
    
    # Scores
    overall_score = Column(Integer)
    privacy_score = Column(Integer)
    transparency_score = Column(Integer)
    resource_score = Column(Integer)
    design_score = Column(Integer)
    
    # Raw data as JSONB
    trackers = Column(JSONB)
    permissions = Column(JSONB)
    policy_analysis = Column(JSONB)
    review_summary = Column(JSONB)
    
    # Metadata
    scoring_version = Column(String(20), default='v1.0.0')
    analysis_duration_seconds = Column(Integer)
    
    # Relationship back to app
    app = relationship("App", back_populates="analyses")
    
    __table_args__ = (
        CheckConstraint("overall_score BETWEEN 0 AND 100"),
        CheckConstraint("privacy_score BETWEEN 0 AND 100"),
        CheckConstraint("transparency_score BETWEEN 0 AND 100"),
        CheckConstraint("resource_score BETWEEN 0 AND 100"),
        CheckConstraint("design_score BETWEEN 0 AND 100"),
    )
    
    def __repr__(self):
        return f"<AnalysisResult(id={self.id}, app_id={self.app_id}, score={self.overall_score})>"
