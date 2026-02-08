"""
Network - TCP socket implementation for P2P communication
"""
import socket
import threading
import time
from queue import Queue, Empty
from protocol import (Protocol, HEADER_SIZE, MSG_VIDEO_FRAME, MSG_TEXT_MESSAGE, MSG_HEARTBEAT, MSG_USER_INFO,
                      MSG_BATTLESHIP_INVITE, MSG_BATTLESHIP_ACCEPT, MSG_BATTLESHIP_SHIP_PLACEMENT,
                      MSG_BATTLESHIP_MOVE, MSG_BATTLESHIP_RESULT, MSG_BATTLESHIP_QUIT, MSG_AI_COMMENT)


class NetworkConnection:
    """Manages TCP connection for bidirectional communication."""
    
    def __init__(self, sock=None):
        """
        Initialize network connection.
        
        Args:
            sock: Existing socket (for accepted connections)
        """
        self.sock = sock
        self.connected = False
        self.running = False
        
        # Receive queues for different message types
        self.video_queue = Queue(maxsize=5)  # Keep only recent frames
        self.text_queue = Queue()
        self.user_info_queue = Queue()
        self.battleship_queue = Queue()  # For all battleship messages
        self.ai_queue = Queue()  # For AI commentary
        
        # Threads
        self.receive_thread = None
        self.heartbeat_thread = None
        
        # Heartbeat
        self.last_heartbeat = time.time()
        self.heartbeat_interval = 5.0
        self.heartbeat_timeout = 15.0
    
    def connect(self, host, port, timeout=10):
        """
        Connect to a remote host.
        
        Args:
            host: Remote host address
            port: Remote port
            timeout: Connection timeout in seconds
            
        Returns:
            True if connected successfully
        """
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(timeout)
            self.sock.connect((host, port))
            self.sock.settimeout(None)  # Remove timeout after connection
            self.connected = True
            self._start_threads()
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def start_as_accepted(self):
        """Start connection for an accepted socket."""
        if self.sock:
            self.connected = True
            self._start_threads()
    
    def _start_threads(self):
        """Start receive and heartbeat threads."""
        self.running = True
        
        self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
        self.receive_thread.start()
        
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self.heartbeat_thread.start()
    
    def _receive_loop(self):
        """Background thread to receive messages."""
        buffer = b''
        
        while self.running and self.connected:
            try:
                # Receive data
                chunk = self.sock.recv(4096)
                if not chunk:
                    # Connection closed
                    self.connected = False
                    break
                
                buffer += chunk
                
                # Process complete messages in buffer
                while len(buffer) >= HEADER_SIZE:
                    # Parse header
                    msg_type, payload_length = Protocol.decode_header(buffer[:HEADER_SIZE])
                    
                    # Check if we have the full message
                    total_length = HEADER_SIZE + payload_length
                    if len(buffer) < total_length:
                        break  # Wait for more data
                    
                    # Extract payload
                    payload = buffer[HEADER_SIZE:total_length]
                    buffer = buffer[total_length:]  # Remove processed message
                    
                    # Handle message based on type
                    self._handle_message(msg_type, payload)
                    
            except Exception as e:
                if self.running:
                    print(f"Receive error: {e}")
                self.connected = False
                break
    
    def _handle_message(self, msg_type, payload):
        """Handle received message based on type."""
        try:
            if msg_type == MSG_VIDEO_FRAME:
                # Decompress and queue video frame
                ascii_frame = Protocol.decompress_ascii(payload)
                
                # Drop old frames if queue is full
                if self.video_queue.full():
                    try:
                        self.video_queue.get_nowait()
                    except Empty:
                        pass
                
                self.video_queue.put(ascii_frame)
                
            elif msg_type == MSG_TEXT_MESSAGE:
                # Queue text message
                text = payload.decode('utf-8')
                self.text_queue.put(text)
                
            elif msg_type == MSG_HEARTBEAT:
                # Update heartbeat timestamp
                self.last_heartbeat = time.time()
                
            elif msg_type == MSG_USER_INFO:
                # Queue user info
                self.user_info_queue.put(payload)
            
            elif msg_type in [MSG_BATTLESHIP_INVITE, MSG_BATTLESHIP_ACCEPT, MSG_BATTLESHIP_SHIP_PLACEMENT,
                             MSG_BATTLESHIP_MOVE, MSG_BATTLESHIP_RESULT, MSG_BATTLESHIP_QUIT]:
                # Queue battleship messages with type
                self.battleship_queue.put((msg_type, payload))
            
            elif msg_type == MSG_AI_COMMENT:
                # Queue AI commentary
                self.ai_queue.put(payload)
                
        except Exception as e:
            print(f"Error handling message type 0x{msg_type:02x}: {e}")
    
    def _heartbeat_loop(self):
        """Send periodic heartbeats and check for timeouts."""
        while self.running and self.connected:
            try:
                # Send heartbeat
                self.send_heartbeat()
                
                # Check for timeout
                if time.time() - self.last_heartbeat > self.heartbeat_timeout:
                    print("Connection timeout - no heartbeat received")
                    self.connected = False
                    break
                
                time.sleep(self.heartbeat_interval)
                
            except Exception as e:
                if self.running:
                    print(f"Heartbeat error: {e}")
                break
    
    def send(self, data):
        """Send raw data."""
        if not self.connected:
            return False
        
        try:
            self.sock.sendall(data)
            return True
        except Exception as e:
            print(f"Send error: {e}")
            self.connected = False
            return False
    
    def send_video_frame(self, ascii_frame):
        """Send a video frame."""
        msg = Protocol.create_video_message(ascii_frame)
        return self.send(msg)
    
    def send_text(self, text):
        """Send a text message."""
        msg = Protocol.create_text_message(text)
        return self.send(msg)
    
    def send_heartbeat(self):
        """Send a heartbeat message."""
        msg = Protocol.create_heartbeat()
        return self.send(msg)
    
    def get_user_info(self, timeout=0.1):
        """
        Get user info from the queue.
        
        Returns:
            Payload bytes or None
        """
        try:
            return self.user_info_queue.get(timeout=timeout)
        except Empty:
            return None
    
    def get_video_frame(self, timeout=0.1):
        """
        Get a video frame from the queue.
        
        Returns:
            ASCII frame string or None
        """
        try:
            return self.video_queue.get(timeout=timeout)
        except Empty:
            return None
    
    def get_text_message(self, timeout=0.1):
        """
        Get a text message from the queue.
        
        Returns:
            Text string or None
        """
        try:
            return self.text_queue.get(timeout=timeout)
        except Empty:
            return None
    
    def get_battleship_message(self, timeout=0.1):
        """
        Get a battleship game message from the queue.
        
        Returns:
            Tuple of (msg_type, payload) or None
        """
        try:
            return self.battleship_queue.get(timeout=timeout)
        except Empty:
            return None
    
    def get_ai_comment(self, timeout=0.1):
        """
        Get an AI comment from the queue.
        
        Returns:
            AI comment string or None
        """
        try:
            return self.ai_queue.get(timeout=timeout)
        except Empty:
            return None
    
    def close(self):
        """Close the connection."""
        self.running = False
        self.connected = False
        
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
    
    def is_connected(self):
        """Check if connection is active."""
        return self.connected


