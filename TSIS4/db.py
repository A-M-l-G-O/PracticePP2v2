import datetime

try:
    import psycopg2
    import psycopg2.extras
    _PSYCOPG2_AVAILABLE = True
except ImportError:
    _PSYCOPG2_AVAILABLE = False

from config import DB_CONFIG

_DDL = """
CREATE TABLE IF NOT EXISTS players (
    id       SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS game_sessions (
    id            SERIAL PRIMARY KEY,
    player_id     INTEGER REFERENCES players(id),
    score         INTEGER   NOT NULL,
    level_reached INTEGER   NOT NULL,
    played_at     TIMESTAMP DEFAULT NOW()
);
"""


def _connect():
    if not _PSYCOPG2_AVAILABLE:
        raise RuntimeError("psycopg2 not installed")
    return psycopg2.connect(**DB_CONFIG)


def init_db():
    """Create tables if they don't exist. Returns True on success."""
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute(_DDL)
        return True
    except Exception as e:
        print(f"[DB] init_db failed: {e}")
        return False


def get_or_create_player(username: str) -> int | None:
    """Return the player's id, inserting a new row if necessary."""
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO players (username) VALUES (%s) "
                    "ON CONFLICT (username) DO NOTHING",
                    (username,),
                )
                cur.execute(
                    "SELECT id FROM players WHERE username = %s",
                    (username,),
                )
                row = cur.fetchone()
                return row[0] if row else None
    except Exception as e:
        print(f"[DB] get_or_create_player failed: {e}")
        return None


def save_session(player_id: int, score: int, level_reached: int) -> bool:
    """Insert a game session row."""
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO game_sessions "
                    "(player_id, score, level_reached) "
                    "VALUES (%s, %s, %s)",
                    (player_id, score, level_reached),
                )
        return True
    except Exception as e:
        print(f"[DB] save_session failed: {e}")
        return False


def get_personal_best(player_id: int) -> int:
    """Return the player's highest score, or 0 if none."""
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT COALESCE(MAX(score), 0) FROM game_sessions "
                    "WHERE player_id = %s",
                    (player_id,),
                )
                row = cur.fetchone()
                return row[0] if row else 0
    except Exception as e:
        print(f"[DB] get_personal_best failed: {e}")
        return 0


def get_top10():
    """Return list of (rank, username, score, level_reached, played_at)."""
    try:
        with _connect() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("""
                    SELECT p.username,
                           gs.score,
                           gs.level_reached,
                           gs.played_at
                    FROM game_sessions gs
                    JOIN players p ON p.id = gs.player_id
                    ORDER BY gs.score DESC
                    LIMIT 10
                """)
                rows = cur.fetchall()
                return [
                    (i + 1, r["username"], r["score"],
                     r["level_reached"], r["played_at"])
                    for i, r in enumerate(rows)
                ]
    except Exception as e:
        print(f"[DB] get_top10 failed: {e}")
        return []