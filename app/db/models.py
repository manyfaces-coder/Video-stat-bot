from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, ForeignKey
from datetime import datetime


Base = declarative_base()

"""
Таблица videos (итоговая статистика по ролику)

id — идентификатор видео;

creator_id — идентификатор креатора;

video_created_at — дата и время публикации видео;

views_count — финальное количество просмотров;

likes_count — финальное количество лайков;

comments_count — финальное количество комментариев;

reports_count — финальное количество жалоб;

служебные поля created_at, updated_at.
"""

class Video(Base):

    __tablename__ = "videos"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    creator_id: Mapped[str] = mapped_column(String, index=True)

    video_created_at: Mapped[datetime] = mapped_column(DateTime)
    views_count: Mapped[int] = mapped_column(Integer)
    likes_count: Mapped[int] = mapped_column(Integer)
    comments_count: Mapped[int] = mapped_column(Integer)
    reports_count: Mapped[int] = mapped_column(Integer)

    created_at: Mapped[datetime] = mapped_column(DateTime)
    updated_at: Mapped[datetime] = mapped_column(DateTime)

    snapshots: Mapped[list["VideoSnapshot"]] = relationship(
        "VideoSnapshot",
        back_populates="video",
        cascade="all, delete-orphan",
    )


"""
Таблица video_snapshots (почасовые замеры по ролику)
Каждый снапшот относится к одному видео и содержит:
id — идентификатор снапшота;

video_id — ссылка на соответствующее видео;

текущие значения: views_count, likes_count, comments_count, reports_count на момент замера;

приращения: delta_views_count, delta_likes_count, delta_comments_count, delta_reports_count — насколько изменилось значение с прошлого замера;

created_at — время замера (раз в час);

updated_at — служебное поле.
"""

class VideoSnapshot(Base):
    __tablename__ = "video_snapshots"
    id: Mapped[str] = mapped_column(String, primary_key=True)

    video_id: Mapped[str] = mapped_column(
        String, ForeignKey("videos.id"), index=True
    )

    views_count: Mapped[int] = mapped_column(Integer)
    likes_count: Mapped[int] = mapped_column(Integer)
    comments_count: Mapped[int] = mapped_column(Integer)
    reports_count: Mapped[int] = mapped_column(Integer)

    delta_views_count: Mapped[int] = mapped_column(Integer)
    delta_likes_count: Mapped[int] = mapped_column(Integer)
    delta_comments_count: Mapped[int] = mapped_column(Integer)
    delta_reports_count: Mapped[int] = mapped_column(Integer)

    created_at: Mapped[datetime] = mapped_column(DateTime)
    updated_at: Mapped[datetime] = mapped_column(DateTime)

    video: Mapped[Video] = relationship("Video", back_populates="snapshots")