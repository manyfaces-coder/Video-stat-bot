import os
import ijson

from sqlalchemy import insert, create_engine
from sqlalchemy.orm import Session

from app.db.models import Base
from app.db.database import DATABASE_URL
from app.db.models import Video, VideoSnapshot


# Настройки импорта
SNAPSHOT_PART_SIZE = 10000   # сколько снапшотов копим в памяти перед вставкой
ENGINE = None

def import_file(path: str):
    """
    Потоковый импорт

    ijson читает файл потоком и отдаёт по одному объекту video из массива videos
    На каждое video:
        1 - вставляем строку в videos (1 запись)
        2 - вставляем snapshots частями (по 10k)
    """
    inserted_videos = 0
    inserted_snapshots = 0

    # Читаем в бинарном режиме (последовательно)
    with open(path, "rb") as f:
        # ijson.items(f, "videos.item") выдает каждый элемент массива videos по одному
        videos_iter = ijson.items(f, "videos.item")

        # Одна сессия на весь импорт — ок, но мы коммитим порциями
        with Session(ENGINE) as session:
            for video in videos_iter:
                try:
                    # 1) Вставляем запись в videos
                    video_row = {
                        "id": video["id"],
                        "creator_id": video["creator_id"],
                        "video_created_at": video["video_created_at"],
                        "views_count": video["views_count"],
                        "likes_count": video["likes_count"],
                        "comments_count": video["comments_count"],
                        "reports_count": video["reports_count"],
                        "created_at": video["created_at"],
                        "updated_at": video["updated_at"],
                    }

                    # insert() возвращает SQLAlchemy Core выражение INSERT INTO
                    # оно работает на уровне SQL/таблицы, Video() не создается как python объект => работает быстрее
                    session.execute(insert(Video).values(**video_row))
                    inserted_videos += 1

                    # 2) Вставляем snapshots частями
                    part = []
                    for s in video.get("snapshots", []):
                        part.append({
                            "id": s["id"],
                            "video_id": video["id"],
                            "views_count": s["views_count"],
                            "likes_count": s["likes_count"],
                            "comments_count": s["comments_count"],
                            "reports_count": s["reports_count"],
                            "delta_views_count": s["delta_views_count"],
                            "delta_likes_count": s["delta_likes_count"],
                            "delta_comments_count": s["delta_comments_count"],
                            "delta_reports_count": s["delta_reports_count"],
                            "created_at": s["created_at"],
                            "updated_at": s["updated_at"],
                        })

                        # Если набрал SNAPSHOT_PART_SIZE, то отправляем данные в БД и очищаем память
                        if len(part) >= SNAPSHOT_PART_SIZE:
                            session.execute(insert(VideoSnapshot), part)
                            inserted_snapshots += len(part)
                            part.clear()

                    # Вставляем остаток снапшотов (если меньше заданного размера)
                    if part:
                        session.execute(insert(VideoSnapshot), part)
                        inserted_snapshots += len(part)
                        part.clear()

                    # Коммитим после каждого видео.
                    session.commit()
                except Exception as exp:
                    # откатить текущую транзакцию
                    session.rollback()
                    print(f"Ошибка на видео id={video.get('id')}: {exp}")

                    raise

    return inserted_videos, inserted_snapshots

def init_db():
    global ENGINE
    ENGINE = create_engine(DATABASE_URL)
    Base.metadata.create_all(bind=ENGINE)

if __name__ == "__main__":
    init_db()
    # нормализуем путь до файла
    path_json = os.path.normpath("data/videos.json")

    v, s = import_file(path_json)
    print(f"Импортировано videos: {v}, snapshots: {s}")

