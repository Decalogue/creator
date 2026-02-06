import os
from evermemos import EverMemOS

evermemos_api_key = os.getenv("EVERMEMOS_API_KEY")

memory = EverMemOS(api_key=evermemos_api_key).v1.memories


def add_memory(messages):
    for message in messages:
        response = memory.add(**message)
        print(f"Status: {response.status}, Message: {response.message}, Request ID: {response.request_id}")


def get_memory(user_id):
    response = memory.get(
        extra_query={"user_id": user_id}
    )
    memories = response.result.memories
    print(f"Fetched {len(memories) if memories else 0} memories")
    return memories


def search_memory(user_id, query):
    response = memory.search(
        extra_query={
            "user_id": user_id,
            "query": query
        }
    )
    total = response.result.total_count
    print(f"Found {total} memories")
    return response.result.memories


def delete_memory(user_id, memory_id):
    response = memory.delete(
        extra_query={
            "user_id": user_id,
            "memory_id": memory_id
        }
    )
    print(f"Status: {response.status}, Message: {response.message}, Request ID: {response.request_id}")


if __name__ == "__main__":
    messages = [
        {
            "message_id": "msg_001",
            "create_time": "2026-02-6T10:00:00Z",
            "sender": "user_demo_001",
            "sender_name": "Demo User",
            "group_id": "group_001",
            "content": "I like black Americano, no sugar, the stronger the better!"
        }
    ]
    add_memory(messages)

    memories = get_memory("user_demo_001")
    print(memories)

    memories = search_memory("user_demo_001", "coffee preference")
    print(memories)
