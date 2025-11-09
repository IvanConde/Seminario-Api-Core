import sys
from sqlalchemy import text

from src.database import engine

CHECK_STATEMENT = text(
    """
    SELECT COUNT(*) AS column_exists
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = :schema
      AND TABLE_NAME = 'conversations'
      AND COLUMN_NAME = 'category'
    """
)

ALTER_STATEMENT = text(
    """
    ALTER TABLE conversations
        ADD COLUMN category ENUM('consulta','pedido','reclamo','sin_categoria')
            NOT NULL DEFAULT 'sin_categoria'
    """
)


def main() -> int:
    with engine.begin() as connection:
        result = connection.execute(
            CHECK_STATEMENT,
            {"schema": engine.url.database},
        )
        column_exists = result.scalar_one()
        if column_exists:
            return 0

        connection.execute(ALTER_STATEMENT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
