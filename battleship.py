"""
Battleship Game - Classic naval combat game
"""
import random
import time
from enum import Enum
from typing import List, Tuple, Optional, Set


class CellState(Enum):
    """State of a grid cell."""
    EMPTY = "~"
    SHIP = "S"
    HIT = "X"
    MISS = "O"
    SUNK = "#"


class Orientation(Enum):
    """Ship orientation."""
    HORIZONTAL = "H"
    VERTICAL = "V"


class Ship:
    """Represents a ship on the grid."""
    
    def __init__(self, name: str, size: int, start_pos: Tuple[int, int], orientation: Orientation):
        """
        Initialize a ship.
        
        Args:
            name: Ship name (e.g., "Carrier")
            size: Ship length in cells
            start_pos: Starting position (row, col)
            orientation: HORIZONTAL or VERTICAL
        """
        self.name = name
        self.size = size
        self.start_pos = start_pos
        self.orientation = orientation
        self.hit_positions: Set[Tuple[int, int]] = set()
        
    @property
    def positions(self) -> List[Tuple[int, int]]:
        """Get all positions occupied by this ship."""
        positions = []
        row, col = self.start_pos
        for i in range(self.size):
            if self.orientation == Orientation.HORIZONTAL:
                positions.append((row, col + i))
            else:
                positions.append((row + i, col))
        return positions
    
    @property
    def is_sunk(self) -> bool:
        """Check if ship is completely sunk."""
        return len(self.hit_positions) == self.size
    
    def hit(self, position: Tuple[int, int]) -> bool:
        """
        Hit the ship at a position.
        
        Args:
            position: Position to hit
            
        Returns:
            True if this was a valid hit, False otherwise
        """
        if position in self.positions:
            self.hit_positions.add(position)
            return True
        return False


