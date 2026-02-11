# AI Trash-Talker Setup Guide

## What is it?
The AI Commentator is an optional feature that adds hilarious trash-talk commentary to your Battleship games using AI!

## Do I need it?
**No!** The game works perfectly without it. The AI is just for extra fun.

## How does it work?

### Shared AI Commentary (Network Synced!)
- If **either** player has Ollama installed, **both players see the same AI commentary** 🎉
- The HOST generates the AI comments and sends them to both players
- Only one player needs Ollama for both to enjoy the trash talk!
- If both players have Ollama, the host's AI is used

### What you'll see:

**HOST has Ollama, CLIENT doesn't:**
```
[HOST sees:]
System: 🤖 You are the AI Commentator! Both players will see your AI's trash talk
System: A5 - HIT! ✕
🤖 AI: Wow, lucky shot! Even a broken clock is right twice a day 😏

[CLIENT sees:]
System: 💤 Waiting for opponent's AI commentary...
System: A5 - HIT! ✕
🤖 AI: Wow, lucky shot! Even a broken clock is right twice a day 😏
```

**Neither player has Ollama:**
```
System: A5 - HIT! ✕
(No AI commentary - just normal game messages)
```

**Both have Ollama:**
```
[HOST generates, both see:]
System: 🤖 You are the AI Commentator! Both players will see your AI's trash talk
System: A5 - HIT! ✕
🤖 AI: Wow, lucky shot! Even a broken clock is right twice a day 😏
```

## Installation (Optional)

### Step 1: Install Ollama
1. Visit https://ollama.com
2. Download for your OS (Windows/Mac/Linux)
3. Install and run it

### Step 2: Download a Model
Open terminal/command prompt and run:
```bash
ollama pull llama3.2:1b
```

This downloads a small, fast AI model (~1GB). Other options:
- `llama3.2:3b` - Bigger, smarter, slower
- `llama3:8b` - Even better, needs more RAM

### Step 3: Start Playing!
Just start the game - the AI will automatically detect Ollama and start trash-talking!

## Using the AI

### Commands:
- `/ai <message>` - Talk back to the AI commentator
  - Example: `/ai that was a terrible shot!`
  - Example: `/ai you think you're so funny`

### When does AI comment?
The AI automatically comments on:
- **Game start** - Opening trash talk
- **Hits** - Celebrates or roasts
- **Misses** - Makes fun of your aim
- **Sunk ships** - Dramatic reactions
- **Victory/Defeat** - Final commentary

### Example Session:
```
You: /battleship
System: 🤖 AI Commentator is active! (Type /ai to trash-talk back)
🤖 AI: Oh boy, another Battleship game! Let's see if you can hit water... oh wait 😂

[Game starts...]

System: B5 - MISS! ○
🤖 AI: B5? More like B-Nope! 🌊

You: /ai watch me hit the next one
🤖 AI: Sure, sure... I'll be here with the popcorn 🍿

System: B6 - HIT! ✕
🤖 AI: Okay okay, I'll give you that one! But let's see if you can do it twice in a row 😏
```

## Troubleshooting

### "AI Commentator offline"
This means Ollama isn't running or installed.
- Check if Ollama is running (it should be in your system tray/menu bar)
- Try running `ollama list` in terminal to see if it's installed
- Install from https://ollama.com if needed

### AI responses are slow
- First response is always slower (model loads)
- Subsequent responses are faster
- Try a smaller model: `ollama pull llama3.2:1b`

### AI responses are weird/repetitive
- The AI has a sarcastic personality by design!
- It keeps things short and playful
- Each response is unique based on game context

### I want to disable AI commentary
The AI can be disabled, but that feature isn't implemented yet. For now, just don't install Ollama and you'll get simple fallbacks.

## Privacy Note
- **All AI processing happens on YOUR computer**
- No data is sent to the cloud
- No internet connection required (after downloading the model)
- The other player cannot see your AI commentary
- Your AI commentary is NOT sent over the network

## Requirements
- **RAM:** 2GB minimum for llama3.2:1b, 8GB for larger models
- **Storage:** ~1GB for model files
- **CPU:** Any modern processor (GPU not required but helps)
- **OS:** Windows, Mac, or Linux

---

**Remember: This is completely optional! The game works great without it.**
