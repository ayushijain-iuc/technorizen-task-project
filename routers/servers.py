from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import User, Server
from schemas import ServerCreate, ServerUpdate, ServerResponse
from auth import get_current_user

router = APIRouter(prefix="/api/servers", tags=["Servers"])


@router.post("", response_model=ServerResponse, status_code=status.HTTP_201_CREATED)
async def create_server(
    server_data: ServerCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new remote server entry"""
    # Normalize SSH key: ensure newlines are preserved
    ssh_key_normalized = None
    if server_data.ssh_key:
        # If key has escaped newlines, convert them to actual newlines
        ssh_key_normalized = server_data.ssh_key.replace('\\n', '\n')
    
    new_server = Server(
        user_id=current_user.id,
        name=server_data.name,
        host=server_data.host,
        port=server_data.port,
        username=server_data.username,
        password=server_data.password if server_data.password else None,
        ssh_key=ssh_key_normalized,
        description=server_data.description
    )
    db.add(new_server)
    db.commit()
    db.refresh(new_server)
    
    return new_server


@router.get("", response_model=List[ServerResponse])
async def get_servers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all servers for current user"""
    servers = db.query(Server).filter(Server.user_id == current_user.id).all()
    return servers


@router.get("/{server_id}", response_model=ServerResponse)
async def get_server(
    server_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific server by ID"""
    server = db.query(Server).filter(
        Server.id == server_id,
        Server.user_id == current_user.id
    ).first()
    
    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Server not found"
        )
    
    return server


@router.put("/{server_id}", response_model=ServerResponse)
async def update_server(
    server_id: int,
    server_data: ServerUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a server"""
    server = db.query(Server).filter(
        Server.id == server_id,
        Server.user_id == current_user.id
    ).first()
    
    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Server not found"
        )
    
    # Update fields
    update_data = server_data.model_dump(exclude_unset=True)
    
    # If password is being set (even if empty string), clear ssh_key (and vice versa) to ensure only one auth method
    if 'password' in update_data:
        # Password is being set, clear SSH key if not explicitly provided in this update
        if 'ssh_key' not in update_data:
            update_data['ssh_key'] = None
    elif 'ssh_key' in update_data:
        # SSH key is being set, clear password if not explicitly provided in this update
        if 'password' not in update_data:
            update_data['password'] = None
    
    for field, value in update_data.items():
        # Handle empty strings - convert to None for optional fields
        if field in ['password', 'ssh_key', 'description'] and value == "":
            value = None
        # Normalize SSH key: ensure newlines are preserved
        if field == 'ssh_key' and value:
            value = value.replace('\\n', '\n')
        setattr(server, field, value)
    
    db.commit()
    db.refresh(server)
    
    return server


@router.delete("/{server_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_server(
    server_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a server"""
    server = db.query(Server).filter(
        Server.id == server_id,
        Server.user_id == current_user.id
    ).first()
    
    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Server not found"
        )
    
    db.delete(server)
    db.commit()
    
    return None

