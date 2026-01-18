#!/usr/bin/env python3
"""
Interactive setup wizard for Telegram API credentials.
Opens browser for API registration, collects credentials, and performs first login.
"""

import os
import sys
import webbrowser
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

console = Console()

ENV_FILE = Path(__file__).parent / ".env"
SESSION_NAME = "tg_agent"


def setup_credentials():
    """Collect Telegram API credentials from user."""
    console.print()
    console.print(Panel.fit(
        "[bold cyan]Telegram API Credentials[/bold cyan]\n\n"
        "To read your messages, we need API access.\n"
        "You'll create an 'app' on Telegram's site\n"
        "and copy two values: api_id and api_hash.",
        border_style="cyan"
    ))
    console.print()

    # Open browser for API registration
    if Confirm.ask("Open [link=https://my.telegram.org/apps]my.telegram.org/apps[/link] in browser?", default=True):
        webbrowser.open("https://my.telegram.org/apps")
        console.print()
        console.print("[dim]1. Log in with your phone number[/dim]")
        console.print("[dim]2. Go to 'API development tools'[/dim]")
        console.print("[dim]3. Create an app (any name works)[/dim]")
        console.print("[dim]4. Copy api_id and api_hash below[/dim]")
        console.print()

    # Collect credentials
    api_id = Prompt.ask("[bold]api_id[/bold]").strip()
    api_hash = Prompt.ask("[bold]api_hash[/bold]").strip()

    # Validate
    if not api_id.isdigit():
        console.print("[red]Error: api_id should be a number[/red]")
        sys.exit(1)

    if len(api_hash) != 32:
        console.print("[yellow]Warning: api_hash is usually 32 characters[/yellow]")
        if not Confirm.ask("Continue anyway?", default=False):
            sys.exit(1)

    # Save to .env
    env_content = f"""# Telegram API credentials
API_ID={api_id}
API_HASH={api_hash}

# LLM model (qwen2.5:7b, llama3.2, mistral)
OLLAMA_MODEL=qwen2.5:7b
"""
    ENV_FILE.write_text(env_content)
    console.print(f"[green]Saved to {ENV_FILE}[/green]")

    return api_id, api_hash


def telegram_login(api_id: str, api_hash: str):
    """Perform first Telegram login to create session."""
    console.print()
    console.print(Panel.fit(
        "[bold cyan]Telegram Login[/bold cyan]\n\n"
        "Now we'll authenticate with Telegram.\n"
        "This uses the official MTProto API — same as\n"
        "the desktop app. Your session stays local.\n\n"
        "[green]All messages are processed locally.[/green]\n"
        "[green]Nothing is sent to external servers.[/green]\n\n"
        "[bold]What happens next:[/bold]\n"
        "  1. Enter your phone number\n"
        "  2. Telegram sends a code to your app\n"
        "  3. Enter the code here\n"
        "  4. If 2FA enabled — enter password (hidden)\n\n"
        "[dim]Press Ctrl+C to cancel[/dim]",
        border_style="cyan"
    ))
    console.print()

    # Import pyrogram here to avoid import errors if not installed
    try:
        from pyrogram import Client
    except ImportError:
        console.print("[red]Error: pyrogram not installed. Run: pip install pyrogram tgcrypto[/red]")
        sys.exit(1)

    session_path = Path(__file__).parent / SESSION_NAME

    try:
        # Create client (Pyrogram uses getpass internally for 2FA)
        with Client(
            name=str(session_path),
            api_id=int(api_id),
            api_hash=api_hash,
            workdir=str(Path(__file__).parent)
        ) as app:
            me = app.get_me()
            console.print()
            console.print(f"[green]Logged in as {me.first_name} (@{me.username or 'no username'})[/green]")
            console.print(f"[dim]Session saved to {session_path}.session[/dim]")
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled.[/yellow]")
        sys.exit(0)


def get_existing_credentials():
    """Check if valid credentials exist in .env file."""
    if not ENV_FILE.exists():
        return None, None

    from dotenv import load_dotenv
    load_dotenv(ENV_FILE)

    api_id = os.getenv("API_ID")
    api_hash = os.getenv("API_HASH")

    if api_id and api_hash and api_id != "your_api_id_here":
        return api_id, api_hash

    return None, None


def main():
    console.print()
    console.print("[bold]TG Summarizer Setup[/bold]")
    console.print("=" * 40)

    session_file = Path(__file__).parent / f"{SESSION_NAME}.session"
    api_id, api_hash = get_existing_credentials()

    # Case 1: Fully configured (credentials + session)
    if api_id and api_hash and session_file.exists():
        console.print(f"[dim]Found credentials: {ENV_FILE}[/dim]")
        console.print(f"[dim]Found session: {session_file}[/dim]")
        if not Confirm.ask("Reconfigure?", default=False):
            console.print("[green]Ready! Run: ./summarize --unread[/green]")
            return
        # User wants to reconfigure — get new credentials
        api_id, api_hash = setup_credentials()

    # Case 2: Have credentials but no session — just need to login
    elif api_id and api_hash:
        console.print(f"[dim]Found credentials: {ENV_FILE}[/dim]")
        console.print("[dim]Session not found, need to login.[/dim]")

    # Case 3: No credentials — full setup
    else:
        api_id, api_hash = setup_credentials()

    # Login to Telegram
    telegram_login(api_id, api_hash)

    console.print()
    console.print(Panel.fit(
        "[bold green]Setup Complete![/bold green]\n\n"
        "Try it now:\n"
        "  [cyan]./summarize --unread[/cyan]\n"
        "  [cyan]./summarize --last 20[/cyan]",
        border_style="green"
    ))


if __name__ == "__main__":
    main()
