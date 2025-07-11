#!/usr/bin/env python3
"""
Health Analysis Agent API Entry Point
Accepts command line arguments for user_id and archetype
"""

import sys
import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from coordinator import HealthCoordinator

# Load environment variables from .env file
# Check multiple locations for .env file
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
env_locations = [
    current_dir / ".env",
    parent_dir / ".env",
    Path.cwd() / ".env"
]

env_loaded = False
for env_path in env_locations:
    if env_path.exists():
        load_dotenv(env_path)
        env_loaded = True
        print(f"[DEBUG] Loaded .env from: {env_path}")
        break

if not env_loaded:
    print("[DEBUG] No .env file found. Please create one using env.example as template.")
    load_dotenv()  # Load from system environment

def main():
    if len(sys.argv) != 3:
        print("Usage: python main_api.py <user_id> <archetype>")
        print("Archetypes: Foundation Builder, Transformation Seeker, Systematic Improver, Peak Performer, Resilience Rebuilder, Connected Explorer")
        sys.exit(1)
    
    user_id = sys.argv[1]
    archetype = sys.argv[2]
    
    # Validate archetype
    valid_archetypes = [
        "Foundation Builder",
        "Transformation Seeker", 
        "Systematic Improver",
        "Peak Performer",
        "Resilience Rebuilder",
        "Connected Explorer"
    ]
    
    if archetype not in valid_archetypes:
        print(f"❌ Invalid archetype: {archetype}")
        print(f"Valid archetypes: {', '.join(valid_archetypes)}")
        sys.exit(1)
    
    print("🏥 Welcome to the Health Analysis System!")
    print(f"Enter the user profile ID to analyze: {user_id}")
    print("\n" + "="*80)
    print("🎯 SELECT YOUR ROUTINE PLAN ARCHETYPE")
    print("="*80)
    print("Choose the approach that best matches your personality and wellness goals:")
    print()
    
    # Display archetype options
    archetype_descriptions = {
        "Foundation Builder": "🏗️ Simple, sustainable basics for beginners or those rebuilding health habits",
        "Transformation Seeker": "🚀 Ambitious individuals ready for major lifestyle changes and dramatic improvement",
        "Systematic Improver": "🔬 Detail-oriented, methodical approach with evidence-based, incremental progress",
        "Peak Performer": "🏆 High-achieving individuals seeking elite-level performance optimization",
        "Resilience Rebuilder": "🌱 Gentle restoration and recovery-focused approach for burnout or stress recovery",
        "Connected Explorer": "🌍 Social connection and adventure-oriented wellness with community focus"
    }
    
    for i, (arch, desc) in enumerate(archetype_descriptions.items(), 1):
        print(f"{i}. {arch}")
        print(f"   {desc}")
        print()
    
    print(f"✅ Selected: {archetype}")
    print("="*80)
    print()
    
    # Run the analysis
    asyncio.run(run_analysis_wrapper(user_id, archetype))

async def run_analysis_wrapper(user_id: str, archetype: str):
    """Async wrapper for running the health analysis"""
    try:
        # Get database URL from environment or use default
        database_url = os.getenv("DATABASE_URL")
        openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Debug: Print environment variables (without exposing sensitive data)
        print(f"[DEBUG] DATABASE_URL loaded: {'Yes' if database_url else 'No'}")
        print(f"[DEBUG] OPENAI_API_KEY loaded: {'Yes' if openai_api_key else 'No'}")
        
        # Provide helpful error messages
        if not database_url:
            print("❌ DATABASE_URL not found in environment variables.")
            print("Please create a .env file with your database configuration.")
            print("See env.example file for template.")
            sys.exit(1)
        
        if not openai_api_key:
            print("❌ OPENAI_API_KEY not found in environment variables.")
            print("Please add your OpenAI API key to the .env file.")
            print("See env.example file for template.")
            sys.exit(1)
        
        # Initialize the coordinator
        coordinator = HealthCoordinator(user_id, database_url)
        
        # Run the analysis
        await coordinator.run_analysis(archetype)
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 