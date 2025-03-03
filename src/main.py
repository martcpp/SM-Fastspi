# filepath: /C:/Users/Dell/Desktop/smfastapi/SM-Fastspi/src/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from jose import JWTError, jwt
import models, schemas, auth, database, config
from database import SessionLocal, engine , get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# @app.get("/")
# def read_root():
#     return {"Hello": "World"}

# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: str = None):
#     return {"item_id": item_id, "q": q}

# @app.post("/users/", response_model=schemas.User)
# def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
#     db_user = models.User(name=user.name, email=user.email)
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user


@app.post("/users/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = models.User(
        name=user.name, email=user.email, password=auth.get_password_hash(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/users/login", response_model=schemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    refresh_token = auth.create_refresh_token(data={"sub": user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
    }


@app.post("/users/reset-password")
def reset_password(email: str, new_password: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.password = auth.get_password_hash(new_password)
    db.commit()
    return {"message": "Password reset successful"}


@app.delete("/users/deactivate/{username}")
def deactivate_user(username: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.name == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deactivated"}


@app.post("/users/token/refresh", response_model=schemas.Token)
def refresh_access_token(refresh_token: str, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            refresh_token, config.SECRET_KEY, algorithms=[config.ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
    }


@app.get("/users/me", response_model=schemas.User)
def read_users_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user


@app.get("/magazines/")
def get_magazines(db: Session = Depends(get_db)):
    magazines = db.query(models.Magazine).all()
    return magazines


@app.post("/magazines/", response_model=schemas.Magazine)
def create_magazine(magazine: schemas.MagazineCreate, db: Session = Depends(get_db)):
    new_magazine = models.Magazine(**magazine.dict())
    db.add(new_magazine)
    db.commit()
    db.refresh(new_magazine)
    return new_magazine


@app.get("/magazines/{magazine_id}", response_model=schemas.Magazine)
def get_magazine(magazine_id: int, db: Session = Depends(get_db)):
    magazine = (
        db.query(models.Magazine).filter(models.Magazine.id == magazine_id).first()
    )
    if not magazine:
        raise HTTPException(status_code=404, detail="Magazine not found")
    return magazine


@app.put("/magazines/{magazine_id}", response_model=schemas.Magazine)
def update_magazine(
    magazine_id: int, magazine: schemas.MagazineCreate, db: Session = Depends(get_db)
):
    db_magazine = (
        db.query(models.Magazine).filter(models.Magazine.id == magazine_id).first()
    )
    if not db_magazine:
        raise HTTPException(status_code=404, detail="Magazine not found")
    for key, value in magazine.dict().items():
        setattr(db_magazine, key, value)
    db.commit()
    db.refresh(db_magazine)
    return db_magazine


@app.delete("/magazines/{magazine_id}")
def delete_magazine(magazine_id: int, db: Session = Depends(get_db)):
    magazine = (
        db.query(models.Magazine).filter(models.Magazine.id == magazine_id).first()
    )
    if not magazine:
        raise HTTPException(status_code=404, detail="Magazine not found")
    db.delete(magazine)
    db.commit()
    return {"message": "Magazine deleted"}


@app.get("/plans/")
def get_plans(db: Session = Depends(get_db)):
    plans = db.query(models.Plan).all()
    return plans


@app.post("/plans/", response_model=schemas.Plan)
def create_plan(plan: schemas.PlanCreate, db: Session = Depends(get_db)):
    new_plan = models.Plan(**plan.dict())
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)
    return new_plan


@app.get("/plans/{plan_id}", response_model=schemas.Plan)
def get_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(models.Plan).filter(models.Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan


@app.put("/plans/{plan_id}", response_model=schemas.Plan)
def update_plan(plan_id: int, plan: schemas.PlanCreate, db: Session = Depends(get_db)):
    db_plan = db.query(models.Plan).filter(models.Plan.id == plan_id).first()
    if not db_plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    for key, value in plan.dict().items():
        setattr(db_plan, key, value)
    db.commit()
    db.refresh(db_plan)
    return db_plan


@app.delete("/plans/{plan_id}")
def delete_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(models.Plan).filter(models.Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    db.delete(plan)
    db.commit()
    return {"message": "Plan deleted"}


@app.get("/subscriptions/")
def get_subscriptions(db: Session = Depends(get_db)):
    subscriptions = db.query(models.Subscription).all()
    return subscriptions


@app.post("/subscriptions/", response_model=schemas.Subscription)
def create_subscription(
    subscription: schemas.SubscriptionCreate, db: Session = Depends(get_db)
):
    new_subscription = models.Subscription(**subscription.dict())
    db.add(new_subscription)
    db.commit()
    db.refresh(new_subscription)
    return new_subscription


@app.get("/subscriptions/{subscription_id}", response_model=schemas.Subscription)
def get_subscription(subscription_id: int, db: Session = Depends(get_db)):
    subscription = (
        db.query(models.Subscription)
        .filter(models.Subscription.id == subscription_id)
        .first()
    )
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return subscription


@app.put("/subscriptions/{subscription_id}", response_model=schemas.Subscription)
def update_subscription(
    subscription_id: int,
    subscription: schemas.SubscriptionCreate,
    db: Session = Depends(get_db),
):
    db_subscription = (
        db.query(models.Subscription)
        .filter(models.Subscription.id == subscription_id)
        .first()
    )
    if not db_subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    for key, value in subscription.dict().items():
        setattr(db_subscription, key, value)
    db.commit()
    db.refresh(db_subscription)
    return db_subscription


@app.delete("/subscriptions/{subscription_id}")
def delete_subscription(subscription_id: int, db: Session = Depends(get_db)):
    subscription = (
        db.query(models.Subscription)
        .filter(models.Subscription.id == subscription_id)
        .first()
    )
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    db.delete(subscription)
    db.commit()
    return {"message": "Subscription deleted"}
