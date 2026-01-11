# A2A Workflow - Understanding Agent-to-Agent Protocol

![A2A Protocol Image](https://storage.googleapis.com/gweb-developer-goog-blog-assets/images/image2.original_6xqVyTd.jpg)

## What is A2A Protocol?

```
     ┌─────────────┐         ┌─────────────┐         ┌─────────────┐
     │   Agent 1   │         │   Agent 2   │         │   Agent 3   │
     │ (Weather)   │         │ (Calculator)│         │ (Database)  │
     └──────┬──────┘         └──────┬──────┘         └──────┬──────┘
            │                       │                       │
            │     A2A Protocol      │     A2A Protocol      │
            └───────────────────────┼───────────────────────┘
                                    │
                            ┌───────▼────────┐
                            │  Agent Network  │
                            │  (Discovery &   │
                            │  Communication) │
                            └────────────────┘
```

The **Agent-to-Agent (A2A) Protocol** is a standardized communication framework that allows different AI agents to discover each other, understand their capabilities, and work together seamlessly.

Think of it like a universal language for agents - just as humans use English to communicate across countries, agents use A2A protocol to communicate regardless of how they're built or what language they're programmed in.

### Core Concepts

#### 1. Agent Card (Discovery)
Every A2A agent publishes an **Agent Card** - a JSON document that describes:
- **Who am I?** - Agent name, version, and description
- **What can I do?** - List of skills/capabilities
- **How do I work?** - Supported input/output modes (text, image, file, etc.)
- **How to reach me?** - Communication protocols (JSON-RPC, HTTP, WebSocket)

This allows clients to automatically discover what an agent can do without any manual setup.

#### 2. Skills
A skill is a **discrete capability** that an agent can perform. Each skill has:
- **Unique ID** - For referencing the skill programmatically
- **Name & Description** - For displaying to users
- **Examples** - Sample inputs showing how to use the skill
- **Tags** - Categories for organization (e.g., "greeting", "weather", "calculation")

#### 3. Messages
Structured communication between client and agent:
- **Role** - Who is speaking (user or assistant)
- **Content** - The actual message (text, images, files, etc.)
- **Message ID** - Unique identifier for tracking conversations
- **Context** - Additional metadata about the conversation

#### 4. Transport Protocols
Different ways messages can be transmitted:
- **JSON-RPC** - Synchronous request-response over HTTP
- **Server-Sent Events (SSE)** - Streaming responses from agent
- **WebSocket** - Real-time bidirectional communication

### Why A2A Protocol Matters

| Benefit | Why It Matters |
|---------|----------------|
| **Standardized Discovery** | No need to manually configure how agents work - they tell you |
| **Interoperability** | Different agents (made by different teams/companies) can work together |
| **Language Agnostic** | Implement in Python, JavaScript, Go, Java - doesn't matter |
| **Extensibility** | Add new skills without breaking existing connections |
| **Type Safety** | Strong typing with validation prevents errors |

---

## Our Learning Example: Greeting Agent

We built a simple **Greeting Agent** to learn how A2A protocol works in practice. Here's what it demonstrates:

### What the Greeting Agent Does

The agent is simple - it listens for messages and responds with a greeting. But in doing so, it teaches us all the fundamental concepts of A2A protocol.

```
User: "Hi How are you?"
Agent: "Hi Everyone! Welcome to Waqar's A2A workflow."
```

### Project Architecture

```
┌─────────────────────────────────────────────┐
│           A2A Protocol Stack                 │
├─────────────────────────────────────────────┤
│                                              │
│  CLIENT (client.py)                         │
│  ├─ Discovers agent via Agent Card          │
│  ├─ Creates A2A client connection           │
│  └─ Sends messages                          │
│           │                                  │
│           │ HTTP/JSON-RPC                   │
│           ▼                                  │
│  SERVER (Starlette + Uvicorn)              │
│  ├─ Publishes Agent Card                    │
│  ├─ Receives messages                       │
│  └─ Forwards to agent                       │
│           │                                  │
│           ▼                                  │
│  AGENT (GreetingAgent)                      │
│  ├─ Defines skills                          │
│  ├─ Processes messages                      │
│  └─ Returns responses                       │
│                                              │
└─────────────────────────────────────────────┘
```

### The Three Components

#### 1. Agent Definition (`agent_executor.py`)

```python
class GreetingAgent:
    """The actual agent logic"""
    async def invoke(self) -> str:
        return "Hi Everyone! Welcome to Waqar's A2A workflow."
```

This is the business logic - what the agent actually does. In this case, it just returns a greeting string.

#### 2. Agent Executor (`agent_executor.py`)

```python
class GreetingAgentExecutor(AgentExecutor):
    """Integrates agent with A2A framework"""
    
    async def execute(self, context: RequestContext, event_queue: EventQueue):
        # Step 1: Run the agent logic
        result = await self.agent.invoke()
        
        # Step 2: Convert to A2A message format
        message = new_agent_text_message(result)
        
        # Step 3: Queue the response to send to client
        await event_queue.enqueue_event(message)
```

This bridges the gap between the agent and the A2A protocol. It:
- Receives requests from the protocol framework
- Calls the agent logic
- Converts the response to A2A format
- Sends it back to the client

#### 3. Server Setup (`__main__.py`)

```python
# Step 1: Define what the agent can do
greeting_skill = AgentSkill(
    id="hello_world",
    name="Greet",
    description="Return a greeting",
    tags=["greeting", "hello", "world"],
    examples=["Hey", "Hi", "Hello"]
)

# Step 2: Create the Agent Card (published to clients)
agent_card = AgentCard(
    name="Greeting Agent",
    description="A simple agent that returns a greeting",
    url="http://localhost:9999/",
    skills=[greeting_skill],
    version="1.0.0"
)

# Step 3: Start the HTTP server
server = A2AStarletteApplication(
    http_handler=DefaultRequestHandler(
        agent_executor=GreetingAgentExecutor(),
        task_store=InMemoryTaskStore()
    ),
    agent_card=agent_card,
)
uvicorn.run(server.build(), host="0.0.0.0", port=9999)
```

This sets up the server that:
- Publishes the Agent Card for discovery
- Listens for incoming messages
- Routes them to the agent executor

### How Messages Flow Through the System

#### Step 1: Discovery
```
Client: "Are you there?"
Server responds with Agent Card showing:
  - Name: "Greeting Agent"
  - Skill: "Greet" (id: hello_world)
  - URL: http://localhost:9999/
```

#### Step 2: Connection
Client now knows:
- Where the agent is
- What it can do
- How to talk to it

#### Step 3: Message Exchange
```
Client sends: {
  "message": "Hi How are you?",
  "role": "user"
}

Server receives and creates RequestContext

RequestContext → GreetingAgentExecutor.execute()
              → GreetingAgent.invoke()
              → Returns greeting string
              → Converts to A2A message
              → Queues for transmission

Client receives: {
  "message": "Hi Everyone! Welcome to Waqar's A2A workflow.",
  "role": "assistant"
}
```

---

## Key A2A Protocol Features Demonstrated

### 1. **Agent Card (Discovery)**
The greeting agent publishes its metadata at `/.well-known/agent.json`:
```json
{
  "name": "Greeting Agent",
  "description": "A simple agent that returns a greeting",
  "version": "1.0.0",
  "url": "http://localhost:9999/",
  "skills": [{
    "id": "hello_world",
    "name": "Greet",
    "description": "Return a greeting",
    "tags": ["greeting", "hello", "world"],
    "examples": ["Hey", "Hi", "Hello"]
  }],
  "defaultInputModes": ["text"],
  "defaultOutputModes": ["text"]
}
```

### 2. **Skill Definition**
Skills tell clients exactly what the agent can do:
- Users can see available skills
- Systems can programmatically discover capabilities
- Examples show how to use each skill

### 3. **Message Protocol**
Messages follow a standard format:
```
Client → Message → Server → Agent → Response → Client
```

Each message contains role (user/assistant), content, and metadata.

### 4. **Async/Non-blocking**
Both the agent and protocol use async patterns:
```python
async def invoke(self) -> str:
    # Non-blocking operation
    return greeting

async def execute(self, context, event_queue):
    # Non-blocking execution
    result = await self.agent.invoke()
```

This allows agents to handle multiple requests simultaneously without blocking.

---

## How This Demonstrates A2A Protocol Concepts

| A2A Concept | How Our Example Shows It |
|-------------|-------------------------|
| **Agent Card** | Server publishes skill definition and metadata |
| **Skill Definition** | "Greet" skill with examples and descriptions |
| **Message Format** | Client sends structured message, gets structured response |
| **Async Execution** | Agent uses async/await for non-blocking operations |
| **Standardized Communication** | HTTP/JSON-RPC for universal compatibility |
| **Discovery** | Client automatically learns what agent can do |

---

## Why This Matters for Learning A2A

Our greeting agent is intentionally simple because:

1. **Easy to understand** - Focus on protocol, not business logic
2. **Complete example** - Shows all A2A components working together
3. **Extensible** - Easy to add more features and complexity
4. **Realistic** - Uses production-ready libraries and patterns

---

## Scaling the Concept

Once you understand how the greeting agent works, you can build much more complex systems:

- **Weather Agent** - Returns weather data
- **Calculator Agent** - Performs calculations
- **Database Agent** - Queries databases
- **Multi-skill Agent** - Handles multiple different tasks
- **Agent Networks** - Agents calling other agents

All follow the same A2A protocol principles as our simple greeting agent.

---

**Project Version:** 0.1.0  
**Author:** Waqar (A2A Workflow Team)  
**Date:** January 11, 2026
