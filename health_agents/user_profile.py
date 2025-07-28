from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from dataclasses import dataclass
import os
import asyncpg
import json

# Pydantic models for data structure
class ScoreData(BaseModel):
    id: str
    profile_id: str
    type: str
    score: float
    data: Dict[str, Any]
    score_date_time: str  # Changed to str since it's text in DB
    created_at: datetime
    updated_at: datetime

class ArchetypeData(BaseModel):
    id: str
    profile_id: str
    name: str
    periodicity: str
    value: str
    data: Dict[str, Any]
    start_date_time: datetime
    end_date_time: datetime
    created_at: datetime
    updated_at: datetime

class BiomarkerData(BaseModel):
    id: str
    profile_id: str
    category: str
    type: str
    data: Dict[str, Any]
    start_date_time: datetime
    end_date_time: datetime
    created_at: datetime
    updated_at: datetime

class UserProfileContext(BaseModel):
    user_id: str
    scores: List[ScoreData]
    archetypes: List[ArchetypeData]
    biomarkers: List[BiomarkerData]
    date_range: Dict[str, datetime]

@dataclass
class UserProfileService:
    """Service class to handle user profile data fetching and structuring"""
    
    def __init__(self):
        # Initialize PostgreSQL connection
        self.database_url = os.getenv("DATABASE_URL")
        
        if not self.database_url:
            raise ValueError("Missing DATABASE_URL in environment variables")
    
    async def get_db_connection(self):
        """Get database connection"""
        # Disable prepared statements for pgbouncer compatibility
        return await asyncpg.connect(self.database_url, statement_cache_size=0)
        
    def get_date_range(self, days: int = 7) -> tuple[datetime, datetime]:
        """Get date range for the last N days"""
        # Based on actual data analysis:
        # - Scores: 2025-06-27 to 2025-07-07 (created_at)
        # - Archetypes: 2025-06-01 to 2025-06-30
        # - Biomarkers: 2025-06-12 to 2025-07-07
        # Using latest available date as end_date
        end_date = datetime(2025, 7, 7, 22, 50, 11)  # Latest score timestamp
        start_date = end_date - timedelta(days=days)
        return start_date, end_date
    
    def datetime_to_string(self, dt: datetime) -> str:
        """Convert datetime to string format for SQL queries"""
        return dt.isoformat()
    
    def parse_score_date_time(self, score_date_str: str) -> datetime:
        """Parse score_date_time string to datetime object for comparison"""
        try:
            # Handle different possible formats
            if 'T' in score_date_str:
                return datetime.fromisoformat(score_date_str.replace('Z', '+00:00'))
            else:
                return datetime.strptime(score_date_str, '%Y-%m-%d %H:%M:%S')
        except Exception as e:
            print(f"Error parsing date string {score_date_str}: {e}")
            return datetime.now()
    
    async def fetch_scores_data(self, profile_id: str, days: int = 7) -> List[ScoreData]:
        """Fetch scores data for the last N days"""
        start_date, end_date = self.get_date_range(days)
        
        try:
            conn = await self.get_db_connection()
            
            # Use created_at for filtering since score_date_time is unreliable (has old dates and nulls)
            query = """
                SELECT id, profile_id, type, score, data, score_date_time, created_at, updated_at
                FROM scores 
                WHERE profile_id = $1 
                AND created_at >= $2 
                AND created_at <= $3
                ORDER BY created_at DESC
            """
            
            # Pass datetime objects directly (AsyncPG expects datetime, not strings)
            rows = await conn.fetch(query, profile_id, start_date, end_date)
            await conn.close()
            
            scores = []
            for row in rows:
                try:
                    # Parse JSON string to dictionary
                    data_dict = json.loads(row['data']) if isinstance(row['data'], str) else row['data']
                    
                    # Handle score_date_time as text (can be null or unreliable)
                    score_date_time = row['score_date_time'] if row['score_date_time'] else ""
                    
                    scores.append(ScoreData(
                        id=str(row['id']),
                        profile_id=row['profile_id'],
                        type=row['type'],
                        score=float(row['score']),
                        data=data_dict,
                        score_date_time=score_date_time,
                        created_at=row['created_at'],
                        updated_at=row['updated_at']
                    ))
                except Exception as row_error:
                    print(f"Error processing score row: {row_error}")
                    continue
            
            return scores
            
        except Exception as e:
            print(f"Error fetching scores data: {e}")
            return []
    
    async def fetch_archetypes_data(self, profile_id: str, days: int = 7) -> List[ArchetypeData]:
        """Fetch archetypes data for the last N days"""
        # For archetypes, we need to adjust the date range since they end on 2025-06-30
        # but our default range starts from 2025-06-30 (7 days before 2025-07-07)
        start_date, end_date = self.get_date_range(days)
        
        # Adjust end date for archetypes since they only go to 2025-06-30
        archetype_end_date = min(end_date, datetime(2025, 6, 30, 23, 59, 59))
        
        try:
            conn = await self.get_db_connection()
            
            query = """
                SELECT id, profile_id, name, periodicity, value, data, start_date_time, end_date_time, created_at, updated_at
                FROM archetypes 
                WHERE profile_id = $1 
                AND start_date_time >= $2 
                AND start_date_time <= $3
                ORDER BY start_date_time DESC
            """
            
            # Pass datetime objects directly (AsyncPG expects datetime, not strings)
            rows = await conn.fetch(query, profile_id, start_date, archetype_end_date)
            await conn.close()
            
            archetypes = []
            for row in rows:
                try:
                    # Parse JSON string to dictionary
                    data_dict = json.loads(row['data']) if isinstance(row['data'], str) else row['data']
                    
                    archetypes.append(ArchetypeData(
                        id=str(row['id']),
                        profile_id=row['profile_id'],
                        name=row['name'],
                        periodicity=row['periodicity'],
                        value=row['value'],
                        data=data_dict,
                        start_date_time=row['start_date_time'],
                        end_date_time=row['end_date_time'],
                        created_at=row['created_at'],
                        updated_at=row['updated_at']
                    ))
                except Exception as row_error:
                    print(f"Error processing archetype row: {row_error}")
                    continue
            
            return archetypes
            
        except Exception as e:
            print(f"Error fetching archetypes data: {e}")
            return []
    
    async def fetch_biomarkers_data(self, profile_id: str, days: int = 7) -> List[BiomarkerData]:
        """Fetch biomarkers data for the last N days"""
        start_date, end_date = self.get_date_range(days)
        
        try:
            conn = await self.get_db_connection()
            
            query = """
                SELECT id, profile_id, category, type, data, start_date_time, end_date_time, created_at, updated_at
                FROM biomarkers 
                WHERE profile_id = $1 
                AND start_date_time >= $2 
                AND start_date_time <= $3
                ORDER BY start_date_time DESC
            """
            
            # Pass datetime objects directly (AsyncPG expects datetime, not strings)
            rows = await conn.fetch(query, profile_id, start_date, end_date)
            await conn.close()
            
            biomarkers = []
            for row in rows:
                try:
                    # Parse JSON string to dictionary
                    data_dict = json.loads(row['data']) if isinstance(row['data'], str) else row['data']
                    
                    biomarkers.append(BiomarkerData(
                        id=str(row['id']),
                        profile_id=row['profile_id'],
                        category=row['category'],
                        type=row['type'],
                        data=data_dict,
                        start_date_time=row['start_date_time'],
                        end_date_time=row['end_date_time'],
                        created_at=row['created_at'],
                        updated_at=row['updated_at']
                    ))
                except Exception as row_error:
                    print(f"Error processing biomarker row: {row_error}")
                    continue
            
            return biomarkers
            
        except Exception as e:
            print(f"Error fetching biomarkers data: {e}")
            return []
    

    
    async def get_user_profile_context(self, profile_id: str, days: int = 7) -> UserProfileContext:
        """Main method to fetch and structure all user profile data"""
        
        # Fetch data from all tables
        scores = await self.fetch_scores_data(profile_id, days)
        archetypes = await self.fetch_archetypes_data(profile_id, days)
        biomarkers = await self.fetch_biomarkers_data(profile_id, days)
        
        # Create date range info
        start_date, end_date = self.get_date_range(days)
        date_range = {
            "start_date": start_date,
            "end_date": end_date,
            "days": days
        }
        
        return UserProfileContext(
            user_id=profile_id,
            scores=scores,
            archetypes=archetypes,
            biomarkers=biomarkers,
            date_range=date_range
        )



# Utility function to get user profile context
async def get_user_profile_context(profile_id: str, days: int = 7) -> UserProfileContext:
    """Utility function to get user profile context for use with agents"""
    service = UserProfileService()
    return await service.get_user_profile_context(profile_id, days)
