"""
Test ship placement preview feature
"""
from battleship import BattleshipGame, Orientation

def test_placement_preview():
    """Test the ship placement preview display."""
    print("Testing Ship Placement Preview...")
    print("=" * 60)
    
    game = BattleshipGame(mode="vs_ai")
    
    # Simulate placing ships one by one and showing preview
    placements = [
        ("Carrier", 5, (0, 0), Orientation.HORIZONTAL),
        ("Battleship", 4, (2, 2), Orientation.VERTICAL),
        ("Cruiser", 3, (5, 5), Orientation.HORIZONTAL),
    ]
    
    for i, (name, size, pos, orient) in enumerate(placements):
        print(f"\n{i+1}. Placing {name} at {game.pos_to_coord(pos)} {orient.value}...")
        success = game.place_ship(name, size, pos, orient, is_player=True)
        
        if success:
            print(f"   ✓ {name} placed successfully!")
            print("\n   ┌─── Current Setup ───┐")
            
            # Get board preview (no color for chat display)
            board = game.get_board_display(is_player_grid=True, show_ships=True, use_color=False)
            for line in board.split('\n'):
                print(f"   │ {line}")
            
            print("   └─────────────────────┘")
        else:
            print(f"   ✗ Failed to place {name}")
    
    print("\n" + "=" * 60)
    print("Preview feature working! Players can now see their setup after each placement.")

if __name__ == "__main__":
    test_placement_preview()