class BattleshipGame:
    """Main Battleship game logic."""
    
    # Ship definitions
    SHIP_TYPES = [
        ("Carrier", 5),
        ("Battleship", 4),
        ("Cruiser", 3),
        ("Submarine", 3),
        ("Destroyer", 2)
    ]
    
    GRID_SIZE = 10
    
    def __init__(self, mode: str = "vs_human"):
        """
        Initialize game.
        
        Args:
            mode: "vs_human" or "vs_ai"
        """
        self.mode = mode
        self.grid_size = self.GRID_SIZE
        
        # Player grids
        self.player_ships: List[Ship] = []
        self.opponent_ships: List[Ship] = []
        
        # Attack tracking
        self.player_attacks: Set[Tuple[int, int]] = set()
        self.opponent_attacks: Set[Tuple[int, int]] = set()
        
        # Game state
        self.game_phase = "setup"  # "setup", "playing", "finished"
        self.player_turn = True
        self.winner = None
        
    @staticmethod
    def coord_to_pos(coord: str) -> Optional[Tuple[int, int]]:
        """
        Convert coordinate string to position.
        
        Args:
            coord: Coordinate string (e.g., "A5", "J10")
            
        Returns:
            (row, col) tuple or None if invalid
        """
        coord = coord.strip().upper()
        if len(coord) < 2:
            return None
        
        row_char = coord[0]
        col_str = coord[1:]
        
        if row_char < 'A' or row_char > 'J':
            return None
        
        try:
            col = int(col_str)
            if col < 1 or col > 10:
                return None
        except ValueError:
            return None
        
        row = ord(row_char) - ord('A')
        col = col - 1
        
        return (row, col)
    
    @staticmethod
    def pos_to_coord(pos: Tuple[int, int]) -> str:
        """
        Convert position to coordinate string.
        
        Args:
            pos: (row, col) tuple
            
        Returns:
            Coordinate string (e.g., "A5")
        """
        row, col = pos
        row_char = chr(ord('A') + row)
        col_num = col + 1
        return f"{row_char}{col_num}"
    
    def is_valid_placement(self, ship_size: int, start_pos: Tuple[int, int], 
                          orientation: Orientation, ships: List[Ship]) -> bool:
        """
        Check if ship placement is valid.
        
        Args:
            ship_size: Size of ship to place
            start_pos: Starting position
            orientation: Ship orientation
            ships: Existing ships to check against
            
        Returns:
            True if placement is valid
        """
        row, col = start_pos
        
        # Check bounds
        if orientation == Orientation.HORIZONTAL:
            if col + ship_size > self.grid_size:
                return False
        else:
            if row + ship_size > self.grid_size:
                return False
        
        # Get positions this ship would occupy
        positions = []
        for i in range(ship_size):
            if orientation == Orientation.HORIZONTAL:
                positions.append((row, col + i))
            else:
                positions.append((row + i, col))
        
        # Check for overlaps with existing ships
        for ship in ships:
            ship_positions = ship.positions
            for pos in positions:
                if pos in ship_positions:
                    return False
        
        return True
    
    def place_ship(self, name: str, size: int, start_pos: Tuple[int, int], 
                   orientation: Orientation, is_player: bool = True) -> bool:
        """
        Place a ship on the grid.
        
        Args:
            name: Ship name
            size: Ship size
            start_pos: Starting position
            orientation: Ship orientation
            is_player: True for player ship, False for opponent
            
        Returns:
            True if placement successful
        """
        ships = self.player_ships if is_player else self.opponent_ships
        
        if not self.is_valid_placement(size, start_pos, orientation, ships):
            return False
        
        ship = Ship(name, size, start_pos, orientation)
        ships.append(ship)
        return True
    
    def attack(self, position: Tuple[int, int], is_player_attacking: bool = True) -> Tuple[str, Optional[str]]:
        """
        Attack a position.
        
        Args:
            position: Position to attack
            is_player_attacking: True if player is attacking, False if opponent
            
        Returns:
            Tuple of (result, ship_name)
            result: "hit", "miss", "sunk", "already_attacked", "invalid"
            ship_name: Name of ship if sunk, None otherwise
        """
        row, col = position
        
        # Validate position
        if row < 0 or row >= self.grid_size or col < 0 or col >= self.grid_size:
            return ("invalid", None)
        
        # Check which side is being attacked
        if is_player_attacking:
            attacks = self.player_attacks
            ships = self.opponent_ships
        else:
            attacks = self.opponent_attacks
            ships = self.player_ships
        
        # Check if already attacked
        if position in attacks:
            return ("already_attacked", None)
        
        # Record attack
        attacks.add(position)
        
        # Check for hit
        for ship in ships:
            if position in ship.positions:
                ship.hit(position)
                if ship.is_sunk:
                    return ("sunk", ship.name)
                return ("hit", None)
        
        return ("miss", None)
    
    def get_cell_state(self, position: Tuple[int, int], is_player_grid: bool, 
                       show_ships: bool = True) -> CellState:
        """
        Get the state of a cell for display.
        
        Args:
            position: Cell position
            is_player_grid: True for player's grid, False for opponent's
            show_ships: Whether to show ship positions (False for opponent's grid)
            
        Returns:
            CellState enum value
        """
        if is_player_grid:
            ships = self.player_ships
            attacks = self.opponent_attacks
        else:
            ships = self.opponent_ships
            attacks = self.player_attacks
        
        # Check if position was attacked
        if position in attacks:
            # Check if it's a hit
            for ship in ships:
                if position in ship.positions:
                    if ship.is_sunk:
                        return CellState.SUNK
                    return CellState.HIT
            return CellState.MISS
        
        # Show ships if allowed (player's own grid)
        if show_ships:
            for ship in ships:
                if position in ship.positions:
                    return CellState.SHIP
        
        return CellState.EMPTY
    
    def check_winner(self) -> Optional[str]:
        """
        Check if there's a winner.
        
        Returns:
            "player", "opponent", or None
        """
        # Check if all opponent ships are sunk
        if all(ship.is_sunk for ship in self.opponent_ships):
            return "player"
        
        # Check if all player ships are sunk
        if all(ship.is_sunk for ship in self.player_ships):
            return "opponent"
        
        return None
    
    def get_remaining_ships(self, is_player: bool = True) -> int:
        """
        Get number of remaining (not sunk) ships.
        
        Args:
            is_player: True for player, False for opponent
            
        Returns:
            Number of ships still afloat
        """
        ships = self.player_ships if is_player else self.opponent_ships
        return sum(1 for ship in ships if not ship.is_sunk)
    
    def get_board_display(self, is_player_grid: bool, show_ships: bool = True, use_color: bool = True) -> str:
        """
        Get ASCII representation of a board.
        
        Args:
            is_player_grid: True for player's grid, False for attacks
            show_ships: Whether to show ship positions
            use_color: Whether to use ANSI color codes
            
        Returns:
            ASCII board string
        """
        lines = []
        
        # ANSI color codes
        BLUE = '\033[94m'    # Ships
        RED = '\033[91m'     # Hits
        YELLOW = '\033[93m'  # Misses
        GRAY = '\033[90m'    # Sunk ships
        CYAN = '\033[96m'    # Water
        RESET = '\033[0m'
        BOLD = '\033[1m'
        
        # Header
        header = "    " + " ".join(f"{i:2}" for i in range(1, self.grid_size + 1))
        lines.append(header)
        
        # Rows
        for row in range(self.grid_size):
            row_char = chr(ord('A') + row)
            row_str = f" {row_char}  "
            
            for col in range(self.grid_size):
                state = self.get_cell_state((row, col), is_player_grid, show_ships)
                
                if use_color:
                    # Apply colors based on state
                    if state == CellState.SHIP:
                        row_str += f" {BLUE}{BOLD}{state.value}{RESET} "
                    elif state == CellState.HIT:
                        row_str += f" {RED}{BOLD}{state.value}{RESET} "
                    elif state == CellState.MISS:
                        row_str += f" {YELLOW}{state.value}{RESET} "
                    elif state == CellState.SUNK:
                        row_str += f" {GRAY}{state.value}{RESET} "
                    else:  # EMPTY
                        row_str += f" {CYAN}{state.value}{RESET} "
                else:
                    row_str += f" {state.value} "
            
            lines.append(row_str)
        
        return "\n".join(lines)


