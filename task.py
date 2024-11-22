import asyncio
import uuid
import logging
from typing import Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum, auto
import sqlite3
import threading
import queue
import hashlib
import json
import time
class TaskStatus(Enum):
    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()

@dataclass
class Task:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ''
    status: TaskStatus = TaskStatus.PENDING
    data: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    result: Any = None
    error: str = ''

class TaskManager:
    def __init__(self, max_workers=4, database_path='tasks.db'):
        self.task_queue = queue.Queue()
        self.completed_tasks = {}
        self.max_workers = max_workers
        self.database_path = database_path
        self._init_database()
        self._start_workers()

    def _init_database(self):
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    status TEXT,
                    data TEXT,
                    created_at REAL,
                    result TEXT,
                    error TEXT
                )
            ''')
            conn.commit()

    def _start_workers(self):
        self.workers = []
        for _ in range(self.max_workers):
            worker = threading.Thread(target=self._worker_loop, daemon=True)
            worker.start()
            self.workers.append(worker)

    def _worker_loop(self):
        while True:
            try:
                task = self.task_queue.get(block=True, timeout=5)
                self._process_task(task)
            except queue.Empty:
                continue
            except Exception as e:
                logging.error(f"Worker error: {e}")

    def _process_task(self, task: Task):
        try:
            task.status = TaskStatus.RUNNING
            task.result = self._execute_task(task.name, task.data)
            task.status = TaskStatus.COMPLETED
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
        
        self._save_task(task)
        self.completed_tasks[task.id] = task

    def _execute_task(self, task_name: str, data: Dict[str, Any]) -> Any:
        # task-specific logic
        if task_name == 'data_processing':
            return self._process_data(data)
        elif task_name == 'complex_computation':
            return self._perform_computation(data)
        else:
            raise ValueError(f"Unknown task type: {task_name}")

    def _process_data(self, data):
        # data processing task
        raw_data = data.get('raw_data', [])
        processed_data = [hashlib.md5(str(item).encode()).hexdigest() for item in raw_data]
        return processed_data

    def _perform_computation(self, data):
        # complex computation task
        iterations = data.get('iterations', 1000)
        return sum(i**2 for i in range(iterations))

    def _save_task(self, task: Task):
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO tasks 
                (id, name, status, data, created_at, result, error)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                task.id, 
                task.name, 
                task.status.name, 
                json.dumps(task.data), 
                task.created_at,
                json.dumps(task.result) if task.result is not None else None,
                task.error
            ))
            conn.commit()

    def add_task(self, name: str, data: Dict[str, Any] = {}) -> Task:
        task = Task(name=name, data=data)
        self.task_queue.put(task)
        return task

    def get_task(self, task_id: str) -> Task:
        return self.completed_tasks.get(task_id)

    def get_all_tasks(self) -> List[Task]:
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM tasks')
            tasks = cursor.fetchall()
        
        return [
            Task(
                id=task[0],
                name=task[1],
                status=TaskStatus[task[2]],
                data=json.loads(task[3]),
                created_at=task[4],
                result=json.loads(task[5]) if task[5] else None,
                error=task[6]
            ) for task in tasks
        ]

async def main():
    task_manager = TaskManager()

    # Add some example tasks
    task1 = task_manager.add_task('data_processing', {
        'raw_data': [1, 2, 3, 4, 5]
    })

    task2 = task_manager.add_task('complex_computation', {
        'iterations': 5000
    })

    # Wait a bit to let tasks complete
    await asyncio.sleep(3)

    # Retrieve and print task results
    print(f"Task 1 Result: {task_manager.get_task(task1.id).result}")
    print(f"Task 2 Result: {task_manager.get_task(task2.id).result}")



if __name__ == '__main__':
    asyncio.run(main())