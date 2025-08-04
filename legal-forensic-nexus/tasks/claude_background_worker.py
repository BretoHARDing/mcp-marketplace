#!/usr/bin/env python3
"""
Claude Opus 4 Background Worker
Legal-Forensic Nexus Integration

This module manages Claude's task queue and integrates with other AI agents
for comprehensive legal analysis and forensic processing.
"""

import json
import logging
import asyncio
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from lib.nexus_core import NexusCore
from lib.task_manager import TaskManager
from agents.claude_agent import ClaudeOpus4Agent


class ClaudeBackgroundWorker:
    """Background worker for Claude Opus 4 legal engineering tasks."""
    
    def __init__(self, config_path: str = "../config/nexus_config.json"):
        """Initialize the background worker with configuration."""
        self.config_path = Path(__file__).parent / config_path
        self.config = self._load_config()
        self.setup_logging()
        
        # Initialize core components
        self.nexus = NexusCore(self.config)
        self.task_manager = TaskManager(agent_name="Claude_Opus_4")
        self.agent = ClaudeOpus4Agent(self.config["agents"]["Claude_Opus_4"])
        
        # Task registry
        self.task_registry = {
            "affidavit_contradiction_scanner": self.scan_affidavit_contradictions,
            "iccpr_violation_detector": self.detect_iccpr_violations,
            "legalbert_parser_interface": self.interface_with_legalbert,
            "forensic_metadata_audit": self.audit_forensic_metadata,
            "kable_principle_analyzer": self.analyze_kable_principle,
            "statutory_matcher": self.match_statutory_provisions
        }
        
        self.logger.info("Claude Background Worker initialized")
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        with open(self.config_path, 'r') as f:
            return json.load(f)
    
    def setup_logging(self):
        """Configure logging based on config settings."""
        log_config = self.config["logging"]
        logging.basicConfig(
            level=getattr(logging, log_config["level"]),
            format=log_config["format"],
            handlers=[
                logging.FileHandler(log_config["file"]),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("ClaudeBackgroundWorker")
    
    async def scan_affidavit_contradictions(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Scan affidavits for logical contradictions and timeline inconsistencies."""
        self.logger.info(f"Scanning affidavit contradictions: {task_data}")
        
        result = {
            "task_id": task_data.get("task_id"),
            "timestamp": datetime.now().isoformat(),
            "contradictions": [],
            "timeline_issues": [],
            "signature_anomalies": []
        }
        
        # Process affidavit data
        affidavit_path = task_data.get("affidavit_path")
        if affidavit_path:
            # Analyze document structure, signatures, and content
            analysis = await self.agent.analyze_affidavit(affidavit_path)
            result.update(analysis)
        
        # Send results to GPT-4o for synthesis
        await self.nexus.send_to_agent("GPT4o", {
            "type": "contradiction_analysis",
            "data": result
        })
        
        return result
    
    async def detect_iccpr_violations(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect potential ICCPR (International Covenant on Civil and Political Rights) violations."""
        self.logger.info(f"Detecting ICCPR violations: {task_data}")
        
        result = {
            "task_id": task_data.get("task_id"),
            "timestamp": datetime.now().isoformat(),
            "violations": [],
            "articles_affected": [],
            "severity": "unknown"
        }
        
        # Analyze against ICCPR articles
        document_text = task_data.get("document_text", "")
        context = task_data.get("context", {})
        
        # Check key ICCPR articles
        iccpr_checks = {
            "Article 9": "Liberty and security of person",
            "Article 14": "Fair trial rights",
            "Article 17": "Privacy rights",
            "Article 19": "Freedom of expression"
        }
        
        violations = await self.agent.check_human_rights_violations(
            document_text, 
            framework="ICCPR",
            articles=list(iccpr_checks.keys()),
            context=context
        )
        
        result["violations"] = violations
        result["severity"] = self._assess_severity(violations)
        
        return result
    
    async def interface_with_legalbert(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Interface with LegalBERT for statutory analysis."""
        self.logger.info(f"Interfacing with LegalBERT: {task_data}")
        
        # Prepare data for LegalBERT
        query = task_data.get("query", "")
        statutes = task_data.get("statutes", ["EvidenceAct1995", "CrimesAct1900"])
        
        # Send to LegalBERT through Nexus
        legalbert_response = await self.nexus.query_agent("LegalBERT", {
            "type": "statutory_analysis",
            "query": query,
            "statutes": statutes,
            "jurisdiction": "NSW"
        })
        
        # Process and enhance results
        enhanced_results = await self.agent.enhance_legal_analysis(
            legalbert_response,
            additional_context=task_data.get("context", {})
        )
        
        return enhanced_results
    
    async def audit_forensic_metadata(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Audit forensic metadata for integrity and chain of custody issues."""
        self.logger.info(f"Auditing forensic metadata: {task_data}")
        
        # Get timestamp data from Gemini
        gemini_data = await self.nexus.query_agent("Gemini_Pro", {
            "type": "timestamp_extraction",
            "source": task_data.get("source_file"),
            "media_type": task_data.get("media_type", "unknown")
        })
        
        # Perform comprehensive audit
        audit_result = await self.agent.audit_metadata(
            metadata=task_data.get("metadata", {}),
            timestamps=gemini_data.get("timestamps", []),
            chain_of_custody=task_data.get("custody_log", [])
        )
        
        return audit_result
    
    async def analyze_kable_principle(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze case against Kable Principle (constitutional validity)."""
        self.logger.info(f"Analyzing Kable Principle: {task_data}")
        
        result = {
            "task_id": task_data.get("task_id"),
            "timestamp": datetime.now().isoformat(),
            "kable_analysis": {
                "separation_of_powers": {},
                "judicial_independence": {},
                "institutional_integrity": {}
            },
            "constitutional_issues": [],
            "recommendations": []
        }
        
        # Analyze constitutional implications
        analysis = await self.agent.analyze_constitutional_validity(
            case_data=task_data.get("case_data", {}),
            principle="Kable",
            jurisdiction="NSW"
        )
        
        result["kable_analysis"] = analysis
        result["constitutional_issues"] = self._identify_constitutional_issues(analysis)
        
        return result
    
    async def match_statutory_provisions(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Match facts to statutory provisions and identify applicable sections."""
        self.logger.info(f"Matching statutory provisions: {task_data}")
        
        facts = task_data.get("facts", [])
        statutes = task_data.get("statutes", ["CrimesAct1900", "EvidenceAct1995"])
        
        # Use LegalBERT for initial matching
        legalbert_matches = await self.nexus.query_agent("LegalBERT", {
            "type": "provision_matching",
            "facts": facts,
            "statutes": statutes
        })
        
        # Enhance with Claude's legal reasoning
        enhanced_matches = await self.agent.enhance_statutory_matching(
            initial_matches=legalbert_matches,
            facts=facts,
            case_context=task_data.get("context", {})
        )
        
        return enhanced_matches
    
    def _assess_severity(self, violations: List[Dict[str, Any]]) -> str:
        """Assess the severity of human rights violations."""
        if not violations:
            return "none"
        
        severity_scores = {
            "liberty": 5,
            "fair_trial": 5,
            "torture": 5,
            "privacy": 3,
            "expression": 3
        }
        
        max_score = 0
        for violation in violations:
            violation_type = violation.get("type", "").lower()
            for key, score in severity_scores.items():
                if key in violation_type:
                    max_score = max(max_score, score)
        
        if max_score >= 5:
            return "critical"
        elif max_score >= 3:
            return "high"
        elif max_score >= 1:
            return "medium"
        return "low"
    
    def _identify_constitutional_issues(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify specific constitutional issues from Kable analysis."""
        issues = []
        
        # Check separation of powers
        if analysis.get("separation_of_powers", {}).get("violated"):
            issues.append({
                "type": "separation_of_powers",
                "severity": "high",
                "details": analysis["separation_of_powers"].get("details", "")
            })
        
        # Check judicial independence
        if analysis.get("judicial_independence", {}).get("compromised"):
            issues.append({
                "type": "judicial_independence",
                "severity": "critical",
                "details": analysis["judicial_independence"].get("details", "")
            })
        
        return issues
    
    async def process_task_queue(self):
        """Process tasks from the queue continuously."""
        self.logger.info("Starting task queue processing")
        
        while True:
            try:
                # Get next task from queue
                task = await self.task_manager.get_next_task()
                
                if task:
                    task_type = task.get("type")
                    task_handler = self.task_registry.get(task_type)
                    
                    if task_handler:
                        self.logger.info(f"Processing task: {task_type}")
                        result = await task_handler(task.get("data", {}))
                        
                        # Mark task complete
                        await self.task_manager.complete_task(
                            task_id=task.get("id"),
                            result=result
                        )
                    else:
                        self.logger.warning(f"Unknown task type: {task_type}")
                
                # Brief pause between tasks
                await asyncio.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Error processing task: {e}")
                await asyncio.sleep(5)  # Longer pause on error
    
    async def boot_nexus(self, link_legalbert: bool = True, case_id: Optional[str] = None):
        """Boot the Nexus system and establish agent connections."""
        self.logger.info("Booting Legal-Forensic Nexus...")
        
        # Initialize Nexus core
        await self.nexus.initialize()
        
        # Establish LegalBERT connection if requested
        if link_legalbert:
            self.logger.info("Establishing LegalBERT handshake...")
            await self.nexus.connect_agent("LegalBERT")
        
        # Connect to other agents
        await self.nexus.connect_agent("GPT4o")
        await self.nexus.connect_agent("Gemini_Pro")
        
        # Load case data if provided
        if case_id:
            self.logger.info(f"Loading case data: {case_id}")
            await self.nexus.load_case(case_id)
        
        self.logger.info("Nexus boot complete - all systems operational")
    
    async def run(self, args):
        """Main run method."""
        # Boot Nexus if requested
        if args.boot_nexus:
            await self.boot_nexus(
                link_legalbert=args.link_legalbert,
                case_id=args.case_id
            )
        
        # Start processing tasks
        await self.process_task_queue()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Claude Opus 4 Background Worker - Legal-Forensic Nexus"
    )
    
    parser.add_argument(
        "--boot-nexus",
        action="store_true",
        help="Boot the Nexus system on startup"
    )
    
    parser.add_argument(
        "--link-legalbert",
        action="store_true",
        help="Establish LegalBERT connection"
    )
    
    parser.add_argument(
        "--case-id",
        type=str,
        help="Case ID to load on startup"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        default="../config/nexus_config.json",
        help="Path to configuration file"
    )
    
    args = parser.parse_args()
    
    # Create and run worker
    worker = ClaudeBackgroundWorker(config_path=args.config)
    
    # Run async event loop
    asyncio.run(worker.run(args))


if __name__ == "__main__":
    main()