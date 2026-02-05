"""
AI Assistant for Battleship Trash Talk
Uses Ollama for local, free AI responses
"""
import requests
import json
import random


class BattleshipAI_Assistant:
    """AI assistant that provides trash talk during Battleship games."""
    
    def __init__(self, ollama_url="http://localhost:11434"):
        """
        Initialize AI assistant.
        
        Args:
            ollama_url: URL where Ollama is running (default: localhost:11434)
        """
        self.ollama_url = ollama_url
        self.model = "llama3.2:latest"  # Fast, lightweight model
        self.conversation_history = []
        self.personality = """You are a hilarious, sarcastic commentator watching a Battleship game.
You love to trash-talk both players equally, make fun of their misses, celebrate their hits,
and provide running commentary. Keep responses SHORT (1-2 sentences max). Be funny, cheeky, 
and entertaining. Use emojis occasionally. Don't be mean - keep it playful."""
    
    def is_available(self):
        """Check if Ollama is running and available."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def generate_response(self, prompt, context=None):
        """
        Generate AI response to a prompt.
        
        Args:
            prompt: User's message or game event
            context: Optional game context
            
        Returns:
            AI response string or None if failed
        """
        if not self.is_available():
            return self._get_fallback_response(prompt)
        
        try:
            # Build the full prompt with personality and context
            full_prompt = f"{self.personality}\n\n"
            if context:
                full_prompt += f"Game Context: {context}\n\n"
            full_prompt += f"Respond to: {prompt}"
            
            # Call Ollama API
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.9,  # Higher = more creative
                        "num_predict": 50,   # Keep responses short
                    }
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                return self._get_fallback_response(prompt)
                
        except Exception as e:
            print(f"AI Assistant error: {e}")
            return self._get_fallback_response(prompt)
    
    def _get_fallback_response(self, prompt):
        """Get a fallback response when AI is unavailable."""
        fallbacks = [
            "🤖 AI offline, but I'm still watching you... 👀",
            "My circuits are tingling with anticipation!",
            "Calculating optimal trash talk... ERROR 404",
            "beep boop I am a robot 🤖",
            "AI.exe has stopped working (but the game continues!)"
        ]
        return random.choice(fallbacks)
    
    def comment_on_hit(self, player_name, coordinate, is_player_local=True):
        """Generate trash talk for a hit."""
        if is_player_local:
            prompts = [
                f"{player_name} hit at {coordinate}! React with excitement and trash talk the defender",
                f"A HIT at {coordinate}! Give {player_name} props but stay sarcastic",
                f"{player_name} lands a hit at {coordinate}! Make a funny comment"
            ]
        else:
            prompts = [
                f"Opponent hit {player_name} at {coordinate}! Mock their defense",
                f"{player_name} got hit at {coordinate}! Roast their ship placement",
                f"OUCH! {player_name} takes a hit at {coordinate}! React dramatically"
            ]
        return self.generate_response(random.choice(prompts))
    
    def comment_on_miss(self, player_name, coordinate, is_player_local=True):
        """Generate trash talk for a miss."""
        prompts = [
            f"{player_name} missed at {coordinate}! Make fun of their aim",
            f"Another miss at {coordinate}! Roast {player_name}'s targeting skills",
            f"{player_name} hit water at {coordinate}! React with sarcasm",
            f"MISS at {coordinate}! Give {player_name} some playful grief"
        ]
        return self.generate_response(random.choice(prompts))
    
    def comment_on_sunk(self, player_name, ship_name, is_player_local=True):
        """Generate trash talk for sinking a ship."""
        if is_player_local:
            prompts = [
                f"{player_name} sunk a {ship_name}! Celebrate dramatically!",
                f"The {ship_name} is down! {player_name} is on fire! React with hype",
                f"{player_name} just destroyed a {ship_name}! Give them credit but stay cheeky"
            ]
        else:
            prompts = [
                f"{player_name}'s {ship_name} just sank! Mock their loss",
                f"Down goes {player_name}'s {ship_name}! React to their pain",
                f"{player_name} lost their {ship_name}! Make a Titanic joke"
            ]
        return self.generate_response(random.choice(prompts))
    
    def comment_on_victory(self, winner_name, loser_name):
        """Generate trash talk for game end."""
        prompt = f"{winner_name} defeated {loser_name}! Give a victory speech with playful trash talk for both"
        return self.generate_response(prompt)
    
    def comment_on_game_start(self, player1, player2=None):
        """Generate opening trash talk."""
        if player2:
            prompt = f"Game starting between {player1} and {player2}! Set the tone with hype and playful jabs"
        else:
            prompt = f"{player1} is playing against AI! Make a funny comment about this matchup"
        return self.generate_response(prompt)
    
    def respond_to_chat(self, player_name, message):
        """Respond to player's /ai command."""
        context = f"{player_name} said to you during a Battleship game"
        return self.generate_response(message, context=context)
    
    def set_model(self, model_name):
        """Change the Ollama model being used."""
        self.model = model_name
    
    def get_available_models(self):
        """Get list of available Ollama models."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=2)
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
        except:
            pass
        return []
