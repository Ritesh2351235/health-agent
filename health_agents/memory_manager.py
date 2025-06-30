import json
import asyncio
import os
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass
import asyncpg
from .nutrition_plan_agent import NutritionPlanResult
from .routine_plan_agent import RoutinePlanResult

@dataclass
class UserMemory:
    """User memory data structure"""
    profile_id: str
    user_preferences: Dict[str, Any]
    health_goals: Dict[str, Any]
    dietary_restrictions: Dict[str, Any]
    lifestyle_context: Dict[str, Any]
    medical_conditions: Dict[str, Any]
    last_analysis_result: Optional[str]
    analysis_insights: Dict[str, Any]
    last_nutrition_plan: Optional[Dict[str, Any]]
    last_routine_plan: Optional[Dict[str, Any]]
    health_trends: Dict[str, Any]
    improvement_areas: Dict[str, Any]
    success_patterns: Dict[str, Any]
    total_analyses: int
    last_analysis_date: Optional[datetime]
    nutrition_plan_date: Optional[datetime]
    routine_plan_date: Optional[datetime]

class MemoryManager:
    """Manages user memory for health analysis continuity"""
    
    def __init__(self, database_url: str = None):
        # Use the same approach as existing user_profile.py
        self.database_url = database_url or os.getenv("DATABASE_URL")
        
        if not self.database_url:
            raise ValueError("Missing DATABASE_URL in environment variables. Please set DATABASE_URL or pass database_url parameter.")
        
        self.connection = None
    
    def _serialize_for_json(self, obj: Any) -> str:
        """Helper function to serialize objects to JSON, handling datetime objects"""
        def datetime_handler(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")
        
        return json.dumps(obj, default=datetime_handler)
    
    async def connect(self):
        """Establish database connection"""
        try:
            self.connection = await asyncpg.connect(self.database_url)
        except Exception as e:
            print(f"Error connecting to database: {e}")
            raise
    
    async def disconnect(self):
        """Close database connection"""
        if self.connection:
            await self.connection.close()
    
    async def get_user_memory(self, profile_id: str) -> Optional[UserMemory]:
        """Retrieve user memory from database"""
        if not self.connection:
            await self.connect()
        
        try:
            query = """
                SELECT profile_id, user_preferences, health_goals, dietary_restrictions, 
                       lifestyle_context, medical_conditions, last_analysis_result, 
                       analysis_insights, last_nutrition_plan, last_routine_plan, 
                       health_trends, improvement_areas, success_patterns, total_analyses,
                       last_analysis_date, nutrition_plan_date, routine_plan_date
                FROM memory 
                WHERE profile_id = $1
            """
            
            row = await self.connection.fetchrow(query, profile_id)
            
            if row:
                return UserMemory(
                    profile_id=row['profile_id'],
                    user_preferences=row['user_preferences'] or {},
                    health_goals=row['health_goals'] or {},
                    dietary_restrictions=row['dietary_restrictions'] or {},
                    lifestyle_context=row['lifestyle_context'] or {},
                    medical_conditions=row['medical_conditions'] or {},
                    last_analysis_result=row['last_analysis_result'],
                    analysis_insights=row['analysis_insights'] or {},
                    last_nutrition_plan=row['last_nutrition_plan'],
                    last_routine_plan=row['last_routine_plan'],
                    health_trends=row['health_trends'] or {},
                    improvement_areas=row['improvement_areas'] or {},
                    success_patterns=row['success_patterns'] or {},
                    total_analyses=row['total_analyses'] or 0,
                    last_analysis_date=row['last_analysis_date'],
                    nutrition_plan_date=row['nutrition_plan_date'],
                    routine_plan_date=row['routine_plan_date']
                )
            return None
            
        except Exception as e:
            print(f"Error retrieving user memory: {e}")
            return None
    
    async def create_user_memory(self, profile_id: str, 
                                user_preferences: Dict[str, Any] = None,
                                health_goals: Dict[str, Any] = None,
                                dietary_restrictions: Dict[str, Any] = None,
                                lifestyle_context: Dict[str, Any] = None,
                                medical_conditions: Dict[str, Any] = None) -> bool:
        """Create initial user memory record"""
        if not self.connection:
            await self.connect()
        
        try:
            query = """
                INSERT INTO memory (profile_id, user_preferences, health_goals, 
                                  dietary_restrictions, lifestyle_context, medical_conditions)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (profile_id) DO NOTHING
            """
            
            await self.connection.execute(
                query, profile_id,
                self._serialize_for_json(user_preferences or {}),
                self._serialize_for_json(health_goals or {}),
                self._serialize_for_json(dietary_restrictions or {}),
                self._serialize_for_json(lifestyle_context or {}),
                self._serialize_for_json(medical_conditions or {})
            )
            return True
            
        except Exception as e:
            print(f"Error creating user memory: {e}")
            return False
    
    async def update_analysis_result(self, profile_id: str, analysis_result: str, 
                                   insights: Dict[str, Any] = None) -> bool:
        """Update memory with new analysis result"""
        if not self.connection:
            await self.connect()
        
        try:
            query = """
                UPDATE memory 
                SET last_analysis_result = $2,
                    analysis_insights = $3,
                    last_analysis_date = NOW(),
                    total_analyses = total_analyses + 1
                WHERE profile_id = $1
            """
            
            await self.connection.execute(
                query, profile_id, analysis_result, 
                self._serialize_for_json(insights or {})
            )
            return True
            
        except Exception as e:
            print(f"Error updating analysis result: {e}")
            return False
    
    async def update_nutrition_plan(self, profile_id: str, 
                                  nutrition_plan: NutritionPlanResult) -> bool:
        """Update memory with new nutrition plan"""
        if not self.connection:
            await self.connect()
        
        try:
            # Convert nutrition plan to dict for JSON storage
            plan_dict = {
                "date": nutrition_plan.date,
                "nutrition": {
                    "summary": nutrition_plan.nutrition.summary,
                    "nutritional_info": {
                        "calories": nutrition_plan.nutrition.nutritional_info.calories,
                        "protein": nutrition_plan.nutrition.nutritional_info.protein,
                        "protein_percent": nutrition_plan.nutrition.nutritional_info.protein_percent,
                        "carbs": nutrition_plan.nutrition.nutritional_info.carbs,
                        "carbs_percent": nutrition_plan.nutrition.nutritional_info.carbs_percent,
                        "fat": nutrition_plan.nutrition.nutritional_info.fat,
                        "fat_percent": nutrition_plan.nutrition.nutritional_info.fat_percent,
                        "fiber": nutrition_plan.nutrition.nutritional_info.fiber,
                        "sugar": nutrition_plan.nutrition.nutritional_info.sugar,
                        "sodium": nutrition_plan.nutrition.nutritional_info.sodium,
                        "potassium": nutrition_plan.nutrition.nutritional_info.potassium,
                        "vitamins": {
                            "Vitamin_D": nutrition_plan.nutrition.nutritional_info.vitamins.Vitamin_D,
                            "Calcium": nutrition_plan.nutrition.nutritional_info.vitamins.Calcium,
                            "Iron": nutrition_plan.nutrition.nutritional_info.vitamins.Iron,
                            "Magnesium": nutrition_plan.nutrition.nutritional_info.vitamins.Magnesium
                        }
                    },
                    # Add all meal blocks...
                    "Early_Morning": self._meal_block_to_dict(nutrition_plan.nutrition.Early_Morning),
                    "Breakfast": self._meal_block_to_dict(nutrition_plan.nutrition.Breakfast),
                    "Morning_Snack": self._meal_block_to_dict(nutrition_plan.nutrition.Morning_Snack),
                    "Lunch": self._meal_block_to_dict(nutrition_plan.nutrition.Lunch),
                    "Afternoon_Snack": self._meal_block_to_dict(nutrition_plan.nutrition.Afternoon_Snack),
                    "Dinner": self._meal_block_to_dict(nutrition_plan.nutrition.Dinner),
                    "Evening_Snack": self._meal_block_to_dict(nutrition_plan.nutrition.Evening_Snack)
                }
            }
            
            query = """
                UPDATE memory 
                SET last_nutrition_plan = $2,
                    nutrition_plan_date = NOW()
                WHERE profile_id = $1
            """
            
            await self.connection.execute(query, profile_id, self._serialize_for_json(plan_dict))
            return True
            
        except Exception as e:
            print(f"Error updating nutrition plan: {e}")
            return False
    
    async def update_routine_plan(self, profile_id: str, 
                                routine_plan: RoutinePlanResult) -> bool:
        """Update memory with new routine plan"""
        if not self.connection:
            await self.connect()
        
        try:
            # Convert routine plan to dict for JSON storage
            plan_dict = {
                "date": routine_plan.date,
                "routine": {
                    "summary": routine_plan.routine.summary,
                    "morning_wakeup": self._time_block_to_dict(routine_plan.routine.morning_wakeup),
                    "focus_block": self._time_block_to_dict(routine_plan.routine.focus_block),
                    "afternoon_recharge": self._time_block_to_dict(routine_plan.routine.afternoon_recharge),
                    "evening_winddown": self._time_block_to_dict(routine_plan.routine.evening_winddown)
                }
            }
            
            query = """
                UPDATE memory 
                SET last_routine_plan = $2,
                    routine_plan_date = NOW()
                WHERE profile_id = $1
            """
            
            await self.connection.execute(query, profile_id, self._serialize_for_json(plan_dict))
            return True
            
        except Exception as e:
            print(f"Error updating routine plan: {e}")
            return False
    
    async def update_user_context(self, profile_id: str, 
                                 user_preferences: Dict[str, Any] = None,
                                 health_goals: Dict[str, Any] = None,
                                 dietary_restrictions: Dict[str, Any] = None,
                                 lifestyle_context: Dict[str, Any] = None,
                                 medical_conditions: Dict[str, Any] = None) -> bool:
        """Update user context information"""
        if not self.connection:
            await self.connect()
        
        try:
            update_fields = []
            params = [profile_id]
            param_count = 2
            
            if user_preferences is not None:
                update_fields.append(f"user_preferences = ${param_count}")
                params.append(self._serialize_for_json(user_preferences))
                param_count += 1
            
            if health_goals is not None:
                update_fields.append(f"health_goals = ${param_count}")
                params.append(self._serialize_for_json(health_goals))
                param_count += 1
            
            if dietary_restrictions is not None:
                update_fields.append(f"dietary_restrictions = ${param_count}")
                params.append(self._serialize_for_json(dietary_restrictions))
                param_count += 1
            
            if lifestyle_context is not None:
                update_fields.append(f"lifestyle_context = ${param_count}")
                params.append(self._serialize_for_json(lifestyle_context))
                param_count += 1
            
            if medical_conditions is not None:
                update_fields.append(f"medical_conditions = ${param_count}")
                params.append(self._serialize_for_json(medical_conditions))
                param_count += 1
            
            if not update_fields:
                return True
            
            query = f"""
                UPDATE memory 
                SET {', '.join(update_fields)}
                WHERE profile_id = $1
            """
            
            await self.connection.execute(query, *params)
            return True
            
        except Exception as e:
            print(f"Error updating user context: {e}")
            return False
    
    def _meal_block_to_dict(self, meal_block) -> Dict[str, Any]:
        """Convert meal block to dictionary"""
        return {
            "time_range": meal_block.time_range,
            "nutrition_tip": meal_block.nutrition_tip,
            "meals": [
                {
                    "name": meal.name,
                    "details": meal.details,
                    "calories": meal.calories,
                    "protein": meal.protein,
                    "macros": {
                        "carbs": meal.macros.carbs,
                        "fat": meal.macros.fat
                    }
                }
                for meal in meal_block.meals
            ]
        }
    
    def _time_block_to_dict(self, time_block) -> Dict[str, Any]:
        """Convert time block to dictionary"""
        return {
            "time_range": time_block.time_range,
            "why_it_matters": time_block.why_it_matters,
            "tasks": [
                {
                    "task": task.task,
                    "reason": task.reason
                }
                for task in time_block.tasks
            ]
        }
    
    def format_memory_context(self, memory: UserMemory) -> str:
        """Format memory into context string for analysis"""
        if not memory:
            return "No previous memory available for this user."
        
        context_parts = []
        
        # User preferences and goals
        if memory.user_preferences:
            context_parts.append(f"User Preferences: {self._serialize_for_json(memory.user_preferences)}")
        
        if memory.health_goals:
            context_parts.append(f"Health Goals: {self._serialize_for_json(memory.health_goals)}")
        
        if memory.dietary_restrictions:
            context_parts.append(f"Dietary Restrictions: {self._serialize_for_json(memory.dietary_restrictions)}")
        
        if memory.lifestyle_context:
            context_parts.append(f"Lifestyle Context: {self._serialize_for_json(memory.lifestyle_context)}")
        
        if memory.medical_conditions:
            context_parts.append(f"Medical Conditions: {self._serialize_for_json(memory.medical_conditions)}")
        
        # Previous analysis insights
        if memory.last_analysis_result:
            context_parts.append(f"Previous Analysis (from {memory.last_analysis_date}): {memory.last_analysis_result[:500]}...")
        
        if memory.analysis_insights:
            context_parts.append(f"Analysis Insights: {self._serialize_for_json(memory.analysis_insights)}")
        
        # Health trends and patterns
        if memory.health_trends:
            context_parts.append(f"Health Trends: {self._serialize_for_json(memory.health_trends)}")
        
        if memory.success_patterns:
            context_parts.append(f"Success Patterns: {self._serialize_for_json(memory.success_patterns)}")
        
        if memory.improvement_areas:
            context_parts.append(f"Areas for Improvement: {self._serialize_for_json(memory.improvement_areas)}")
        
        # Analysis history
        context_parts.append(f"Total Previous Analyses: {memory.total_analyses}")
        
        return "\n\n".join(context_parts) 