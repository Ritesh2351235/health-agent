from typing import Dict, Any, List
from pydantic import BaseModel
from agents import Agent

class RoutineTask(BaseModel):
    task: str
    reason: str

class RoutineTimeBlock(BaseModel):
    time_range: str
    why_it_matters: str
    tasks: List[RoutineTask]

class DailyRoutine(BaseModel):
    summary: str
    morning_wakeup: RoutineTimeBlock
    focus_block: RoutineTimeBlock
    afternoon_recharge: RoutineTimeBlock
    evening_winddown: RoutineTimeBlock

class RoutinePlanResult(BaseModel):
    """Structured routine plan for a single day"""
    date: str  # Format: "YYYY-MM-DD"
    routine: DailyRoutine

class RoutinePlanService:
    """Service for creating personalized routine plans using AI"""
    
    def __init__(self):
        self.agent = routine_plan_agent
    
    def format_context_for_routine_planning(self, analysis_result: str) -> str:
        """Format metric analysis for routine planning"""
        
        routine_prompt = f"""
## PERSONALIZED ROUTINE PLAN REQUEST

### COMPREHENSIVE HEALTH ANALYSIS
{analysis_result}

### ROUTINE PLAN REQUEST
Based on the comprehensive health analysis above, please create a detailed, personalized routine plan for TODAY that includes:

1. **Morning Wake-up**: Start of day routine with time and specific tasks
2. **Focus Block**: Dedicated productivity/work time with tasks
3. **Afternoon Recharge**: Energy boost activities 
4. **Evening Wind-down**: End of day relaxation routine

Please make the routine practical, sustainable, and directly address the health insights from the analysis.
Each time block should have 2-4 specific tasks with clear reasoning based on the health data.
"""
        
        return routine_prompt
    
    async def create_routine_plan(self, analysis_result: str) -> RoutinePlanResult:
        """Create personalized routine plan using the AI agent"""
        try:
            from agents import Runner
            
            # Format the context for routine planning
            routine_input = self.format_context_for_routine_planning(analysis_result)
            
            # Run the routine planning agent
            result = await Runner.run(
                self.agent,
                input=routine_input
            )
            
            return result.final_output
            
        except Exception as e:
            # Return error in structured format
            from datetime import datetime
            return RoutinePlanResult(
                date=datetime.now().strftime("%Y-%m-%d"),
                routine=DailyRoutine(
                    summary=f"Error creating routine plan: {str(e)}",
                    morning_wakeup=RoutineTimeBlock(
                        time_range="N/A",
                        why_it_matters="Error occurred",
                        tasks=[RoutineTask(task="Unable to generate", reason="System error")]
                    ),
                    focus_block=RoutineTimeBlock(
                        time_range="N/A", 
                        why_it_matters="Error occurred",
                        tasks=[RoutineTask(task="Unable to generate", reason="System error")]
                    ),
                    afternoon_recharge=RoutineTimeBlock(
                        time_range="N/A",
                        why_it_matters="Error occurred", 
                        tasks=[RoutineTask(task="Unable to generate", reason="System error")]
                    ),
                    evening_winddown=RoutineTimeBlock(
                        time_range="N/A",
                        why_it_matters="Error occurred",
                        tasks=[RoutineTask(task="Unable to generate", reason="System error")]
                    )
                )
            )

# Routine Plan Agent Definition
ROUTINE_PLAN_PROMPT = """You are a Personalized Routine Planning Agent, an expert in exercise science, lifestyle optimization, and wellness coaching. You specialize in creating comprehensive daily routines based on individual health data and analysis. You excel at:

**Core Expertise:**
- Exercise physiology and fitness programming
- Sleep optimization and circadian rhythm management
- Stress management and mental wellness strategies
- Habit formation and behavior change
- Recovery and regeneration protocols
- Activity progression and periodization
- Lifestyle medicine and wellness coaching

**Planning Framework:**
1. **Activity Assessment**: Determine optimal exercise types and intensities based on health metrics
2. **Schedule Architecture**: Design realistic daily routines with 4 time blocks
3. **Habit Integration**: Incorporate healthy daily practices that support identified health goals
4. **Sleep Optimization**: Create sleep schedules that enhance recovery and health metrics
5. **Stress Management**: Implement evidence-based stress reduction techniques
6. **Recovery Strategy**: Plan appropriate rest and recovery protocols
7. **Goal Setting**: Establish measurable activity and wellness targets
8. **Progression Planning**: Create adaptive routines that evolve with improving health

**Routine Principles:**
- Base all recommendations on the provided health analysis and user data
- Consider current fitness level, health constraints, and identified areas for improvement
- Balance different types of activities (cardio, strength, flexibility, recovery)
- Address specific health concerns identified in the analysis through targeted activities
- Make routines practical and sustainable for long-term adherence
- Consider time constraints and lifestyle factors
- Provide clear rationale for each recommendation based on health data
- Include both physical and mental wellness components

**Task Guidelines:**
- Each task should be specific and actionable (not vague)
- Provide scientific or health-based reasoning for each task
- Include timing, duration, or specific instructions where relevant
- Address the user's specific health metrics and concerns
- Balance structure with flexibility
- Consider energy patterns and circadian rhythms

**Important Guidelines:**
- Always reference specific health data points when making recommendations
- Explain WHY each activity is recommended based on the user's health profile
- Be specific with durations, intensities, and frequencies
- Consider the interconnection between different aspects of the routine
- Provide actionable, measurable recommendations
- Address any lifestyle factors that could improve the identified health concerns
- Generate routine for TODAY only (single day based on current date)
- Create exactly 4 time blocks: morning_wakeup, focus_block, afternoon_recharge, evening_winddown
- Each time block should have 2-4 tasks with specific reasoning

Remember: You are creating a personalized lifestyle intervention based on real health data. Generate a routine plan for ONLY ONE DAY with structured output containing exactly 4 time blocks.
"""

# Create the routine planning agent
routine_plan_agent = Agent(
    name="Personalized Routine Planning Agent",
    instructions=ROUTINE_PLAN_PROMPT,
    model="gpt-4o-mini",
    output_type=RoutinePlanResult
)

# Utility function for easy access
async def create_personalized_routine_plan(analysis_result: str) -> RoutinePlanResult:
    """
    Create a personalized routine plan based on health analysis and user data
    
    Args:
        analysis_result: String result from the metric analysis agent
        
    Returns:
        Structured RoutinePlanResult object
    """
    service = RoutinePlanService()
    return await service.create_routine_plan(analysis_result)
