"""
AG-UI Protocol implementation for HistAgent.

This module defines the standardized communication protocol between
agents and the user interface, supporting real-time streaming of
agent thoughts, tool calls, and results.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

from pydantic import BaseModel, Field


class AGUIEventType(str, Enum):
    """Event types for AG-UI protocol."""
    
    # Agent lifecycle events
    AGENT_START = "agent_start"
    AGENT_END = "agent_end"
    AGENT_ERROR = "agent_error"
    
    # Thinking process events
    THOUGHT_START = "thought_start"
    THOUGHT_STREAM = "thought_stream"
    THOUGHT_END = "thought_end"
    
    # Tool execution events
    TOOL_START = "tool_start"
    TOOL_STREAM = "tool_stream"
    TOOL_END = "tool_end"
    TOOL_ERROR = "tool_error"
    
    # User interaction events
    USER_INPUT = "user_input"
    USER_APPROVAL = "user_approval"
    USER_REJECTION = "user_rejection"
    
    # Response events
    RESPONSE_START = "response_start"
    RESPONSE_STREAM = "response_stream"
    RESPONSE_END = "response_end"
    
    # System events
    SYSTEM_STATUS = "system_status"
    SYSTEM_ERROR = "system_error"
    
    # Historical research specific events
    RESEARCH_START = "research_start"
    RESEARCH_PROGRESS = "research_progress"
    RESEARCH_RESULT = "research_result"
    RESEARCH_END = "research_end"
    
    # Document analysis events
    DOCUMENT_ANALYSIS_START = "document_analysis_start"
    DOCUMENT_ANALYSIS_PROGRESS = "document_analysis_progress"
    DOCUMENT_ANALYSIS_END = "document_analysis_end"
    
    # Literature search events
    LITERATURE_SEARCH_START = "literature_search_start"
    LITERATURE_SEARCH_PROGRESS = "literature_search_progress"
    LITERATURE_SEARCH_END = "literature_search_end"


class AGUIEvent(BaseModel):
    """Base event structure for AG-UI protocol."""
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: AGUIEventType
    timestamp: datetime = Field(default_factory=datetime.now)
    session_id: Optional[str] = None
    agent_id: Optional[str] = None
    data: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        use_enum_values = True


class ThoughtEvent(AGUIEvent):
    """Event for agent thinking process."""
    
    content: str
    confidence: Optional[float] = None
    reasoning_type: Optional[str] = None  # e.g., "analytical", "creative", "logical"
    
    def __init__(self, content: str, **kwargs):
        super().__init__(
            type=AGUIEventType.THOUGHT_STREAM,
            data={"content": content},
            **kwargs
        )
        self.content = content


class ToolEvent(AGUIEvent):
    """Event for tool execution."""
    
    tool_name: str
    tool_input: Dict[str, Any]
    tool_output: Optional[Dict[str, Any]] = None
    status: str = "running"  # "running", "completed", "failed"
    progress: Optional[float] = None
    
    def __init__(self, tool_name: str, tool_input: Dict[str, Any], **kwargs):
        super().__init__(
            type=AGUIEventType.TOOL_START,
            data={
                "tool_name": tool_name,
                "tool_input": tool_input,
                "status": "running",
            },
            **kwargs
        )
        self.tool_name = tool_name
        self.tool_input = tool_input


class ResearchEvent(AGUIEvent):
    """Event for historical research process."""
    
    research_type: str  # "document_analysis", "literature_search", "timeline_construction"
    query: str
    sources: List[str] = Field(default_factory=list)
    findings: List[Dict[str, Any]] = Field(default_factory=list)
    confidence_score: Optional[float] = None
    
    def __init__(self, research_type: str, query: str, **kwargs):
        super().__init__(
            type=AGUIEventType.RESEARCH_START,
            data={
                "research_type": research_type,
                "query": query,
            },
            **kwargs
        )
        self.research_type = research_type
        self.query = query


class DocumentAnalysisEvent(AGUIEvent):
    """Event for document analysis process."""
    
    document_type: str  # "image", "pdf", "text", "audio", "video"
    document_url: Optional[str] = None
    document_name: Optional[str] = None
    analysis_type: str  # "ocr", "translation", "summarization", "fact_extraction"
    progress: Optional[float] = None
    results: Optional[Dict[str, Any]] = None
    
    def __init__(self, document_type: str, analysis_type: str, **kwargs):
        super().__init__(
            type=AGUIEventType.DOCUMENT_ANALYSIS_START,
            data={
                "document_type": document_type,
                "analysis_type": analysis_type,
            },
            **kwargs
        )
        self.document_type = document_type
        self.analysis_type = analysis_type


class UserInteractionEvent(AGUIEvent):
    """Event for user interaction."""
    
    interaction_type: str  # "approval_request", "input_request", "clarification_request"
    message: str
    options: Optional[List[str]] = None
    timeout: Optional[int] = None  # seconds
    
    def __init__(self, interaction_type: str, message: str, **kwargs):
        super().__init__(
            type=AGUIEventType.USER_INPUT,
            data={
                "interaction_type": interaction_type,
                "message": message,
            },
            **kwargs
        )
        self.interaction_type = interaction_type
        self.message = message


class SystemStatusEvent(AGUIEvent):
    """Event for system status updates."""
    
    status: str  # "healthy", "degraded", "error"
    message: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    
    def __init__(self, status: str, **kwargs):
        super().__init__(
            type=AGUIEventType.SYSTEM_STATUS,
            data={"status": status},
            **kwargs
        )
        self.status = status


class AGUIProtocol:
    """Main protocol handler for AG-UI communication."""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.events: List[AGUIEvent] = []
        self.subscribers: List[callable] = []
    
    def subscribe(self, callback: callable) -> None:
        """Subscribe to protocol events."""
        self.subscribers.append(callback)
    
    def unsubscribe(self, callback: callable) -> None:
        """Unsubscribe from protocol events."""
        if callback in self.subscribers:
            self.subscribers.remove(callback)
    
    async def emit(self, event: AGUIEvent) -> None:
        """Emit an event to all subscribers."""
        event.session_id = self.session_id
        self.events.append(event)
        
        for callback in self.subscribers:
            try:
                await callback(event)
            except Exception as e:
                print(f"Error in event callback: {e}")
    
    def create_thought_event(self, content: str, **kwargs) -> ThoughtEvent:
        """Create a thought event."""
        return ThoughtEvent(content=content, session_id=self.session_id, **kwargs)
    
    def create_tool_event(self, tool_name: str, tool_input: Dict[str, Any], **kwargs) -> ToolEvent:
        """Create a tool event."""
        return ToolEvent(tool_name=tool_name, tool_input=tool_input, session_id=self.session_id, **kwargs)
    
    def create_research_event(self, research_type: str, query: str, **kwargs) -> ResearchEvent:
        """Create a research event."""
        return ResearchEvent(research_type=research_type, query=query, session_id=self.session_id, **kwargs)
    
    def create_document_analysis_event(self, document_type: str, analysis_type: str, **kwargs) -> DocumentAnalysisEvent:
        """Create a document analysis event."""
        return DocumentAnalysisEvent(
            document_type=document_type,
            analysis_type=analysis_type,
            session_id=self.session_id,
            **kwargs
        )
    
    def create_user_interaction_event(self, interaction_type: str, message: str, **kwargs) -> UserInteractionEvent:
        """Create a user interaction event."""
        return UserInteractionEvent(
            interaction_type=interaction_type,
            message=message,
            session_id=self.session_id,
            **kwargs
        )
    
    def create_system_status_event(self, status: str, **kwargs) -> SystemStatusEvent:
        """Create a system status event."""
        return SystemStatusEvent(status=status, session_id=self.session_id, **kwargs)
    
    def get_event_history(self, event_type: Optional[AGUIEventType] = None) -> List[AGUIEvent]:
        """Get event history, optionally filtered by type."""
        if event_type is None:
            return self.events.copy()
        return [event for event in self.events if event.type == event_type]
    
    def clear_history(self) -> None:
        """Clear event history."""
        self.events.clear() 