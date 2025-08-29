def parse_grid_data(system_parameters: dict, grid_data: list[list[str]], grid_name: str) -> list[dict[str, str]]:
    columns: list[str] = system_parameters["Result"]["GridDefinitions"][grid_name]["Columns"]
    if not columns:
        raise RuntimeError("No columns found in grid definition")

    accounts = []
    for row in grid_data:
        if len(row) != len(columns):
            raise ValueError(f"Expected {len(columns)} columns, got {len(row)}")
        account = {col_data["Name"]: row[i] for i, col_data in enumerate(columns)}
        accounts.append(account)

    return accounts
