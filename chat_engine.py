from ai_engine import get_ai_response
from datetime import datetime


class ChatRoom:
    def __init__(self, name, language="Auto", visibility="public"):
        self.name = name
        self.language = language
        self.visibility = visibility  # public / private
        self.members = {}
        self.messages = []
        self.notifications = []
        self.created_at = datetime.now()
        self.last_active = None

    def join(self, username):
        self.members[username] = "online"

    def leave(self, username):
        self.members[username] = "offline"

    def get_notifications(self):
        return self.notifications
    
    def clear_notifications(self):
        self.notifications = []

    def add_message(self, username, content):

        message = {
            "user": username,
            "content": content,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "is_code": "```" in content,
            "mentions_ai": content.startswith("@ai")
        }

        self.messages.append(message)
        self.last_active = datetime.now()

        if message["mentions_ai"]:
            return self.handle_ai(content)

        return None

    def handle_ai(self, content, mode="fix"):
        code = content.replace("@ai", "").strip()

        context_messages = self.messages[-5:]
        context_text = "\n".join(
            [f"{m['user']}: {m['content']}" for m in context_messages]
        )

        ai_output = get_ai_response(code, mode=mode, context=context_text)

        ai_message = {
            "user": "AI_Assistant",
            "content": ai_output,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "ai_mode": mode
        }

        self.messages.append(ai_message)
        self.notifications.append({
            "type": "AI_RESPONSE",
            "message": "AI generated a response",
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        return ai_message
    
    def trigger_ai(self, code, mode):
        context_messages = self.messages[-5:]
        context_text = "\n".join(
            [f"{m['user']}: {m['content']}" for m in context_messages]
        )

        return get_ai_response(code, mode=mode, context=context_text)
    
class ChatRoomManager:
    def __init__(self):
        self.rooms = {}

    def create_room(self, name, language="Auto", visibility="public"):
        self.rooms[name] = ChatRoom(name, language, visibility)

    def get_room(self, room_name):
        return self.rooms.get(room_name)

    def list_rooms(self):
        return [
            {
                "name": room.name,
                "language": room.language,
                "visibility": room.visibility,
                "members_count": len(room.members),
                "last_active": room.last_active.strftime("%H:%M:%S") if room.last_active else "No activity"
            }
            for room in self.rooms.values()
        ]
        
    def get_room_info(self):
        return [
            {
                "name": room.name,
                "language": room.language,
                "members": len(room.members),
                "visibility": room.visibility,
                "last_active": room.messages[-1]["timestamp"] if room.messages else None
            }
            for room in self.rooms.values()
        ]
    
    def search_rooms(self, query):
        return [
            room.name
            for room in self.rooms.values()
            if query.lower() in room.name.lower()
        ]