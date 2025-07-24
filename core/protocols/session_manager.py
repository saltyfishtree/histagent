"""
Session Manager for WebSocket connections.

This module manages active sessions and their associated events.
"""

import logging
from datetime import datetime
from typing import Dict, Optional, List
from .ag_ui_protocol import AGUIEvent

logger = logging.getLogger(__name__)


class Session:
    """Represents an active session."""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.events: List[AGUIEvent] = []
        self.active = True
    
    def add_event(self, event: AGUIEvent) -> None:
        """Add an event to this session."""
        self.events.append(event)
        self.last_activity = datetime.now()
    
    def end_session(self) -> None:
        """Mark session as ended."""
        self.active = False


class SessionManager:
    """Manages active WebSocket sessions."""
    
    def __init__(self):
        self.sessions: Dict[str, Session] = {}
    
    async def create_session(self, session_id: str) -> Session:
        """Create a new session."""
        session = Session(session_id)
        self.sessions[session_id] = session
        logger.info(f"Created session {session_id}")
        return session
    
    async def get_session(self, session_id: str) -> Optional[Session]:
        """Get an existing session."""
        return self.sessions.get(session_id)
    
    async def end_session(self, session_id: str) -> None:
        """End a session."""
        if session_id in self.sessions:
            self.sessions[session_id].end_session()
            logger.info(f"Ended session {session_id}")
    
    async def add_event(self, session_id: str, event: AGUIEvent) -> None:
        """Add an event to a session."""
        if session_id in self.sessions:
            self.sessions[session_id].add_event(event)
    
    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs."""
        return [sid for sid, session in self.sessions.items() if session.active]
    
    def cleanup_inactive_sessions(self) -> None:
        """Remove inactive sessions (for cleanup)."""
        inactive_sessions = [
            sid for sid, session in self.sessions.items() 
            if not session.active
        ]
        for sid in inactive_sessions:
            del self.sessions[sid]
            logger.info(f"Cleaned up inactive session {sid}") 