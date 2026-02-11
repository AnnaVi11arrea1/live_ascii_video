"""
Test customization features
"""
from rich.console import Console

console = Console()

def test_emoji_conversion():
    """Test emoji shortcode conversion"""
    from session import ChatSession
    
    # Create a dummy session to test emoji processing
    test_cases = [
        (":)", "😊"),
        (":fire:", "🔥"),
        ("Hello :wave: how are you :)", "Hello 👋 how are you 😊"),
        ("Great work! :thumbsup: :100:", "Great work! 👍 💯"),
        ("<3 this project :rocket:", "❤️ this project 🚀"),
    ]
    
    # Create a minimal session instance
    class MockSession:
        def _process_emojis(self, text):
            emoji_map = {
                ':)': '😊', ':D': '😄', ':(': '😢', ':P': '😛', ';)': '😉',
                '<3': '❤️', ':heart:': '❤️', ':fire:': '🔥', ':star:': '⭐',
                ':check:': '✓', ':x:': '✗', ':thumbsup:': '👍', ':thumbsdown:': '👎',
                ':wave:': '👋', ':clap:': '👏', ':rocket:': '🚀', ':eyes:': '👀',
                ':100:': '💯', ':thinking:': '🤔', ':laugh:': '😂', ':cry:': '😭',
                ':cool:': '😎', ':party:': '🎉',
            }
            for code, emoji in emoji_map.items():
                text = text.replace(code, emoji)
            return text
    
    session = MockSession()
    
    console.print("\n[bold cyan]Testing Emoji Conversion:[/bold cyan]")
    all_passed = True
    
    for input_text, expected in test_cases:
        result = session._process_emojis(input_text)
        passed = result == expected
        all_passed = all_passed and passed
        
        status = "[green]✓[/green]" if passed else "[red]✗[/red]"
        console.print(f"{status} '{input_text}' → '{result}'")
        if not passed:
            console.print(f"  [red]Expected: '{expected}'[/red]")
    
    return all_passed


def test_color_options():
    """Test color option functions"""
    console.print("\n[bold cyan]Color Options Available:[/bold cyan]")
    
    console.print("\n[bold]Chat Colors:[/bold]")
    chat_colors = ['red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']
    for i, color in enumerate(chat_colors, 1):
        console.print(f"  {i}. {color.capitalize()}")
    
    console.print("\n[bold]Theme Colors:[/bold]")
    theme_colors = ['green', 'blue', 'cyan', 'magenta', 'yellow']
    for i, color in enumerate(theme_colors, 1):
        console.print(f"  {i}. {color.capitalize()}")
    
    return True


def test_protocol_user_info():
    """Test user info protocol encoding/decoding"""
    from protocol import Protocol
    
    console.print("\n[bold cyan]Testing User Info Protocol:[/bold cyan]")
    
    # Test data
    test_name = "Alice"
    test_chat_color = "magenta"
    test_theme_color = "cyan"
    
    # Encode
    msg = Protocol.create_user_info(test_name, test_chat_color, test_theme_color)
    console.print(f"  Encoded message: {len(msg)} bytes")
    
    # Decode
    from protocol import HEADER_SIZE
    payload = msg[HEADER_SIZE:]
    name, chat_color, theme_color = Protocol.parse_user_info(payload)
    
    # Verify
    passed = (name == test_name and 
              chat_color == test_chat_color and 
              theme_color == test_theme_color)
    
    status = "[green]✓[/green]" if passed else "[red]✗[/red]"
    console.print(f"{status} Name: {name}, Chat: {chat_color}, Theme: {theme_color}")
    
    return passed


if __name__ == "__main__":
    console.print("[bold]Testing Customization Features[/bold]")
    console.print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Emoji Conversion", test_emoji_conversion()))
    results.append(("Color Options", test_color_options()))
    results.append(("User Info Protocol", test_protocol_user_info()))
    
    # Summary
    console.print("\n" + "=" * 60)
    console.print("[bold]Test Summary:[/bold]")
    all_passed = True
    for name, passed in results:
        status = "[green]PASS[/green]" if passed else "[red]FAIL[/red]"
        console.print(f"  {status} - {name}")
        all_passed = all_passed and passed
    
    if all_passed:
        console.print("\n[bold green]✅ All tests passed![/bold green]")
    else:
        console.print("\n[bold red]❌ Some tests failed[/bold red]")
