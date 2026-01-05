import paramiko
from typing import Tuple, Optional
from io import StringIO, BytesIO
import logging
import base64
import re
from config import settings

logger = logging.getLogger(__name__)


class SSHService:
    """Service for executing commands on remote servers via SSH"""
    
    @staticmethod
    def is_command_dangerous(command: str) -> bool:
        """Check if command is potentially dangerous"""
        command_lower = command.lower().strip()
        
        # Check against blocked commands list
        for blocked in settings.BLOCKED_COMMANDS:
            if blocked.lower() in command_lower:
                return True
        
        # Additional dangerous patterns
        dangerous_patterns = [
            "rm -rf",
            "format",
            "mkfs",
            "dd if=",
            "> /dev/",
            "chmod 777",
            ":(){ :|:& };:",
        ]
        
        for pattern in dangerous_patterns:
            if pattern in command_lower:
                # Allow if it's in a safe context (like in quotes or comments)
                # Simple check: if pattern appears without being in quotes
                if pattern in command_lower:
                    # More sophisticated check could be added here
                    return True
        
        return False
    
    @staticmethod
    def execute_command(
        host: str,
        port: int,
        username: str,
        command: str,
        password: Optional[str] = None,
        ssh_key: Optional[str] = None
    ) -> Tuple[bool, Optional[str], Optional[str], Optional[int]]:
        """
        Execute command on remote server via SSH
        
        Returns:
            Tuple of (success, output, error, exit_status)
        """
        # Check if command is dangerous
        if SSHService.is_command_dangerous(command):
            error_msg = f"Command blocked: Potentially dangerous command detected"
            logger.warning(f"Blocked dangerous command: {command}")
            return False, None, error_msg, None
        
        ssh_client = None
        try:
            # Create SSH client
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Connect to server
            # Prefer password over SSH key if both are present (password is more reliable)
            # Also skip SSH key if it's clearly invalid (too short)
            use_ssh_key = False
            if ssh_key:
                ssh_key_content = ssh_key.strip()
                # Skip SSH key if it's too short (likely invalid/dummy key)
                # Real RSA keys are typically 1500+ characters when base64 encoded
                key_length = len(ssh_key_content.replace('\n', '').replace(' ', '').replace('\r', '').replace('\t', ''))
                if key_length < 500:
                    logger.warning(f"SSH key too short ({key_length} chars), skipping and using password authentication if available")
                    use_ssh_key = False
                    ssh_key = None  # Clear invalid key so password will be used
                else:
                    use_ssh_key = True
            
            # Prefer password over SSH key if both are available
            if password and ssh_key:
                logger.info("Both password and SSH key available, using password authentication")
                use_ssh_key = False
                ssh_key = None
            
            if use_ssh_key and ssh_key:
                # Key-based authentication
                private_key = None
                ssh_key_content = ssh_key.strip()
                
                # Convert \n escape sequences to actual newlines
                # This handles keys stored in JSON/database with escaped newlines
                # The key might be stored with literal backslash-n characters
                
                # Method 1: Replace literal backslash-n (two characters: backslash + n)
                # This handles keys stored as: "-----BEGIN...\\nMII..."
                ssh_key_content = ssh_key_content.replace('\\n', '\n')
                ssh_key_content = ssh_key_content.replace('\\r\\n', '\n')
                ssh_key_content = ssh_key_content.replace('\r\n', '\n')
                
                # Method 2: Use regex to replace any number of backslashes followed by n
                # This handles: \n, \\n, \\\n, etc.
                ssh_key_content = re.sub(r'\\+n', '\n', ssh_key_content)
                
                # Method 3: Multiple passes for nested escaping
                for _ in range(10):
                    old = ssh_key_content
                    ssh_key_content = ssh_key_content.replace('\\n', '\n')
                    if old == ssh_key_content:
                        break
                
                # Method 4: If still has issues, try decoding as if it's a Python string literal
                if '\\n' in ssh_key_content:
                    try:
                        # Try to decode as if it's a Python string with escape sequences
                        ssh_key_content = ssh_key_content.encode('latin1').decode('unicode_escape')
                    except Exception:
                        pass
                
                # Final aggressive cleanup: ensure ALL backslash-n are replaced
                while '\\n' in ssh_key_content:
                    ssh_key_content = ssh_key_content.replace('\\n', '\n')
                
                # Check if key is missing PEM headers (just base64 content)
                # If it doesn't start with -----BEGIN, it might be just the base64 part
                if not ssh_key_content.startswith('-----BEGIN'):
                    # Try to detect if it's base64 encoded key content
                    # Remove all whitespace and check if it looks like base64
                    key_clean = ssh_key_content.strip().replace('\n', '').replace(' ', '').replace('\r', '').replace('\t', '')
                    
                    # Check if it looks like base64 (alphanumeric + / + =)
                    # Base64 keys are typically much longer than 20 characters
                    is_base64_like = len(key_clean) >= 20 and all(c.isalnum() or c in '+/=' for c in key_clean)
                    
                    if is_base64_like:
                        # Looks like base64 content without headers - wrap it
                        logger.info(f"SSH key appears to be base64 content ({len(key_clean)} chars) without PEM headers. Wrapping in RSA PRIVATE KEY format...")
                        # Wrap in RSA PRIVATE KEY headers (most common)
                        # Split into 64-char lines (standard PEM format)
                        wrapped_key = "-----BEGIN RSA PRIVATE KEY-----\n"
                        for i in range(0, len(key_clean), 64):
                            wrapped_key += key_clean[i:i+64] + "\n"
                        wrapped_key += "-----END RSA PRIVATE KEY-----"
                        ssh_key_content = wrapped_key
                        logger.info("Successfully wrapped base64 content in PEM format")
                    else:
                        # Doesn't look like valid key content
                        error_detail = f"Invalid SSH key format. "
                        if len(key_clean) < 20:
                            error_detail += f"Key too short ({len(key_clean)} chars). "
                        else:
                            error_detail += f"Key doesn't look like valid base64. "
                        error_detail += f"Key must be in PEM format (start with -----BEGIN) or be valid base64 encoded key content. "
                        error_detail += f"Received: {ssh_key_content[:80]}..."
                        logger.error(error_detail)
                        raise ValueError(error_detail)
                
                # Log final state for debugging
                newline_count = ssh_key_content.count('\n')
                backslash_n_count = ssh_key_content.count('\\n')
                logger.info(f"SSH key normalization: {newline_count} newlines, {backslash_n_count} remaining \\n")
                
                if backslash_n_count > 0:
                    logger.warning(f"SSH key still has {backslash_n_count} literal \\n characters - key might be corrupted")
                
                # Try to decode base64 if it looks encoded
                try:
                    # Check if it's base64 encoded (common when storing keys)
                    if not ssh_key_content.startswith('-----BEGIN'):
                        # Try base64 decoding
                        try:
                            decoded_key = base64.b64decode(ssh_key_content, validate=True)
                            ssh_key_content = decoded_key.decode('utf-8', errors='ignore')
                            # Convert \n escape sequences again after decoding
                            ssh_key_content = ssh_key_content.replace('\\n', '\n')
                        except Exception:
                            # If base64 decode fails, might not be base64, continue with original
                            pass
                except Exception:
                    # If decoding fails, use original key
                    pass
                
                # Ensure key has proper newlines
                if '\\n' in ssh_key_content:
                    ssh_key_content = ssh_key_content.replace('\\n', '\n')
                
                # Try different key types in order of commonality
                key_io = StringIO(ssh_key_content)
                key_parsed = False
                last_error = None
                
                # Try RSA key first (most common)
                try:
                    key_io.seek(0)
                    private_key = paramiko.RSAKey.from_private_key(key_io)
                    key_parsed = True
                    logger.info("Successfully parsed RSA key")
                except Exception as e:
                    last_error = str(e)
                    error_msg = str(e).lower()
                    # Check if it's a format issue
                    if 'not a valid' in error_msg or 'invalid' in error_msg:
                        logger.warning(f"RSA key format issue: {e}")
                    else:
                        logger.debug(f"RSA key parse failed: {e}")
                
                # Try ED25519 key (modern, common)
                if not key_parsed:
                    try:
                        key_io.seek(0)
                        private_key = paramiko.Ed25519Key.from_private_key(key_io)
                        key_parsed = True
                        logger.info("Successfully parsed ED25519 key")
                    except Exception as e:
                        last_error = str(e)
                        logger.debug(f"ED25519 key parse failed: {e}")
                
                # Try ECDSA key
                if not key_parsed:
                    try:
                        key_io.seek(0)
                        private_key = paramiko.ECDSAKey.from_private_key(key_io)
                        key_parsed = True
                        logger.info("Successfully parsed ECDSA key")
                    except Exception as e:
                        last_error = str(e)
                        logger.debug(f"ECDSA key parse failed: {e}")
                
                # Try DSS key as last resort (rare)
                if not key_parsed:
                    try:
                        key_io.seek(0)
                        private_key = paramiko.DSSKey.from_private_key(key_io)
                        key_parsed = True
                        logger.info("Successfully parsed DSS key")
                    except Exception as e:
                        last_error = str(e)
                        # If DSS parsing says "encountered RSA key", it means RSA format was detected but parsing failed
                        if 'encountered RSA key' in str(e).lower() or 'expected DSA key' in str(e).lower():
                            last_error = f"RSA key format detected but key content is invalid or corrupted. Original error: {e}"
                        logger.debug(f"DSS key parse failed: {e}")
                
                if not key_parsed:
                    # Log the key content for debugging
                    key_preview = ssh_key_content[:100]
                    actual_newlines = ssh_key_content.count('\n')
                    literal_backslash_n = ssh_key_content.count('\\n')
                    
                    # Check key length - real RSA keys are typically 1500+ chars in base64
                    key_length = len(ssh_key_content.replace('\n', '').replace(' ', ''))
                    
                    # Create a readable preview
                    preview_display = key_preview.replace('\n', '[NL]').replace('\\n', '[BS-N]')
                    
                    # Determine the likely issue
                    if key_length < 500:
                        issue_detail = f"SSH key appears to be too short ({key_length} chars). Real RSA private keys are typically 1500+ characters when base64 encoded. "
                    elif 'not a valid' in last_error.lower() or 'invalid' in last_error.lower():
                        issue_detail = f"SSH key format is invalid. "
                    else:
                        issue_detail = f"SSH key parsing failed. "
                    
                    error_msg = (
                        f"Unable to parse SSH key. {issue_detail}"
                        f"Last error: {last_error}. "
                        f"Key stats: {actual_newlines} newlines, {literal_backslash_n} escaped \\n, {key_length} total chars. "
                        f"Preview: {preview_display[:60]}... "
                        f"Please ensure you're using a valid SSH private key in PEM format, or use password authentication instead."
                    )
                    logger.error(error_msg)
                    raise ValueError(error_msg)
                
                ssh_client.connect(
                    hostname=host,
                    port=port,
                    username=username,
                    pkey=private_key,
                    timeout=30
                )
            elif password:
                # Password-based authentication
                ssh_client.connect(
                    hostname=host,
                    port=port,
                    username=username,
                    password=password,
                    timeout=30
                )
            else:
                raise ValueError("Either password or ssh_key must be provided for authentication")
            
            # Execute command
            stdin, stdout, stderr = ssh_client.exec_command(command, timeout=60)
            
            # Read output
            output = stdout.read().decode('utf-8', errors='ignore')
            error = stderr.read().decode('utf-8', errors='ignore')
            exit_status = stdout.channel.recv_exit_status()
            
            success = exit_status == 0
            
            logger.info(f"Command executed on {host}: {command[:50]}... Exit status: {exit_status}")
            
            return success, output if output else None, error if error else None, exit_status
            
        except paramiko.AuthenticationException:
            error_msg = "SSH authentication failed: Invalid credentials"
            logger.error(f"SSH authentication failed for {username}@{host}:{port}")
            return False, None, error_msg, None
        except paramiko.SSHException as e:
            error_msg = f"SSH error: {str(e)}"
            logger.error(f"SSH error on {host}: {str(e)}")
            return False, None, error_msg, None
        except ValueError as e:
            error_msg = f"Configuration error: {str(e)}"
            logger.error(f"Configuration error for {host}: {str(e)}")
            return False, None, error_msg, None
        except Exception as e:
            error_msg = f"Error executing command: {str(e)}"
            logger.error(f"Error executing command on {host}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False, None, error_msg, None
        finally:
            if ssh_client:
                ssh_client.close()

