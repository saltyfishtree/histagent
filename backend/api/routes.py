"""
RESTful API routes for HistAgent.

This module provides REST API endpoints for agent management,
session handling, and historical research operations.
"""

import logging
from typing import Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File, Form
from pydantic import BaseModel, Field

from core.protocols.websocket_protocol import websocket_protocol
from core.protocols.ag_ui_protocol import AGUIEventType

logger = logging.getLogger(__name__)

# Create API router
api_router = APIRouter()


# Pydantic models for API
class SessionInfo(BaseModel):
    """Session information model."""
    session_id: str
    created_at: str
    is_active: bool
    event_count: int
    last_activity: Optional[str] = None


class ResearchRequest(BaseModel):
    """Research request model."""
    query: str = Field(..., description="Research query")
    research_type: str = Field(default="general", description="Type of research")
    sources: List[str] = Field(default_factory=list, description="Specific sources to search")
    language: Optional[str] = Field(default="en", description="Language for research")
    max_results: int = Field(default=10, description="Maximum number of results")


class ResearchResponse(BaseModel):
    """Research response model."""
    session_id: str
    research_id: str
    status: str
    message: str


class DocumentAnalysisRequest(BaseModel):
    """Document analysis request model."""
    document_type: str = Field(..., description="Type of document")
    analysis_type: str = Field(..., description="Type of analysis")
    document_url: Optional[str] = Field(None, description="URL to document")
    language: Optional[str] = Field(default="auto", description="Document language")


class DocumentAnalysisResponse(BaseModel):
    """Document analysis response model."""
    session_id: str
    analysis_id: str
    status: str
    message: str


class EventFilter(BaseModel):
    """Event filter model."""
    event_types: Optional[List[str]] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    limit: int = Field(default=100, ge=1, le=1000)


# Session management endpoints
@api_router.post("/sessions", response_model=SessionInfo)
async def create_session():
    """Create a new session."""
    session_id = str(uuid4())
    
    # This would typically create a session in a database
    # For now, we'll just return the session info
    from datetime import datetime
    
    return SessionInfo(
        session_id=session_id,
        created_at=datetime.now().isoformat(),
        is_active=True,
        event_count=0,
    )


@api_router.get("/sessions", response_model=List[SessionInfo])
async def list_sessions():
    """List all active sessions."""
    active_sessions = websocket_protocol.get_active_sessions()
    
    sessions = []
    for session_id in active_sessions:
        protocol = websocket_protocol.get_protocol(session_id)
        if protocol:
            sessions.append(SessionInfo(
                session_id=session_id,
                created_at="2024-01-01T00:00:00",  # Would come from database
                is_active=True,
                event_count=len(protocol.events),
            ))
    
    return sessions


