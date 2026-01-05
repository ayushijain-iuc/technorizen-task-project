# SSH Manager API

A comprehensive backend REST API service for managing remote Linux servers via SSH, with user authentication, profile management, and email notifications.

## Features

- 🔐 **User Authentication**: JWT-based authentication with secure password hashing (bcrypt)
- 👤 **User Profile Management**: Complete CRUD operations for user profiles (First Name, Last Name, Age, Email, Phone, Profile Photo)
- 🖥️ **Remote Server Management**: Add, view, update, and delete remote Linux servers
- ⚡ **SSH Command Execution**: Execute commands on remote servers via SSH with security restrictions
- 📧 **Email Notifications**: Send email notifications via SendGrid or SMTP for command executions
- 📝 **Command Logging**: Track all command executions with timestamps and server details
- 🛡️ **Security**: Block potentially destructive commands (rm -rf, format, etc.)

## Technology Stack

- **Framework**: FastAPI (Python)
- **Database**: Supabase PostgreSQL (recommended) or SQLite
- **Authentication**: JWT (JSON Web Tokens) with bcrypt password hashing
- **SSH**: Paramiko library
- **Email**: SendGrid API or SMTP
- **Deployment**: Render, Vercel (or any WSGI/ASGI compatible server)

## Project Structure

```
.
├── main.py                 # Main FastAPI application
├── config.py              # Configuration settings
├── database.py            # Database connection and session management
├── models.py              # SQLAlchemy database models
├── schemas.py             # Pydantic schemas for request/response validation
├── auth.py                # Authentication and JWT utilities
├── ssh_service.py         # SSH command execution service
├── email_service.py       # Email notification service
├── routers/               # API route handlers
│   ├── __init__.py
│   ├── auth.py           # Authentication routes (register, login)
│   ├── profile.py        # Profile management routes
│   ├── servers.py        # Server management routes
│   └── commands.py       # Command execution routes
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── render.yaml           # Render deployment configuration
├── vercel.json           # Vercel deployment configuration
├── Procfile              # Process file for deployment
└── README.md             # This file
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Local Setup

1. **Clone the repository** (or download the project files)

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Create environment file**:
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env and configure your settings
   ```

5. **Configure environment variables** in `.env`:
   ```env
   # Database (Supabase PostgreSQL - Recommended)
   DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.YOUR_PROJECT.supabase.co:5432/postgres
   
   # For local development with SQLite (optional):
   # DATABASE_URL=sqlite:///./ssh_manager.db
   
   # JWT Secret Key (generate a secure random string)
   SECRET_KEY=your-secret-key-here-change-in-production-min-32-chars
   
   # Email Configuration (choose SendGrid or SMTP)
   # Option 1: SendGrid
   SENDGRID_API_KEY=your-sendgrid-api-key-here
   EMAIL_FROM=noreply@yourdomain.com
   EMAIL_FROM_NAME=SSH Manager
   
   # Option 2: SMTP (Direct settings)
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   SMTP_USE_TLS=True
   
   # Option 3: SMTP (Django-style settings - also supported)
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   DEFAULT_FROM_EMAIL=your-email@gmail.com
   ```

6. **Initialize the database** (done automatically on first run):
   ```bash
   python -c "from database import init_db; init_db()"
   ```

7. **Run the application**:
   ```bash
   python main.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

8. **Access the API**:
   - API: http://localhost:8000
   - Interactive API Docs (Swagger): http://localhost:8000/docs
   - Alternative API Docs (ReDoc): http://localhost:8000/redoc

## API Endpoints

### Authentication

- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user information

### Profile Management

- `POST /api/profile` - Create user profile (multipart/form-data for photo upload)
- `GET /api/profile` - Get current user profile
- `PUT /api/profile` - Update user profile (multipart/form-data for photo upload)
- `DELETE /api/profile` - Delete user profile

### Server Management

- `POST /api/servers` - Create a new server entry
- `GET /api/servers` - Get all servers for current user
- `GET /api/servers/{server_id}` - Get a specific server
- `PUT /api/servers/{server_id}` - Update a server
- `DELETE /api/servers/{server_id}` - Delete a server

### Command Execution

- `POST /api/commands/execute` - Execute a command on a remote server
- `GET /api/commands/logs` - Get command execution logs
- `GET /api/commands/logs/{log_id}` - Get a specific command log

## Usage Examples

### 1. Register a User

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepassword123"
  }'
```

### 2. Login

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john_doe&password=securepassword123"
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Create Profile

```bash
curl -X POST "http://localhost:8000/api/profile" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "first_name=John" \
  -F "last_name=Doe" \
  -F "age=30" \
  -F "phone_no=+1234567890" \
  -F "profile_photo=@/path/to/photo.jpg"
```

