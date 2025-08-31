import socket
import threading
import sqlite3
import hashlib
import requests
import logging

# Server Configuration
HOST = '127.0.0.1'
PORT = 65432

API_KEY = "1204d66abcb02a7a59a3bcac67f8e90a"
WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather"

# Logger Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("server.log"),
        logging.StreamHandler()
    ]
)


# Define States
class ClientState:
    INITIAL = "INITIAL"
    AUTHENTICATING = "AUTHENTICATING"
    AUTHENTICATED = "AUTHENTICATED"
    SELECT_CIPHER = "SELECT_CIPHER"
    WEATHER_SEARCH = "WEATHER_SEARCH"
    DISCONNECTED = "DISCONNECTED"


class StateMachine:
    def __init__(self):
        self.state = ClientState.INITIAL
        self.cipher = None

    def set_state(self, new_state):
        logging.info(f"State transition: {self.state} -> {new_state}")
        self.state = new_state

    def get_state(self):
        return self.state

    def set_cipher(self, cipher):
        logging.info(f"Cipher selected: {cipher}")
        self.cipher = cipher

    def get_cipher(self):
        return self.cipher


# Initialize Database
def init_database():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        password_hash TEXT
                     )''')
    # Insert default records
    cursor.execute('''INSERT OR IGNORE INTO users (username, password_hash) VALUES (?, ?)''',
                   ("user1", hashlib.sha256("password1".encode()).hexdigest()))
    cursor.execute('''INSERT OR IGNORE INTO users (username, password_hash) VALUES (?, ?)''',
                   ("user2", hashlib.sha256("password2".encode()).hexdigest()))

    conn.commit()
    conn.close()

# API call
def get_weather_data(location):
    try:
        params = {
            'q': location,
            'appid': API_KEY,
            'units': 'metric',
        }
        response = requests.get(WEATHER_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            weather_info = f"City: {data['name']}\n" \
                           f"Temperature: {data['main']['temp']}°C\n" \
                           f"Humidity: {data['main']['humidity']}%\n" \
                           f"Weather: {data['weather'][0]['description'].capitalize()}\n"
            return weather_info
        else:
            return f"Error: Unable to fetch weather data for {location}."
    except Exception as e:
        logging.error("Error fetching weather data: " + str(e))
        return "Exception occurred: " + str(e)



# Caesar Cipher
def caesar_cipher(text, shift):
    encrypted = ""
    for char in text:
        if char.isalpha():
            shift_base = 65 if char.isupper() else 97
            encrypted += chr((ord(char) - shift_base + shift) % 26 + shift_base)
        else:
            encrypted += char
    return encrypted

# Vigenere Cipher
def vigenere_cipher(text, key):
    key = key.lower()
    encrypted = ""
    key_index = 0
    for char in text:
        if char.isalpha():
            shift = ord(key[key_index % len(key)]) - 97
            shift_base = 65 if char.isupper() else 97
            encrypted += chr((ord(char) - shift_base + shift) % 26 + shift_base)
            key_index += 1
        else:
            encrypted += char
    return encrypted

# Authenticate User
def authenticate_user(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT password_hash FROM users WHERE username = ?', (username,))
    record = cursor.fetchone()
    conn.close()

    if record:
        stored_hash = record[0]
        input_hash = hashlib.sha256(password.encode()).hexdigest()
        print(f"Stored hash: {stored_hash}")
        print(f"Input hash: {input_hash}")
        return stored_hash == input_hash
    else:
        print("Username not found.")
        return False


# Handle Client Connection
def handle_client(client_socket, address):
    state_machine = StateMachine()
    logging.info(f"Connection established with {address}")
    state_machine.set_state(ClientState.AUTHENTICATING)

    try:
        # Authenticate user
        credentials = client_socket.recv(1024).decode()
        username, password = credentials.split(",")

        if authenticate_user(username, password):
            state_machine.set_state(ClientState.SELECT_CIPHER)
            client_socket.send(b"True")
            logging.info(f"User '{username}' authenticated successfully.")
        else:
            state_machine.set_state(ClientState.DISCONNECTED)
            client_socket.send(b"False")
            logging.warning(f"Authentication failed for user '{username}'.")
            return

        # Select Cipher
        cipher = client_socket.recv(1024).decode()
        state_machine.set_cipher(cipher)

        # Weather Search
        state_machine.set_state(ClientState.WEATHER_SEARCH)
        while state_machine.get_state() == ClientState.WEATHER_SEARCH:
            location = client_socket.recv(1024).decode()
            if location.lower() == "exit":
                state_machine.set_state(ClientState.DISCONNECTED)
                break
            weather_info = get_weather_data(location)

            # Apply cipher
            if state_machine.get_cipher() == "Caesar":
                encrypted_data = caesar_cipher(weather_info, shift=3)
            elif state_machine.get_cipher() == "Vigenère":
                encrypted_data = vigenere_cipher(weather_info, key="key")
            else:
                encrypted_data = weather_info

            client_socket.send(encrypted_data.encode())

    except Exception as e:
        logging.error(f"Error handling client {address}: {e}")
    finally:
        state_machine.set_state(ClientState.DISCONNECTED)
        logging.info(f"Client {address} disconnected.")
        client_socket.close()


# Start Server
def start_server():
    init_database()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(2)
    logging.info(f"Server started on {HOST}:{PORT}")

    print(get_weather_data('Thessaloniki'))

    try:
        while True:
            client_socket, address = server_socket.accept()
            threading.Thread(target=handle_client, args=(client_socket, address)).start()
    except KeyboardInterrupt:
        logging.info("Shutting down server...")
    finally:
        server_socket.close()


if __name__ == "__main__":
    start_server()
