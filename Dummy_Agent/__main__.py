from a2a.types import AgentCard, AgentSkill, AgentCapabilities
from a2a.server.request_handlers import DefaultRequestHandler
from agent_executor import GreetingAgentExecutor
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.apps import A2AStarletteApplication
import uvicorn

def main():

    greeting_skill = AgentSkill(
        id="hello_world",
        name="Greet",
        description="Return a greeting",
        tags=["greeting", "hello", "world"],
        examples=["Hey", "Hi", "Hello"]
    )

    agent_card = AgentCard(
        name="Greeting Agent",
        description="A simple agent that returns a greeting",
        url="http://localhost:9999/",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[greeting_skill],
        version="1.0.0",
        capabilities=AgentCapabilities()
    )


    request_handler=DefaultRequestHandler(
        agent_executor=GreetingAgentExecutor(),
        task_store=InMemoryTaskStore()
    )



    server = A2AStarletteApplication(
        http_handler=request_handler,
        agent_card=agent_card,
    )


    uvicorn.run(server.build(), host="0.0.0.0", port=9999)


if __name__ == "__main__":
    main()

"""
To test the agent, you can run the following command in your terminal after starting the server:
curl http://localhost:9999/.well-known/agent.json
"""