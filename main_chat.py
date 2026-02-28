from chat_engine import ChatRoomManager

manager = ChatRoomManager()
manager.create_room("Backend")
room = manager.get_room("Backend")

username = input("Enter your username: ")
room.join(username)

print("Type messages. Use '@ai <code>' to trigger AI.\n")

while True:
    msg = input("You: ")
    ai_response = room.add_message(username, msg)

    if ai_response:
        print(f"\nAI: {ai_response['content']}\n")