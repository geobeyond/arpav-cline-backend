import sqlalchemy
import sqlmodel


def add_substring_filter(statement, value: str, *columns):
    filter_ = value.replace("%", "")
    filter_ = f"%{filter_}%"
    if len(columns) == 1:
        result = statement.where(columns[0].ilike(filter_))  # type: ignore[attr-defined]
    elif len(columns) > 1:
        result = statement.where(sqlalchemy.or_(*[c.ilike(filter_) for c in columns]))
    else:
        raise RuntimeError("Invalid columns argument")
    return result


def get_total_num_records(session: sqlmodel.Session, statement):
    return session.exec(
        sqlmodel.select(sqlmodel.func.count()).select_from(statement)
    ).first()


def slugify_internal_value(value: str) -> str:
    """Replace characters in input string in to make it usable as a name."""
    to_translate = "-\, '"
    return value.translate(value.maketrans(to_translate, "_" * len(to_translate)))
