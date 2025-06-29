from dotenv import load_dotenv
from rich.console import Console
import asyncio
from rich.prompt import Prompt
from coordinator import HealthCoordinator
import os

load_dotenv()

console = Console()

async def main() -> None:
    console.print("[bold green]🏥 Welcome to the Health Analysis System![/bold green]")

    # Basic environment check
    if not os.getenv("DATABASE_URL") or not os.getenv("OPENAI_API_KEY"):
        console.print("[bold red]❌ Missing required environment variables (DATABASE_URL, OPENAI_API_KEY)[/bold red]")
        return

    # Get user input
    profile_id = Prompt.ask("Enter the user profile ID to analyze")
    if not profile_id.strip():
        console.print("[bold red]Please enter a valid profile ID.[/bold red]")
        return

    # Initialize and run health coordinator
    health_coordinator = HealthCoordinator(profile_id=profile_id)
    await health_coordinator.run_analysis()

if __name__ == "__main__":
    asyncio.run(main())