class NetworkServer:
    """TCP server for hosting connections."""
    
    def __init__(self, host='0.0.0.0', port=5000):
        """
        Initialize server.
        
        Args:
            host: Host address to bind to (0.0.0.0 for all interfaces)
            port: Port to listen on
        """
        self.host = host
        self.port = port
        self.server_sock = None
        self.connection = None
    
    def start(self):
        """Start listening for connections."""
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock.bind((self.host, self.port))
        self.server_sock.listen(1)
        return True
    
    def accept(self, timeout=None):
        """
        Accept an incoming connection.
        
        Args:
            timeout: Timeout in seconds (None for blocking)
            
        Returns:
            NetworkConnection or None
        """
        if timeout:
            self.server_sock.settimeout(timeout)
        
        try:
            client_sock, addr = self.server_sock.accept()
            print(f"Accepted connection from {addr}")
            
            connection = NetworkConnection(sock=client_sock)
            connection.start_as_accepted()
            self.connection = connection
            return connection
            
        except socket.timeout:
            return None
        except Exception as e:
            print(f"Accept error: {e}")
            return None
    
    def close(self):
        """Close the server."""
        if self.connection:
            self.connection.close()
        
        if self.server_sock:
            try:
                self.server_sock.close()
            except:
                pass


if __name__ == "__main__":
    # Test network communication on localhost
    print("Network Communication Test")
    print("Testing on localhost:5555")
    
    # Server thread
    def server_test():
        server = NetworkServer(host='127.0.0.1', port=5555)
        server.start()
        print("Server: Waiting for connection...")
        
        conn = server.accept(timeout=10)
        if conn:
            print("Server: Connected!")
            
            # Send test message
            conn.send_text("Hello from server!")
            
            # Receive message
            time.sleep(0.5)
            msg = conn.get_text_message()
            if msg:
                print(f"Server received: {msg}")
            
            time.sleep(2)
            conn.close()
        
        server.close()
    
    # Start server in thread
    server_thread = threading.Thread(target=server_test, daemon=True)
    server_thread.start()
    
    time.sleep(1)  # Let server start
    
    # Client
    print("Client: Connecting...")
    client = NetworkConnection()
    
    if client.connect('127.0.0.1', 5555):
        print("Client: Connected!")
        
        # Receive message
        time.sleep(0.5)
        msg = client.get_text_message()
        if msg:
            print(f"Client received: {msg}")
        
        # Send response
        client.send_text("Hello from client!")
        
        time.sleep(2)
        client.close()
    
    server_thread.join(timeout=5)
    print("\n✅ Network test complete!")
