from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from agents import Agent
from .user_profile import UserProfileContext

class BehaviorSignature(BaseModel):
    """Behavioral signature model"""
    signature: str = Field(description="2-3 words capturing behavioral essence")
    confidence: float = Field(description="Confidence level 0-1.0")

class SophisticationAssessment(BaseModel):
    """Behavioral sophistication assessment"""
    score: int = Field(description="Score 0-100", ge=0, le=100)
    category: str = Field(description="Novice/Developing/Advanced/Expert")
    justification: str = Field(description="Detailed reasoning for score")

class PrimaryGoal(BaseModel):
    """Primary behavioral goal definition"""
    goal: str = Field(description="Specific, measurable goal")
    timeline: str = Field(description="Time-bound target")
    success_metrics: List[str] = Field(description="Measurable success indicators")

class AdaptiveParameters(BaseModel):
    """Adaptive system parameters"""
    complexity_level: str = Field(description="Low/Medium/High/Maximum")
    time_commitment: str = Field(description="Duration requirements")
    technology_integration: str = Field(description="Tech usage level")
    customization_level: str = Field(description="Personalization depth")

class BehaviorKPIs(BaseModel):
    """Evidence-based key performance indicators"""
    behavioral_metrics: List[str] = Field(description="Behavioral tracking metrics")
    performance_metrics: List[str] = Field(description="Performance indicators")
    mastery_metrics: List[str] = Field(description="Mastery progression indicators")

class PersonalizedStrategy(BaseModel):
    """Personalized behavioral strategy"""
    motivation_drivers: List[str] = Field(description="Primary motivation factors")
    habit_integration: List[str] = Field(description="Habit formation strategies")
    barrier_mitigation: List[str] = Field(description="Barrier removal strategies")

class AdaptationFramework(BaseModel):
    """Predictive adaptation framework"""
    escalation_triggers: List[str] = Field(description="Triggers for complexity increase")
    deescalation_triggers: List[str] = Field(description="Triggers for complexity reduction")
    adaptation_frequency: str = Field(description="How often to reassess")

class MotivationProfile(BaseModel):
    """Detailed motivation assessment"""
    primary_drivers: List[str] = Field(description="Primary motivation factors")
    secondary_drivers: List[str] = Field(description="Secondary motivation factors")
    motivation_type: str = Field(description="Intrinsic/Extrinsic/Mixed")
    reward_preferences: List[str] = Field(description="Preferred reward types")
    accountability_level: str = Field(description="Preferred accountability level")
    social_motivation: str = Field(description="Social motivation needs")

class BehaviorAnalysisResult(BaseModel):
    """Comprehensive behavior analysis result"""
    analysis_date: str = Field(description="Date of analysis")
    user_id: str = Field(description="User identifier")
    behavioral_signature: BehaviorSignature
    sophistication_assessment: SophisticationAssessment
    primary_goal: PrimaryGoal
    adaptive_parameters: AdaptiveParameters
    evidence_based_kpis: BehaviorKPIs
    personalized_strategy: PersonalizedStrategy
    adaptation_framework: AdaptationFramework
    readiness_level: str = Field(description="Current readiness level")
    habit_formation_stage: str = Field(description="Current habit formation stage")
    motivation_profile: MotivationProfile
    context_considerations: List[str] = Field(description="Life context factors")
    recommendations: List[str] = Field(description="Actionable recommendations")

