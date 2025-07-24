"""
WebSocket router for real-time communication.

This module provides WebSocket endpoints for real-time communication
between the frontend and backend.
"""

import json
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import HTMLResponse

from core.protocols.websocket_protocol import websocket_protocol

logger = logging.getLogger(__name__)

# Create WebSocket router
websocket_router = APIRouter()


async def _websocket_handler(
    websocket: WebSocket,
    session_id: Optional[str] = None,
):
    """Shared WebSocket handler for both endpoints."""
    session_id = await websocket_protocol.connect(websocket, session_id)
    
    try:
        while True:
            # Wait for messages from the client
            message_text = await websocket.receive_text()
            
            try:
                # Parse JSON message
                message = json.loads(message_text) if message_text else {}
                await websocket_protocol.handle_message(session_id, message)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON message from {session_id}: {e}")
                # Send error response
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "data": {"message": "Invalid JSON format"},
                    "timestamp": datetime.now().isoformat()
                }))
            except Exception as e:
                logger.error(f"Error processing message from {session_id}: {e}")
                await websocket.send_text(json.dumps({
                    "type": "error", 
                    "data": {"message": str(e)},
                    "timestamp": datetime.now().isoformat()
                }))
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
        await websocket_protocol.disconnect(session_id)
    except Exception as e:
        logger.error(f"Error in WebSocket connection {session_id}: {e}")
        await websocket_protocol.disconnect(session_id)


@websocket_router.websocket("/agent")
async def websocket_agent_endpoint(
    websocket: WebSocket,
    session_id: Optional[str] = Query(None, description="Session ID for reconnection"),
):
    """Main WebSocket endpoint for agent communication."""
    await _websocket_handler(websocket, session_id)


@websocket_router.websocket("")
async def websocket_root_endpoint(websocket: WebSocket):
    """WebSocket endpoint at /ws for frontend compatibility.""" 
    await _websocket_handler(websocket)


@websocket_router.websocket("/")
async def websocket_root_slash_endpoint(websocket: WebSocket):
    """WebSocket endpoint at /ws/ for frontend compatibility.""" 
    await _websocket_handler(websocket)


# Test page for WebSocket connection
@websocket_router.get("/test")
async def websocket_test_page():
    """Test page for WebSocket connection."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>HistAgent WebSocket Test</title>
        <meta charset="UTF-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .container { max-width: 800px; margin: 0 auto; }
            .message-box { 
                height: 300px; 
                border: 1px solid #ccc; 
                padding: 10px; 
                overflow-y: auto; 
                margin-bottom: 10px;
                background: #f9f9f9;
            }
            .controls { margin-bottom: 10px; }
            input[type="text"] { width: 300px; padding: 5px; }
            button { padding: 5px 10px; margin: 0 5px; }
            .status { 
                padding: 10px; 
                margin-bottom: 10px; 
                border-radius: 5px; 
            }
            .connected { background: #d4edda; color: #155724; }
            .disconnected { background: #f8d7da; color: #721c24; }
            .event { 
                margin-bottom: 10px; 
                padding: 8px; 
                background: white; 
                border-left: 4px solid #007bff; 
            }
            .event-type { font-weight: bold; color: #007bff; }
            .event-data { margin-top: 5px; }
            .timestamp { color: #666; font-size: 0.9em; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>HistAgent WebSocket Test</h1>
            
            <div id="status" class="status disconnected">
                Status: Disconnected
            </div>
            
            <div class="controls">
                <button onclick="connect()">Connect</button>
                <button onclick="disconnect()">Disconnect</button>
                <button onclick="clearMessages()">Clear Messages</button>
            </div>
            
            <div class="controls">
                <input type="text" id="messageInput" placeholder="Enter message..." />
                <button onclick="sendMessage()">Send Message</button>
            </div>
            
            <div class="controls">
                <button onclick="subscribeToEvents()">Subscribe to All Events</button>
                <button onclick="sendPing()">Send Ping</button>
            </div>
            
            <div id="messages" class="message-box"></div>
        </div>
        
        <script>
            let ws = null;
            let sessionId = null;
            
            function connect() {
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const wsUrl = `${protocol}//${window.location.host}/ws/agent`;
                
                ws = new WebSocket(wsUrl);
                
                ws.onopen = function(event) {
                    updateStatus('Connected', true);
                    addMessage('Connection opened');
                };
                
                ws.onmessage = function(event) {
                    try {
                        const data = JSON.parse(event.data);
                        displayEvent(data);
                        
                        if (data.type === 'connection_established') {
                            sessionId = data.session_id;
                            addMessage(`Session ID: ${sessionId}`);
                        }
                    } catch (e) {
                        addMessage(`Raw message: ${event.data}`);
                    }
                };
                
                ws.onclose = function(event) {
                    updateStatus('Disconnected', false);
                    addMessage('Connection closed');
                };
                
                ws.onerror = function(error) {
                    updateStatus('Error', false);
                    addMessage(`Error: ${error}`);
                };
            }
            
            function disconnect() {
                if (ws) {
                    ws.close();
                    ws = null;
                }
            }
            
            function sendMessage() {
                const input = document.getElementById('messageInput');
                const message = input.value.trim();
                
                if (message && ws && ws.readyState === WebSocket.OPEN) {
                    const payload = {
                        type: 'user_input',
                        message: message,
                        timestamp: new Date().toISOString()
                    };
                    
                    ws.send(JSON.stringify(payload));
                    input.value = '';
                    addMessage(`Sent: ${message}`);
                }
            }
            
            function subscribeToEvents() {
                if (ws && ws.readyState === WebSocket.OPEN) {
                    const payload = {
                        type: 'subscribe',
                        event_types: [
                            'thought_stream',
                            'tool_start',
                            'tool_end',
                            'research_start',
                            'research_end',
                            'system_status'
                        ]
                    };
                    
                    ws.send(JSON.stringify(payload));
                    addMessage('Subscribed to events');
                }
            }
            
            function sendPing() {
                if (ws && ws.readyState === WebSocket.OPEN) {
                    const payload = {
                        type: 'ping',
                        timestamp: new Date().toISOString()
                    };
                    
                    ws.send(JSON.stringify(payload));
                    addMessage('Ping sent');
                }
            }
            
            function updateStatus(status, connected) {
                const statusDiv = document.getElementById('status');
                statusDiv.textContent = `Status: ${status}`;
                statusDiv.className = `status ${connected ? 'connected' : 'disconnected'}`;
            }
            
            function addMessage(message) {
                const messagesDiv = document.getElementById('messages');
                const messageDiv = document.createElement('div');
                messageDiv.innerHTML = `<span class="timestamp">${new Date().toLocaleTimeString()}</span> ${message}`;
                messagesDiv.appendChild(messageDiv);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }
            
            function displayEvent(event) {
                const messagesDiv = document.getElementById('messages');
                const eventDiv = document.createElement('div');
                eventDiv.className = 'event';
                
                const timestamp = new Date(event.timestamp).toLocaleTimeString();
                const eventType = event.type;
                const eventData = JSON.stringify(event.data, null, 2);
                
                eventDiv.innerHTML = `
                    <div class="event-type">${eventType}</div>
                    <div class="timestamp">${timestamp}</div>
                    <div class="event-data"><pre>${eventData}</pre></div>
                `;
                
                messagesDiv.appendChild(eventDiv);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }
            
            function clearMessages() {
                document.getElementById('messages').innerHTML = '';
            }
            
            // Handle Enter key in message input
            document.getElementById('messageInput').addEventListener('keypress', function(event) {
                if (event.key === 'Enter') {
                    sendMessage();
                }
            });
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content) 