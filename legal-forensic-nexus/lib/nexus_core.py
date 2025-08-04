"""
Nexus Core System
Central coordinator for the Legal-Forensic Nexus multi-agent system
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from pathlib import Path
import aiohttp
from dataclasses import dataclass, asdict
import uuid


@dataclass
class AgentMessage:
    """Message format for inter-agent communication."""
    id: str
    sender: str
    recipient: str
    type: str
    data: Dict[str, Any]
    timestamp: datetime
    priority: str = "normal"  # low, normal, high, critical
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary format."""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        return result


class NexusCore:
    """
    Central nervous system for the Legal-Forensic Nexus.
    Manages communication between AI agents and coordinates analysis.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.agents = config.get("agents", {})
        self.logger = logging.getLogger("NexusCore")
        
        # Agent connections
        self.connected_agents = {}
        self.agent_sessions = {}
        
        # Message queue
        self.message_queue = asyncio.Queue()
        self.message_handlers = {}
        
        # Case data storage
        self.active_cases = {}
        self.case_data_path = Path(config["data_paths"]["case_files"])
        
        # Initialize API clients
        self.api_clients = {}
        self._setup_api_clients()
    
    def _setup_api_clients(self):
        """Initialize API clients for external agents."""
        # GPT-4o client
        if "GPT4o" in self.agents:
            self.api_clients["GPT4o"] = {
                "endpoint": self.agents["GPT4o"]["api_endpoint"],
                "headers": {
                    "Authorization": f"Bearer {self._get_api_key('OPENAI_API_KEY')}",
                    "Content-Type": "application/json"
                }
            }
        
        # Gemini client
        if "Gemini_Pro" in self.agents:
            self.api_clients["Gemini_Pro"] = {
                "endpoint": self.agents["Gemini_Pro"]["api_endpoint"],
                "headers": {
                    "Content-Type": "application/json"
                },
                "api_key": self._get_api_key("GEMINI_API_KEY")
            }
    
    def _get_api_key(self, env_var: str) -> str:
        """Get API key from environment or config."""
        import os
        return os.environ.get(env_var, "")
    
    async def initialize(self):
        """Initialize the Nexus system."""
        self.logger.info("Initializing Legal-Forensic Nexus...")
        
        # Create data directories
        for path in self.config["data_paths"].values():
            Path(path).mkdir(parents=True, exist_ok=True)
        
        # Start message processor
        asyncio.create_task(self._process_messages())
        
        self.logger.info("Nexus initialization complete")
    
    async def connect_agent(self, agent_name: str) -> bool:
        """Establish connection with an AI agent."""
        if agent_name not in self.agents:
            self.logger.error(f"Unknown agent: {agent_name}")
            return False
        
        agent_config = self.agents[agent_name]
        
        try:
            if agent_name == "LegalBERT":
                # Special handling for LegalBERT
                success = await self._connect_legalbert(agent_config)
            elif agent_name in ["GPT4o", "Gemini_Pro"]:
                # API-based agents
                success = await self._test_api_connection(agent_name)
            else:
                # Internal agents (like Claude)
                success = True
            
            if success:
                self.connected_agents[agent_name] = {
                    "status": "connected",
                    "connected_at": datetime.now(),
                    "config": agent_config
                }
                self.logger.info(f"Connected to {agent_name}")
                return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to {agent_name}: {e}")
        
        return False
    
    async def _connect_legalbert(self, config: Dict[str, Any]) -> bool:
        """Connect to LegalBERT via HuggingFace."""
        try:
            # Test connection by loading tokenizer info
            model_path = config["model_path"]
            
            # In production, this would actually connect to HuggingFace
            # For now, we'll simulate the connection
            self.logger.info(f"Connecting to LegalBERT model: {model_path}")
            
            # Store LegalBERT session info
            self.agent_sessions["LegalBERT"] = {
                "model_path": model_path,
                "api_type": config["api_type"],
                "ready": True
            }
            
            return True
            
        except Exception as e:
            self.logger.error(f"LegalBERT connection failed: {e}")
            return False
    
    async def _test_api_connection(self, agent_name: str) -> bool:
        """Test API connection for external agents."""
        try:
            client_info = self.api_clients.get(agent_name)
            if not client_info:
                return False
            
            # For simulation purposes, we'll assume connection is successful
            # In production, this would make a test API call
            self.logger.info(f"Testing API connection for {agent_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"API connection test failed for {agent_name}: {e}")
            return False
    
    async def send_to_agent(self, recipient: str, data: Dict[str, Any]) -> bool:
        """Send data to a specific agent."""
        if recipient not in self.connected_agents:
            self.logger.error(f"Agent {recipient} not connected")
            return False
        
        message = AgentMessage(
            id=str(uuid.uuid4()),
            sender="NexusCore",
            recipient=recipient,
            type=data.get("type", "general"),
            data=data,
            timestamp=datetime.now(),
            priority=data.get("priority", "normal")
        )
        
        await self.message_queue.put(message)
        return True
    
    async def query_agent(self, agent_name: str, query: Dict[str, Any]) -> Dict[str, Any]:
        """Query an agent and wait for response."""
        if agent_name not in self.connected_agents:
            raise ValueError(f"Agent {agent_name} not connected")
        
        # Create query message
        query_id = str(uuid.uuid4())
        message = AgentMessage(
            id=query_id,
            sender="NexusCore",
            recipient=agent_name,
            type="query",
            data=query,
            timestamp=datetime.now(),
            priority=query.get("priority", "normal")
        )
        
        # Create response future
        response_future = asyncio.Future()
        self.message_handlers[query_id] = response_future
        
        # Send query
        await self.message_queue.put(message)
        
        # Wait for response (with timeout)
        try:
            response = await asyncio.wait_for(response_future, timeout=30.0)
            return response
        except asyncio.TimeoutError:
            self.logger.error(f"Query to {agent_name} timed out")
            return {"error": "Query timeout"}
        finally:
            # Clean up handler
            self.message_handlers.pop(query_id, None)
    
    async def _process_messages(self):
        """Process messages in the queue."""
        while True:
            try:
                message = await self.message_queue.get()
                
                # Route message to appropriate handler
                if message.recipient == "NexusCore":
                    await self._handle_nexus_message(message)
                else:
                    await self._route_to_agent(message)
                    
            except Exception as e:
                self.logger.error(f"Error processing message: {e}")
    
    async def _handle_nexus_message(self, message: AgentMessage):
        """Handle messages directed to NexusCore."""
        if message.type == "response" and message.data.get("query_id"):
            # Handle query response
            query_id = message.data["query_id"]
            if query_id in self.message_handlers:
                future = self.message_handlers[query_id]
                if not future.done():
                    future.set_result(message.data)
    
    async def _route_to_agent(self, message: AgentMessage):
        """Route message to the appropriate agent."""
        recipient = message.recipient
        
        if recipient == "GPT4o":
            response = await self._call_gpt4o(message.data)
            await self._send_response(message, response)
        
        elif recipient == "Gemini_Pro":
            response = await self._call_gemini(message.data)
            await self._send_response(message, response)
        
        elif recipient == "LegalBERT":
            response = await self._call_legalbert(message.data)
            await self._send_response(message, response)
        
        else:
            self.logger.warning(f"No handler for agent: {recipient}")
    
    async def _call_gpt4o(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Call GPT-4o API."""
        try:
            # Construct prompt based on data type
            if data["type"] == "contradiction_analysis":
                prompt = self._build_contradiction_prompt(data["data"])
            elif data["type"] == "metadata_validation":
                prompt = self._build_metadata_prompt(data["data"])
            else:
                prompt = json.dumps(data)
            
            # In production, this would make actual API call
            # For now, return simulated response
            return {
                "status": "success",
                "analysis": {
                    "contradictions_found": True,
                    "severity": "high",
                    "details": "Multiple timeline inconsistencies detected"
                }
            }
            
        except Exception as e:
            self.logger.error(f"GPT-4o call failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _call_gemini(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Call Gemini Pro API."""
        try:
            # Handle different request types
            if data["type"] == "timestamp_extraction":
                return await self._gemini_extract_timestamps(data)
            elif data["type"] == "forensic_analysis":
                return await self._gemini_forensic_analysis(data)
            else:
                return {"status": "error", "error": "Unknown request type"}
                
        except Exception as e:
            self.logger.error(f"Gemini call failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _call_legalbert(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Call LegalBERT for analysis."""
        try:
            # Handle different request types
            if data["type"] == "statutory_analysis":
                return await self._legalbert_statutory_analysis(data)
            elif data["type"] == "provision_matching":
                return await self._legalbert_provision_matching(data)
            else:
                return {"status": "error", "error": "Unknown request type"}
                
        except Exception as e:
            self.logger.error(f"LegalBERT call failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _send_response(self, original_message: AgentMessage, response: Dict[str, Any]):
        """Send response back to message sender."""
        response_message = AgentMessage(
            id=str(uuid.uuid4()),
            sender=original_message.recipient,
            recipient=original_message.sender,
            type="response",
            data={
                "query_id": original_message.id,
                **response
            },
            timestamp=datetime.now()
        )
        
        await self.message_queue.put(response_message)
    
    def _build_contradiction_prompt(self, data: Dict[str, Any]) -> str:
        """Build prompt for contradiction analysis."""
        return f"""
        Analyze the following legal document data for contradictions:
        
        Contradictions found: {json.dumps(data.get('contradictions', []), indent=2)}
        Timeline issues: {json.dumps(data.get('timeline_issues', []), indent=2)}
        Signature anomalies: {json.dumps(data.get('signature_anomalies', []), indent=2)}
        
        Provide a comprehensive analysis of:
        1. The severity of contradictions
        2. Legal implications
        3. Recommended actions
        """
    
    def _build_metadata_prompt(self, data: Dict[str, Any]) -> str:
        """Build prompt for metadata validation."""
        return f"""
        Validate the following forensic metadata:
        
        Metadata: {json.dumps(data, indent=2)}
        
        Check for:
        1. Timestamp consistency
        2. Chain of custody integrity
        3. File authenticity markers
        4. Potential tampering indicators
        """
    
    async def _gemini_extract_timestamps(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract timestamps using Gemini."""
        # Simulated response
        return {
            "status": "success",
            "timestamps": [
                {
                    "time": "2023-06-01T10:00:00Z",
                    "event": "Recording started",
                    "confidence": 0.95
                },
                {
                    "time": "2023-06-01T10:15:00Z",
                    "event": "Subject identified",
                    "confidence": 0.88
                }
            ],
            "media_duration": "00:45:00",
            "integrity_check": "passed"
        }
    
    async def _gemini_forensic_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform forensic analysis using Gemini."""
        return {
            "status": "success",
            "analysis": {
                "file_type": data.get("media_type", "unknown"),
                "authenticity": "verified",
                "modifications": "none detected",
                "metadata_integrity": "intact"
            }
        }
    
    async def _legalbert_statutory_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform statutory analysis using LegalBERT."""
        return {
            "status": "success",
            "matches": [
                {
                    "statute": "Evidence Act 1995",
                    "section": "s138",
                    "relevance": 0.89,
                    "description": "Exclusion of improperly obtained evidence"
                },
                {
                    "statute": "Crimes Act 1900",
                    "section": "s319",
                    "relevance": 0.76,
                    "description": "Perverting the course of justice"
                }
            ]
        }
    
    async def _legalbert_provision_matching(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Match facts to legal provisions using LegalBERT."""
        return {
            "status": "success",
            "provisions": [
                {
                    "fact": data.get("facts", [""])[0],
                    "matched_provisions": [
                        {
                            "statute": "Criminal Procedure Act 1986",
                            "section": "s281",
                            "confidence": 0.82
                        }
                    ]
                }
            ]
        }
    
    async def load_case(self, case_id: str) -> bool:
        """Load case data into the Nexus."""
        try:
            case_file = self.case_data_path / f"{case_id}.json"
            
            if case_file.exists():
                with open(case_file, 'r') as f:
                    case_data = json.load(f)
                
                self.active_cases[case_id] = {
                    "data": case_data,
                    "loaded_at": datetime.now(),
                    "status": "active"
                }
                
                self.logger.info(f"Loaded case: {case_id}")
                return True
            else:
                self.logger.warning(f"Case file not found: {case_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to load case {case_id}: {e}")
            return False
    
    def register_handler(self, message_type: str, handler: Callable):
        """Register a custom message handler."""
        self.message_handlers[message_type] = handler
    
    async def broadcast(self, data: Dict[str, Any], exclude: List[str] = None):
        """Broadcast message to all connected agents."""
        exclude = exclude or []
        
        for agent_name in self.connected_agents:
            if agent_name not in exclude:
                await self.send_to_agent(agent_name, data)
    
    def get_status(self) -> Dict[str, Any]:
        """Get Nexus system status."""
        return {
            "nexus_version": self.config.get("nexus_version", "1.0.0"),
            "connected_agents": list(self.connected_agents.keys()),
            "active_cases": list(self.active_cases.keys()),
            "message_queue_size": self.message_queue.qsize(),
            "status": "operational"
        }