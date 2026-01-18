#!/usr/bin/env python3
"""
Tests for TG Summarizer.
Run: python tests.py
"""

import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add parent dir to path
sys.path.insert(0, str(Path(__file__).parent))

from rich.console import Console

console = Console()


def test_imports():
    """Test that all required packages are installed."""
    console.print("[bold]Test: imports[/bold]")

    try:
        import pyrogram
        console.print("  [green]✓[/green] pyrogram")
    except ImportError as e:
        console.print(f"  [red]✗[/red] pyrogram: {e}")
        return False

    try:
        import ollama
        console.print("  [green]✓[/green] ollama")
    except ImportError as e:
        console.print(f"  [red]✗[/red] ollama: {e}")
        return False

    try:
        import rich
        console.print("  [green]✓[/green] rich")
    except ImportError as e:
        console.print(f"  [red]✗[/red] rich: {e}")
        return False

    try:
        from dotenv import load_dotenv
        console.print("  [green]✓[/green] python-dotenv")
    except ImportError as e:
        console.print(f"  [red]✗[/red] python-dotenv: {e}")
        return False

    return True


def test_ollama_connection():
    """Test that Ollama is running and accessible."""
    console.print("[bold]Test: Ollama connection[/bold]")

    try:
        import ollama
        models = ollama.list()
        console.print("  [green]✓[/green] Ollama is running")
        return True
    except Exception as e:
        console.print(f"  [red]✗[/red] Cannot connect to Ollama: {e}")
        console.print("  [dim]Run: ollama serve[/dim]")
        return False


def test_model_available():
    """Test that the required model is downloaded."""
    console.print("[bold]Test: Model availability[/bold]")

    try:
        import ollama
        models = ollama.list()
        model_names = [m.model for m in models.models]

        # Check for qwen2.5:7b or similar
        required_model = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

        # Check exact match or base name match
        found = False
        for name in model_names:
            if required_model in name or name.startswith(required_model.split(":")[0]):
                console.print(f"  [green]✓[/green] Model found: {name}")
                found = True
                break

        if not found:
            console.print(f"  [red]✗[/red] Model '{required_model}' not found")
            console.print(f"  [dim]Available: {', '.join(model_names)}[/dim]")
            console.print(f"  [dim]Run: ollama pull {required_model}[/dim]")
            return False

        return True
    except Exception as e:
        console.print(f"  [red]✗[/red] Error: {e}")
        return False


def test_env_file():
    """Test that .env file exists and has required fields."""
    console.print("[bold]Test: .env configuration[/bold]")

    env_file = Path(__file__).parent / ".env"

    if not env_file.exists():
        console.print("  [yellow]![/yellow] .env file not found (run setup.py first)")
        return None  # Skip, not a failure

    from dotenv import load_dotenv
    load_dotenv(env_file)

    api_id = os.getenv("API_ID")
    api_hash = os.getenv("API_HASH")

    if not api_id or api_id == "your_api_id_here":
        console.print("  [red]✗[/red] API_ID not configured")
        return False
    console.print("  [green]✓[/green] API_ID configured")

    if not api_hash or api_hash == "your_api_hash_here":
        console.print("  [red]✗[/red] API_HASH not configured")
        return False
    console.print("  [green]✓[/green] API_HASH configured")

    return True


def test_session_file():
    """Test that Telegram session exists."""
    console.print("[bold]Test: Telegram session[/bold]")

    session_file = Path(__file__).parent / "tg_agent.session"

    if not session_file.exists():
        console.print("  [yellow]![/yellow] Session file not found (run setup.py first)")
        return None  # Skip, not a failure

    console.print("  [green]✓[/green] Session file exists")
    return True


def test_chunking():
    """Test message chunking logic."""
    console.print("[bold]Test: Message chunking[/bold]")

    from summarize import chunk_messages

    # Create test messages
    messages = [
        {"sender": "Alice", "text": "Hello " * 100},  # ~600 chars
        {"sender": "Bob", "text": "World " * 100},    # ~600 chars
        {"sender": "Charlie", "text": "Test " * 100}, # ~500 chars
    ]

    # Test with small max_chars to force chunking
    chunks = chunk_messages(messages, max_chars=700)

    if len(chunks) >= 2:
        console.print(f"  [green]✓[/green] Chunking works ({len(chunks)} chunks created)")
        return True
    else:
        console.print(f"  [red]✗[/red] Expected multiple chunks, got {len(chunks)}")
        return False


def test_format_messages():
    """Test message formatting for LLM."""
    console.print("[bold]Test: Message formatting[/bold]")

    from summarize import format_messages_for_llm

    messages = [
        {"sender": "Alice", "text": "Hello!"},
        {"sender": "", "text": "System message"},
    ]

    formatted = format_messages_for_llm(messages, "Test Chat")

    if "Chat: Test Chat" in formatted and "Alice: Hello!" in formatted:
        console.print("  [green]✓[/green] Formatting works correctly")
        return True
    else:
        console.print("  [red]✗[/red] Formatting issue")
        console.print(f"  [dim]{formatted}[/dim]")
        return False


def test_cli_help():
    """Test that CLI --help works."""
    console.print("[bold]Test: CLI --help[/bold]")

    import subprocess
    result = subprocess.run(
        [sys.executable, "summarize.py", "--help"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent
    )

    if result.returncode == 0 and "--unread" in result.stdout:
        console.print("  [green]✓[/green] CLI help works")
        return True
    else:
        console.print("  [red]✗[/red] CLI help failed")
        console.print(f"  [dim]{result.stderr}[/dim]")
        return False


def test_ollama_generate():
    """Test actual LLM generation (quick test)."""
    console.print("[bold]Test: LLM generation[/bold]")

    try:
        import ollama

        model = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
        response = ollama.generate(
            model=model,
            prompt="Say 'test ok' in 2 words:",
        )

        if response and response.get('response'):
            console.print(f"  [green]✓[/green] LLM responds: {response['response'][:50]}...")
            return True
        else:
            console.print("  [red]✗[/red] Empty response from LLM")
            return False
    except Exception as e:
        console.print(f"  [red]✗[/red] LLM error: {e}")
        return False


def main():
    console.print()
    console.print("[bold cyan]TG Summarizer Tests[/bold cyan]")
    console.print("=" * 40)
    console.print()

    results = {
        "passed": 0,
        "failed": 0,
        "skipped": 0
    }

    tests = [
        test_imports,
        test_ollama_connection,
        test_model_available,
        test_env_file,
        test_session_file,
        test_chunking,
        test_format_messages,
        test_cli_help,
        test_ollama_generate,
    ]

    for test in tests:
        try:
            result = test()
            if result is True:
                results["passed"] += 1
            elif result is False:
                results["failed"] += 1
            else:  # None = skipped
                results["skipped"] += 1
        except Exception as e:
            console.print(f"  [red]✗[/red] Exception: {e}")
            results["failed"] += 1
        console.print()

    # Summary
    console.print("=" * 40)
    console.print(f"[green]Passed: {results['passed']}[/green]  ", end="")
    console.print(f"[red]Failed: {results['failed']}[/red]  ", end="")
    console.print(f"[yellow]Skipped: {results['skipped']}[/yellow]")

    if results["failed"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
