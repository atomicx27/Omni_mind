import time
import threading
from typing import Callable, Any

class TTLWatchdog:
    def __init__(self, check_interval: int = 30):
        self.check_interval = check_interval
        self.running = False
        self.thread = None
        self.tasks = {}

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._poll_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

    def register_task(self, task_id: str, ttl: int, timeout_callback: Callable):
        self.tasks[task_id] = {
            "start_time": time.time(),
            "ttl": ttl,
            "callback": timeout_callback
        }

    def complete_task(self, task_id: str):
        if task_id in self.tasks:
            del self.tasks[task_id]

    def _poll_loop(self):
        while self.running:
            current_time = time.time()
            tasks_to_remove = []

            for task_id, task_info in self.tasks.items():
                if current_time - task_info["start_time"] > task_info["ttl"]:
                    try:
                        task_info["callback"](task_id)
                    except Exception as e:
                        print(f"Error in timeout callback for {task_id}: {e}")
                    tasks_to_remove.append(task_id)

            for task_id in tasks_to_remove:
                if task_id in self.tasks:
                    del self.tasks[task_id]

            time.sleep(self.check_interval)
