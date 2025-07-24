"""
WebSocket Protocol implementation for real-time communication.

This module handles WebSocket connections and provides real-time
event streaming between the backend and frontend.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4

from fastapi import WebSocket, WebSocketDisconnect

from .ag_ui_protocol import AGUIEvent, AGUIEventType
from .session_manager import SessionManager

logger = logging.getLogger(__name__)


class WebSocketConnection:
    """Represents a WebSocket connection with associated metadata."""
    
    def __init__(self, websocket: WebSocket, session_id: str):
        self.websocket = websocket
        self.session_id = session_id
        self.connected = True
        
    async def send_message(self, message: Dict[str, Any]) -> None:
        """Send a message to the WebSocket client."""
        if not self.connected:
            return
            
        try:
            await self.websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Failed to send message to {self.session_id}: {e}")
            self.connected = False
            
    async def send_raw_message(self, message: Dict[str, Any]) -> None:
        """Send a raw message without AG-UI protocol wrapping."""
        await self.send_message(message)
        
    async def send_ag_ui_event(self, event: AGUIEvent) -> None:
        """Send an AG-UI protocol event."""
        await self.send_message(event.model_dump())
        
    async def close(self) -> None:
        """Close the WebSocket connection."""
        if self.connected:
            try:
                await self.websocket.close()
            except Exception as e:
                logger.error(f"Error closing WebSocket for {self.session_id}: {e}")
            finally:
                self.connected = False


class WebSocketProtocol:
    """Manages WebSocket connections and AG-UI protocol communication."""
    
    def __init__(self):
        self.connections: Dict[str, WebSocketConnection] = {}
        self.session_manager = SessionManager()
        
    async def connect(self, websocket: WebSocket, session_id: Optional[str] = None) -> str:
        """Establish a new WebSocket connection."""
        await websocket.accept()
        
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid4())
        
        # Create connection
        connection = WebSocketConnection(websocket, session_id)
        self.connections[session_id] = connection
        
        # Register session
        await self.session_manager.create_session(session_id)
        
        logger.info(f"New WebSocket connection established for session {session_id}")
        
        # Send connection confirmation
        await connection.send_raw_message({
            "type": "connection_established",
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
        })
        
        return session_id
    
    async def disconnect(self, session_id: str) -> None:
        """Disconnect and clean up a WebSocket connection."""
        if session_id in self.connections:
            connection = self.connections[session_id]
            await connection.close()
            del self.connections[session_id]
            
        # Update session
        await self.session_manager.end_session(session_id)
        
        logger.info(f"WebSocket connection closed for session {session_id}")
    
    async def handle_message(self, session_id: str, message: Dict[str, Any]) -> None:
        """Handle incoming message from WebSocket client."""
        try:
            # Process the message based on type
            message_type = message.get("type")
            
            if message_type == "chat_message":
                await self._handle_chat_message(session_id, message)
            elif message_type == "user_message":
                await self._handle_user_message(session_id, message)
            elif message_type == "tool_request":
                await self._handle_tool_request(session_id, message)
            elif message_type == "research_request":
                await self._handle_research_request(session_id, message)
            elif message_type == "ping":
                await self._handle_ping(session_id)
            else:
                logger.warning(f"Unknown message type: {message_type}")
                
        except Exception as e:
            logger.error(f"Error handling message from {session_id}: {e}")
            await self.send_error(session_id, str(e))
    
    async def send_event(self, session_id: str, event_type: AGUIEventType, data: Any) -> None:
        """Send an AG-UI event to a specific session."""
        if session_id not in self.connections:
            logger.warning(f"Attempted to send event to non-existent session: {session_id}")
            return
        
        event = AGUIEvent(
            type=event_type,
            data=data,
            timestamp=datetime.now()
        )
        
        connection = self.connections[session_id]
        await connection.send_ag_ui_event(event)
        
        # Update session
        await self.session_manager.add_event(session_id, event)
    
    async def broadcast_event(self, event_type: AGUIEventType, data: Any) -> None:
        """Broadcast an AG-UI event to all connected sessions."""
        event = AGUIEvent(
            type=event_type,
            data=data,
            timestamp=datetime.now()
        )
        
        for session_id, connection in self.connections.items():
            if connection.connected:
                await connection.send_ag_ui_event(event)
                await self.session_manager.add_event(session_id, event)
    
    async def send_error(self, session_id: str, error_message: str) -> None:
        """Send an error message to a specific session."""
        await self.send_event(session_id, AGUIEventType.ERROR, {
            "message": error_message,
            "timestamp": datetime.now().isoformat()
        })
    
    async def _handle_chat_message(self, session_id: str, message: Dict[str, Any]) -> None:
        """Handle chat message from client."""
        content = message.get("data", {}).get("content", "")
        
        # Send thinking process event
        await self.send_event(session_id, AGUIEventType.THOUGHT_STREAM, {
            "thought": f"Processing user message: {content[:50]}...",
            "confidence": 0.8
        })
        
        # Simulate AI response (replace with actual AI integration)
        response = f"I received your message: {content}. This is a demo response."
        
        await self.send_event(session_id, AGUIEventType.CHAT_RESPONSE, {
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
    
    async def _handle_tool_request(self, session_id: str, message: Dict[str, Any]) -> None:
        """Handle tool execution request from client."""
        tool_name = message.get("data", {}).get("tool", "")
        parameters = message.get("data", {}).get("parameters", {})
        
        # Send tool start event
        await self.send_event(session_id, AGUIEventType.TOOL_START, {
            "tool": tool_name,
            "parameters": parameters
        })
        
        # Simulate tool execution
        await asyncio.sleep(1)  # Simulate processing time
        
        # Send tool result
        await self.send_event(session_id, AGUIEventType.TOOL_RESULT, {
            "tool": tool_name,
            "result": f"Tool {tool_name} executed successfully",
            "status": "completed"
        })
    
    async def _handle_research_request(self, session_id: str, message: Dict[str, Any]) -> None:
        """Handle research request from client."""
        query = message.get("data", {}).get("query", "")
        
        # Send research start event
        await self.send_event(session_id, AGUIEventType.RESEARCH_START, {
            "query": query,
            "estimated_duration": "2-3 minutes"
        })
        
        # Simulate research process
        steps = [
            "Searching historical databases...",
            "Analyzing documents...",
            "Cross-referencing sources...",
            "Generating summary..."
        ]
        
        for i, step in enumerate(steps):
            await self.send_event(session_id, AGUIEventType.RESEARCH_PROGRESS, {
                "step": step,
                "progress": (i + 1) / len(steps),
                "current_step": i + 1,
                "total_steps": len(steps)
            })
            await asyncio.sleep(0.5)  # Simulate processing time
        
        # Send research result
        await self.send_event(session_id, AGUIEventType.RESEARCH_RESULT, {
            "query": query,
            "summary": f"Research completed for: {query}",
            "sources": ["Source 1", "Source 2", "Source 3"],
            "confidence": 0.85
        })
    
    def get_connected_sessions(self) -> Set[str]:
        """Get all currently connected session IDs."""
        return {sid for sid, conn in self.connections.items() if conn.connected}
    
    def get_active_sessions(self) -> List[str]:
        """Get all active session IDs (alias for get_connected_sessions)."""
        return list(self.get_connected_sessions())
    
    def is_session_connected(self, session_id: str) -> bool:
        """Check if a session is currently connected."""
        return session_id in self.connections and self.connections[session_id].connected
    
    def is_session_active(self, session_id: str) -> bool:
        """Check if a session is active (alias for is_session_connected)."""
        return self.is_session_connected(session_id)

    async def _handle_user_message(self, session_id: str, message: Dict[str, Any]) -> None:
        """Handle user message from frontend."""
        data = message.get("data", {})
        content = data.get("content", "")
        attachments = data.get("attachments", [])
        
        logger.info(f"Received user message from {session_id}: {content[:100]}...")
        
        # Send message response back to frontend
        await self._send_message_response(session_id, {
            "type": "message",
            "data": {
                "content": f"收到您的消息：{content}\n\n这是一个演示回复。HistAgent正在处理您的请求...",
                "attachments": []
            },
            "timestamp": datetime.now().isoformat()
        })
        
        # If there are attachments, process them
        if attachments:
            await self._process_attachments(session_id, attachments)

    async def _handle_ping(self, session_id: str) -> None:
        """Handle ping message for heartbeat."""
        if session_id in self.connections:
            connection = self.connections[session_id]
            await connection.send_raw_message({
                "type": "pong",
                "timestamp": datetime.now().isoformat()
            })

    async def _send_message_response(self, session_id: str, response: Dict[str, Any]) -> None:
        """Send a message response to the frontend."""
        if session_id in self.connections:
            connection = self.connections[session_id]
            await connection.send_raw_message(response)

    async def _process_attachments(self, session_id: str, attachments: list) -> None:
        """Process file attachments."""
        for attachment in attachments:
            logger.info(f"Processing attachment: {attachment.get('name', 'unknown')}")
            # Here you would implement actual file processing
            # For now, just send a confirmation
            await self._send_message_response(session_id, {
                "type": "message", 
                "data": {
                    "content": f"已接收附件：{attachment.get('name', 'unknown file')}",
                    "attachments": []
                },
                "timestamp": datetime.now().isoformat()
            })


# Global instance
websocket_protocol = WebSocketProtocol() 