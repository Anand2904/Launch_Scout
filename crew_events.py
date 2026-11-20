import os

# Skip CrewAI's cloud trace-sharing prompt (we show our own trace in the app)
os.environ.setdefault("CREWAI_TRACING_ENABLED", "false")

import time

from crewai.events import (
    crewai_event_bus,
    TaskStartedEvent,
    TaskCompletedEvent,
    ToolUsageStartedEvent,
    ToolUsageFinishedEvent,
)

_queue = None


def set_queue(q):
    """The app gives us a queue; every crew event is pushed into it."""
    global _queue
    _queue = q


def _emit(kind, agent, **data):
    if _queue is not None and agent:
        _queue.put({"t": time.time(), "kind": kind, "agent": agent, **data})


def _task_agent(event):
    task = getattr(event, "task", None)
    agent = getattr(task, "agent", None)
    return getattr(agent, "role", None) or getattr(event, "agent_role", None)


@crewai_event_bus.on(TaskStartedEvent)
def _on_task_started(source, event):
    _emit("task_start", _task_agent(event))


@crewai_event_bus.on(TaskCompletedEvent)
def _on_task_completed(source, event):
    raw = getattr(event.output, "raw", "") or ""
    _emit("task_done", _task_agent(event), chars=len(raw))


@crewai_event_bus.on(ToolUsageStartedEvent)
def _on_tool_started(source, event):
    _emit("tool_start", event.agent_role, tool=event.tool_name, args=event.tool_args)


@crewai_event_bus.on(ToolUsageFinishedEvent)
def _on_tool_finished(source, event):
    _emit(
        "tool_done",
        event.agent_role,
        tool=event.tool_name,
        chars=len(str(event.output or "")),
    )