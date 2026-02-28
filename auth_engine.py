class AuthManager:
    def __init__(self):
        self.users = {}  # username -> password

    def signup(self, username, password):
        if username in self.users:
            return False, "User already exists"
        self.users[username] = password
        return True, "User created"

    def login(self, username, password):
        if self.users.get(username) == password:
            return True, "Login successful"
        return False, "Invalid credentials"