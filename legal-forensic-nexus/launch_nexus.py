#!/usr/bin/env python3
"""
Legal-Forensic Nexus Launcher
Quick start script for the multi-agent legal analysis system
"""

import argparse
import asyncio
import subprocess
import sys
import os
from pathlib import Path


def setup_environment():
    """Ensure environment is properly configured."""
    print("🔧 Setting up Legal-Forensic Nexus environment...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    # Set environment variables if not present
    env_vars = {
        "OPENAI_API_KEY": "your-openai-api-key-here",
        "GEMINI_API_KEY": "your-gemini-api-key-here",
        "PYTHONPATH": str(Path(__file__).parent)
    }
    
    for var, default in env_vars.items():
        if var not in os.environ:
            print(f"⚠️  {var} not set. Using placeholder value.")
            os.environ[var] = default


def launch_claude_worker(boot_nexus: bool = True, case_id: str = None):
    """Launch Claude background worker."""
    print("\n🤖 Launching Claude Opus 4 Background Worker...")
    
    cmd = [
        sys.executable,
        "tasks/claude_background_worker.py"
    ]
    
    if boot_nexus:
        cmd.extend(["--boot-nexus", "--link-legalbert"])
    
    if case_id:
        cmd.extend(["--case-id", case_id])
    
    try:
        subprocess.run(cmd, cwd=Path(__file__).parent)
    except KeyboardInterrupt:
        print("\n👋 Shutting down Nexus...")


def run_specific_task(task_description: str):
    """Run a specific task using Claude Opus tasker."""
    print(f"\n📋 Running task: {task_description}")
    
    cmd = [
        sys.executable,
        "tasks/claude_opus_tasker.py",
        "--task",
        task_description
    ]
    
    subprocess.run(cmd, cwd=Path(__file__).parent)


def show_status():
    """Display system status."""
    print("\n📊 Legal-Forensic Nexus Status")
    print("=" * 50)
    print("✅ System: Initialized")
    print("📁 Workspace:", Path(__file__).parent)
    print("\n🤖 Available Agents:")
    print("  • Claude Opus 4 - Legal Engineer")
    print("  • GPT-4o - Metadata Validator")
    print("  • Gemini Pro - Forensic Analyst")
    print("  • LegalBERT - Statutory Matcher")
    print("\n🛠️ Available Tasks:")
    print("  • Affidavit contradiction scanning")
    print("  • ICCPR violation detection")
    print("  • Kable Principle analysis")
    print("  • Forensic metadata auditing")
    print("=" * 50)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Legal-Forensic Nexus Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start the Nexus with a specific case
  python launch_nexus.py --start --case CK89AJ
  
  # Run a specific task
  python launch_nexus.py --task "Analyze affidavit for ICCPR violations"
  
  # Show system status
  python launch_nexus.py --status
        """
    )
    
    parser.add_argument(
        "--start",
        action="store_true",
        help="Start the Nexus system"
    )
    
    parser.add_argument(
        "--case",
        type=str,
        help="Case ID to load on startup"
    )
    
    parser.add_argument(
        "--task",
        type=str,
        help="Run a specific task"
    )
    
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show system status"
    )
    
    args = parser.parse_args()
    
    # Setup environment
    setup_environment()
    
    # Handle commands
    if args.status:
        show_status()
    elif args.task:
        run_specific_task(args.task)
    elif args.start:
        print("""
╔══════════════════════════════════════════════════════════════╗
║          LEGAL-FORENSIC NEXUS v1.0.0                         ║
║                                                              ║
║  Advanced Multi-Agent Legal Analysis System                  ║
║  Powered by Claude Opus 4, GPT-4o, Gemini Pro & LegalBERT  ║
╚══════════════════════════════════════════════════════════════╝
        """)
        launch_claude_worker(boot_nexus=True, case_id=args.case)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()