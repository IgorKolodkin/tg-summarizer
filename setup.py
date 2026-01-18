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
        "[bold cyan]Telegram API Setup[/bold cyan]\n\n"
        "You need API credentials from Telegram.\n"
        "This is a one-time setup.",
        border_style="cyan"
    ))
    console.print()

    # Open browser for API registration
    if Confirm.ask("Open [link=https://my.telegram.org/apps]my.telegram.org/apps[/link] in browser?", default=True):
        webbrowser.open("https://my.telegram.org/apps")
        console.print()
        console.print("[dim]1. Log in with your phone number[/dim]")
        console.print("[dim]2. Go to 'API development tools'[/dim]")
        console.print("[dim]3. Create an app (any name/short name)[/dim]")
        console.print("[dim]4. Copy api_id and api_hash below[/dim]")
        console.print()

    # Collect credentials
    api_id = Prompt.ask("[bold]api_id[/bold]").strip()
    api_hash = Prompt.ask("[bold]api_hash[/bold]").strip()

    # Validate
    if not api_id.isdigit():
        console.print("[red]Error: api_id must be a number[/red]")
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
    console.print(f"[green]Saved credentials to {ENV_FILE}[/green]")

    return api_id, api_hash


def get_password():
    """Prompt for 2FA password with hidden input."""
    import getpass
    console.print()
    console.print("[yellow]Two-factor authentication enabled.[/yellow]")
    return getpass.getpass("Enter 2FA password (hidden): ")


def telegram_login(api_id: str, api_hash: str):
    """Perform first Telegram login to create session."""
    console.print()
    console.print(Panel.fit(
        "[bold cyan]Telegram Login[/bold cyan]\n\n"
        "[green]This is safe and legal:[/green]\n"
        "  - We use official Telegram API (MTProto)\n"
        "  - Your credentials stay on YOUR device only\n"
        "  - Session file is stored locally, not sent anywhere\n"
        "  - You can revoke access anytime in Telegram settings\n\n"
        "[bold]What will happen:[/bold]\n"
        "  1. Enter your phone number\n"
        "  2. Telegram sends you a code (in the app)\n"
        "  3. Enter the code here\n"
        "  4. If you have 2FA - enter password (hidden)\n\n"
        "[dim]Press Ctrl+C anytime to cancel[/dim]",
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
        # Create client with custom password handler for hidden input
        with Client(
            name=str(session_path),
            api_id=int(api_id),
            api_hash=api_hash,
            workdir=str(Path(__file__).parent),
            password=get_password  # Callable for hidden password input
        ) as app:
            me = app.get_me()
            console.print()
            console.print(f"[green]Logged in as: {me.first_name} (@{me.username or 'no username'})[/green]")
            console.print(f"[dim]Session saved to {session_path}.session[/dim]")
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled by user.[/yellow]")
        sys.exit(0)


def main():
    console.print()
    console.print("[bold]TG Summarizer Setup[/bold]")
    console.print("=" * 40)

    # Check if already configured
    if ENV_FILE.exists():
        from dotenv import load_dotenv
        load_dotenv(ENV_FILE)

        api_id = os.getenv("API_ID")
        api_hash = os.getenv("API_HASH")

        if api_id and api_hash and api_id != "your_api_id_here":
            console.print(f"[dim]Found existing config in {ENV_FILE}[/dim]")

            session_file = Path(__file__).parent / f"{SESSION_NAME}.session"
            if session_file.exists():
                console.print(f"[dim]Found existing session: {session_file}[/dim]")
                if not Confirm.ask("Reconfigure?", default=False):
                    console.print("[green]Setup complete! Run: python summarize.py --help[/green]")
                    return

    # Run setup
    api_id, api_hash = setup_credentials()
    telegram_login(api_id, api_hash)

    console.print()
    console.print(Panel.fit(
        "[bold green]Setup Complete![/bold green]\n\n"
        "Try it now:\n"
        "  [cyan]python summarize.py --last 10[/cyan]\n"
        "  [cyan]python summarize.py --unread[/cyan]",
        border_style="green"
    ))


if __name__ == "__main__":
    main()
