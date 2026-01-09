### SSH Manager API

SSH Manager API is a backend REST API built with **FastAPI** that lets you manage remote Linux servers over **SSH** from a single place.

With this project you can:

- **Register and login users** with JWT‑based authentication  
- **Store remote server details** (host, port, username, password or SSH key)  
- **Execute SSH commands** on those servers using Paramiko  
- **Block dangerous commands** (like `rm -rf`, `mkfs`, etc.) for safety  
- **Log every command execution** with output and status  
- **Send email notifications** for important actions (via SendGrid or SMTP)

The focus of the project is on **security**, **logging**, and keeping each user’s servers and command history **isolated and private**.
