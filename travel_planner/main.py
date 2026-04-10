from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
import httpx
from typing import List

import models, schemas, database
from database import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Travel Planner API")

API_CACHE = {}

async def validate_place_external(external_id: int) -> bool:
    """Checks whether a location exists in the Art Institute of Chicago API and caches the result to minimize API calls."""
    if external_id in API_CACHE:
        return API_CACHE[external_id]
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.artic.edu/api/v1/artworks/{external_id}")
        exists = response.status_code == 200
        API_CACHE[external_id] = exists  
        return exists


@app.post("/projects/", response_model=schemas.ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(project: schemas.ProjectCreate, db: Session = Depends(database.get_db)):
    for place in project.places:
        is_valid = await validate_place_external(place.external_id)
        if not is_valid:
            raise HTTPException(
                status_code=400, 
                detail=f"Place with external_id {place.external_id} does not exist in the Art Institute API."
            )

    db_project = models.Project(
        name=project.name, 
        description=project.description, 
        start_date=project.start_date
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    for place in project.places:
        db_place = models.Place(project_id=db_project.id, external_id=place.external_id, notes=place.notes)
        db.add(db_place)
    
    db.commit()
    db.refresh(db_project)
    return db_project

@app.get("/projects/", response_model=List[schemas.ProjectResponse])
def list_projects(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    projects = db.query(models.Project).offset(skip).limit(limit).all()
    return projects

@app.get("/projects/{project_id}", response_model=schemas.ProjectResponse)
def get_project(project_id: int, db: Session = Depends(database.get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@app.put("/projects/{project_id}", response_model=schemas.ProjectResponse)
def update_project(project_id: int, project_update: schemas.ProjectUpdate, db: Session = Depends(database.get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    update_data = project_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)
    
    db.commit()
    db.refresh(project)
    return project

@app.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(database.get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if any(place.is_visited for place in project.places):
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete project: One or more places are already marked as visited."
        )
    
    db.delete(project)
    db.commit()



@app.post("/projects/{project_id}/places/", response_model=schemas.PlaceResponse, status_code=status.HTTP_201_CREATED)
async def add_place_to_project(project_id: int, place: schemas.PlaceCreate, db: Session = Depends(database.get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if len(project.places) >= 10:
        raise HTTPException(status_code=400, detail="A project can have a maximum of 10 places.")
    
    if any(p.external_id == place.external_id for p in project.places):
        raise HTTPException(status_code=400, detail="This place is already in the project.")

    is_valid = await validate_place_external(place.external_id)
    if not is_valid:
        raise HTTPException(status_code=400, detail="Place does not exist in the Art Institute API.")

    db_place = models.Place(project_id=project_id, external_id=place.external_id, notes=place.notes)
    db.add(db_place)
    db.commit()
    db.refresh(db_place)
    return db_place

@app.get("/projects/{project_id}/places/", response_model=List[schemas.PlaceResponse])
def list_places(project_id: int, db: Session = Depends(database.get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project.places

@app.get("/projects/{project_id}/places/{place_id}", response_model=schemas.PlaceResponse)
def get_place(project_id: int, place_id: int, db: Session = Depends(database.get_db)):
    place = db.query(models.Place).filter(models.Place.id == place_id, models.Place.project_id == project_id).first()
    if not place:
        raise HTTPException(status_code=404, detail="Place not found in this project")
    return place

@app.put("/projects/{project_id}/places/{place_id}", response_model=schemas.PlaceResponse)
def update_place(project_id: int, place_id: int, place_update: schemas.PlaceUpdate, db: Session = Depends(database.get_db)):
    place = db.query(models.Place).filter(models.Place.id == place_id, models.Place.project_id == project_id).first()
    if not place:
        raise HTTPException(status_code=404, detail="Place not found in this project")
    
    update_data = place_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(place, key, value)
    
    db.commit()
    db.refresh(place)
    return place