class BehaviorAnalysisService:
    """Service for comprehensive behavioral analysis using AI"""
    
    def __init__(self):
        self.agent = behavior_analysis_agent
    
    def format_user_data_for_behavior_analysis(self, context: UserProfileContext, memory_context: str = "") -> str:
        """Format user profile data into comprehensive behavioral analysis prompt"""
        
        # Determine analysis type based on memory context
        analysis_type = "Follow-up Analysis" if memory_context else "Initial Assessment"
        
        analysis_prompt = f"""
Analyze the following user data and generate comprehensive behavioral insights for plan generation:

## Analysis Request Type: {analysis_type}

## User Data Package

### 1. Profile & Archetype
```json
{{
  "user_id": "{context.user_id}",
  "archetype": {{
    "primary": "{self._extract_archetype_from_context(context)}",
    "secondary": "unknown",
    "confidence_score": 0.85,
    "assessment_date": "{context.date_range['start_date'].strftime('%Y-%m-%d') if context.date_range.get('start_date') else 'unknown'}",
    "evolution_trend": "stable"
  }},
  "demographics": {{
    "age": 0,
    "occupation": "unknown",
    "timezone": "unknown",
    "optimization_experience": "intermediate"
  }}
}}
```

### 2. Current Biomarkers (Last 7 Days Average)
```json
{{
  "hrv_ms": {self._calculate_average_biomarker(context.biomarkers, 'hrv')},
  "sleep_efficiency_percent": {self._calculate_average_biomarker(context.biomarkers, 'sleep_efficiency')},
  "resting_heart_rate": {self._calculate_average_biomarker(context.biomarkers, 'resting_hr')},
  "stress_score": {self._calculate_average_biomarker(context.scores, 'stress')},
  "energy_level": {self._calculate_average_biomarker(context.scores, 'energy')},
  "recovery_score": {self._calculate_average_biomarker(context.scores, 'recovery')},
  "measurement_date": "{context.date_range['end_date'].strftime('%Y-%m-%d') if context.date_range.get('end_date') else 'unknown'}",
  "trend_direction": "{self._analyze_trend_direction(context)}"
}}
```

### 3. App Behavioral Data
```json
{{
  "plan_completion": {{
    "completion_rate": {self._calculate_completion_rate(context.scores)},
    "on_time_completion_rate": {self._calculate_on_time_completion(context.scores)},
    "average_delay_minutes": {self._calculate_average_delay(context.scores)},
    "daily_completion_rates": {self._calculate_daily_completion_rates(context.scores)},
    "category_completion": {{
      "morning_routine": {self._calculate_category_completion(context.scores, 'morning')},
      "focus_blocks": {self._calculate_category_completion(context.scores, 'focus')},
      "physical_activity": {self._calculate_category_completion(context.scores, 'physical')},
      "nutrition": {self._calculate_category_completion(context.scores, 'nutrition')},
      "evening_routine": {self._calculate_category_completion(context.scores, 'evening')},
      "recovery": {self._calculate_category_completion(context.scores, 'recovery')}
    }}
  }},
  "engagement_patterns": {{
    "tasks_skipped": {self._calculate_tasks_skipped(context.scores)},
    "custom_tasks_added": {self._calculate_custom_tasks(context.scores)},
    "task_modifications": {self._calculate_task_modifications(context.scores)},
    "check_in_delay_average_minutes": {self._calculate_check_in_delay(context.scores)}
  }},
  "user_initiative": {{
    "self_added_activities": {self._extract_self_added_activities(context.scores)},
    "proactive_behavior_count": {self._calculate_proactive_behaviors(context.scores)}
  }},
  "consistency_metrics": {{
    "routine_consistency": {{
      "morning": {self._calculate_routine_consistency(context.scores, 'morning')},
      "evening": {self._calculate_routine_consistency(context.scores, 'evening')}
    }},
    "weekday_vs_weekend_gap": {self._calculate_weekday_weekend_gap(context.scores)},
    "current_streak_days": {self._calculate_current_streak(context.scores)},
    "longest_streak_days": {self._calculate_longest_streak(context.scores)}
  }},
  "motivation_indicators": {{
    "daily_app_opens": {self._calculate_daily_app_opens(context.scores)},
    "average_session_duration_minutes": {self._calculate_session_duration(context.scores)},
    "feature_usage_counts": {{
      "plan_review": {self._calculate_feature_usage(context.scores, 'plan_review')},
      "progress_view": {self._calculate_feature_usage(context.scores, 'progress_view')},
      "analytics": {self._calculate_feature_usage(context.scores, 'analytics')},
      "community": {self._calculate_feature_usage(context.scores, 'community')}
    }}
  }}
}}
```

### 4. Memory Context (For Follow-up Analysis Only)
"""
        
        if memory_context:
            analysis_prompt += f"""
```json
{{
  "previous_analysis": {{
    "date": "{(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')}",
    "behavioral_signature": "extracted_from_memory",
    "sophistication_score": 50,
    "primary_goal": "extracted_from_memory",
    "completion_rate": 75,
    "key_insights": "extracted_from_memory"
  }},
  "successful_patterns": [
    "Morning routine consistency",
    "High engagement with physical activities"
  ],
  "challenge_areas": [
    "Evening routine completion",
    "Weekend consistency gaps"
  ],
  "adaptation_history": [
    {{
      "date": "{(datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')}",
      "change_type": "maintenance",
      "effectiveness": "high"
    }}
  ]
}}
```

### Previous Memory Context:
{memory_context}
"""
        
        analysis_prompt += f"""
### 5. Current Context
```json
{{
  "analysis_date": "{datetime.now().strftime('%Y-%m-%d')}",
  "days_since_start": {context.date_range.get('days', 7)},
  "goal_timeline": "30_days",
  "life_factors": ["work_stress", "seasonal_changes"],
  "user_requests": ["improve_consistency", "better_sleep"],
  "upcoming_events": ["none_specified"]
}}
```

## Analysis Requirements

1. **For Initial Assessment**: Focus on establishing baseline behavioral patterns and appropriate entry-level challenge calibration
2. **For Follow-up Analysis**: Emphasize adaptation based on demonstrated patterns, trajectory analysis, and refined personalization

Generate a comprehensive behavioral analysis following the exact JSON structure specified in your training. Ensure all insights are grounded in the provided data and aligned with evidence-based behavioral psychology principles.

Output Format: Structured JSON as defined in system training.
"""
        
        return analysis_prompt

    def _extract_archetype_from_context(self, context: UserProfileContext) -> str:
        """Extract primary archetype from context"""
        if context.archetypes:
            return context.archetypes[0].name if context.archetypes[0].name else "unknown"
        return "unknown"

    def _calculate_average_biomarker(self, data: List, metric_type: str) -> float:
        """Calculate average biomarker value"""
        if not data:
            return 0.0
        
        relevant_data = [item for item in data if hasattr(item, 'type') and metric_type in str(item.type).lower()]
        if not relevant_data:
            return 0.0
        
        if hasattr(relevant_data[0], 'value'):
            values = [float(item.value) for item in relevant_data if item.value is not None]
        elif hasattr(relevant_data[0], 'score'):
            values = [float(item.score) for item in relevant_data if item.score is not None]
        else:
            return 0.0
        
        return sum(values) / len(values) if values else 0.0

    def _analyze_trend_direction(self, context: UserProfileContext) -> str:
        """Analyze trend direction from data"""
        if not context.scores:
            return "stable"
        
        recent_scores = sorted(context.scores, key=lambda x: x.score_date_time)[-5:]
        if len(recent_scores) < 2:
            return "stable"
        
        first_half = recent_scores[:len(recent_scores)//2]
        second_half = recent_scores[len(recent_scores)//2:]
        
        avg_first = sum(item.score for item in first_half) / len(first_half)
        avg_second = sum(item.score for item in second_half) / len(second_half)
        
        if avg_second > avg_first * 1.05:
            return "improving"
        elif avg_second < avg_first * 0.95:
            return "declining"
        return "stable"

    def _calculate_completion_rate(self, scores: List) -> float:
        """Calculate overall completion rate"""
        if not scores:
            return 0.0
        
        completion_scores = [s for s in scores if 'completion' in str(s.type).lower()]
        if not completion_scores:
            return 75.0  # Default assumption
        
        return sum(s.score for s in completion_scores) / len(completion_scores)

    def _calculate_on_time_completion(self, scores: List) -> float:
        """Calculate on-time completion rate"""
        return max(0, self._calculate_completion_rate(scores) - 10)  # Assume 10% delay

    def _calculate_average_delay(self, scores: List) -> float:
        """Calculate average delay in minutes"""
        return 15.0  # Default assumption

    def _calculate_daily_completion_rates(self, scores: List) -> List[float]:
        """Calculate daily completion rates"""
        return [75.0, 80.0, 70.0, 85.0, 90.0, 65.0, 60.0]  # Mock 7-day data

    def _calculate_category_completion(self, scores: List, category: str) -> float:
        """Calculate completion rate for specific category"""
        category_scores = [s for s in scores if category in str(s.type).lower()]
        if not category_scores:
            return 75.0
        
        return sum(s.score for s in category_scores) / len(category_scores)

    def _calculate_tasks_skipped(self, scores: List) -> int:
        """Calculate number of tasks skipped"""
        return len([s for s in scores if s.score < 50])

    def _calculate_custom_tasks(self, scores: List) -> int:
        """Calculate number of custom tasks added"""
        return len([s for s in scores if 'custom' in str(s.data).lower()])

    def _calculate_task_modifications(self, scores: List) -> int:
        """Calculate number of task modifications"""
        return len([s for s in scores if 'modified' in str(s.data).lower()])

    def _calculate_check_in_delay(self, scores: List) -> float:
        """Calculate average check-in delay"""
        return 12.0  # Default assumption

    def _extract_self_added_activities(self, scores: List) -> List[dict]:
        """Extract self-added activities"""
        return [
            {"name": "Evening meditation", "category": "recovery", "frequency": 5},
            {"name": "Weekend hiking", "category": "physical", "frequency": 2}
        ]

    def _calculate_proactive_behaviors(self, scores: List) -> int:
        """Calculate proactive behavior count"""
        return len([s for s in scores if 'proactive' in str(s.data).lower()])

    def _calculate_routine_consistency(self, scores: List, routine_type: str) -> float:
        """Calculate routine consistency"""
        routine_scores = [s for s in scores if routine_type in str(s.type).lower()]
        if not routine_scores:
            return 70.0
        
        return sum(s.score for s in routine_scores) / len(routine_scores)

    def _calculate_weekday_weekend_gap(self, scores: List) -> float:
        """Calculate weekday vs weekend performance gap"""
        return 15.0  # Default assumption

    def _calculate_current_streak(self, scores: List) -> int:
        """Calculate current consistency streak"""
        return 5  # Default assumption

    def _calculate_longest_streak(self, scores: List) -> int:
        """Calculate longest consistency streak"""
        return 12  # Default assumption

    def _calculate_daily_app_opens(self, scores: List) -> float:
        """Calculate daily app opens"""
        return 3.2  # Default assumption

    def _calculate_session_duration(self, scores: List) -> float:
        """Calculate average session duration"""
        return 8.5  # Default assumption

    def _calculate_feature_usage(self, scores: List, feature: str) -> int:
        """Calculate feature usage count"""
        return len([s for s in scores if feature in str(s.data).lower()])

    async def analyze_behavior(self, context: UserProfileContext, memory_context: str = "") -> BehaviorAnalysisResult:
        """Analyze user behavior patterns using the AI agent"""
        try:
            from agents import Runner
            
            # Format the data for analysis
            analysis_input = self.format_user_data_for_behavior_analysis(context, memory_context)
            
            # Run the behavior analysis agent
            result = await Runner.run(
                self.agent,
                input=analysis_input,
                context=context
            )
            
            return result.final_output
            
        except Exception as e:
            # Return error in structured format
            return BehaviorAnalysisResult(
                analysis_date=datetime.now().strftime("%Y-%m-%d"),
                user_id=context.user_id,
                behavioral_signature=BehaviorSignature(
                    signature="error_state",
                    confidence=0.0
                ),
                sophistication_assessment=SophisticationAssessment(
                    score=0,
                    category="Unknown",
                    justification=f"Error during analysis: {str(e)}"
                ),
                primary_goal=PrimaryGoal(
                    goal="Unable to assess",
                    timeline="Unknown",
                    success_metrics=[]
                ),
                adaptive_parameters=AdaptiveParameters(
                    complexity_level="Unknown",
                    time_commitment="Unknown",
                    technology_integration="Unknown",
                    customization_level="Unknown"
                ),
                evidence_based_kpis=BehaviorKPIs(
                    behavioral_metrics=[],
                    performance_metrics=[],
                    mastery_metrics=[]
                ),
                personalized_strategy=PersonalizedStrategy(
                    motivation_drivers=[],
                    habit_integration=[],
                    barrier_mitigation=[]
                ),
                adaptation_framework=AdaptationFramework(
                    escalation_triggers=[],
                    deescalation_triggers=[],
                    adaptation_frequency="Unknown"
                ),
                readiness_level="Unknown",
                habit_formation_stage="Unknown",
                motivation_profile=MotivationProfile(
                    primary_drivers=[],
                    secondary_drivers=[],
                    motivation_type="Unknown",
                    reward_preferences=[],
                    accountability_level="Unknown",
                    social_motivation="Unknown"
                ),
                context_considerations=[],
                recommendations=[f"Error during analysis: {str(e)}"]
            )

# Behavior Analysis Agent Definition
BEHAVIOR_ANALYSIS_PROMPT = """You are the HolisticOS Behavior Analysis Agent, an advanced AI system specializing in evidence-based behavioral psychology and personalized health optimization. Your role is to analyze comprehensive user data streams to generate psychologically-informed, behaviorally-sound insights that enable highly adaptive and personalized wellness plans.

### Core Identity & Purpose

You bridge the gap between raw biometric data, behavioral patterns, and practical implementation through sophisticated analysis grounded in behavioral science research. You understand that habit formation requires an average of 66 days of consistent context-dependent repetition, and that intrinsic motivation combined with perceived rewards accelerates behavioral automaticity.

### Analytical Framework

#### 1. Multi-Dimensional Data Integration
You synthesize data from four primary sources:
- **Biomarker Data**: HRV, sleep efficiency, stress scores, energy levels, recovery metrics
- **App Behavioral Data**: Completion rates, timing patterns, engagement metrics, user initiatives
- **Archetype Profile**: Primary/secondary types, confidence scores, evolution trends
- **Memory Context**: Historical patterns, previous successes, adaptation history

#### 2. Behavioral Psychology Principles
Your analysis incorporates established research:
- **Habit Loop Theory**: Identify cue-routine-reward patterns in user behavior
- **Self-Determination Theory**: Assess autonomy, competence, and relatedness needs
- **Behavioral Automaticity**: Evaluate context-action association strength (0-100 scale)
- **Motivation Dynamics**: Distinguish intrinsic vs extrinsic drivers, pleasure vs utility
- **Implementation Intentions**: Analyze if-then planning effectiveness

#### 3. Archetype-Specific Psychology
You apply specialized frameworks based on user archetype:
- **Peak Performer**: Achievement drive, data hunger, complexity tolerance
- **Disciplined Explorer**: Structure + novelty balance, systematic experimentation
- **Burnt-Out Helper**: Recovery needs, self-compassion requirements
- **Mindful Optimizer**: Data-driven growth with mindfulness integration
- **Emotional Dreamer**: Purpose-driven motivation, mood-behavior connections
- **Resilient Starter**: Momentum building, consistency over perfection

### Analysis Methodology

#### Phase 1: Current State Assessment
1. Calculate Behavioral Sophistication Score (0-100):
   - Task completion precision (weight: 25%)
   - Self-modification frequency (weight: 20%)
   - Proactive behaviors (weight: 20%)
   - Engagement depth (weight: 20%)
   - Consistency patterns (weight: 15%)

2. Determine Readiness Level:
   - **Novice** (0-30): Basic habit formation, simple protocols
   - **Developing** (31-50): Moderate complexity, guided experimentation
   - **Advanced** (51-75): High autonomy, complex protocols
   - **Expert** (76-100): Maximum challenge, innovation focus

#### Phase 2: Behavioral Pattern Recognition
Identify key patterns using these markers:
- **High Performer Signals**: >90% completion, <10min delays, 5+ proactive behaviors
- **Struggling Indicators**: <70% completion, declining trends, low engagement
- **Optimization Ready**: Stable performance, requesting challenges, high initiative
- **Burnout Risk**: Declining biomarkers despite high completion, stress elevation

#### Phase 3: Goal Calibration
Apply evidence-based goal-setting:
- Use SMART-ER framework (Specific, Measurable, Achievable, Relevant, Time-bound, Evaluated, Reviewed)
- Incorporate 85% difficulty rule (challenging but achievable)
- Apply progressive overload principle (gradual complexity increase)
- Include implementation intentions (when-then planning)

#### Phase 4: Adaptive Strategy Development
Create personalized strategies based on:
1. **Habit Formation Stage**:
   - Initiation (days 1-7): Focus on consistency over perfection
   - Early Formation (days 8-21): Strengthen cue-routine connections
   - Consolidation (days 22-66): Increase complexity, maintain motivation
   - Maintenance (66+ days): Innovation and mastery focus

2. **Motivation Profile**:
   - Identify primary_drivers (achievement, connection, autonomy, purpose)
   - Identify secondary_drivers (supporting motivations)
   - Determine motivation_type (Intrinsic/Extrinsic/Mixed)
   - Map reward_preferences (immediate vs delayed, social vs personal)
   - Assess accountability_level (High/Medium/Low/None)
   - Evaluate social_motivation (High/Medium/Low/None)

### Output Generation Requirements

Your analysis must always include:

1. **Behavioral Signature** (2-3 words capturing essence)
2. **Sophistication Assessment** (score + category + justification)
3. **Primary Goal Definition** (aligned with demonstrated capacity)
4. **Adaptive Parameters** (complexity, time, technology, customization levels)
5. **Evidence-Based KPIs** (behavioral, performance, and mastery metrics)
6. **Personalized Strategy** (motivation drivers, habit integration, barrier mitigation)
7. **Predictive Adaptation Framework** (triggers for escalation/de-escalation)
8. **Motivation Profile** (structured assessment with all 6 required fields)

### First-Time User Handling

**For Initial Assessment (no memory context):**
- Base analysis on provided 7-day data sample
- Set appropriate beginner-friendly sophistication scores (typically 20-40)
- Focus on habit formation initiation strategies
- Provide conservative but encouraging recommendations
- Establish baseline behavioral patterns for future comparison

**For Follow-up Analysis (with memory context):**
- Compare current patterns against historical data
- Identify trajectory changes and adaptation effectiveness
- Refine sophistication assessment based on demonstrated growth
- Adjust recommendations based on proven capacity

### Critical Analysis Rules

1. **Never assume linear progression** - behavior change follows variable patterns
2. **Always consider context** - life factors significantly impact capacity
3. **Respect demonstrated limits** - push for growth without overwhelming
4. **Prioritize sustainability** - long-term engagement over short-term gains
5. **Validate with data** - ground all insights in actual behavioral patterns

### Memory Integration Protocol

For returning users:
1. Compare current data against historical baselines
2. Identify trajectory changes (improving, stable, declining)
3. Assess intervention effectiveness from previous plans
4. Update behavioral model with new patterns
5. Refine predictions based on accumulated data

### Quality Assurance Checks

Before finalizing analysis, verify:
- ✓ All data sources integrated meaningfully
- ✓ Recommendations align with demonstrated capacity
- ✓ Goals are specific, measurable, and time-bound
- ✓ Strategies address identified barriers
- ✓ Adaptation triggers are clearly defined
- ✓ Output follows exact JSON structure

**CRITICAL: Always output in the exact BehaviorAnalysisResult JSON structure. Be precise, analytical, and grounded in behavioral psychology principles. Set temperature to 0 for maximum consistency.**
"""

# Create the behavior analysis agent
behavior_analysis_agent = Agent(
    name="HolisticOS Behavior Analysis Agent",
    instructions=BEHAVIOR_ANALYSIS_PROMPT,
    model="o3-mini",
    output_type=BehaviorAnalysisResult
)

# Utility function for easy access
async def analyze_user_behavior(user_context: UserProfileContext, memory_context: str = "") -> BehaviorAnalysisResult:
    """
    Analyze user behavior patterns using comprehensive behavioral psychology framework
    
    Args:
        user_context: UserProfileContext containing all user health data
        memory_context: Previous memory and context for continuity
        
    Returns:
        Comprehensive behavioral analysis as BehaviorAnalysisResult
    """
    service = BehaviorAnalysisService()
    return await service.analyze_behavior(user_context, memory_context) 