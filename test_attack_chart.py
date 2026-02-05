"""
Test attack history chart display
"""
from battleship import BattleshipGame, BattleshipAI, Orientation
from blessed import Terminal

def test_attack_chart():
    """Test the attack history chart display."""
    print("Testing Attack History Chart...")
    print("=" * 60)
    
    # Create game and AI
    game = BattleshipGame(mode="vs_ai")
    ai = BattleshipAI(game)
    ai.place_ships()
    
    # Place player ships
    game.place_ship("Carrier", 5, (0, 0), Orientation.HORIZONTAL, is_player=True)
    game.place_ship("Battleship", 4, (2, 0), Orientation.HORIZONTAL, is_player=True)
    game.place_ship("Cruiser", 3, (4, 0), Orientation.HORIZONTAL, is_player=True)
    game.place_ship("Submarine", 3, (6, 0), Orientation.VERTICAL, is_player=True)
    game.place_ship("Destroyer", 2, (9, 0), Orientation.HORIZONTAL, is_player=True)
    
    game.game_phase = "playing"
    
    # Make some attacks
    attacks = [
        ((0, 0), "Testing A1"),
        ((1, 1), "Testing B2"),
        ((2, 2), "Testing C3"),
        ((5, 5), "Testing F6"),
        ((7, 3), "Testing H4"),
    ]
    
    term = Terminal()
    
    for pos, desc in attacks:
        result, ship = game.attack(pos, is_player_attacking=True)
        coord = game.pos_to_coord(pos)
        
        if result == "hit":
            print(f"\n{desc} ({coord}): HIT! ✕")
        else:
            print(f"\n{desc} ({coord}): MISS ○")
        
        # Display attack chart
        print("\n┌─── Your Attack History ───┐")
        
        # Build the board with colors
        lines = []
        # Header
        header = "    " + " ".join(f"{i:2}" for i in range(1, game.grid_size + 1))
        lines.append(header)
        
        # Rows (show first 6 rows only for brevity)
        for row in range(6):
            row_char = chr(ord('A') + row)
            row_str = f" {row_char}  "
            
            for col in range(game.grid_size):
                cell_pos = (row, col)
                
                if cell_pos in game.player_attacks:
                    # Check if it was a hit
                    is_hit = False
                    for ship in game.opponent_ships:
                        if cell_pos in ship.positions:
                            is_hit = True
                            break
                    
                    if is_hit:
                        row_str += f" {term.red('X')} "
                    else:
                        row_str += f" {term.white('O')} "
                else:
                    row_str += f" {term.cyan('~')} "
            
            lines.append(row_str)
        
        for line in lines:
            print(f"│ {line}")
        
        print(f"│ Legend: {term.red('X')}=Hit {term.white('O')}=Miss {term.cyan('~')}=Unknown")
        print("└──────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("✓ Attack chart display working!")

if __name__ == "__main__":
    test_attack_chart()
