---
name: create-agent-adapter
description: >
  Create a Paperclip adapter for JARVIS so Paperclip can orchestrate
  JARVIS as a local agent. Use when connecting JARVIS voice assistant
  to Paperclip's company OS, or when building any new agent adapter.
  Triggers on: "create JARVIS adapter", "connect JARVIS to Paperclip",
  "build agent adapter", "make JARVIS work with Paperclip".
metadata:
  sources:
    - kind: github-file
      repo: paperclipai/paperclip
      path: .agents/skills/create-agent-adapter/SKILL.md
      attribution: paperclipai
      license: MIT
      usage: referenced
---

# JARVIS Adapter for Paperclip

## What This Creates

A `jarvis_local` adapter so Paperclip can:
- Send tasks to JARVIS via jarvis_crew_bridge.py
- Receive status reports back
- Show JARVIS runs in Paperclip dashboard
- Schedule tasks for JARVIS agents

## Adapter Structure

```
packages/adapters/jarvis-local/
  src/
    index.ts          # type="jarvis_local", label="JARVIS (Local)"
    server/
      execute.ts      # Calls jarvis_crew_bridge.py
      parse.ts        # Parses JARVIS output
      test.ts         # Checks JARVIS is running
    ui/
      build-config.ts
      parse-stdout.ts
    cli/
      format-event.ts
```

## Core Execute Logic

```typescript
// execute.ts — JARVIS adapter
async function execute(ctx: AdapterExecutionContext) {
  const { topic, task_type } = ctx.config;

  // Call JARVIS via Python bridge
  const result = await fetch("http://localhost:8765/task", {
    method: "POST",
    body: JSON.stringify({
      task: ctx.runtime.sessionParams?.prompt,
      type: task_type || "youtube_pipeline"
    })
  });

  return {
    exitCode: 0,
    summary: `JARVIS completed: ${task_type}`,
    resultJson: await result.json()
  };
}
```

## JARVIS Bridge Server

Add to JARVIS-AI-Assistant/jarvis_paperclip_bridge.py:

```python
from flask import Flask, request, jsonify
import asyncio
from jarvis_crew_bridge import create_youtube_video, get_agent_status

app = Flask(__name__)

@app.route('/task', methods=['POST'])
def handle_task():
    data = request.json
    task = data.get('task', '')
    task_type = data.get('type', 'general')

    if 'video' in task_type:
        result = asyncio.run(create_youtube_video(task))
    else:
        result = {"status": "done", "message": f"Task: {task}"}

    return jsonify(result)

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify({"status": "online", "agent": "JARVIS"})

if __name__ == '__main__':
    app.run(port=8765)
```

## adapter type registration

```
.paperclip.yaml mein:
agents:
  ceo:
    adapter:
      type: jarvis_local
      config:
        bridgeUrl: "http://localhost:8765"
```
