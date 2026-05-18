from __future__ import annotations

import asyncio
import os

from agent.workflow import AgentWorkflow


async def hourly_demo_loop() -> None:
    """Optional demo scheduler; manual dashboard controls remain the primary path."""
    if os.getenv("SCHEDULER_ENABLED", "false").lower() != "true":
        return
    workflow = AgentWorkflow()
    snapshots = ["10am", "12pm", "2pm"]
    index = 0
    while True:
        workflow.ingest(snapshots[index % len(snapshots)])
        index += 1
        await asyncio.sleep(3600)

