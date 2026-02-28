class AuthManager:
    def __init__(self):
        # Pre-loaded accounts for judges
        self.users = {
            "SanketMohapatra06": "password123",
            "VarunSir": "gate2026",
            "Asmit": "ai_god"
        }

    def signup(self, username, password):
        if not username or not password:
            return False, "Fields cannot be empty"
        if username in self.users:
            return False, "User already exists"
        self.users[username] = password
        return True, "User created successfully!"

    def login(self, username, password):
        # Using .get() prevents a KeyError if the user doesn't exist
        if self.users.get(username) == password:
            return True, "Login successful"
        return False, "Invalid username or password"
