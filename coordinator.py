import time
import json
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

console = Console()

class HealthCoordinator:
    def __init__(self, profile_id: str):
        self.profile_id = profile_id

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

    async def run_analysis(self, days: int = 7):
        """Complete health analysis workflow with nutrition and routine planning"""
        
        with trace("Health Analysis Workflow"):
            console.print(f"[bold cyan]🏥 Starting Comprehensive Health Analysis for Profile: {self.profile_id}[/bold cyan]")
            
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
            
            # Step 2: Run health metrics analysis
            console.print("[cyan]🤖 Running AI-powered health metrics analysis...[/cyan]")
            try:
                with console.status("[bold cyan]Analyzing health metrics with AI...") as status:
                    analysis_result = await analyze_user_health_metrics(user_context)
                
                console.print("[bold green]✅ Health analysis complete![/bold green]\n")
                
                # Display the analysis results
                console.print(Panel(
                    Markdown(analysis_result),
                    title="🏥 Health Analysis Report",
                    border_style="green"
                ))
                
            except Exception as e:
                console.print(f"[bold red]❌ Error during health analysis: {str(e)}[/bold red]")
                return
            
            # Step 3: Create personalized nutrition plan
            console.print("[cyan]🥗 Creating personalized nutrition plan...[/cyan]")
            try:
                with console.status("[bold cyan]Generating nutrition recommendations...") as status:
                    nutrition_plan = await create_personalized_nutrition_plan(analysis_result)
                
                console.print("[bold green]✅ Nutrition plan created![/bold green]\n")
                
                # Display the nutrition plan
                self.display_nutrition_plan(nutrition_plan)
                
            except Exception as e:
                console.print(f"[bold red]❌ Error creating nutrition plan: {str(e)}[/bold red]")
            
            # Step 4: Create personalized routine plan
            console.print("[cyan]🏃‍♀️ Creating personalized routine plan...[/cyan]")
            try:
                with console.status("[bold cyan]Generating routine recommendations...") as status:
                    routine_plan = await create_personalized_routine_plan(analysis_result)
                
                console.print("[bold green]✅ Routine plan created![/bold green]\n")
                
                # Display the routine plan
                self.display_routine_plan(routine_plan)
                
            except Exception as e:
                console.print(f"[bold red]❌ Error creating routine plan: {str(e)}[/bold red]")
            
            # Final summary
            console.print("\n" + "="*80)
            console.print("[bold green]🎉 COMPREHENSIVE HEALTH ANALYSIS COMPLETE! 🎉[/bold green]")
            console.print("="*80)
            console.print(f"[cyan]✅ Health metrics analyzed for profile: {self.profile_id}[/cyan]")
            console.print(f"[cyan]✅ Personalized nutrition plan generated (Structured Output)[/cyan]")
            console.print(f"[cyan]✅ Personalized routine plan generated (Structured Output)[/cyan]")
            console.print(f"[dim]Analysis period: {user_context.date_range['start_date']} to {user_context.date_range['end_date']}[/dim]")
            console.print("="*80)