### 4. Add a Server

```bash
curl -X POST "http://localhost:8000/api/servers" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Production Server",
    "host": "192.168.1.100",
    "port": 22,
    "username": "ubuntu",
    "password": "server_password",
    "description": "Main production server"
  }'
```

### 5. Execute Command

```bash
curl -X POST "http://localhost:8000/api/commands/execute" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "server_id": 1,
    "command": "ls -la"
  }'
```

## Deployment

### Deploying to Render

1. **Create a Render account** at https://render.com

2. **Create a new Web Service**:
   - Connect your Git repository
   - Select "Python 3" as the environment
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Add Environment Variables**:
   - `DATABASE_URL`: PostgreSQL connection string (Render provides free PostgreSQL)
   - `SECRET_KEY`: Generate a secure random string
   - `SENDGRID_API_KEY`: Your SendGrid API key
   - `EMAIL_FROM`: Your sender email
   - Other variables as needed

4. **Deploy**: Render will automatically deploy your application

### Deploying to Vercel

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Deploy**:
   ```bash
   vercel
   ```

3. **Set Environment Variables** in Vercel dashboard

**Note**: This project is configured to use Supabase PostgreSQL, which works perfectly with Vercel. Supabase provides a free PostgreSQL database that's ideal for deployment.

### Deploying to Your Own Server

1. **SSH into your server**

2. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd technorizen
   ```

3. **Set up Python environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.example .env
   nano .env  # Edit with your settings
   ```

5. **Set up a process manager** (e.g., systemd, supervisor, or PM2):
   
   Example systemd service (`/etc/systemd/system/ssh-manager.service`):
   ```ini
   [Unit]
   Description=SSH Manager API
   After=network.target

   [Service]
   User=www-data
   WorkingDirectory=/path/to/technorizen
   Environment="PATH=/path/to/technorizen/venv/bin"
   ExecStart=/path/to/technorizen/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

6. **Start the service**:
   ```bash
   sudo systemctl start ssh-manager
   sudo systemctl enable ssh-manager
   ```

7. **Set up reverse proxy** (Nginx recommended):
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

## Security Considerations

1. **Secret Key**: Always use a strong, random secret key in production
2. **HTTPS**: Use HTTPS in production (Let's Encrypt for free SSL)
3. **Database**: Use PostgreSQL in production instead of SQLite
4. **Password**: Store strong passwords, consider implementing password complexity requirements
5. **SSH Keys**: Prefer SSH key-based authentication over passwords for servers
6. **Rate Limiting**: Consider adding rate limiting to prevent abuse
7. **Input Validation**: All inputs are validated, but always validate on client side too
8. **Command Filtering**: Dangerous commands are blocked, but review the blocklist for your use case

## Email Configuration

### Using SendGrid (Recommended)

1. Sign up at https://sendgrid.com
2. Create an API key in SendGrid dashboard
3. Add `SENDGRID_API_KEY` to your `.env` file
4. Set `EMAIL_FROM` to your verified sender email

### Using SMTP (Gmail Example)

1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Configure in `.env` using **either** format:

   **Option A: Direct SMTP settings**
   ```env
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   SMTP_USE_TLS=True
   EMAIL_FROM=your-email@gmail.com
   EMAIL_FROM_NAME=SSH Manager
   ```

   **Option B: Django-style settings (also supported)**
   ```env
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   DEFAULT_FROM_EMAIL=your-email@gmail.com
   EMAIL_FROM_NAME=SSH Manager
   ```

**Note**: The application automatically detects and uses Django-style email settings if present, making it compatible with existing Django projects.

## Database Migration

For production deployments, consider using Alembic for database migrations:

```bash
# Initialize Alembic (if not already done)
alembic init alembic

# Create a migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

## Testing

You can test the API using:
- **Swagger UI**: http://localhost:8000/docs (interactive testing)
- **curl**: Command-line HTTP client
- **Postman**: API testing tool
- **Python requests**: For automated testing

## Troubleshooting

### Common Issues

1. **Database locked (SQLite)**:
   - Ensure only one instance is running
   - Consider using PostgreSQL for production

2. **SSH connection failed**:
   - Verify server credentials
   - Check firewall rules
   - Ensure SSH service is running on the remote server

3. **Email not sending**:
   - Verify API key/SMTP credentials
   - Check email service logs
   - Ensure sender email is verified (SendGrid)

4. **Port already in use**:
   - Change port in uvicorn command: `--port 8001`
   - Or stop the process using the port

## License

This project is provided as-is for educational and production use.

## Support

For issues and questions, please refer to the API documentation at `/docs` endpoint or create an issue in the repository.

