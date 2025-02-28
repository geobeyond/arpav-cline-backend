import enum
import typing

import sqlalchemy
import sqlmodel


def add_values_in_list_filter(
    statement,
    value: typing.Union[list, str, enum.Enum],
    column: sqlalchemy.Column,
):
    if not isinstance(value, list):
        values = [value]
    else:
        values = value
    values = [v.name if isinstance(v, enum.Enum) else v for v in values]
    if len(values) == 1:
        result = statement.where(values[0] == sqlalchemy.any_(column))
    else:
        result = statement.where(
            sqlalchemy.or_(
                *[v == sqlalchemy.any_(column) for v in values],
            )
        )
    return result


def add_multiple_values_filter(
    statement,
    value: typing.Union[list[typing.Any]],
    column: sqlalchemy.Column,
):
    if not isinstance(value, list):
        values = [value]
    else:
        values = value
    if len(values) == 1:
        result = statement.where(column == values[0])
    else:
        result = statement.where(
            sqlalchemy.or_(
                *[column == v for v in values],
            )
        )
    return result


def add_substring_filter(statement, value: typing.Union[list[str], str], *columns):
    """Add a string-based comparison to the statement"""
    prepared_values = []
    if isinstance(value, list):
        for v in value:
            prepared_values.append(f'%{v.replace("%", "")}%')
    else:
        prepared_values.append(f'%{value.replace("%", "")}%')

    if len(columns) == 1:
        if len(prepared_values) == 1:
            result = statement.where(columns[0].ilike(prepared_values[0]))  # type: ignore[attr-defined]
        else:
            or_clauses = [columns[0].ilike(v) for v in prepared_values]
            result = statement.where(sqlalchemy.or_(*or_clauses))
    elif len(columns) > 1:
        if len(prepared_values) == 1:
            result = statement.where(
                sqlalchemy.or_(*[c.ilike(prepared_values[0]) for c in columns])
            )
        else:
            result = statement.where(
                sqlalchemy.or_(
                    *[
                        sqlalchemy.or_(*[c.ilike(v) for v in prepared_values])
                        for c in columns
                    ]
                )
            )
    else:
        raise RuntimeError("Invalid columns argument")
    return result


def old_add_substring_filter(statement, value: str, *columns):
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
