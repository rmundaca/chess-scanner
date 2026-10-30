from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, inspect, text

from app.core.database import Base


class Scan(Base):
    """Position read from a diagram. Images live in data/scans/<id>/ (board.jpg, photo.jpg)."""

    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=True)
    placement = Column(String, nullable=False)  # first FEN field (always with White at the bottom)
    side = Column(String(1), nullable=False, default="w")
    castling = Column(String(4), nullable=False, default="-")
    flipped = Column(Boolean, nullable=False, default=False)  # the diagram has Black at the bottom
    corners = Column(Text, nullable=True)  # JSON [[x, y]] x4 normalized to the photo
    has_photo = Column(Boolean, nullable=False, default=False)
    predicted = Column(String(64), nullable=True)  # model proposal: 64 squares in visual order, "." = empty
    model_id = Column(String(16), nullable=True)  # model that made the proposal
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


# Columns added after the first version: table -> [(name, SQLite DDL)]
_NEW_COLUMNS = {
    "scans": [("predicted", "VARCHAR(64)"), ("model_id", "VARCHAR(16)")],
}

# Idempotent statements to fix legacy data
_DATA_FIXES = [
    # "UPDATE scans SET castling = '-' WHERE castling IS NULL",
]


def init_db_migrations(engine):
    """Add new columns and fix legacy data in existing SQLite databases."""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    with engine.begin() as conn:
        for table, cols in _NEW_COLUMNS.items():
            if table not in tables:
                continue
            existing = {c["name"] for c in inspector.get_columns(table)}
            for name, ddl in cols:
                if name not in existing:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {name} {ddl}"))
        for stmt in _DATA_FIXES:
            conn.execute(text(stmt))
