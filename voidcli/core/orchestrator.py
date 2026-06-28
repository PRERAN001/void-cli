# core/orchestrator.py

class Orchestrator:

    def __init__(self, session):

        self.session = session

    def run(self):

        while self.session.bus.has_events():

            event = self.session.bus.consume()

            agents = self.session.registry.find_agents(event)

            if not agents:

                if event.event_type == "TASK_COMPLETED":
                    task = self.session.tasks.get(event.task_id)
                    if task:
                        task.status = "COMPLETED"
                        if task.result:
                            print(task.result)
                    print("Task completed.")
                elif event.event_type == "TOOL_FAILED":
                    task = self.session.tasks.get(event.task_id)
                    if task:
                        task.status = "FAILED"
                    print(f"Tool failed: {event.payload.get('error')}")
                else:
                    print(f"No agent for {event.event_type}")

                continue

            for agent in agents:

                print(f"[{agent.name}] -> {event.event_type}")

                new_events = agent.handle(event)

                if new_events:

                    for e in new_events:

                        self.session.bus.publish(e)
