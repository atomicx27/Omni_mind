"use client";

import { useEffect, useState } from "react";

interface Task {
  task_id: string;
  status: string;
  assigned_persona: string;
}

export default function Home() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [killStatus, setKillStatus] = useState<string | null>(null);

  useEffect(() => {
    const eventSource = new EventSource("http://localhost:8000/events");

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "task.update") {
        setTasks(data.tasks);
      }
    };

    eventSource.onerror = (error) => {
      console.error("SSE error:", error);
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, []);

  const handleKillSwitch = async () => {
    try {
      const response = await fetch("http://localhost:8000/kill", {
        method: "POST",
      });
      const result = await response.json();
      setKillStatus(result.message);
    } catch (error) {
      console.error("Kill switch error:", error);
      setKillStatus("Failed to send kill signal");
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8 font-sans">
      <header className="mb-8 flex justify-between items-center">
        <h1 className="text-3xl font-bold">Sovereign AGI Dashboard</h1>
        <button
          onClick={handleKillSwitch}
          className="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
        >
          KILL SWITCH
        </button>
      </header>

      {killStatus && (
        <div className="mb-4 p-4 bg-red-900/50 border border-red-500 rounded text-red-200">
          {killStatus}
        </div>
      )}

      <div>
        <h2 className="text-xl font-semibold mb-4 border-b border-gray-700 pb-2">Active Tasks</h2>
        {tasks.length === 0 ? (
          <p className="text-gray-400">No active tasks.</p>
        ) : (
          <div className="grid gap-4">
            {tasks.map((task) => (
              <div
                key={task.task_id}
                className="bg-gray-800 p-4 rounded-lg border border-gray-700 shadow flex justify-between items-center"
              >
                <div>
                  <div className="text-sm text-gray-400 font-mono mb-1">{task.task_id}</div>
                  <div className="font-semibold text-lg">{task.assigned_persona}</div>
                </div>
                <div>
                  <span
                    className={`px-3 py-1 rounded-full text-sm font-medium ${
                      task.status === "RESOLVED"
                        ? "bg-green-900/50 text-green-300"
                        : task.status === "FAILED"
                        ? "bg-red-900/50 text-red-300"
                        : "bg-blue-900/50 text-blue-300"
                    }`}
                  >
                    {task.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
