import asyncio
import json
import os
from coordinator import HealthCoordinator

async def test_json_format():
    """Test the new JSON format output from nutrition and routine agents"""
    
    print("🧪 Testing JSON Format Output")
    print("="*60)
    
    # Check environment variables
    if not os.getenv("DATABASE_URL"):
        print("❌ Missing DATABASE_URL environment variable")
        return
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Missing OPENAI_API_KEY environment variable")
        return
    
    # Test profile ID
    profile_id = "test-profile-123"
    
    print(f"🔄 Testing JSON format for profile: {profile_id}")
    print(f"📊 This will test the structured JSON output from:")
    print(f"   1. Nutrition Planning Agent (JSON format)")
    print(f"   2. Routine Planning Agent (JSON format)")
    print()
    
    try:
        # Initialize health coordinator
        health_coordinator = HealthCoordinator(profile_id=profile_id)
        
        # Run the complete analysis workflow with JSON output
        await health_coordinator.run_analysis(days=7)
        
        print("\n🎉 JSON format test completed successfully!")
        print("📋 Expected JSON structure:")
        print("   - Daily routines with time blocks")
        print("   - Tasks with detailed reasoning")
        print("   - Nutrition plans with macro targets")
        print("   - Meal timing recommendations")
        
    except Exception as e:
        print(f"❌ Error during JSON format test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_json_format()) 