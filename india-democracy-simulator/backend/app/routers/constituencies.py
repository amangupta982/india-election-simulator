"""Constituencies router — query election data."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import Constituency
from app.schemas import ConstituencyResponse, ConstituencyListResponse

router = APIRouter(prefix="/constituencies", tags=["constituencies"])


@router.get("", response_model=ConstituencyListResponse)
async def list_constituencies(
    state: str = Query(None), seat_class: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    q = select(Constituency)
    if state:
        q = q.where(Constituency.state_ut == state)
    if seat_class:
        q = q.where(Constituency.seat_class == seat_class)
    result = await db.execute(q.order_by(Constituency.state_ut, Constituency.const_no))
    rows = result.scalars().all()
    return ConstituencyListResponse(
        total=len(rows),
        constituencies=[ConstituencyResponse.model_validate(r) for r in rows],
    )


@router.get("/swing", response_model=ConstituencyListResponse)
async def list_swing(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Constituency)
        .where(Constituency.seat_class.in_(["super_swing", "swing"]))
        .order_by(Constituency.actual_margin_2024)
    )
    rows = result.scalars().all()
    return ConstituencyListResponse(
        total=len(rows),
        constituencies=[ConstituencyResponse.model_validate(r) for r in rows],
    )
