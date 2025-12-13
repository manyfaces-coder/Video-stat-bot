from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_session
from app.db.models import Video, VideoSnapshot

router = APIRouter(prefix="/creators", tags=["Creators"])

# Количество видео у креатора за период
@router.get("/{creator_id}/videos/count")
async def videos_count(
    creator_id: str,
    date_from: date = Query(..., alias="from"),
    date_to: date = Query(..., alias="to"),
    session: AsyncSession = Depends(get_session),
):
    stmt = (
        select(func.count())
        .select_from(Video)
        .where(
            Video.creator_id == creator_id,
            Video.video_created_at.between(date_from, date_to),
        )
    )

    result = await session.execute(stmt)
    return {"count": result.scalar_one()}


# Сколько видео превысило порог (threshold) просмотров
@router.get("/{creator_id}/videos/views_over")
async def videos_views_over(
    creator_id: str,
    threshold: int = Query(..., gt=0),
    session: AsyncSession = Depends(get_session),
):
    stmt = (
        select(func.count())
        .select_from(Video)
        .where(
            Video.creator_id == creator_id,
            Video.views_count > threshold,
        )
    )

    result = await session.execute(stmt)
    return {"count": result.scalar_one()}

# Суммарный прирост просмотров за день
@router.get("/{creator_id}/views/delta_daily")
async def views_delta_daily(
    creator_id: str,
    day: date = Query(..., alias="date"),
    session: AsyncSession = Depends(get_session),
):
    stmt = (
        select(func.coalesce(func.sum(VideoSnapshot.delta_views_count), 0))
        .select_from(VideoSnapshot)
        .join(Video, Video.id == VideoSnapshot.video_id)
        .where(
            Video.creator_id == creator_id,
            func.date(VideoSnapshot.created_at) == day,
        )
    )

    result = await session.execute(stmt)
    return {"delta_views": result.scalar_one()}