class BattleshipAI:
    """AI opponent for Battleship."""
    
    def __init__(self, game: BattleshipGame):
        """
        Initialize AI.
        
        Args:
            game: BattleshipGame instance
        """
        self.game = game
        self.last_hit: Optional[Tuple[int, int]] = None
        self.hunt_targets: List[Tuple[int, int]] = []
        self.hit_sequence: List[Tuple[int, int]] = []
        
    def place_ships(self) -> None:
        """Place AI ships randomly."""
        for name, size in BattleshipGame.SHIP_TYPES:
            placed = False
            attempts = 0
            max_attempts = 100
            
            while not placed and attempts < max_attempts:
                # Random position and orientation
                row = random.randint(0, self.game.grid_size - 1)
                col = random.randint(0, self.game.grid_size - 1)
                orientation = random.choice([Orientation.HORIZONTAL, Orientation.VERTICAL])
                
                placed = self.game.place_ship(name, size, (row, col), orientation, is_player=False)
                attempts += 1
    
    def get_adjacent_cells(self, position: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Get valid adjacent cells (N, S, E, W)."""
        row, col = position
        adjacent = [
            (row - 1, col),  # North
            (row + 1, col),  # South
            (row, col - 1),  # West
            (row, col + 1),  # East
        ]
        
        # Filter to valid positions that haven't been attacked
        valid = []
        for pos in adjacent:
            r, c = pos
            if (0 <= r < self.game.grid_size and 
                0 <= c < self.game.grid_size and
                pos not in self.game.opponent_attacks):
                valid.append(pos)
        
        return valid
    
    def choose_attack(self) -> Tuple[int, int]:
        """
        Choose next attack position using AI strategy.
        
        Returns:
            Position to attack
        """
        # Target mode: Continue in direction of consecutive hits
        if len(self.hit_sequence) >= 2:
            # Determine direction
            if self.hit_sequence[-1][0] == self.hit_sequence[-2][0]:
                # Horizontal
                direction = (0, self.hit_sequence[-1][1] - self.hit_sequence[-2][1])
            else:
                # Vertical
                direction = (self.hit_sequence[-1][0] - self.hit_sequence[-2][0], 0)
            
            # Try continuing in that direction
            next_pos = (self.hit_sequence[-1][0] + direction[0], 
                       self.hit_sequence[-1][1] + direction[1])
            
            r, c = next_pos
            if (0 <= r < self.game.grid_size and 
                0 <= c < self.game.grid_size and
                next_pos not in self.game.opponent_attacks):
                return next_pos
            
            # If can't continue, try opposite direction from first hit
            opposite = (-direction[0], -direction[1])
            next_pos = (self.hit_sequence[0][0] + opposite[0],
                       self.hit_sequence[0][1] + opposite[1])
            
            r, c = next_pos
            if (0 <= r < self.game.grid_size and 
                0 <= c < self.game.grid_size and
                next_pos not in self.game.opponent_attacks):
                return next_pos
        
        # Hunt mode: Check cells adjacent to last hit
        if self.hunt_targets:
            return self.hunt_targets.pop(0)
        
        # Search mode: Random attack
        available = []
        for row in range(self.game.grid_size):
            for col in range(self.game.grid_size):
                pos = (row, col)
                if pos not in self.game.opponent_attacks:
                    available.append(pos)
        
        return random.choice(available) if available else (0, 0)
    
    def process_result(self, position: Tuple[int, int], result: str, ship_name: Optional[str]) -> None:
        """
        Process attack result and update AI state.
        
        Args:
            position: Position that was attacked
            result: Attack result ("hit", "miss", "sunk")
            ship_name: Name of ship if sunk
        """
        if result == "hit":
            self.last_hit = position
            self.hit_sequence.append(position)
            
            # Add adjacent cells to hunt targets
            adjacent = self.get_adjacent_cells(position)
            for adj in adjacent:
                if adj not in self.hunt_targets:
                    self.hunt_targets.append(adj)
        
        elif result == "sunk":
            # Ship sunk - reset hunt mode
            self.last_hit = None
            self.hunt_targets.clear()
            self.hit_sequence.clear()
        
        elif result == "miss":
            # If we were in target mode and missed, switch back to hunt mode
            if len(self.hit_sequence) >= 2:
                # Try other direction or adjacent cells
                pass
