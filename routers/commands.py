from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import re
from database import get_db
from models import User, Server, CommandLog
from schemas import CommandExecute, CommandResponse, CommandLogResponse
from auth import get_current_user
from ssh_service import SSHService
from email_service import EmailService

router = APIRouter(prefix="/api/commands", tags=["Commands"])
@router.post("/execute", response_model=CommandResponse)
async def execute_command(
    command_data: CommandExecute,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):


    server = db.query(Server).filter(
        Server.id == command_data.server_id,
        Server.user_id == current_user.id
    ).first()
    
    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Server not found"
        )
    

    if not server.password and not server.ssh_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Server must have either password or SSH key configured"
        )
    

    ssh_key_normalized = None
    if server.ssh_key:
        ssh_key_normalized = server.ssh_key.replace('\\n', '\n')
        ssh_key_normalized = re.sub(r'\\+n', '\n', ssh_key_normalized)
    

    success, output, error, exit_status = SSHService.execute_command(
        host=server.host,
        port=server.port,
        username=server.username,
        command=command_data.command,
        password=server.password,
        ssh_key=ssh_key_normalized
    )
    

    command_log = CommandLog(
        user_id=current_user.id,
        server_id=server.id,
        command=command_data.command,
        output=output,
        error=error,
        exit_status=exit_status
    )
    db.add(command_log)
    db.commit()
    db.refresh(command_log)
    

    try:
        EmailService.send_command_execution_email(
            to_email=current_user.email,
            server_name=server.name,
            command=command_data.command,
            success=success,
            output=output,
            error=error
        )
    except Exception as e:
        pass
    
    return CommandResponse(
        success=success,
        output=output,
        error=error,
        exit_status=exit_status,
        execution_time=datetime.utcnow()
    )


@router.get("/logs", response_model=List[CommandLogResponse])
async def get_command_logs(
    server_id: int = None,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    query = db.query(CommandLog).filter(CommandLog.user_id == current_user.id)
    
    if server_id:
        server = db.query(Server).filter(
            Server.id == server_id,
            Server.user_id == current_user.id
        ).first()
        if not server:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Server not found"
            )
        query = query.filter(CommandLog.server_id == server_id)
    logs = query.order_by(CommandLog.execution_time.desc()).limit(limit).all()
    return logs


@router.get("/logs/{log_id}", response_model=CommandLogResponse)
async def get_command_log(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    log = db.query(CommandLog).filter(
        CommandLog.id == log_id,
        CommandLog.user_id == current_user.id
    ).first()
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Command log not found"
        )
    
    return log

