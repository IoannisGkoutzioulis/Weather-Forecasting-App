import tkinter as tk
from tkinter import messagebox
import socket


class ClientState:
    LOGIN = "LOGIN"
    AUTHENTICATED = "AUTHENTICATED"
    SELECT_CIPHER = "SELECT_CIPHER"
    WEATHER_SEARCH = "WEATHER_SEARCH"
    DISCONNECTED = "DISCONNECTED"


class StateMachine:
    def __init__(self):
        self.state = ClientState.LOGIN

    def set_state(self, new_state):
        print(f"State transition: {self.state} -> {new_state}")
        self.state = new_state

    def get_state(self):
        return self.state


# Global State Machine
state_machine = StateMachine()


def connect_to_server(username, password):
    HOST = '127.0.0.1'  # Server IP
    PORT = 65432  # Server Port

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((HOST, PORT))
            print(f"Connected to server at {HOST}:{PORT}")

            # Send username and password to server
            credentials = f"{username},{password}"
            client_socket.send(credentials.encode())

            # Server response
            response = client_socket.recv(1024).decode()
            if response == "True":
                state_machine.set_state(ClientState.AUTHENTICATED)
                messagebox.showinfo("Login Successful", "Welcome!")
                open_cipher_selection_gui(client_socket)
            else:
                state_machine.set_state(ClientState.LOGIN)
                messagebox.showwarning("Login Failed", "Invalid credentials.")
    except Exception as e:
        state_machine.set_state(ClientState.DISCONNECTED)
        messagebox.showerror("Connection Error", f"Unable to connect to server. {e}")


def create_login_gui():
    def on_login():
        username = username_entry.get()
        password = password_entry.get()
        if username and password:
            connect_to_server(username, password)
        else:
            messagebox.showwarning("Input Error", "Please enter both username and password.")

    # Initialize GUI
    root = tk.Tk()
    root.title("Login")
    root.geometry("300x200")

    # Username label and entry
    username_label = tk.Label(root, text="Username:")
    username_label.pack(pady=5)
    username_entry = tk.Entry(root)
    username_entry.pack(pady=5)

    # Password label and entry
    password_label = tk.Label(root, text="Password:")
    password_label.pack(pady=5)
    password_entry = tk.Entry(root, show="*")
    password_entry.pack(pady=5)

    # Login button
    login_button = tk.Button(root, text="Login", command=on_login)
    login_button.pack(pady=10)

    root.mainloop()


def open_cipher_selection_gui(client_socket):
    def select_cipher(cipher):
        client_socket.send(cipher.encode())  # stelnoume ton typo kryptografisis ston server
        messagebox.showinfo("Cipher Selected", f"You selected: {cipher}")
        state_machine.set_state(ClientState.WEATHER_SEARCH)
        open_weather_search_gui(client_socket, cipher)

    root = tk.Tk()
    root.title("Select Cipher")
    root.geometry("300x150")

    # Instructions
    label = tk.Label(root, text="Select Encryption Method:")
    label.pack(pady=10)

    # Cipher buttons
    caesar_button = tk.Button(root, text="Caesar Cipher", command=lambda: select_cipher("Caesar"))
    caesar_button.pack(pady=5)

    vigenere_button = tk.Button(root, text="Vigenère Cipher", command=lambda: select_cipher("Vigenère"))
    vigenere_button.pack(pady=5)

    root.mainloop()


def caesar_cipher(text, shift):
    encrypted = ""
    for char in text:
        if char.isalpha():
            shift_base = 65 if char.isupper() else 97
            encrypted += chr((ord(char) - shift_base + shift) % 26 + shift_base)
        else:
            encrypted += char
    return encrypted


# Caesar Decryption
def caesar_decrypt(text, shift):
    return caesar_cipher(text, -shift)


# Vigenere Decryption
def vigenere_decrypt(text, key):
    decrypted = ""
    key = key.lower()
    key_index = 0
    for char in text:
        if char.isalpha():
            shift = -(ord(key[key_index % len(key)]) - 97)
            shift_base = 65 if char.isupper() else 97
            decrypted += chr((ord(char) - shift_base + shift) % 26 + shift_base)
            key_index += 1
        else:
            decrypted += char
    return decrypted


def open_weather_search_gui(client_socket, cipher):
    def search_weather():
        location = location_entry.get()
        if location:
            client_socket.send(location.encode())
            encrypted_response = client_socket.recv(1024).decode()

            # Decrypt data
            if cipher == "Caesar":
                decrypted_data = caesar_decrypt(encrypted_response, shift=3)
            elif cipher == "Vigenère":
                decrypted_data = vigenere_decrypt(encrypted_response, key="key")
            else:
                decrypted_data = encrypted_response  # No decryption

            display_weather(decrypted_data)
        else:
            messagebox.showwarning("Input Error", "Please enter a location.")

    def disconnect():

        client_socket.send(b"exit")  # prepei ta dedomena na einai byte, gia auto exoume to b
        state_machine.set_state(ClientState.DISCONNECTED)
        messagebox.showinfo("Disconnected", "You have been disconnected.")
        root.destroy()

    def display_weather(data):
        weather_window = tk.Toplevel(root)
        weather_window.title("Weather Data")
        weather_window.geometry("400x200")
        weather_label = tk.Label(weather_window, text="Weather Information (Encrypted):", font=("Arial", 12))
        weather_label.pack(pady=10)
        data_label = tk.Label(weather_window, text=data, wraplength=380, justify="left", font=("Arial", 10))
        data_label.pack(pady=5)

    root = tk.Tk()
    root.title("Weather Search")
    root.geometry("400x200")

    # Location input
    location_label = tk.Label(root, text="Enter city or country:")
    location_label.pack(pady=5)
    location_entry = tk.Entry(root, width=30)
    location_entry.pack(pady=5)

    # Search button
    search_button = tk.Button(root, text="Search Weather", command=search_weather)
    search_button.pack(pady=10)

    # Disconnect button
    disconnect_button = tk.Button(root, text="Disconnect", command=disconnect)
    disconnect_button.pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    create_login_gui()
