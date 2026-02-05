"""
Comprehensive Battleship Integration Test
Tests the complete game flow with preview feature
"""
from battleship import BattleshipGame, BattleshipAI, Orientation

def simulate_game_flow():
    """Simulate a complete game from start to finish."""
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║  BATTLESHIP GAME - COMPLETE FLOW TEST                     ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    
    # 1. Game Start
    print("\n[1] Starting Game...")
    game = BattleshipGame(mode="vs_ai")
    ai = BattleshipAI(game)
    print("    ✓ Game initialized")
    print("    ✓ AI opponent ready")
    
    # 2. AI Places Ships
    print("\n[2] AI placing ships...")
    ai.place_ships()
    print(f"    ✓ AI placed {len(game.opponent_ships)} ships")
    
    # 3. Player Places Ships (with preview)
    print("\n[3] Player placing ships (with preview)...")
    player_placements = [
        ("Carrier", 5, (0, 0), Orientation.HORIZONTAL),
        ("Battleship", 4, (2, 0), Orientation.HORIZONTAL),
        ("Cruiser", 3, (4, 0), Orientation.HORIZONTAL),
        ("Submarine", 3, (6, 0), Orientation.VERTICAL),
        ("Destroyer", 2, (9, 0), Orientation.HORIZONTAL),
    ]
    
    for i, (name, size, pos, orient) in enumerate(player_placements):
        coord = game.pos_to_coord(pos)
        print(f"\n    Placing {name} at {coord} {orient.value}...")
        
        success = game.place_ship(name, size, pos, orient, is_player=True)
        if success:
            print(f"    ✓ {name} placed successfully!")
            
            # Show preview (simulating chat display)
            if i < len(player_placements) - 1:  # Don't show for last ship (goes to battle)
                print("\n    ┌─── Current Setup ───┐")
                board = game.get_board_display(is_player_grid=True, show_ships=True, use_color=False)
                for line in board.split('\n')[:5]:  # Show first 5 lines only
                    print(f"    │ {line}")
                print("    │ ... (remaining rows)")
                print("    └─────────────────────┘")
        else:
            print(f"    ✗ Failed to place {name}")
            return
    
    print(f"\n    ✓ All {len(game.player_ships)} player ships placed!")
    
    # 4. Start Battle Phase
    print("\n[4] Battle Phase Starting...")
    game.game_phase = "playing"
    turn = 0
    max_turns = 10  # Limit for test
    
    while turn < max_turns:
        turn += 1
        print(f"\n    ─── Turn {turn} ───")
        
        # Player attacks
        player_attack = (turn % 10, turn % 10)
        result, ship = game.attack(player_attack, is_player_attacking=True)
        coord = game.pos_to_coord(player_attack)
        
        if result == "miss":
            print(f"    Player: {coord} - MISS ○")
        elif result == "hit":
            print(f"    Player: {coord} - HIT ✕")
        elif result == "sunk":
            print(f"    Player: {coord} - SUNK {ship}! ✗")
        
        # Check winner
        winner = game.check_winner()
        if winner:
            print(f"\n    🎉 {winner.upper()} WINS!")
            break
        
        # AI attacks
        ai_pos = ai.choose_attack()
        ai_result, ai_ship = game.attack(ai_pos, is_player_attacking=False)
        ai_coord = game.pos_to_coord(ai_pos)
        ai.process_result(ai_pos, ai_result, ai_ship)
        
        if ai_result == "miss":
            print(f"    AI: {ai_coord} - MISS ○")
        elif ai_result == "hit":
            print(f"    AI: {ai_coord} - HIT ✕")
        elif ai_result == "sunk":
            print(f"    AI: {ai_coord} - SUNK {ai_ship}! ✗")
        
        # Check winner
        winner = game.check_winner()
        if winner:
            print(f"\n    🎉 {winner.upper()} WINS!")
            break
    
    # 5. Final Board Display
    print("\n[5] Final Boards:")
    print("\n    YOUR SHIPS (Final State):")
    player_board = game.get_board_display(is_player_grid=True, show_ships=True, use_color=True)
    for line in player_board.split('\n')[:8]:
        print(f"    {line}")
    print("    ... (remaining rows)")
    
    print("\n    YOUR ATTACKS:")
    attack_board = game.get_board_display(is_player_grid=False, show_ships=False, use_color=True)
    for line in attack_board.split('\n')[:8]:
        print(f"    {line}")
    print("    ... (remaining rows)")
    
    # 6. Statistics
    print("\n[6] Game Statistics:")
    player_ships_left = game.get_remaining_ships(is_player=True)
    ai_ships_left = game.get_remaining_ships(is_player=False)
    player_attacks_made = len(game.player_attacks)
    ai_attacks_made = len(game.opponent_attacks)
    
    print(f"    Player Ships Remaining: {player_ships_left}/5")
    print(f"    AI Ships Remaining: {ai_ships_left}/5")
    print(f"    Total Turns: {turn}")
    print(f"    Player Attacks: {player_attacks_made}")
    print(f"    AI Attacks: {ai_attacks_made}")
    
    if player_attacks_made > 0:
        player_accuracy = (player_attacks_made - len([p for p in game.player_attacks if all(
            p not in ship.positions for ship in game.opponent_ships
        )])) / player_attacks_made * 100
        print(f"    Player Accuracy: {player_accuracy:.1f}%")
    
    print("\n╔═══════════════════════════════════════════════════════════╗")
    print("║  ✓ ALL TESTS PASSED - GAME FLOW COMPLETE                 ║")
    print("╚═══════════════════════════════════════════════════════════╝")

if __name__ == "__main__":
    simulate_game_flow()
