"""
Protocol - Message framing and serialization
"""
import struct
import zlib


# Message types
MSG_VIDEO_FRAME = 0x01
MSG_TEXT_MESSAGE = 0x02
MSG_HEARTBEAT = 0x03
MSG_USER_INFO = 0x04
MSG_BATTLESHIP_INVITE = 0x05
MSG_BATTLESHIP_ACCEPT = 0x06
MSG_BATTLESHIP_SHIP_PLACEMENT = 0x07
MSG_BATTLESHIP_MOVE = 0x08
MSG_BATTLESHIP_RESULT = 0x09
MSG_BATTLESHIP_QUIT = 0x0A

# Protocol constants
HEADER_SIZE = 5  # 1 byte type + 4 bytes length


class Protocol:
    """Handles message framing and serialization."""
    
    @staticmethod
    def encode_message(msg_type, payload):
        """
        Encode a message with type and length header.
        
        Args:
            msg_type: Message type byte (MSG_VIDEO_FRAME, MSG_TEXT_MESSAGE, etc.)
            payload: Bytes payload
            
        Returns:
            Bytes: Encoded message with header
        """
        if isinstance(payload, str):
            payload = payload.encode('utf-8')
        
        payload_length = len(payload)
        
        # Pack: 1 byte type + 4 bytes length (big-endian) + payload
        header = struct.pack('!BI', msg_type, payload_length)
        return header + payload
    
    @staticmethod
    def decode_header(header_bytes):
        """
        Decode message header.
        
        Args:
            header_bytes: 5 bytes containing type and length
            
        Returns:
            Tuple of (msg_type, payload_length)
        """
        if len(header_bytes) < HEADER_SIZE:
            raise ValueError(f"Header too short: {len(header_bytes)} bytes")
        
        msg_type, payload_length = struct.unpack('!BI', header_bytes)
        return msg_type, payload_length
    
    @staticmethod
    def compress_ascii(ascii_string):
        """
        Compress ASCII art string.
        
        Args:
            ascii_string: ASCII art string
            
        Returns:
            Compressed bytes
        """
        return zlib.compress(ascii_string.encode('utf-8'), level=6)
    
    @staticmethod
    def decompress_ascii(compressed_bytes):
        """
        Decompress ASCII art string.
        
        Args:
            compressed_bytes: Compressed data
            
        Returns:
            Decompressed ASCII string
        """
        return zlib.decompress(compressed_bytes).decode('utf-8')
    
    @staticmethod
    def create_video_message(ascii_frame):
        """Create a video frame message."""
        compressed = Protocol.compress_ascii(ascii_frame)
        return Protocol.encode_message(MSG_VIDEO_FRAME, compressed)
    
    @staticmethod
    def create_text_message(text):
        """Create a text message."""
        return Protocol.encode_message(MSG_TEXT_MESSAGE, text.encode('utf-8'))
    
    @staticmethod
    def create_heartbeat():
        """Create a heartbeat message."""
        return Protocol.encode_message(MSG_HEARTBEAT, b'')
    
    @staticmethod
    def create_user_info(name, chat_color, theme_color):
        """Create a user info message with name and colors."""
        import json
        data = {
            'name': name,
            'chat_color': chat_color,
            'theme_color': theme_color
        }
        return Protocol.encode_message(MSG_USER_INFO, json.dumps(data).encode('utf-8'))
    
    @staticmethod
    def parse_user_info(payload):
        """Parse user info from payload."""
        import json
        data = json.loads(payload.decode('utf-8'))
        return data['name'], data['chat_color'], data['theme_color']
    
    # Battleship game messages
    
    @staticmethod
    def create_battleship_invite():
        """Create a battleship game invitation."""
        return Protocol.encode_message(MSG_BATTLESHIP_INVITE, b'')
    
    @staticmethod
    def create_battleship_accept(accepted: bool):
        """Create battleship invitation response."""
        import json
        data = {'accepted': accepted}
        return Protocol.encode_message(MSG_BATTLESHIP_ACCEPT, json.dumps(data).encode('utf-8'))
    
    @staticmethod
    def parse_battleship_accept(payload):
        """Parse battleship acceptance response."""
        import json
        data = json.loads(payload.decode('utf-8'))
        return data['accepted']
    
    @staticmethod
    def create_battleship_ship_placement(ships_data):
        """
        Create ship placement message.
        
        Args:
            ships_data: List of dicts with ship info
        """
        import json
        return Protocol.encode_message(MSG_BATTLESHIP_SHIP_PLACEMENT, json.dumps(ships_data).encode('utf-8'))
    
    @staticmethod
    def parse_battleship_ship_placement(payload):
        """Parse ship placement data."""
        import json
        return json.loads(payload.decode('utf-8'))
    
    @staticmethod
    def create_battleship_move(coordinate: str):
        """Create battleship move (attack) message."""
        return Protocol.encode_message(MSG_BATTLESHIP_MOVE, coordinate.encode('utf-8'))
    
    @staticmethod
    def parse_battleship_move(payload):
        """Parse battleship move."""
        return payload.decode('utf-8')
    
    @staticmethod
    def create_battleship_result(result: str, ship_name: str = None):
        """
        Create battleship attack result message.
        
        Args:
            result: "hit", "miss", "sunk"
            ship_name: Name of ship if sunk
        """
        import json
        data = {'result': result, 'ship_name': ship_name}
        return Protocol.encode_message(MSG_BATTLESHIP_RESULT, json.dumps(data).encode('utf-8'))
    
    @staticmethod
    def parse_battleship_result(payload):
        """Parse battleship result."""
        import json
        data = json.loads(payload.decode('utf-8'))
        return data['result'], data.get('ship_name')
    
    @staticmethod
    def create_battleship_quit():
        """Create battleship quit message."""
        return Protocol.encode_message(MSG_BATTLESHIP_QUIT, b'')


if __name__ == "__main__":
    # Test protocol encoding/decoding
    print("Testing Protocol...")
    
    # Test text message
    text = "Hello, ASCII world!"
    msg = Protocol.create_text_message(text)
    print(f"\nText message: {len(msg)} bytes")
    
    msg_type, length = Protocol.decode_header(msg[:HEADER_SIZE])
    print(f"Type: 0x{msg_type:02x}, Length: {length}")
    payload = msg[HEADER_SIZE:]
    decoded_text = payload.decode('utf-8')
    print(f"Decoded: {decoded_text}")
    assert decoded_text == text, "Text mismatch!"
    
    # Test video frame compression
    ascii_frame = "@@@@@#####*****+++++:::::     \n" * 20
    compressed = Protocol.compress_ascii(ascii_frame)
    decompressed = Protocol.decompress_ascii(compressed)
    
    print(f"\nASCII frame: {len(ascii_frame)} bytes")
    print(f"Compressed: {len(compressed)} bytes")
    print(f"Ratio: {len(compressed)/len(ascii_frame)*100:.1f}%")
    assert decompressed == ascii_frame, "Decompression mismatch!"
    
    # Test video message
    video_msg = Protocol.create_video_message(ascii_frame)
    print(f"Video message total: {len(video_msg)} bytes")
    
    print("\n✅ All protocol tests passed!")
