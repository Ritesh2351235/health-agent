import time
import json
import os
from datetime import datetime, date, time as datetime_time
from agents import Runner, trace
from duckduckgo_search import DDGS
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.json import JSON
from rich.tree import Tree
from health_agents.user_profile import get_user_profile_context
from health_agents.metric_analysis_agent import analyze_user_health_metrics
from health_agents.nutrition_plan_agent import create_personalized_nutrition_plan, NutritionPlanResult
from health_agents.routine_plan_agent import create_personalized_routine_plan, RoutinePlanResult
from health_agents.behavior_analysis_agent import analyze_user_behavior, BehaviorAnalysisResult
from health_agents.memory_manager import MemoryManager

console = Console()

class HealthCoordinator:
    def __init__(self, profile_id: str, database_url: str = None):
        self.profile_id = profile_id
        self.memory_manager = MemoryManager(database_url)

    def serialize_data(self, obj):
        """Helper method to serialize objects with datetime handling"""
        if hasattr(obj, 'dict'):
            data = obj.dict()
        elif hasattr(obj, '__dict__'):
            data = obj.__dict__
        else:
            return str(obj)
        
        # Convert datetime objects to ISO format strings
        def convert_datetime(item):
            if isinstance(item, datetime):
                return item.isoformat()
            elif isinstance(item, date):
                return item.isoformat()
            elif isinstance(item, datetime_time):
                return item.isoformat()
            elif isinstance(item, dict):
                return {k: convert_datetime(v) for k, v in item.items()}
            elif isinstance(item, list):
                return [convert_datetime(v) for v in item]
            else:
                return item
        
        return convert_datetime(data)

    def log_input_data(self, user_context, user_memory, memory_context):
        """Log input data (user profile and memory context) to input.txt in JSON format"""
        try:
            # Prepare input data for logging
            input_data = {
                "timestamp": datetime.now().isoformat(),
                "profile_id": self.profile_id,
                "user_profile": {
                    "date_range": {
                        "start_date": user_context.date_range['start_date'].isoformat() if user_context.date_range.get('start_date') else None,
                        "end_date": user_context.date_range['end_date'].isoformat() if user_context.date_range.get('end_date') else None,
                        "days": user_context.date_range.get('days')
                    },
                    "data_summary": {
                        "scores_count": len(user_context.scores),
                        "archetypes_count": len(user_context.archetypes),
                        "biomarkers_count": len(user_context.biomarkers)
                    },
                    "scores": [self.serialize_data(score) for score in user_context.scores],
                    "archetypes": [self.serialize_data(archetype) for archetype in user_context.archetypes],
                    "biomarkers": [self.serialize_data(biomarker) for biomarker in user_context.biomarkers]
                },
                "memory_context": {
                    "has_memory": user_memory is not None,
                    "total_analyses": user_memory.total_analyses if user_memory else 0,
                    "last_analysis_date": user_memory.last_analysis_date.isoformat() if user_memory and user_memory.last_analysis_date else None,
                    "user_preferences": user_memory.user_preferences if user_memory else {},
                    "health_goals": user_memory.health_goals if user_memory else {},
                    "dietary_restrictions": user_memory.dietary_restrictions if user_memory else {},
                    "lifestyle_context": user_memory.lifestyle_context if user_memory else {},
                    "medical_conditions": user_memory.medical_conditions if user_memory else {},
                    "formatted_context": memory_context
                }
            }
            
            # Append to input.txt file
            with open("input.txt", "a", encoding="utf-8") as f:
                f.write(json.dumps(input_data, indent=2, ensure_ascii=False, default=str) + "\n" + "="*80 + "\n")
            
            console.print("[dim]📝 Input data logged to input.txt[/dim]")
            
        except Exception as e:
            console.print(f"[red]⚠️ Error logging input data: {str(e)}[/red]")

    def log_output_data(self, analysis_result, behavior_analysis=None, nutrition_plan=None, routine_plan=None):
        """Log output data (analysis, behavior analysis, nutrition plan, routine plan) to output.txt in JSON format"""
        try:
            # Prepare output data for logging
            output_data = {
                "timestamp": datetime.now().isoformat(),
                "profile_id": self.profile_id,
                "metric_analysis": analysis_result,
                "behavior_analysis": None,
                "nutrition_plan": None,
                "routine_plan": None
            }
            
            # Add behavior analysis if available
            if behavior_analysis:
                try:
                    output_data["behavior_analysis"] = self.serialize_data(behavior_analysis)
                except Exception as e:
                    output_data["behavior_analysis"] = f"Error serializing behavior analysis: {str(e)}"
            
            # Add nutrition plan if available
            if nutrition_plan:
                try:
                    output_data["nutrition_plan"] = self.serialize_data(nutrition_plan)
                except Exception as e:
                    output_data["nutrition_plan"] = f"Error serializing nutrition plan: {str(e)}"
            
            # Add routine plan if available
            if routine_plan:
                try:
                    output_data["routine_plan"] = self.serialize_data(routine_plan)
                except Exception as e:
                    output_data["routine_plan"] = f"Error serializing routine plan: {str(e)}"
            
            # Append to output.txt file
            with open("output.txt", "a", encoding="utf-8") as f:
                f.write(json.dumps(output_data, indent=2, ensure_ascii=False, default=str) + "\n" + "="*80 + "\n")
            
            console.print("[dim]📝 Output data logged to output.txt[/dim]")
            
        except Exception as e:
            console.print(f"[red]⚠️ Error logging output data: {str(e)}[/red]")

    def display_routine_plan(self, routine_result: RoutinePlanResult):
        """Display structured routine plan data"""
        try:
            tree = Tree(f"📅 🏃‍♀️ Personalized Routine Plan")
            
            # Add date and summary
            day_tree = tree.add(f"[bold cyan]{routine_result.date}[/bold cyan]")
            day_tree.add(f"[yellow]📝 Summary:[/yellow] {routine_result.routine.summary}")
            
            # Add each time block
            time_blocks = [
                ("Morning Wake-up", routine_result.routine.morning_wakeup),
                ("Focus Block", routine_result.routine.focus_block),
                ("Afternoon Recharge", routine_result.routine.afternoon_recharge),
                ("Evening Wind-down", routine_result.routine.evening_winddown)
            ]
            
            for block_name, block_data in time_blocks:
                block_tree = day_tree.add(f"[bold magenta]⏰ {block_name}[/bold magenta]")
                block_tree.add(f"🕐 [bold blue]{block_data.time_range}[/bold blue]")
                block_tree.add(f"[dim]💡 Why: {block_data.why_it_matters}[/dim]")
                
                for i, task in enumerate(block_data.tasks, 1):
                    task_tree = block_tree.add(f"[bold white]{i}. {task.task}[/bold white]")
                    task_tree.add(f"[dim italic]→ {task.reason}[/dim italic]")
            
            console.print(Panel(tree, title="🏃‍♀️ Personalized Routine Plan", border_style="magenta", padding=(1, 2)))
            
        except Exception as e:
            console.print(f"[red]Error displaying routine plan: {str(e)}[/red]")

    def display_nutrition_plan(self, nutrition_result: NutritionPlanResult):
        """Display structured detailed nutrition plan data"""
        try:
            tree = Tree(f"📅 🥗 Personalized Detailed Nutrition Plan")
            
            # Add date and summary
            day_tree = tree.add(f"[bold cyan]{nutrition_result.date}[/bold cyan]")
            day_tree.add(f"[yellow]📝 Summary:[/yellow] {nutrition_result.nutrition.summary}")
            
            # Add comprehensive nutritional targets
            nutrition_tree = day_tree.add("[green]🥗 Daily Nutritional Targets[/green]")
            info = nutrition_result.nutrition.nutritional_info
            nutrition_tree.add(f"• Calories: [bold]{info.calories}[/bold]")
            nutrition_tree.add(f"• Protein: [bold]{info.protein}g ({info.protein_percent}%)[/bold]")
            nutrition_tree.add(f"• Carbs: [bold]{info.carbs}g ({info.carbs_percent}%)[/bold]")
            nutrition_tree.add(f"• Fat: [bold]{info.fat}g ({info.fat_percent}%)[/bold]")
            nutrition_tree.add(f"• Fiber: [bold]{info.fiber}g[/bold]")
            nutrition_tree.add(f"• Sugar: [bold]{info.sugar}g[/bold]")
            nutrition_tree.add(f"• Sodium: [bold]{info.sodium}mg[/bold]")
            nutrition_tree.add(f"• Potassium: [bold]{info.potassium}mg[/bold]")
            
            # Add vitamins
            vitamins_tree = nutrition_tree.add("[magenta]💊 Key Vitamins & Minerals[/magenta]")
            vitamins_tree.add(f"• Vitamin D: [bold]{info.vitamins.Vitamin_D}[/bold]")
            vitamins_tree.add(f"• Calcium: [bold]{info.vitamins.Calcium}[/bold]")
            vitamins_tree.add(f"• Iron: [bold]{info.vitamins.Iron}[/bold]")
            vitamins_tree.add(f"• Magnesium: [bold]{info.vitamins.Magnesium}[/bold]")
            
            # Add each meal block (7 blocks)
            meal_blocks = [
                ("Early Morning", nutrition_result.nutrition.Early_Morning),
                ("Breakfast", nutrition_result.nutrition.Breakfast),
                ("Morning Snack", nutrition_result.nutrition.Morning_Snack),
                ("Lunch", nutrition_result.nutrition.Lunch),
                ("Afternoon Snack", nutrition_result.nutrition.Afternoon_Snack),
                ("Dinner", nutrition_result.nutrition.Dinner),
                ("Evening Snack", nutrition_result.nutrition.Evening_Snack)
            ]
            
            for meal_name, meal_data in meal_blocks:
                meal_tree = day_tree.add(f"[bold magenta]🍽️ {meal_name}[/bold magenta]")
                meal_tree.add(f"🕐 [bold blue]{meal_data.time_range}[/bold blue]")
                meal_tree.add(f"[dim]💡 Tip: {meal_data.nutrition_tip}[/dim]")
                
                # Add individual meals
                for i, meal in enumerate(meal_data.meals, 1):
                    meal_item_tree = meal_tree.add(f"[bold white]{i}. {meal.name}[/bold white]")
                    meal_item_tree.add(f"[green]📋 Details: {meal.details}[/green]")
                    meal_item_tree.add(f"[yellow]🔥 Calories: {meal.calories} | Protein: {meal.protein}g[/yellow]")
                    meal_item_tree.add(f"[cyan]📊 Macros: Carbs {meal.macros.carbs}g | Fat {meal.macros.fat}g[/cyan]")
            
            console.print(Panel(tree, title="🥗 Personalized Detailed Nutrition Plan", border_style="blue", padding=(1, 2)))
            
        except Exception as e:
            console.print(f"[red]Error displaying nutrition plan: {str(e)}[/red]")

    def display_behavior_analysis(self, behavior_result: BehaviorAnalysisResult):
        """Display structured behavior analysis data"""
        try:
            tree = Tree(f"📅 🧠 Behavioral Analysis Report")
            
            # Add date and user
            main_tree = tree.add(f"[bold cyan]{behavior_result.analysis_date} - User: {behavior_result.user_id}[/bold cyan]")
            
            # Behavioral Signature
            signature_tree = main_tree.add(f"[bold magenta]🎯 Behavioral Signature[/bold magenta]")
            signature_tree.add(f"[bold white]'{behavior_result.behavioral_signature.signature}'[/bold white]")
            signature_tree.add(f"[dim]Confidence: {behavior_result.behavioral_signature.confidence:.1%}[/dim]")
            
            # Sophistication Assessment
            sophistication_tree = main_tree.add(f"[bold green]📊 Sophistication Assessment[/bold green]")
            sophistication_tree.add(f"Score: [bold]{behavior_result.sophistication_assessment.score}/100[/bold] ([bold]{behavior_result.sophistication_assessment.category}[/bold])")
            sophistication_tree.add(f"[dim italic]{behavior_result.sophistication_assessment.justification}[/dim italic]")
            
            # Primary Goal
            goal_tree = main_tree.add(f"[bold blue]🎯 Primary Goal[/bold blue]")
            goal_tree.add(f"[bold white]{behavior_result.primary_goal.goal}[/bold white]")
            goal_tree.add(f"Timeline: [bold]{behavior_result.primary_goal.timeline}[/bold]")
            
            success_tree = goal_tree.add("[yellow]📈 Success Metrics[/yellow]")
            for metric in behavior_result.primary_goal.success_metrics:
                success_tree.add(f"• {metric}")
            
            # Adaptive Parameters
            adaptive_tree = main_tree.add(f"[bold purple]⚙️ Adaptive Parameters[/bold purple]")
            adaptive_tree.add(f"• Complexity: [bold]{behavior_result.adaptive_parameters.complexity_level}[/bold]")
            adaptive_tree.add(f"• Time Commitment: [bold]{behavior_result.adaptive_parameters.time_commitment}[/bold]")
            adaptive_tree.add(f"• Technology Integration: [bold]{behavior_result.adaptive_parameters.technology_integration}[/bold]")
            adaptive_tree.add(f"• Customization Level: [bold]{behavior_result.adaptive_parameters.customization_level}[/bold]")
            
            # Readiness & Stage
            status_tree = main_tree.add(f"[bold yellow]📋 Current Status[/bold yellow]")
            status_tree.add(f"Readiness Level: [bold]{behavior_result.readiness_level}[/bold]")
            status_tree.add(f"Habit Formation Stage: [bold]{behavior_result.habit_formation_stage}[/bold]")
            
            # Recommendations
            rec_tree = main_tree.add(f"[bold red]💡 Key Recommendations[/bold red]")
            for i, rec in enumerate(behavior_result.recommendations[:5], 1):  # Show top 5
                rec_tree.add(f"{i}. {rec}")
            
            console.print(Panel(tree, title="🧠 Behavioral Analysis Report", border_style="blue", padding=(1, 2)))
            
        except Exception as e:
            console.print(f"[red]Error displaying behavior analysis: {str(e)}[/red]")

    async def run_analysis(self, days: int = 7):
        """Complete health analysis workflow with nutrition and routine planning"""
        
        # Initialize variables to store results for logging
        analysis_result = None
        nutrition_plan = None
        routine_plan = None
        
        with trace("Health Analysis Workflow"):
            console.print(f"[bold cyan]🏥 Starting Comprehensive Health Analysis for Profile: {self.profile_id}[/bold cyan]")
            
            # Step 0: Initialize memory and retrieve user memory
            console.print("[cyan]🧠 Retrieving user memory and context...[/cyan]")
            try:
                await self.memory_manager.connect()
                user_memory = await self.memory_manager.get_user_memory(self.profile_id)
                
                if user_memory:
                    console.print(Panel(
                        f"[bold green]✅ Memory Retrieved Successfully[/bold green]\n"
                        f"[yellow]Previous Analyses:[/yellow] {user_memory.total_analyses}\n"
                        f"[yellow]Last Analysis:[/yellow] {user_memory.last_analysis_date}\n"
                        f"[yellow]Has Nutrition Plan:[/yellow] {'Yes' if user_memory.last_nutrition_plan else 'No'}\n"
                        f"[yellow]Has Routine Plan:[/yellow] {'Yes' if user_memory.last_routine_plan else 'No'}\n"
                        f"[yellow]User Preferences:[/yellow] {len(user_memory.user_preferences)} items\n"
                        f"[yellow]Health Goals:[/yellow] {len(user_memory.health_goals)} items",
                        title="🧠 User Memory Summary"
                    ))
                else:
                    console.print("[yellow]⚠️ No previous memory found. Creating new memory record...[/yellow]")
                    await self.memory_manager.create_user_memory(self.profile_id)
                    user_memory = await self.memory_manager.get_user_memory(self.profile_id)
                
            except Exception as e:
                console.print(f"[bold red]❌ Error retrieving user memory: {str(e)}[/bold red]")
                user_memory = None
            
            # Step 1: Fetch user profile data
            console.print("[cyan]📊 Fetching user health data...[/cyan]")
            try:
                user_context = await get_user_profile_context(self.profile_id, days=days)
                
                console.print(Panel(
                    f"[bold green]✅ Data Retrieved Successfully[/bold green]\n"
                    f"[yellow]Time Period:[/yellow] {user_context.date_range['start_date']} to {user_context.date_range['end_date']}\n"
                    f"[yellow]Duration:[/yellow] {days} days\n"
                    f"[yellow]Data Summary:[/yellow]\n"
                    f"  • Scores: {len(user_context.scores)} records\n"
                    f"  • Archetypes: {len(user_context.archetypes)} records\n"
                    f"  • Biomarkers: {len(user_context.biomarkers)} records",
                    title="📊 Health Data Summary"
                ))
                
            except Exception as e:
                console.print(f"[bold red]❌ Error fetching user data: {str(e)}[/bold red]")
                return
            
            # Log input data (user profile and memory context)
            console.print("[cyan]📝 Logging input data...[/cyan]")
            try:
                # Format memory context for analysis
                memory_context = ""
                if user_memory:
                    memory_context = self.memory_manager.format_memory_context(user_memory)
                    console.print("[dim]📝 Including previous memory context...[/dim]")
                
                # Log input data before analysis
                self.log_input_data(user_context, user_memory, memory_context)
                
            except Exception as e:
                console.print(f"[red]⚠️ Error logging input data: {str(e)}[/red]")
                memory_context = ""

            # Step 2: Run health metrics analysis with memory context
            console.print("[cyan]🤖 Running AI-powered health metrics analysis...[/cyan]")
            try:
                with console.status("[bold cyan]Analyzing health metrics with AI...") as status:
                    analysis_result = await analyze_user_health_metrics(user_context, memory_context)
                
                console.print("[bold green]✅ Health analysis complete![/bold green]\n")
                
                # Display the analysis results
                console.print(Panel(
                    Markdown(analysis_result),
                    title="🏥 Health Analysis Report",
                    border_style="green"
                ))
                
                # Store analysis result for later logging
                
                # Update memory with analysis result
                if user_memory:
                    # Convert datetime objects to strings for JSON serialization
                    analysis_insights = {
                        "analysis_date_range": {
                            "start_date": user_context.date_range['start_date'].isoformat(),
                            "end_date": user_context.date_range['end_date'].isoformat(),
                            "days": user_context.date_range['days']
                        },
                        "data_summary": {
                            "scores_count": len(user_context.scores),
                            "archetypes_count": len(user_context.archetypes),
                            "biomarkers_count": len(user_context.biomarkers)
                        }
                    }
                    
                    await self.memory_manager.update_analysis_result(
                        self.profile_id, 
                        analysis_result,
                        analysis_insights
                    )
                    console.print("[dim]💾 Analysis results saved to memory...[/dim]")
                
            except Exception as e:
                console.print(f"[bold red]❌ Error during health analysis: {str(e)}[/bold red]")
                return
            
            # Step 3: Run comprehensive behavior analysis
            console.print("[cyan]🧠 Running comprehensive behavior analysis...[/cyan]")
            behavior_analysis = None
            try:
                with console.status("[bold cyan]Analyzing behavioral patterns with AI...") as status:
                    behavior_analysis = await analyze_user_behavior(user_context, memory_context)
                
                console.print("[bold green]✅ Behavior analysis complete![/bold green]\n")
                
                # Display the behavior analysis results
                self.display_behavior_analysis(behavior_analysis)
                
                # Update memory with behavior analysis result
                if user_memory:
                    await self.memory_manager.update_behavior_analysis(self.profile_id, behavior_analysis)
                    console.print("[dim]💾 Behavior analysis saved to memory...[/dim]")
                
            except Exception as e:
                console.print(f"[bold red]❌ Error during behavior analysis: {str(e)}[/bold red]")
                behavior_analysis = None
            
            # Step 4: Create personalized nutrition plan
            console.print("[cyan]🥗 Creating personalized nutrition plan...[/cyan]")
            try:
                with console.status("[bold cyan]Generating nutrition recommendations...") as status:
                    nutrition_plan = await create_personalized_nutrition_plan(analysis_result)
                
                console.print("[bold green]✅ Nutrition plan created![/bold green]\n")
                
                # Display the nutrition plan
                self.display_nutrition_plan(nutrition_plan)
                
                # Update memory with nutrition plan
                if user_memory:
                    await self.memory_manager.update_nutrition_plan(self.profile_id, nutrition_plan)
                    console.print("[dim]💾 Nutrition plan saved to memory...[/dim]")
                
            except Exception as e:
                console.print(f"[bold red]❌ Error creating nutrition plan: {str(e)}[/bold red]")
                nutrition_plan = None
            
            # Step 5: Create personalized routine plan (with behavior analysis integration)
            console.print("[cyan]🏃‍♀️ Creating personalized routine plan with behavioral insights...[/cyan]")
            try:
                with console.status("[bold cyan]Generating behaviorally-informed routine recommendations...") as status:
                    routine_plan = await create_personalized_routine_plan(analysis_result, behavior_analysis)
                
                console.print("[bold green]✅ Behaviorally-informed routine plan created![/bold green]\n")
                
                # Display the routine plan
                self.display_routine_plan(routine_plan)
                
                # Update memory with routine plan
                if user_memory:
                    await self.memory_manager.update_routine_plan(self.profile_id, routine_plan)
                    console.print("[dim]💾 Routine plan saved to memory...[/dim]")
                
            except Exception as e:
                console.print(f"[bold red]❌ Error creating routine plan: {str(e)}[/bold red]")
                routine_plan = None
            
            # Log complete output data (analysis + behavior analysis + nutrition plan + routine plan)
            console.print("[cyan]📝 Logging complete output data...[/cyan]")
            try:
                self.log_output_data(analysis_result, behavior_analysis, nutrition_plan, routine_plan)
            except Exception as e:
                console.print(f"[red]⚠️ Error logging output data: {str(e)}[/red]")
            
            # Final summary
            console.print("\n" + "="*80)
            console.print("[bold green]🎉 COMPREHENSIVE HEALTH ANALYSIS COMPLETE! 🎉[/bold green]")
            console.print("="*80)
            console.print(f"[cyan]✅ Health metrics analyzed for profile: {self.profile_id}[/cyan]")
            console.print(f"[cyan]✅ Comprehensive behavior analysis completed (Structured Output)[/cyan]")
            console.print(f"[cyan]✅ Personalized nutrition plan generated (Structured Output)[/cyan]")
            console.print(f"[cyan]✅ Behaviorally-informed routine plan generated (Structured Output)[/cyan]")
            console.print(f"[cyan]✅ User memory updated with latest results[/cyan]")
            console.print(f"[dim]Analysis period: {user_context.date_range['start_date']} to {user_context.date_range['end_date']}[/dim]")
            console.print("="*80)
            
            # Cleanup
            try:
                await self.memory_manager.disconnect()
            except Exception as e:
                console.print(f"[dim]⚠️ Warning: Error disconnecting from database: {str(e)}[/dim]")