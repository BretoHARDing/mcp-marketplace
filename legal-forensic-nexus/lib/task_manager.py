"""
Task Manager
Manages task queues and job coordination for Legal-Forensic Nexus agents
"""

import asyncio
import json
import sqlite3
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import uuid
from enum import Enum
from dataclasses import dataclass, asdict
import logging


class TaskStatus(Enum):
    """Task status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Task priority levels."""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class Task:
    """Represents a task in the system."""
    id: str
    agent_name: str
    type: str
    data: Dict[str, Any]
    status: TaskStatus
    priority: TaskPriority
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary format."""
        result = asdict(self)
        result['status'] = self.status.value
        result['priority'] = self.priority.value
        result['created_at'] = self.created_at.isoformat()
        result['updated_at'] = self.updated_at.isoformat()
        if self.started_at:
            result['started_at'] = self.started_at.isoformat()
        if self.completed_at:
            result['completed_at'] = self.completed_at.isoformat()
        return result


class TaskManager:
    """
    Manages task queues for Legal-Forensic Nexus agents.
    Provides persistent storage and priority-based task scheduling.
    """
    
    def __init__(self, agent_name: str, db_path: str = None):
        self.agent_name = agent_name
        self.logger = logging.getLogger(f"TaskManager-{agent_name}")
        
        # Database setup
        if db_path is None:
            db_path = Path(__file__).parent.parent / "data" / "tasks.db"
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # In-memory task queue for performance
        self.task_queue = asyncio.PriorityQueue()
        self._load_pending_tasks()
    
    def _init_database(self):
        """Initialize SQLite database for task persistence."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                agent_name TEXT NOT NULL,
                type TEXT NOT NULL,
                data TEXT NOT NULL,
                status TEXT NOT NULL,
                priority INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                started_at TEXT,
                completed_at TEXT,
                result TEXT,
                error TEXT
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_agent_status 
            ON tasks(agent_name, status)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_priority_created 
            ON tasks(priority DESC, created_at ASC)
        """)
        
        conn.commit()
        conn.close()
    
    def _load_pending_tasks(self):
        """Load pending tasks from database into memory queue."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM tasks 
            WHERE agent_name = ? AND status IN (?, ?)
            ORDER BY priority DESC, created_at ASC
        """, (self.agent_name, TaskStatus.PENDING.value, TaskStatus.IN_PROGRESS.value))
        
        for row in cursor.fetchall():
            task = self._row_to_task(row)
            # Reset in-progress tasks to pending
            if task.status == TaskStatus.IN_PROGRESS:
                task.status = TaskStatus.PENDING
                self._update_task_db(task)
            
            # Add to priority queue (negative priority for max heap behavior)
            asyncio.create_task(
                self.task_queue.put((-task.priority.value, task.created_at.timestamp(), task))
            )
        
        conn.close()
    
    def _row_to_task(self, row: tuple) -> Task:
        """Convert database row to Task object."""
        return Task(
            id=row[0],
            agent_name=row[1],
            type=row[2],
            data=json.loads(row[3]),
            status=TaskStatus(row[4]),
            priority=TaskPriority(row[5]),
            created_at=datetime.fromisoformat(row[6]),
            updated_at=datetime.fromisoformat(row[7]),
            started_at=datetime.fromisoformat(row[8]) if row[8] else None,
            completed_at=datetime.fromisoformat(row[9]) if row[9] else None,
            result=json.loads(row[10]) if row[10] else None,
            error=row[11]
        )
    
    def _update_task_db(self, task: Task):
        """Update task in database."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE tasks SET 
                status = ?, updated_at = ?, started_at = ?, 
                completed_at = ?, result = ?, error = ?
            WHERE id = ?
        """, (
            task.status.value,
            task.updated_at.isoformat(),
            task.started_at.isoformat() if task.started_at else None,
            task.completed_at.isoformat() if task.completed_at else None,
            json.dumps(task.result) if task.result else None,
            task.error,
            task.id
        ))
        
        conn.commit()
        conn.close()
    
    async def create_task(
        self,
        task_type: str,
        data: Dict[str, Any],
        priority: TaskPriority = TaskPriority.NORMAL
    ) -> str:
        """Create a new task and add to queue."""
        task_id = str(uuid.uuid4())
        now = datetime.now()
        
        task = Task(
            id=task_id,
            agent_name=self.agent_name,
            type=task_type,
            data=data,
            status=TaskStatus.PENDING,
            priority=priority,
            created_at=now,
            updated_at=now
        )
        
        # Save to database
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO tasks (
                id, agent_name, type, data, status, priority,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            task.id,
            task.agent_name,
            task.type,
            json.dumps(task.data),
            task.status.value,
            task.priority.value,
            task.created_at.isoformat(),
            task.updated_at.isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        # Add to queue
        await self.task_queue.put((-priority.value, now.timestamp(), task))
        
        self.logger.info(f"Created task {task_id} of type {task_type}")
        return task_id
    
    async def get_next_task(self) -> Optional[Dict[str, Any]]:
        """Get next task from queue."""
        try:
            # Get task from priority queue
            _, _, task = await self.task_queue.get()
            
            # Mark as in progress
            task.status = TaskStatus.IN_PROGRESS
            task.started_at = datetime.now()
            task.updated_at = datetime.now()
            
            self._update_task_db(task)
            
            return {
                "id": task.id,
                "type": task.type,
                "data": task.data,
                "priority": task.priority.name
            }
            
        except asyncio.QueueEmpty:
            return None
    
    async def complete_task(self, task_id: str, result: Dict[str, Any]):
        """Mark task as completed with result."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        now = datetime.now()
        
        cursor.execute("""
            UPDATE tasks SET 
                status = ?, completed_at = ?, updated_at = ?, result = ?
            WHERE id = ?
        """, (
            TaskStatus.COMPLETED.value,
            now.isoformat(),
            now.isoformat(),
            json.dumps(result),
            task_id
        ))
        
        conn.commit()
        conn.close()
        
        self.logger.info(f"Completed task {task_id}")
    
    async def fail_task(self, task_id: str, error: str):
        """Mark task as failed with error."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        now = datetime.now()
        
        cursor.execute("""
            UPDATE tasks SET 
                status = ?, completed_at = ?, updated_at = ?, error = ?
            WHERE id = ?
        """, (
            TaskStatus.FAILED.value,
            now.isoformat(),
            now.isoformat(),
            error,
            task_id
        ))
        
        conn.commit()
        conn.close()
        
        self.logger.error(f"Failed task {task_id}: {error}")
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            task = self._row_to_task(row)
            return task.to_dict()
        
        return None
    
    def get_agent_tasks(
        self,
        status: Optional[TaskStatus] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get tasks for this agent."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        if status:
            cursor.execute("""
                SELECT * FROM tasks 
                WHERE agent_name = ? AND status = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (self.agent_name, status.value, limit))
        else:
            cursor.execute("""
                SELECT * FROM tasks 
                WHERE agent_name = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (self.agent_name, limit))
        
        tasks = []
        for row in cursor.fetchall():
            task = self._row_to_task(row)
            tasks.append(task.to_dict())
        
        conn.close()
        
        return tasks
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get statistics about the task queue."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        stats = {
            "agent": self.agent_name,
            "queue_size": self.task_queue.qsize(),
            "tasks_by_status": {},
            "tasks_by_priority": {},
            "average_completion_time": None
        }
        
        # Count by status
        cursor.execute("""
            SELECT status, COUNT(*) FROM tasks 
            WHERE agent_name = ?
            GROUP BY status
        """, (self.agent_name,))
        
        for status, count in cursor.fetchall():
            stats["tasks_by_status"][status] = count
        
        # Count by priority
        cursor.execute("""
            SELECT priority, COUNT(*) FROM tasks 
            WHERE agent_name = ? AND status = ?
            GROUP BY priority
        """, (self.agent_name, TaskStatus.PENDING.value))
        
        for priority, count in cursor.fetchall():
            stats["tasks_by_priority"][TaskPriority(priority).name] = count
        
        # Average completion time
        cursor.execute("""
            SELECT AVG(
                julianday(completed_at) - julianday(started_at)
            ) * 24 * 60 * 60 as avg_seconds
            FROM tasks 
            WHERE agent_name = ? 
            AND status = ? 
            AND completed_at IS NOT NULL 
            AND started_at IS NOT NULL
        """, (self.agent_name, TaskStatus.COMPLETED.value))
        
        result = cursor.fetchone()
        if result and result[0]:
            stats["average_completion_time"] = f"{result[0]:.2f} seconds"
        
        conn.close()
        
        return stats
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending task."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Check if task is pending
        cursor.execute("""
            SELECT status FROM tasks WHERE id = ?
        """, (task_id,))
        
        row = cursor.fetchone()
        if not row or row[0] != TaskStatus.PENDING.value:
            conn.close()
            return False
        
        # Update status
        now = datetime.now()
        cursor.execute("""
            UPDATE tasks SET 
                status = ?, updated_at = ?
            WHERE id = ?
        """, (TaskStatus.CANCELLED.value, now.isoformat(), task_id))
        
        conn.commit()
        conn.close()
        
        self.logger.info(f"Cancelled task {task_id}")
        return True
    
    def cleanup_old_tasks(self, days: int = 30):
        """Clean up completed/failed tasks older than specified days."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        cursor.execute("""
            DELETE FROM tasks 
            WHERE agent_name = ? 
            AND status IN (?, ?, ?)
            AND julianday('now') - julianday(completed_at) > ?
        """, (
            self.agent_name,
            TaskStatus.COMPLETED.value,
            TaskStatus.FAILED.value,
            TaskStatus.CANCELLED.value,
            days
        ))
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        self.logger.info(f"Cleaned up {deleted} old tasks")
        return deleted