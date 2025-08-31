
# Weather Forecasting App

A Python-based client-server application that allows users to securely retrieve real-time weather information using a GUI. The system employs socket communication, user authentication, and optional encryption (Caesar or Vigenère cipher) for secure data transfer.

---

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Dependencies](#dependencies)
- [Documentation](#documentation)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
- [Contributors](#contributors)
- [License](#license)

---

## Introduction

This project consists of a server that connects to the OpenWeatherMap API and a Tkinter-based client that allows users to:
- Authenticate using predefined credentials.
- Select an encryption method (Caesar or Vigenère).
- Query weather data for any city.

The server handles authentication, logging, and data retrieval, while the client offers a user-friendly graphical interface.

---

## Features

- Socket-based communication between client and server
- SQLite-based user authentication
- Graphical client interface using Tkinter
- Optional encryption (Caesar/Vigenère cipher)
- Integration with OpenWeatherMap API
- Logging system for monitoring (saved to `server.log`)

---

## Installation

### Prerequisites

- Python 3.12
- Internet access (for weather data)
- IDE like PyCharm or Visual Studio Code (recommended)

### Setup

1. **Clone or Extract the Repository**
   - Ensure the project structure includes both `Client` and `Server` directories.

2. **Install Python**
   - Download from [python.org](https://www.python.org/) and install.
   - Add Python to PATH during installation.

3. **Install Dependencies**
   Open a terminal in both `Client` and `Server` directories and run:
   ```bash
   pip install requests
   ```

---

## Usage

### 1. Start the Server

```bash
cd Server
python server.py
```
The server will start listening on `127.0.0.1:65432`.

### 2. Run the Client

```bash
cd Client
python client.py
```

You will be presented with a GUI to:
- **Log in** using:
  - `user1 / password1`
  - `user2 / password2`
- **Select a cipher method** (Caesar or Vigenère).
- **Search for weather** information by entering a city name.

---

## Configuration

- **Weather API Key** is hardcoded in `server.py`:
  ```python
  API_KEY = "1204d66abcb02a7a59a3bcac67f8e90a"
  ```
  Replace it with your own OpenWeatherMap API key if needed.

- **Database Initialization**: The server auto-generates `users.db` with default users. To add more, modify `init_database()` in `server.py`.

---

## Dependencies

The following libraries are used (some are part of the standard library):

- `socket`
- `threading`
- `sqlite3`
- `hashlib`
- `requests`
- `tkinter`
- `logging`

Install non-standard packages via:
```bash
pip install requests
```

---

## Documentation

Documentation is included in the `Documentation/` folder:

- **Requirements.txt** – Setup, usage, and troubleshooting guide
- **Implementation Log.rtf** – (Optional) Development log
- **Testing.rtf** – (Optional) Testing procedures and results

---

## Examples

1. **Login Screen**  
   Enter valid credentials.

2. **Cipher Selection**  
   Choose Caesar or Vigenère.

3. **Weather Query**  
   Enter a city name and view the weather.

---

## Troubleshooting

| Problem                          | Solution                                                                 |
|----------------------------------|--------------------------------------------------------------------------|
| Cannot connect to server         | Ensure server is running and accessible at `127.0.0.1:65432`             |
| Weather data not showing         | Check API key and internet connection                                   |
| Database authentication failure  | Delete `users.db` and restart server to regenerate defaults              |
| Tkinter not working              | Ensure `tkinter` is installed and supported by your Python installation |

---

## Contributors

- Project designed and implemented by original submitter.
- Maintained and reviewed via automated documentation tools.

---

## License

This project is free to use and modify for educational purposes.
