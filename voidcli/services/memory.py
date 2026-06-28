# services/memory.py

class Memory:
    

    def __init__(self, system_prompt: str):
        self.messages = [
            {
                "role": "system",
                "content": system_prompt
            }
        ]

    def add_user(self, content: str):
        self.messages.append({
            "role": "user",
            "content": content
        })

    def add_assistant(self, message: dict):
        
        self.messages.append(message)

    def add_tool(self, tool_call_id: str, tool_name: str, result: str):
       
        self.messages.append({
            "role": "tool",
            "tool_call_id": tool_call_id,
            "name": tool_name,
            "content": result
        })

    def get_messages(self):
        return self.messages

    def clear(self):
        system = self.messages[0]
        self.messages = [system]

    def last_message(self):
        return self.messages[-1]

    def print_history(self):
        for msg in self.messages:
            print(f"{msg['role'].upper()}:")
            print(msg)
            print("-" * 40)