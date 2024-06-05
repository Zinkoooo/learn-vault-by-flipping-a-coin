from pathlib import Path
from fastapi import FastAPI, Depends, Request
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .database import SessionLocal, engine
from . import models
from .config import general_settings

models.Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(
    title="Flip A Coin",
    description="Basic API used by example in Vault learning course. Project for University of Picardie (Amiens, France) - Master's Degree."
)

BASE_DIR = Path(__file__).resolve().parent
app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static"
)
templates = Jinja2Templates(directory=BASE_DIR / "templates")

@app.get("/livez")
def alive():
    return("I'm alive!")

def init_score(score: models.Score | None, db: Session):
    if score is None:
        score = models.Score(heads=0, tails=0)
        db.add(score)
        db.commit()
        db.refresh(score)
        return score

@app.get("/", response_class=HTMLResponse)
def homepage(request: Request, db: Session = Depends(get_db)):
    score = db.query(models.Score).first()
    init_score(score=score, db=db)

    return templates.TemplateResponse(
        request=request, name="index.html", context={
                                                "heads_count": score.heads,
                                                "tails_count": score.tails
                                            }
    )

@app.get("/tails")
def get_tails(db: Session = Depends(get_db)):
    score = db.query(models.Score).first()
    init_score(score=score, db=db)
    return score.tails

@app.post("/tails")
def increment_tails(db: Session = Depends(get_db)):
    score = db.query(models.Score).first()
    init_score(score=score, db=db)
    score.tails += 1
    db.commit()
    db.refresh(score)
    return score.tails

@app.get("/heads")
def get_heads(db: Session = Depends(get_db)):
    score = db.query(models.Score).first()
    init_score(score=score, db=db)
    return score.heads

@app.post("/heads")
def increment_heads(db: Session = Depends(get_db)):
    score = db.query(models.Score).first()
    init_score(score=score, db=db)
    score.heads += 1
    db.commit()
    db.refresh(score)
    return score.heads

@app.post("/reset")
def reset_score(db: Session = Depends(get_db)):
    score = db.query(models.Score).first()
    if score is None:
      init_score(score=score, db=db)
    else:
      score.heads = 0
      score.tails = 0
      db.commit()
      db.refresh(score)
    return score

@app.get("/secret")
def display_secret(db: Session = Depends(get_db)):
    return general_settings.secret_value
