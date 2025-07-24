"""
Unit tests for AG-UI protocol implementation.
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from core.protocols.ag_ui_protocol import (
    AGUIProtocol,
    AGUIEvent,
    AGUIEventType,
    ThoughtEvent,
    ToolEvent,
    ResearchEvent,
    DocumentAnalysisEvent,
    UserInteractionEvent,
    SystemStatusEvent,
)


class TestAGUIProtocol:
    """Test cases for AGUIProtocol class."""

    def test_protocol_initialization(self):
        """Test protocol initialization."""
        session_id = "test_session_123"
        protocol = AGUIProtocol(session_id)
        
        assert protocol.session_id == session_id
        assert protocol.events == []
        assert protocol.subscribers == []

    def test_subscribe_unsubscribe(self):
        """Test subscription and unsubscription."""
        protocol = AGUIProtocol("test_session")
        callback = MagicMock()
        
        # Test subscription
        protocol.subscribe(callback)
        assert callback in protocol.subscribers
        
        # Test unsubscription
        protocol.unsubscribe(callback)
        assert callback not in protocol.subscribers

    @pytest.mark.asyncio
    async def test_emit_event(self):
        """Test event emission."""
        protocol = AGUIProtocol("test_session")
        callback = AsyncMock()
        
        protocol.subscribe(callback)
        
        # Create and emit event
        event = AGUIEvent(
            type=AGUIEventType.SYSTEM_STATUS,
            data={"status": "healthy"}
        )
        
        await protocol.emit(event)
        
        # Verify event was added to history
        assert len(protocol.events) == 1
        assert protocol.events[0].session_id == "test_session"
        
        # Verify callback was called
        callback.assert_called_once_with(event)

    def test_create_thought_event(self):
        """Test thought event creation."""
        protocol = AGUIProtocol("test_session")
        content = "I need to analyze this historical document."
        
        event = protocol.create_thought_event(content)
        
        assert isinstance(event, ThoughtEvent)
        assert event.content == content
        assert event.type == AGUIEventType.THOUGHT_STREAM
        assert event.session_id == "test_session"

    def test_create_tool_event(self):
        """Test tool event creation."""
        protocol = AGUIProtocol("test_session")
        tool_name = "document_analyzer"
        tool_input = {"document_url": "https://example.com/doc.pdf"}
        
        event = protocol.create_tool_event(tool_name, tool_input)
        
        assert isinstance(event, ToolEvent)
        assert event.tool_name == tool_name
        assert event.tool_input == tool_input
        assert event.type == AGUIEventType.TOOL_START
        assert event.session_id == "test_session"

    def test_create_research_event(self):
        """Test research event creation."""
        protocol = AGUIProtocol("test_session")
        research_type = "document_analysis"
        query = "Find information about World War II"
        
        event = protocol.create_research_event(research_type, query)
        
        assert isinstance(event, ResearchEvent)
        assert event.research_type == research_type
        assert event.query == query
        assert event.type == AGUIEventType.RESEARCH_START
        assert event.session_id == "test_session"

    def test_create_document_analysis_event(self):
        """Test document analysis event creation."""
        protocol = AGUIProtocol("test_session")
        document_type = "pdf"
        analysis_type = "ocr"
        
        event = protocol.create_document_analysis_event(document_type, analysis_type)
        
        assert isinstance(event, DocumentAnalysisEvent)
        assert event.document_type == document_type
        assert event.analysis_type == analysis_type
        assert event.type == AGUIEventType.DOCUMENT_ANALYSIS_START
        assert event.session_id == "test_session"

    def test_create_user_interaction_event(self):
        """Test user interaction event creation."""
        protocol = AGUIProtocol("test_session")
        interaction_type = "approval_request"
        message = "Do you want to proceed with the analysis?"
        
        event = protocol.create_user_interaction_event(interaction_type, message)
        
        assert isinstance(event, UserInteractionEvent)
        assert event.interaction_type == interaction_type
        assert event.message == message
        assert event.type == AGUIEventType.USER_INPUT
        assert event.session_id == "test_session"

    def test_create_system_status_event(self):
        """Test system status event creation."""
        protocol = AGUIProtocol("test_session")
        status = "healthy"
        
        event = protocol.create_system_status_event(status)
        
        assert isinstance(event, SystemStatusEvent)
        assert event.status == status
        assert event.type == AGUIEventType.SYSTEM_STATUS
        assert event.session_id == "test_session"

    def test_get_event_history(self):
        """Test event history retrieval."""
        protocol = AGUIProtocol("test_session")
        
        # Add some events
        event1 = AGUIEvent(type=AGUIEventType.SYSTEM_STATUS, data={"status": "healthy"})
        event2 = AGUIEvent(type=AGUIEventType.THOUGHT_STREAM, data={"content": "thinking..."})
        
        protocol.events.extend([event1, event2])
        
        # Get all events
        all_events = protocol.get_event_history()
        assert len(all_events) == 2
        
        # Get filtered events
        status_events = protocol.get_event_history(AGUIEventType.SYSTEM_STATUS)
        assert len(status_events) == 1
        assert status_events[0].type == AGUIEventType.SYSTEM_STATUS

    def test_clear_history(self):
        """Test event history clearing."""
        protocol = AGUIProtocol("test_session")
        
        # Add some events
        event = AGUIEvent(type=AGUIEventType.SYSTEM_STATUS, data={"status": "healthy"})
        protocol.events.append(event)
        
        assert len(protocol.events) == 1
        
        # Clear history
        protocol.clear_history()
        assert len(protocol.events) == 0


class TestAGUIEvent:
    """Test cases for AGUIEvent and its subclasses."""

    def test_agui_event_creation(self):
        """Test basic AGUIEvent creation."""
        event = AGUIEvent(
            type=AGUIEventType.SYSTEM_STATUS,
            data={"status": "healthy"}
        )
        
        assert event.type == AGUIEventType.SYSTEM_STATUS
        assert event.data == {"status": "healthy"}
        assert event.session_id is None
        assert event.agent_id is None
        assert isinstance(event.timestamp, datetime)
        assert event.id is not None

    def test_thought_event_creation(self):
        """Test ThoughtEvent creation."""
        content = "I need to analyze this document."
        event = ThoughtEvent(content)
        
        assert event.content == content
        assert event.type == AGUIEventType.THOUGHT_STREAM
        assert event.data["content"] == content

    def test_tool_event_creation(self):
        """Test ToolEvent creation."""
        tool_name = "document_analyzer"
        tool_input = {"document_url": "https://example.com/doc.pdf"}
        
        event = ToolEvent(tool_name, tool_input)
        
        assert event.tool_name == tool_name
        assert event.tool_input == tool_input
        assert event.type == AGUIEventType.TOOL_START
        assert event.status == "running"

    def test_research_event_creation(self):
        """Test ResearchEvent creation."""
        research_type = "document_analysis"
        query = "Find information about World War II"
        
        event = ResearchEvent(research_type, query)
        
        assert event.research_type == research_type
        assert event.query == query
        assert event.type == AGUIEventType.RESEARCH_START
        assert event.sources == []
        assert event.findings == []

    def test_document_analysis_event_creation(self):
        """Test DocumentAnalysisEvent creation."""
        document_type = "pdf"
        analysis_type = "ocr"
        
        event = DocumentAnalysisEvent(document_type, analysis_type)
        
        assert event.document_type == document_type
        assert event.analysis_type == analysis_type
        assert event.type == AGUIEventType.DOCUMENT_ANALYSIS_START
        assert event.progress is None
        assert event.results is None

    def test_user_interaction_event_creation(self):
        """Test UserInteractionEvent creation."""
        interaction_type = "approval_request"
        message = "Do you want to proceed?"
        
        event = UserInteractionEvent(interaction_type, message)
        
        assert event.interaction_type == interaction_type
        assert event.message == message
        assert event.type == AGUIEventType.USER_INPUT
        assert event.options is None
        assert event.timeout is None

    def test_system_status_event_creation(self):
        """Test SystemStatusEvent creation."""
        status = "healthy"
        
        event = SystemStatusEvent(status)
        
        assert event.status == status
        assert event.type == AGUIEventType.SYSTEM_STATUS
        assert event.message is None
        assert event.metrics is None


class TestAGUIEventType:
    """Test cases for AGUIEventType enum."""

    def test_event_type_values(self):
        """Test event type values."""
        assert AGUIEventType.AGENT_START == "agent_start"
        assert AGUIEventType.THOUGHT_STREAM == "thought_stream"
        assert AGUIEventType.TOOL_START == "tool_start"
        assert AGUIEventType.RESEARCH_START == "research_start"
        assert AGUIEventType.DOCUMENT_ANALYSIS_START == "document_analysis_start"
        assert AGUIEventType.USER_INPUT == "user_input"
        assert AGUIEventType.SYSTEM_STATUS == "system_status"

    def test_event_type_enum_behavior(self):
        """Test event type enum behavior."""
        # Test enum iteration
        event_types = list(AGUIEventType)
        assert len(event_types) > 0
        
        # Test enum value access
        assert AGUIEventType("agent_start") == AGUIEventType.AGENT_START
        
        # Test invalid value
        with pytest.raises(ValueError):
            AGUIEventType("invalid_event_type") 