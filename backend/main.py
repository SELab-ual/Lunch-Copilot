
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy import select, func, asc, desc
from sqlalchemy.orm import Session
from typing import Optional

from db import engine, get_session
from models import Base, RestaurantType, Restaurant
from schemas import (
    RestaurantTypeCreate, RestaurantTypeOut,
    RestaurantCreate, RestaurantOut,
    RestaurantListItem, SearchResponse
)

app = FastAPI(title="ALI Sprint 1 API", version="0.1.0")

# Create tables on startup (prototype only)
Base.metadata.create_all(bind=engine)

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

# --- Admin minimal endpoints ---
@app.post("/admin/restaurant-types", response_model=RestaurantTypeOut)
def create_restaurant_type(payload: RestaurantTypeCreate, session: Session = Depends(get_session)):
    name = payload.name.strip()
    rt = session.execute(select(RestaurantType).where(func.lower(RestaurantType.name)==name.lower())).scalar_one_or_none()
    if rt:
        raise HTTPException(status_code=409, detail="Restaurant type already exists")
    rt = RestaurantType(name=name)
    session.add(rt)
    session.flush()
    return rt

@app.get("/restaurant-types", response_model=list[RestaurantTypeOut])
def list_restaurant_types(session: Session = Depends(get_session)):
    rows = session.execute(select(RestaurantType).order_by(RestaurantType.name.asc())).scalars().all()
    return rows

@app.post("/admin/restaurants", response_model=RestaurantOut)
def create_restaurant(payload: RestaurantCreate, session: Session = Depends(get_session)):
    # Validate type exists
    rtype = session.get(RestaurantType, payload.type_id)
    if not rtype:
        raise HTTPException(status_code=400, detail="Invalid type_id")
    r = Restaurant(
        name=payload.name.strip(),
        average_price=payload.average_price,
        address=payload.address.strip(),
        phone=payload.phone.strip(),
        email=str(payload.email),
        description=(payload.description or '').strip() or None,
        type_id=payload.type_id,
    )
    session.add(r)
    session.flush()
    return RestaurantOut(
        id=r.id,
        name=r.name,
        average_price=r.average_price,
        address=r.address,
        phone=r.phone,
        email=r.email,
        description=r.description,
        type_id=r.type_id,
        type_name=rtype.name,
    )

# --- Search endpoints ---
@app.get("/restaurants/{rid}", response_model=RestaurantOut)
def get_restaurant(rid: int, session: Session = Depends(get_session)):
    stmt = (
        select(Restaurant, RestaurantType.name)
        .join(RestaurantType, Restaurant.type_id == RestaurantType.id)
        .where(Restaurant.id == rid)
    )
    row = session.execute(stmt).first()
    if not row:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    r, type_name = row
    return RestaurantOut(
        id=r.id,
        name=r.name,
        average_price=r.average_price,
        address=r.address,
        phone=r.phone,
        email=r.email,
        description=r.description,
        type_id=r.type_id,
        type_name=type_name,
    )

@app.get("/restaurants/search", response_model=SearchResponse)
def search_restaurants(
    q: Optional[str] = Query(default=None, description="Free-text across name, description, address"),
    type_id: Optional[int] = Query(default=None),
    price_min: Optional[int] = Query(default=None, ge=0),
    price_max: Optional[int] = Query(default=None, ge=0),
    sort: Optional[str] = Query(default="price", pattern="^(price|name)$"),
    order: Optional[str] = Query(default="asc", pattern="^(asc|desc)$"),
    limit: int = Query(default=100, ge=1, le=100),
    session: Session = Depends(get_session)
):
    # Build filters
    stmt = (
        select(Restaurant.id, Restaurant.name, Restaurant.average_price, RestaurantType.name.label('type_name'))
        .join(RestaurantType, Restaurant.type_id == RestaurantType.id)
    )

    if q:
        like = f"%{q.strip().lower()}%"
        stmt = stmt.where(
            func.lower(Restaurant.name).like(like) |
            func.lower(Restaurant.description).like(like) |
            func.lower(Restaurant.address).like(like) |
            func.lower(RestaurantType.name).like(like)
        )

    if type_id:
        stmt = stmt.where(Restaurant.type_id == type_id)

    if price_min is not None:
        stmt = stmt.where(Restaurant.average_price >= price_min)
    if price_max is not None:
        stmt = stmt.where(Restaurant.average_price <= price_max)

    if sort == 'price':
        order_by = asc(Restaurant.average_price) if order == 'asc' else desc(Restaurant.average_price)
    else:
        order_by = asc(Restaurant.name) if order == 'asc' else desc(Restaurant.name)

    stmt_sorted = stmt.order_by(order_by).limit(limit)

    items = [
        RestaurantListItem(id=i, name=n, average_price=p, type_name=t)
        for (i, n, p, t) in session.execute(stmt_sorted).all()
    ]

    # total (without limit)
    total = session.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()

    return SearchResponse(total=total, items=items)
