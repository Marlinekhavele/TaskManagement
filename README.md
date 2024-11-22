Task Management System
- A robust Python-based task management system with concurrent processing, task tracking, and persistent storage.

### Features:
- Asynchronous task processing
- Multithreaded worker system
- SQLite-based task persistence
- Dynamic task execution
- Comprehensive error handling
- Flexible task management

### Requirements:
- Python 3.8+
Libraries:
- asyncio
- sqlite3
- threading
- uuid
- logging

#### Installation:
```bash 
git clone https://github.com/Marlinekhavele/TaskManagement
cd Task
pip install -r requirements.txt
```
#### Usage:
Basic Task Creation
```bash 
from task_manager TaskManager

# Initialize task manager
task_manager = TaskManager()

# Add tasks
task1 = task_manager.add_task('data_processing', {
    'raw_data': [1, 2, 3, 4, 5]
})

task2 = task_manager.add_task('complex_computation', {
    'iterations': 5000
})
```

##### Retrieving Task Results:
Get task by ID
```bash
result = task_manager.get_task(task1.id)
print(f"Task Status: {result.status}")
print(f"Task Result: {result.result}")
```
##### Extending Task Types
To add custom task types, modify the ```_execute_task()``` method:
```bash
def _execute_task(self, task_name: str, data: Dict[str, Any]) -> Any:
    if task_name == 'your_custom_task':
        return self._custom_task_handler(data)
```
Configuration
```max_workers```: Configure concurrent worker count
```database_path```: Specify custom SQLite database location

```bash
task_manager = TaskManager(
    max_workers=6, 
    database_path='custom_tasks.db'
)
```
#### Error Handling

- Tasks with errors are marked with ```TaskStatus.FAILED```
- Error details stored in ```task.error```

#### Persistent Storage

- All tasks are automatically saved to SQLite database
- Retrieve task history using ```get_all_tasks()```

#### Performance Considerations:
- Adjustable worker count
- Asynchronous processing
- Minimal overhead for task management

#### Contributing:
- Fork the repository
- Create feature branch
- Commit changes
- Push to branch
- Create pull request