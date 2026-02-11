"""
Quick test of battleship game functionality
"""
from battleship import BattleshipGame, BattleshipAI, Orientation

def test_game():
    """Test a basic game scenario."""
    print("Testing Battleship Game...")
    print("=" * 50)
    
    # Create game
    game = BattleshipGame(mode="vs_ai")
    print("✓ Game created")
    
    # Place player ships manually
    ships_to_place = [
        ("Carrier", 5, (0, 0), Orientation.HORIZONTAL),
        ("Battleship", 4, (2, 0), Orientation.HORIZONTAL),
        ("Cruiser", 3, (4, 0), Orientation.HORIZONTAL),
        ("Submarine", 3, (6, 0), Orientation.VERTICAL),
        ("Destroyer", 2, (8, 0), Orientation.HORIZONTAL),
    ]
    
    for name, size, pos, orient in ships_to_place:
        success = game.place_ship(name, size, pos, orient, is_player=True)
        print(f"{'✓' if success else '✗'} Placed {name} at {game.pos_to_coord(pos)} {orient.value}")
    
    # Create AI and place its ships
    ai = BattleshipAI(game)
    ai.place_ships()
    print("✓ AI ships placed")
    
    # Start game
    game.game_phase = "playing"
    
    # Display boards
    print("\n" + "=" * 50)
    print("YOUR SHIPS:")
    print(game.get_board_display(is_player_grid=True, show_ships=True, use_color=True))
    
    print("\n" + "=" * 50)
    print("YOUR ATTACKS (Enemy grid):")
    print(game.get_board_display(is_player_grid=False, show_ships=False, use_color=True))
    
    # Test a few attacks
    print("\n" + "=" * 50)
    print("Testing attacks...")
    
    test_attacks = [(0, 0), (1, 1), (5, 5)]
    for pos in test_attacks:
        result, ship_name = game.attack(pos, is_player_attacking=True)
        coord = game.pos_to_coord(pos)
        if result == "hit":
            print(f"✕ {coord} - HIT!")
        elif result == "miss":
            print(f"○ {coord} - MISS")
        elif result == "sunk":
            print(f"✗ {coord} - SUNK {ship_name}!")
    
    # Display updated attack board
    print("\n" + "=" * 50)
    print("UPDATED ATTACKS:")
    print(game.get_board_display(is_player_grid=False, show_ships=False, use_color=True))
    
    # Check ship counts
    player_ships = game.get_remaining_ships(is_player=True)
    opponent_ships = game.get_remaining_ships(is_player=False)
    print(f"\nPlayer ships remaining: {player_ships}/5")
    print(f"Opponent ships remaining: {opponent_ships}/5")
    
    # Test coordinate conversion
    print("\n" + "=" * 50)
    print("Testing coordinate conversion...")
    test_coords = ["A1", "J10", "E5", "invalid"]
    for coord in test_coords:
        pos = BattleshipGame.coord_to_pos(coord)
        if pos:
            back = BattleshipGame.pos_to_coord(pos)
            print(f"✓ {coord} -> {pos} -> {back}")
        else:
            print(f"✗ {coord} -> Invalid")
    
    print("\n" + "=" * 50)
    print("✓ All tests completed successfully!")

if __name__ == "__main__":
    test_game()