@api_router.get("/sessions/{session_id}", response_model=SessionInfo)
async def get_session(session_id: str):
    """Get session information."""
    if not websocket_protocol.is_session_active(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    
    protocol = websocket_protocol.get_protocol(session_id)
    if not protocol:
        raise HTTPException(status_code=404, detail="Session protocol not found")
    
    return SessionInfo(
        session_id=session_id,
        created_at="2024-01-01T00:00:00",  # Would come from database
        is_active=True,
        event_count=len(protocol.events),
    )


@api_router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session."""
    if not websocket_protocol.is_session_active(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    
    await websocket_protocol.disconnect(session_id)
    return {"message": "Session deleted successfully"}


# Research endpoints
@api_router.post("/sessions/{session_id}/research", response_model=ResearchResponse)
async def start_research(
    session_id: str,
    request: ResearchRequest,
    background_tasks: BackgroundTasks
):
    """Start a research task."""
    if not websocket_protocol.is_session_active(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    
    protocol = websocket_protocol.get_protocol(session_id)
    if not protocol:
        raise HTTPException(status_code=404, detail="Session protocol not found")
    
    research_id = str(uuid4())
    
    # Create research start event
    research_event = protocol.create_research_event(
        research_type=request.research_type,
        query=request.query,
        metadata={
            "research_id": research_id,
            "sources": request.sources,
            "language": request.language,
            "max_results": request.max_results,
        }
    )
    
    # Schedule background task to process research
    background_tasks.add_task(
        _process_research_task,
        session_id,
        research_id,
        request
    )
    
    await protocol.emit(research_event)
    
    return ResearchResponse(
        session_id=session_id,
        research_id=research_id,
        status="started",
        message="Research task started successfully"
    )


@api_router.post("/sessions/{session_id}/documents/analyze", response_model=DocumentAnalysisResponse)
async def analyze_document(
    session_id: str,
    request: DocumentAnalysisRequest,
    background_tasks: BackgroundTasks
):
    """Analyze a document."""
    if not websocket_protocol.is_session_active(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    
    protocol = websocket_protocol.get_protocol(session_id)
    if not protocol:
        raise HTTPException(status_code=404, detail="Session protocol not found")
    
    analysis_id = str(uuid4())
    
    # Create document analysis start event
    analysis_event = protocol.create_document_analysis_event(
        document_type=request.document_type,
        analysis_type=request.analysis_type,
        metadata={
            "analysis_id": analysis_id,
            "document_url": request.document_url,
            "language": request.language,
        }
    )
    
    # Schedule background task to process document analysis
    background_tasks.add_task(
        _process_document_analysis_task,
        session_id,
        analysis_id,
        request
    )
    
    await protocol.emit(analysis_event)
    
    return DocumentAnalysisResponse(
        session_id=session_id,
        analysis_id=analysis_id,
        status="started",
        message="Document analysis started successfully"
    )


@api_router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
):
    """Upload a file and return file information."""
    try:
        # Generate unique file ID
        file_id = str(uuid4())
        
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Reset file pointer for potential reuse
        await file.seek(0)
        
        # Here you would save the file to storage
        # For now, we'll just return the file information
        
        return {
            "success": True,
            "data": {
                "id": file_id,
                "name": file.filename,
                "type": file.content_type,
                "size": file_size,
                "url": f"/files/{file_id}",  # Would be actual file URL
            },
            "message": "File uploaded successfully"
        }
        
    except Exception as e:
        logger.error(f"File upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@api_router.post("/sessions/{session_id}/documents/upload")
async def upload_document(
    session_id: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    analysis_type: str = Form(...)
):
    """Upload and analyze a document."""
    if not websocket_protocol.is_session_active(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    
    protocol = websocket_protocol.get_protocol(session_id)
    if not protocol:
        raise HTTPException(status_code=404, detail="Session protocol not found")
    
    analysis_id = str(uuid4())
    
    # Save uploaded file (implement proper file handling)
    # For now, we'll just simulate the process
    
    # Create document analysis start event
    analysis_event = protocol.create_document_analysis_event(
        document_type=file.content_type or "unknown",
        analysis_type=analysis_type,
        metadata={
            "analysis_id": analysis_id,
            "filename": file.filename,
            "file_size": file.size,
        }
    )
    
    # Schedule background task to process uploaded document
    background_tasks.add_task(
        _process_uploaded_document_task,
        session_id,
        analysis_id,
        file,
        analysis_type
    )
    
    await protocol.emit(analysis_event)
    
    return DocumentAnalysisResponse(
        session_id=session_id,
        analysis_id=analysis_id,
        status="started",
        message="Document upload and analysis started successfully"
    )


# Event history endpoints
@api_router.get("/sessions/{session_id}/events")
async def get_session_events(
    session_id: str,
    event_filter: Optional[EventFilter] = None
):
    """Get session event history."""
    if not websocket_protocol.is_session_active(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    
    protocol = websocket_protocol.get_protocol(session_id)
    if not protocol:
        raise HTTPException(status_code=404, detail="Session protocol not found")
    
    events = protocol.get_event_history()
    
    # Apply filters if provided
    if event_filter:
        if event_filter.event_types:
            events = [e for e in events if e.type.value in event_filter.event_types]
        
        # Apply time filters (would need proper datetime parsing)
        # if event_filter.start_time:
        #     events = [e for e in events if e.timestamp >= event_filter.start_time]
        # if event_filter.end_time:
        #     events = [e for e in events if e.timestamp <= event_filter.end_time]
        
        events = events[:event_filter.limit]
    
    return {
        "session_id": session_id,
        "events": [
            {
                "id": event.id,
                "type": event.type.value,
                "timestamp": event.timestamp.isoformat(),
                "data": event.data,
                "metadata": event.metadata,
            }
            for event in events
        ],
        "total_count": len(events),
    }


@api_router.delete("/sessions/{session_id}/events")
async def clear_session_events(session_id: str):
    """Clear session event history."""
    if not websocket_protocol.is_session_active(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    
    protocol = websocket_protocol.get_protocol(session_id)
    if not protocol:
        raise HTTPException(status_code=404, detail="Session protocol not found")
    
    protocol.clear_history()
    return {"message": "Session event history cleared"}


# System status endpoints
@api_router.get("/system/status")
async def get_system_status():
    """Get system status."""
    active_sessions = websocket_protocol.get_active_sessions()
    
    return {
        "status": "healthy",
        "active_sessions": len(active_sessions),
        "total_events": sum(
            len(websocket_protocol.get_protocol(session_id).events)
            for session_id in active_sessions
            if websocket_protocol.get_protocol(session_id)
        ),
        "available_event_types": [event_type.value for event_type in AGUIEventType],
    }


# Background task functions
async def _process_research_task(
    session_id: str,
    research_id: str,
    request: ResearchRequest
):
    """Process research task in background."""
    try:
        protocol = websocket_protocol.get_protocol(session_id)
        if not protocol:
            return
        
        # Simulate research progress
        import asyncio
        
        # Progress updates
        for progress in [0.2, 0.5, 0.8]:
            await asyncio.sleep(2)  # Simulate work
            
            progress_event = protocol.create_research_event(
                research_type=request.research_type,
                query=request.query,
                metadata={
                    "research_id": research_id,
                    "progress": progress,
                    "status": "in_progress",
                }
            )
            progress_event.type = AGUIEventType.RESEARCH_PROGRESS
            await protocol.emit(progress_event)
        
        # Final result
        result_event = protocol.create_research_event(
            research_type=request.research_type,
            query=request.query,
            metadata={
                "research_id": research_id,
                "status": "completed",
                "results": [
                    {"title": "Example Result 1", "source": "Academic Source"},
                    {"title": "Example Result 2", "source": "Historical Archive"},
                ]
            }
        )
        result_event.type = AGUIEventType.RESEARCH_END
        await protocol.emit(result_event)
        
    except Exception as e:
        logger.error(f"Error processing research task: {e}")


async def _process_document_analysis_task(
    session_id: str,
    analysis_id: str,
    request: DocumentAnalysisRequest
):
    """Process document analysis task in background."""
    try:
        protocol = websocket_protocol.get_protocol(session_id)
        if not protocol:
            return
        
        # Simulate document analysis
        import asyncio
        
        # Progress updates
        for progress in [0.3, 0.6, 0.9]:
            await asyncio.sleep(1.5)  # Simulate work
            
            progress_event = protocol.create_document_analysis_event(
                document_type=request.document_type,
                analysis_type=request.analysis_type,
                metadata={
                    "analysis_id": analysis_id,
                    "progress": progress,
                    "status": "in_progress",
                }
            )
            progress_event.type = AGUIEventType.DOCUMENT_ANALYSIS_PROGRESS
            await protocol.emit(progress_event)
        
        # Final result
        result_event = protocol.create_document_analysis_event(
            document_type=request.document_type,
            analysis_type=request.analysis_type,
            metadata={
                "analysis_id": analysis_id,
                "status": "completed",
                "results": {
                    "extracted_text": "Example extracted text...",
                    "analysis_summary": "This document appears to be...",
                    "confidence": 0.85,
                }
            }
        )
        result_event.type = AGUIEventType.DOCUMENT_ANALYSIS_END
        await protocol.emit(result_event)
        
    except Exception as e:
        logger.error(f"Error processing document analysis task: {e}")


async def _process_uploaded_document_task(
    session_id: str,
    analysis_id: str,
    file: UploadFile,
    analysis_type: str
):
    """Process uploaded document task in background."""
    try:
        protocol = websocket_protocol.get_protocol(session_id)
        if not protocol:
            return
        
        # Read file content
        content = await file.read()
        
        # Reset file pointer
        await file.seek(0)
        
        # Simulate document processing
        import asyncio
        
        # Progress updates
        for progress in [0.25, 0.5, 0.75]:
            await asyncio.sleep(2)  # Simulate work
            
            progress_event = protocol.create_document_analysis_event(
                document_type=file.content_type or "unknown",
                analysis_type=analysis_type,
                metadata={
                    "analysis_id": analysis_id,
                    "filename": file.filename,
                    "progress": progress,
                    "status": "in_progress",
                }
            )
            progress_event.type = AGUIEventType.DOCUMENT_ANALYSIS_PROGRESS
            await protocol.emit(progress_event)
        
        # Final result
        result_event = protocol.create_document_analysis_event(
            document_type=file.content_type or "unknown",
            analysis_type=analysis_type,
            metadata={
                "analysis_id": analysis_id,
                "filename": file.filename,
                "status": "completed",
                "results": {
                    "file_size": len(content),
                    "analysis_summary": f"Processed {file.filename} successfully",
                    "confidence": 0.9,
                }
            }
        )
        result_event.type = AGUIEventType.DOCUMENT_ANALYSIS_END
        await protocol.emit(result_event)
        
    except Exception as e:
        logger.error(f"Error processing uploaded document task: {e}")
    finally:
        await file.close() 