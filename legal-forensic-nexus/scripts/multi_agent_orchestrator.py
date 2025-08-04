#!/usr/bin/env python3
"""
Multi-Agent Orchestrator for Legal-Forensic Nexus
Deploys all agents simultaneously for comprehensive case analysis
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from datetime import datetime
import argparse
import logging
from typing import Dict, Any, List
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from lib.nexus_core import NexusCore
from lib.task_manager import TaskManager, TaskPriority, TaskStatus
from agents.claude_agent import ClaudeOpus4Agent


class MultiAgentOrchestrator:
    """Orchestrates multiple AI agents for comprehensive legal analysis."""
    
    def __init__(self, case_file: str):
        # Load environment variables
        load_dotenv()
        
        self.case_file = Path(case_file)
        self.case_data = self._load_case_data()
        
        # Setup logging
        self.setup_logging()
        
        # Load configuration
        config_path = Path(__file__).parent.parent / "config" / "nexus_config.json"
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Update config with environment variables
        self._update_config_with_env()
        
        # Initialize components
        self.nexus = NexusCore(self.config)
        self.task_managers = {}
        self.results = {
            "case_id": self.case_data.get("case_id", "unknown"),
            "analysis_started": datetime.now().isoformat(),
            "agents": {},
            "findings": {
                "contradictions": [],
                "human_rights_violations": [],
                "constitutional_issues": [],
                "forensic_anomalies": []
            }
        }
    
    def setup_logging(self):
        """Configure logging for the orchestrator."""
        log_level = os.getenv("NEXUS_LOG_LEVEL", "INFO")
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'orchestrator_{datetime.now():%Y%m%d_%H%M%S}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("MultiAgentOrchestrator")
    
    def _load_case_data(self) -> Dict[str, Any]:
        """Load case data from JSON file."""
        if not self.case_file.exists():
            raise FileNotFoundError(f"Case file not found: {self.case_file}")
        
        with open(self.case_file, 'r') as f:
            return json.load(f)
    
    def _update_config_with_env(self):
        """Update configuration with environment variables."""
        # Update API keys from environment
        if os.getenv("OPENAI_API_KEY"):
            self.config["agents"]["GPT4o"]["api_key"] = os.getenv("OPENAI_API_KEY")
        
        if os.getenv("GEMINI_API_KEY"):
            self.config["agents"]["Gemini_Pro"]["api_key"] = os.getenv("GEMINI_API_KEY")
        
        # Note: Claude (Anthropic) key would be used if we were making direct API calls
        # For now, Claude runs as the orchestrator itself
    
    async def initialize_nexus(self):
        """Initialize the Nexus system and connect all agents."""
        self.logger.info("Initializing Legal-Forensic Nexus...")
        
        await self.nexus.initialize()
        
        # Connect all agents
        agents = ["Claude_Opus_4", "GPT4o", "Gemini_Pro", "LegalBERT"]
        
        for agent in agents:
            self.logger.info(f"Connecting to {agent}...")
            success = await self.nexus.connect_agent(agent)
            
            if success:
                self.logger.info(f"✓ {agent} connected")
                self.task_managers[agent] = TaskManager(agent)
            else:
                self.logger.warning(f"✗ Failed to connect to {agent}")
    
    async def deploy_all_agents(self):
        """Deploy all agents with their specific tasks."""
        self.logger.info("=== DEPLOYING ALL AGENTS ===")
        
        # Create tasks for each agent based on case data
        tasks = []
        
        # Claude Opus 4 - Legal Analysis Lead
        if "Claude_Opus_4" in self.task_managers:
            tasks.extend([
                self._deploy_claude_tasks(),
            ])
        
        # GPT-4o - Metadata Validation
        if "GPT4o" in self.task_managers:
            tasks.extend([
                self._deploy_gpt4o_tasks(),
            ])
        
        # Gemini Pro - Forensic Analysis
        if "Gemini_Pro" in self.task_managers:
            tasks.extend([
                self._deploy_gemini_tasks(),
            ])
        
        # LegalBERT - Statutory Analysis
        if "LegalBERT" in self.task_managers:
            tasks.extend([
                self._deploy_legalbert_tasks(),
            ])
        
        # Execute all deployments in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"Task failed: {result}")
    
    async def _deploy_claude_tasks(self):
        """Deploy Claude Opus 4 tasks."""
        self.logger.info("📋 Deploying Claude Opus 4 tasks...")
        
        tm = self.task_managers["Claude_Opus_4"]
        
        # Task 1: Analyze affidavits for contradictions
        if "affidavits" in self.case_data:
            for affidavit in self.case_data["affidavits"]:
                task_id = await tm.create_task(
                    "affidavit_contradiction_scanner",
                    {
                        "affidavit_path": affidavit.get("path", ""),
                        "affidavit_data": affidavit,
                        "case_id": self.case_data.get("case_id")
                    },
                    TaskPriority.HIGH
                )
                self.logger.info(f"  ✓ Created affidavit analysis task: {task_id}")
        
        # Task 2: Check for ICCPR violations
        task_id = await tm.create_task(
            "iccpr_violation_detector",
            {
                "document_text": self._extract_case_text(),
                "context": {
                    "case_type": self.case_data.get("case_type"),
                    "jurisdiction": self.case_data.get("jurisdiction", "NSW")
                }
            },
            TaskPriority.HIGH
        )
        self.logger.info(f"  ✓ Created ICCPR violation detection task: {task_id}")
        
        # Task 3: Kable Principle analysis
        task_id = await tm.create_task(
            "kable_principle_analyzer",
            {
                "case_data": {
                    "procedural_irregularities": len(self.case_data.get("issues", [])),
                    "executive_involvement": self.case_data.get("executive_involvement"),
                    "case_name": self.case_data.get("case_name")
                }
            },
            TaskPriority.NORMAL
        )
        self.logger.info(f"  ✓ Created Kable Principle analysis task: {task_id}")
    
    async def _deploy_gpt4o_tasks(self):
        """Deploy GPT-4o tasks for metadata validation."""
        self.logger.info("📋 Deploying GPT-4o tasks...")
        
        # Send contradiction analysis request
        if "timeline" in self.case_data:
            await self.nexus.send_to_agent("GPT4o", {
                "type": "contradiction_analysis",
                "priority": "high",
                "data": {
                    "timeline": self.case_data["timeline"],
                    "statements": self.case_data.get("statements", [])
                }
            })
            self.logger.info("  ✓ Sent timeline contradiction analysis to GPT-4o")
        
        # Send metadata validation request
        if "evidence_files" in self.case_data:
            for evidence in self.case_data["evidence_files"]:
                await self.nexus.send_to_agent("GPT4o", {
                    "type": "metadata_validation",
                    "priority": "normal",
                    "data": evidence.get("metadata", {})
                })
            self.logger.info("  ✓ Sent metadata validation requests to GPT-4o")
    
    async def _deploy_gemini_tasks(self):
        """Deploy Gemini Pro tasks for forensic analysis."""
        self.logger.info("📋 Deploying Gemini Pro tasks...")
        
        # Process forensic media files
        if "forensic_media" in self.case_data:
            for media in self.case_data["forensic_media"]:
                await self.nexus.send_to_agent("Gemini_Pro", {
                    "type": "timestamp_extraction",
                    "priority": "high",
                    "source_file": media.get("path", ""),
                    "media_type": media.get("type", "unknown")
                })
                self.logger.info(f"  ✓ Sent {media.get('type')} for timestamp extraction")
        
        # Forensic integrity analysis
        if "evidence_files" in self.case_data:
            for evidence in self.case_data["evidence_files"]:
                await self.nexus.send_to_agent("Gemini_Pro", {
                    "type": "forensic_analysis",
                    "priority": "normal",
                    "media_type": evidence.get("type"),
                    "metadata": evidence.get("metadata", {})
                })
            self.logger.info("  ✓ Sent forensic integrity analysis requests")
    
    async def _deploy_legalbert_tasks(self):
        """Deploy LegalBERT tasks for statutory analysis."""
        self.logger.info("📋 Deploying LegalBERT tasks...")
        
        # Statutory analysis
        facts = self._extract_facts()
        if facts:
            await self.nexus.send_to_agent("LegalBERT", {
                "type": "statutory_analysis",
                "query": " ".join(facts[:3]),  # Top 3 facts
                "statutes": ["EvidenceAct1995", "CrimesAct1900", "CriminalProcedureAct1986"],
                "jurisdiction": self.case_data.get("jurisdiction", "NSW")
            })
            self.logger.info("  ✓ Sent statutory analysis request")
        
        # Provision matching
        await self.nexus.send_to_agent("LegalBERT", {
            "type": "provision_matching",
            "facts": facts,
            "statutes": ["CrimesAct1900", "EvidenceAct1995"]
        })
        self.logger.info("  ✓ Sent provision matching request")
    
    def _extract_case_text(self) -> str:
        """Extract text content from case data."""
        text_parts = []
        
        # Add case summary
        if "summary" in self.case_data:
            text_parts.append(self.case_data["summary"])
        
        # Add statements
        for statement in self.case_data.get("statements", []):
            text_parts.append(statement.get("content", ""))
        
        # Add affidavit content
        for affidavit in self.case_data.get("affidavits", []):
            text_parts.append(affidavit.get("content", ""))
        
        return "\n\n".join(text_parts)
    
    def _extract_facts(self) -> List[str]:
        """Extract key facts from case data."""
        facts = []
        
        # Extract from timeline
        for event in self.case_data.get("timeline", []):
            facts.append(event.get("description", ""))
        
        # Extract from issues
        for issue in self.case_data.get("issues", []):
            facts.append(issue.get("description", ""))
        
        # Extract from statements
        for statement in self.case_data.get("statements", []):
            # Take first sentence as fact
            content = statement.get("content", "")
            if content:
                first_sentence = content.split('.')[0] + "."
                facts.append(first_sentence)
        
        return facts[:10]  # Limit to top 10 facts
    
    async def monitor_progress(self):
        """Monitor task progress across all agents."""
        self.logger.info("\n=== MONITORING TASK PROGRESS ===")
        
        monitoring = True
        start_time = datetime.now()
        
        while monitoring:
            await asyncio.sleep(5)  # Check every 5 seconds
            
            all_complete = True
            
            for agent_name, tm in self.task_managers.items():
                stats = tm.get_queue_stats()
                
                pending = stats["tasks_by_status"].get("pending", 0)
                in_progress = stats["tasks_by_status"].get("in_progress", 0)
                completed = stats["tasks_by_status"].get("completed", 0)
                
                if pending > 0 or in_progress > 0:
                    all_complete = False
                
                self.logger.info(
                    f"{agent_name}: Pending={pending}, In Progress={in_progress}, "
                    f"Completed={completed}"
                )
            
            # Check timeout (30 minutes)
            if (datetime.now() - start_time).seconds > 1800:
                self.logger.warning("Analysis timeout reached (30 minutes)")
                monitoring = False
            
            if all_complete:
                self.logger.info("✓ All tasks completed!")
                monitoring = False
    
    async def collect_results(self):
        """Collect and synthesize results from all agents."""
        self.logger.info("\n=== COLLECTING RESULTS ===")
        
        # Collect completed tasks from each agent
        for agent_name, tm in self.task_managers.items():
            completed_tasks = tm.get_agent_tasks(status=TaskStatus.COMPLETED)
            
            self.results["agents"][agent_name] = {
                "tasks_completed": len(completed_tasks),
                "findings": []
            }
            
            # Process results by type
            for task in completed_tasks:
                task_type = task.get("type")
                result = task.get("result", {})
                
                if task_type == "affidavit_contradiction_scanner":
                    self.results["findings"]["contradictions"].extend(
                        result.get("contradictions", [])
                    )
                
                elif task_type == "iccpr_violation_detector":
                    self.results["findings"]["human_rights_violations"].extend(
                        result.get("violations", [])
                    )
                
                elif task_type == "kable_principle_analyzer":
                    self.results["findings"]["constitutional_issues"].append(
                        result.get("kable_analysis", {})
                    )
                
                elif task_type == "forensic_metadata_audit":
                    if result.get("integrity_status") == "compromised":
                        self.results["findings"]["forensic_anomalies"].append(result)
        
        self.results["analysis_completed"] = datetime.now().isoformat()
    
    def generate_report(self):
        """Generate comprehensive analysis report."""
        self.logger.info("\n=== GENERATING REPORT ===")
        
        report_path = Path("analysis_report_") / f"{self.results['case_id']}_{datetime.now():%Y%m%d_%H%M%S}.json"
        
        # Calculate summary statistics
        self.results["summary"] = {
            "total_contradictions": len(self.results["findings"]["contradictions"]),
            "total_violations": len(self.results["findings"]["human_rights_violations"]),
            "constitutional_issues": len(self.results["findings"]["constitutional_issues"]),
            "forensic_anomalies": len(self.results["findings"]["forensic_anomalies"]),
            "critical_findings": self._count_critical_findings()
        }
        
        # Save report
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        self.logger.info(f"✓ Report saved to: {report_path}")
        
        # Print summary
        print("\n" + "="*60)
        print("LEGAL-FORENSIC NEXUS ANALYSIS COMPLETE")
        print("="*60)
        print(f"Case ID: {self.results['case_id']}")
        print(f"Analysis Duration: {self._calculate_duration()}")
        print("\nFINDINGS SUMMARY:")
        print(f"  • Contradictions Found: {self.results['summary']['total_contradictions']}")
        print(f"  • Human Rights Violations: {self.results['summary']['total_violations']}")
        print(f"  • Constitutional Issues: {self.results['summary']['constitutional_issues']}")
        print(f"  • Forensic Anomalies: {self.results['summary']['forensic_anomalies']}")
        print(f"  • CRITICAL FINDINGS: {self.results['summary']['critical_findings']}")
        print("="*60)
    
    def _count_critical_findings(self) -> int:
        """Count critical severity findings."""
        count = 0
        
        # Check contradictions
        for c in self.results["findings"]["contradictions"]:
            if c.get("severity") == "high":
                count += 1
        
        # Check violations
        for v in self.results["findings"]["human_rights_violations"]:
            if v.get("severity") == "critical":
                count += 1
        
        return count
    
    def _calculate_duration(self) -> str:
        """Calculate analysis duration."""
        start = datetime.fromisoformat(self.results["analysis_started"])
        end = datetime.fromisoformat(self.results.get("analysis_completed", datetime.now().isoformat()))
        duration = end - start
        
        return f"{duration.seconds // 60} minutes {duration.seconds % 60} seconds"
    
    async def run(self):
        """Run the complete multi-agent analysis."""
        try:
            # Initialize system
            await self.initialize_nexus()
            
            # Deploy all agents
            await self.deploy_all_agents()
            
            # Monitor progress
            await self.monitor_progress()
            
            # Collect results
            await self.collect_results()
            
            # Generate report
            self.generate_report()
            
        except Exception as e:
            self.logger.error(f"Orchestration failed: {e}")
            raise


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Multi-Agent Orchestrator for Legal-Forensic Analysis"
    )
    
    parser.add_argument(
        "case_file",
        help="Path to case JSON file"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        os.environ["NEXUS_LOG_LEVEL"] = "DEBUG"
    
    # Check if case file exists
    if not Path(args.case_file).exists():
        print(f"❌ Error: Case file not found: {args.case_file}")
        print("\nPlease ensure your case file is in the correct location.")
        print("Expected format: evidence/CASE_NAME.json")
        sys.exit(1)
    
    # Run orchestrator
    orchestrator = MultiAgentOrchestrator(args.case_file)
    asyncio.run(orchestrator.run())


if __name__ == "__main__":
    main()