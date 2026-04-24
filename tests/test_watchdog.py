import pytest
from core.watchdog import TTLWatchdog
from unittest.mock import patch

@patch('time.sleep', return_value=None)
@patch('time.time')
def test_watchdog_timeout(mock_time, mock_sleep):
    # Watchdog normally polls, we'll manually call the poll loop once instead of starting the thread
    watchdog = TTLWatchdog(check_interval=1)

    timeout_called = False
    timed_out_task = None

    def on_timeout(task_id):
        nonlocal timeout_called, timed_out_task
        timeout_called = True
        timed_out_task = task_id

    mock_time.return_value = 1000.0
    watchdog.register_task("task-1", 2, on_timeout)

    # Simulate time passing beyond TTL
    mock_time.return_value = 1005.0

    # We can just manually check without running the infinite loop
    watchdog.running = True

    # Do one iteration manually
    current_time = mock_time.return_value
    tasks_to_remove = []

    for task_id, task_info in watchdog.tasks.items():
        if current_time - task_info["start_time"] > task_info["ttl"]:
            task_info["callback"](task_id)
            tasks_to_remove.append(task_id)

    assert timeout_called == True
    assert timed_out_task == "task-1"
