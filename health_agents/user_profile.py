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
    score_date_time: datetime
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
        return await asyncpg.connect(self.database_url)
        
    def get_date_range(self, days: int = 7) -> tuple[datetime, datetime]:
        """Get date range for the last N days"""
        # Fixed date: 2025-05-19 04:00:00+00
        end_date = datetime(2025, 5, 19, 4, 0, 0)
        start_date = end_date - timedelta(days=days)
        return start_date, end_date
    
    async def fetch_scores_data(self, profile_id: str, days: int = 7) -> List[ScoreData]:
        """Fetch scores data for the last N days"""
        start_date, end_date = self.get_date_range(days)
        
        try:
            conn = await self.get_db_connection()
            
            query = """
                SELECT id, profile_id, type, score, data, score_date_time, created_at, updated_at
                FROM scores 
                WHERE profile_id = $1 
                AND score_date_time >= $2 
                AND score_date_time <= $3
                ORDER BY score_date_time DESC
            """
            
            rows = await conn.fetch(query, profile_id, start_date, end_date)
            await conn.close()
            
            scores = []
            for row in rows:
                # Parse JSON string to dictionary
                data_dict = json.loads(row['data']) if isinstance(row['data'], str) else row['data']
                
                scores.append(ScoreData(
                    id=str(row['id']),
                    profile_id=row['profile_id'],
                    type=row['type'],
                    score=float(row['score']),
                    data=data_dict,
                    score_date_time=row['score_date_time'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                ))
            
            return scores
            
        except Exception as e:
            print(f"Error fetching scores data: {e}")
            return []
    
    async def fetch_archetypes_data(self, profile_id: str, days: int = 7) -> List[ArchetypeData]:
        """Fetch archetypes data for the last N days"""
        start_date, end_date = self.get_date_range(days)
        
        try:
            conn = await self.get_db_connection()
            
            query = """
                SELECT id, profile_id, name, periodicity, value, data, start_date_time, end_date_time, created_at, updated_at
                FROM archetypes 
                WHERE profile_id = $1 
                AND start_date_time >= $2 
                AND end_date_time <= $3
                ORDER BY start_date_time DESC
            """
            
            rows = await conn.fetch(query, profile_id, start_date, end_date)
            await conn.close()
            
            archetypes = []
            for row in rows:
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
                AND end_date_time <= $3
                ORDER BY start_date_time DESC
            """
            
            rows = await conn.fetch(query, profile_id, start_date, end_date)
            await conn.close()
            
            biomarkers = []
            for row in rows:
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
