from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from agents import Agent
from .behavior_analysis_agent import BehaviorAnalysisResult

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
    
    def format_context_for_routine_planning(self, analysis_result: str, behavior_analysis: Optional[BehaviorAnalysisResult] = None) -> str:
        """Format metric analysis and behavior analysis for routine planning"""
        
        routine_prompt = f"""
## PERSONALIZED ROUTINE PLAN REQUEST

### COMPREHENSIVE HEALTH ANALYSIS
{analysis_result}
"""
        
        # Add behavior analysis insights if available
        if behavior_analysis:
            routine_prompt += f"""
### COMPREHENSIVE BEHAVIOR ANALYSIS

#### Behavioral Profile
- **Signature**: {behavior_analysis.behavioral_signature.signature} (Confidence: {behavior_analysis.behavioral_signature.confidence:.1%})
- **Sophistication Level**: {behavior_analysis.sophistication_assessment.score}/100 ({behavior_analysis.sophistication_assessment.category})
- **Readiness Level**: {behavior_analysis.readiness_level}
- **Habit Formation Stage**: {behavior_analysis.habit_formation_stage}

#### Behavioral Insights
- **Justification**: {behavior_analysis.sophistication_assessment.justification}

#### Primary Goal
- **Goal**: {behavior_analysis.primary_goal.goal}
- **Timeline**: {behavior_analysis.primary_goal.timeline}
- **Success Metrics**: {', '.join(behavior_analysis.primary_goal.success_metrics)}

#### Adaptive Parameters
- **Complexity Level**: {behavior_analysis.adaptive_parameters.complexity_level}
- **Time Commitment**: {behavior_analysis.adaptive_parameters.time_commitment}
- **Technology Integration**: {behavior_analysis.adaptive_parameters.technology_integration}
- **Customization Level**: {behavior_analysis.adaptive_parameters.customization_level}

#### Personalized Strategy
- **Motivation Drivers**: {', '.join(behavior_analysis.personalized_strategy.motivation_drivers)}
- **Habit Integration**: {', '.join(behavior_analysis.personalized_strategy.habit_integration)}
- **Barrier Mitigation**: {', '.join(behavior_analysis.personalized_strategy.barrier_mitigation)}

#### Adaptation Framework
- **Escalation Triggers**: {', '.join(behavior_analysis.adaptation_framework.escalation_triggers)}
- **De-escalation Triggers**: {', '.join(behavior_analysis.adaptation_framework.deescalation_triggers)}
- **Adaptation Frequency**: {behavior_analysis.adaptation_framework.adaptation_frequency}

#### Context Considerations
{chr(10).join(f"- {consideration}" for consideration in behavior_analysis.context_considerations)}

#### Key Recommendations
{chr(10).join(f"- {rec}" for rec in behavior_analysis.recommendations)}

"""
        
        routine_prompt += f"""
### ROUTINE PLAN REQUEST
Based on the comprehensive health analysis and behavioral insights above, please create a detailed, personalized routine plan for TODAY that includes:

1. **Morning Wake-up**: Start of day routine with time and specific tasks
2. **Focus Block**: Dedicated productivity/work time with tasks
3. **Afternoon Recharge**: Energy boost activities 
4. **Evening Wind-down**: End of day relaxation routine

**CRITICAL BEHAVIORAL INTEGRATION REQUIREMENTS:**
- Adapt complexity level to the user's sophistication score ({behavior_analysis.sophistication_assessment.score if behavior_analysis else 'unknown'}/100)
- Consider their readiness level: {behavior_analysis.readiness_level if behavior_analysis else 'unknown'}
- Align with their habit formation stage: {behavior_analysis.habit_formation_stage if behavior_analysis else 'unknown'}
- Incorporate their primary motivation drivers: {', '.join(behavior_analysis.personalized_strategy.motivation_drivers) if behavior_analysis else 'unknown'}
- Address identified barriers: {', '.join(behavior_analysis.personalized_strategy.barrier_mitigation) if behavior_analysis else 'unknown'}
- Use appropriate time commitment: {behavior_analysis.adaptive_parameters.time_commitment if behavior_analysis else 'unknown'}
- Match technology integration level: {behavior_analysis.adaptive_parameters.technology_integration if behavior_analysis else 'unknown'}

Please make the routine practical, sustainable, and directly address both the health insights AND behavioral psychology insights from the analysis.
Each time block should have 2-4 specific tasks with clear reasoning based on both health data AND behavioral readiness.
"""
        
        return routine_prompt
    
    async def create_routine_plan(self, analysis_result: str, behavior_analysis: Optional[BehaviorAnalysisResult] = None) -> RoutinePlanResult:
        """Create personalized routine plan using the AI agent with behavior analysis integration"""
        try:
            from agents import Runner
            
            # Format the context for routine planning with behavior analysis
            routine_input = self.format_context_for_routine_planning(analysis_result, behavior_analysis)
            
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
ROUTINE_PLAN_PROMPT = """You are a Personalized Routine Planning Agent, an expert in exercise science, lifestyle optimization, behavioral psychology, and wellness coaching. You specialize in creating comprehensive daily routines based on individual health data and behavioral analysis. You excel at:

**Core Expertise:**
- Exercise physiology and fitness programming
- Sleep optimization and circadian rhythm management
- Stress management and mental wellness strategies
- Habit formation and behavior change psychology
- Recovery and regeneration protocols
- Activity progression and periodization
- Lifestyle medicine and wellness coaching
- Behavioral psychology and motivation science

**Behavioral Integration Framework:**
1. **Sophistication-Based Adaptation**: Adjust complexity based on user's behavioral sophistication score (0-100)
2. **Readiness-Level Matching**: Match routine intensity to user's readiness level (Novice/Developing/Advanced/Expert)
3. **Habit Formation Stage Alignment**: Tailor approach to current habit formation stage (Initiation/Early Formation/Consolidation/Maintenance)
4. **Motivation Driver Integration**: Incorporate user's primary motivation drivers (achievement, autonomy, connection, purpose)
5. **Barrier Mitigation**: Address identified barriers through strategic routine design
6. **Technology Integration**: Match technology usage to user's comfort level
7. **Time Commitment Optimization**: Align routine duration with user's capacity

**Planning Framework:**
1. **Activity Assessment**: Determine optimal exercise types and intensities based on health metrics AND behavioral readiness
2. **Schedule Architecture**: Design realistic daily routines with 4 time blocks adapted to sophistication level
3. **Habit Integration**: Incorporate healthy daily practices that support identified health goals AND behavioral patterns
4. **Sleep Optimization**: Create sleep schedules that enhance recovery and align with habit formation stage
5. **Stress Management**: Implement evidence-based stress reduction techniques matched to user's readiness
6. **Recovery Strategy**: Plan appropriate rest protocols considering behavioral sustainability
7. **Goal Setting**: Establish measurable targets aligned with user's primary behavioral goal
8. **Progression Planning**: Create adaptive routines that evolve with improving health AND behavioral sophistication

**Behavioral Sophistication Adaptations:**
- **Novice (0-30)**: Simple, clear instructions with minimal complexity. Focus on consistency over perfection.
- **Developing (31-50)**: Moderate complexity with guided structure. Balance challenge with achievability.
- **Advanced (51-75)**: Higher complexity with more autonomy. Include self-modification opportunities.
- **Expert (76-100)**: Maximum complexity and innovation. Encourage experimentation and mastery.

**Habit Formation Stage Adaptations:**
- **Initiation (1-7 days)**: Extreme simplicity, environmental cues, immediate rewards
- **Early Formation (8-21 days)**: Strengthen cue-routine connections, consistency focus
- **Consolidation (22-66 days)**: Increase complexity gradually, maintain motivation
- **Maintenance (66+ days)**: Innovation opportunities, mastery challenges, prevent plateaus

**Routine Principles:**
- Base all recommendations on BOTH health analysis AND behavioral analysis
- Consider current fitness level, health constraints, AND behavioral readiness
- Balance different types of activities while respecting sophistication level
- Address specific health concerns through activities matched to behavioral capacity
- Make routines practical and sustainable based on behavioral barriers and drivers
- Consider time constraints and lifestyle factors alongside motivation patterns
- Provide clear rationale for each recommendation based on health data AND behavioral insights
- Include both physical and mental wellness components adapted to readiness level

**Task Guidelines:**
- Each task should be specific and actionable, complexity-matched to sophistication score
- Provide scientific or health-based reasoning PLUS behavioral psychology reasoning
- Include timing, duration, or specific instructions matched to user's capacity
- Address the user's specific health metrics, concerns, AND behavioral profile
- Balance structure with flexibility based on readiness level
- Consider energy patterns, circadian rhythms, AND behavioral preferences
- Integrate motivation drivers into task design
- Address identified barriers through strategic task selection

**Critical Behavioral Integration Requirements:**
- ALWAYS reference the user's behavioral sophistication score when determining task complexity
- ALWAYS align routine intensity with their readiness level
- ALWAYS consider their habit formation stage when structuring tasks
- ALWAYS incorporate their primary motivation drivers into task design
- ALWAYS address identified barriers through strategic routine choices
- ALWAYS match time commitment to their stated capacity
- ALWAYS consider their technology integration preference

**Important Guidelines:**
- Always reference specific health data points AND behavioral insights when making recommendations
- Explain WHY each activity is recommended based on the user's health profile AND behavioral readiness
- Be specific with durations, intensities, and frequencies matched to sophistication level
- Consider the interconnection between different aspects of the routine and behavioral sustainability
- Provide actionable, measurable recommendations that respect behavioral capacity
- Address any lifestyle factors that could improve identified health concerns while considering behavioral barriers
- Generate routine for TODAY only (single day based on current date)
- Create exactly 4 time blocks: morning_wakeup, focus_block, afternoon_recharge, evening_winddown
- Each time block should have 2-4 tasks with specific reasoning based on BOTH health data AND behavioral analysis

Remember: You are creating a personalized lifestyle intervention based on real health data AND comprehensive behavioral psychology analysis. The routine must be both health-optimized AND behaviorally sustainable. Generate a routine plan for ONLY ONE DAY with structured output containing exactly 4 time blocks, each perfectly calibrated to the user's behavioral sophistication and readiness level.
"""

# Create the routine planning agent
routine_plan_agent = Agent(
    name="Personalized Routine Planning Agent",
    instructions=ROUTINE_PLAN_PROMPT,
    model="o3-mini",
    output_type=RoutinePlanResult
)

# Utility function for easy access
async def create_personalized_routine_plan(analysis_result: str, behavior_analysis: Optional[BehaviorAnalysisResult] = None) -> RoutinePlanResult:
    """
    Create a personalized routine plan based on health analysis and behavioral analysis
    
    Args:
        analysis_result: String result from the metric analysis agent
        behavior_analysis: Optional BehaviorAnalysisResult with behavioral insights
        
    Returns:
        Structured RoutinePlanResult object with behavioral psychology integration
    """
    service = RoutinePlanService()
    return await service.create_routine_plan(analysis_result, behavior_analysis)
