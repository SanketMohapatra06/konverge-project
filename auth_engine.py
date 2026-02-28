class AuthManager:
    def __init__(self):
        # Pre-load some accounts so the judges can test it instantly without signing up
        self.users = {
            "SanketMohapatra06": "password123",
            "VarunSir": "gate2026",
            "Asmit": "ai_god"
        }

    def signup(self, username, password):
        if username in self.users:
            return False, "User already exists"
        self.users[username] = password
        return True, "User created"

    def login(self, username, password):
        if self.users.get(username) == password:
            return True, "Login successful"
        return False, "Invalid credentials"
