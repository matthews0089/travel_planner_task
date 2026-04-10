from pydantic import BaseModel, field_validator
from datetime import date
from typing import List, Optional


class PlaceBase(BaseModel):
    external_id: int
    notes: Optional[str] = None

class PlaceCreate(PlaceBase):
    pass

class PlaceUpdate(BaseModel):
    notes: Optional[str] = None
    is_visited: Optional[bool] = None

class PlaceResponse(PlaceBase):
    id: int
    project_id: int
    is_visited: bool

    class Config:
        from_attributes = True 


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: Optional[date] = None

class ProjectCreate(ProjectBase):
    places: List[PlaceCreate] = []

    @field_validator('places')
    @classmethod
    def validate_places(cls, places):
        if len(places) > 10:
            raise ValueError("A project can have a maximum of 10 places.")
        
        external_ids = [p.external_id for p in places]
        if len(external_ids) != len(set(external_ids)):
            raise ValueError("Duplicate places are not allowed in the same project.")
        
        return places

class ProjectUpdate(ProjectBase):
    name: Optional[str] = None

class ProjectResponse(ProjectBase):
    id: int
    is_completed: bool
    places: List[PlaceResponse] = []

    class Config:
        from_attributes = True