_COLUMNS: dict[str, list[str]] = {}


def init_grid_parsers(system_parameters) -> None:
    global _COLUMNS
    if _COLUMNS:
        raise RuntimeError("Already initialized")

    result = {
        grid_name: [col["Name"] for col in grid_data["Columns"]]
        for grid_name, grid_data in system_parameters["Result"]["GridDefinitions"].items()
    }

    _COLUMNS = result


def parse_grid_data(grid_data: list[list[str]], grid_name: str) -> list[dict]:
    if _COLUMNS is None:
        raise RuntimeError("Not initialized")

    if grid_name not in _COLUMNS:
        raise ValueError(f"Unknown grid name: {grid_name}")

    columns: list[str] = _COLUMNS[grid_name]

    accounts = []
    for row in grid_data:
        if len(row) != len(columns):
            raise ValueError(f"Expected {len(columns)} columns, got {len(row)}")
        account = {col_name: row[i] for i, col_name in enumerate(columns)}
        accounts.append(account)

    return accounts
