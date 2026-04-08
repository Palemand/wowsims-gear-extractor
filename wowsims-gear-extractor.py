import argparse
import json
import sys
from pathlib import Path
from typing import Any


def to_int(value: Any) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def collect_player_objects(root: dict[str, Any]) -> list[dict[str, Any]]:
    players: list[dict[str, Any]] = []

    single_player = root.get("player")
    if isinstance(single_player, dict):
        players.append(single_player)

    top_players = root.get("players")
    if isinstance(top_players, list):
        for player in top_players:
            if isinstance(player, dict):
                players.append(player)

    parties = root.get("parties")
    if isinstance(parties, list):
        for party in parties:
            if not isinstance(party, dict):
                continue
            party_players = party.get("players")
            if not isinstance(party_players, list):
                continue
            for player in party_players:
                if isinstance(player, dict):
                    players.append(player)

    return players


def extract_item_ids_from_player(player: dict[str, Any]) -> list[int]:
    ids: list[int] = []

    equipment = player.get("equipment")
    if not isinstance(equipment, dict):
        return ids

    items = equipment.get("items")
    if not isinstance(items, list):
        return ids

    for item in items:
        if not isinstance(item, dict):
            continue

        item_id = to_int(item.get("id"))
        if item_id is not None:
            ids.append(item_id)

    return ids


def extract_item_ids(root: dict[str, Any]) -> tuple[list[int], int]:
    players = collect_player_objects(root)
    all_ids: list[int] = []

    for player in players:
        all_ids.extend(extract_item_ids_from_player(player))

    # Stable de-duplication while keeping first-seen order.
    unique_ids = list(dict.fromkeys(all_ids))
    return unique_ids, len(players)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract equipped item IDs from a WoWSims JSON export file."
    )
    parser.add_argument("source", help="Path to a WoWSims exported JSON file")
    args = parser.parse_args()

    try:
        source_path = Path(args.source).expanduser()
        data = json.loads(source_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"File not found: {args.source}")
        sys.exit(1)
    except json.JSONDecodeError as err:
        print(f"Invalid JSON: {err}")
        sys.exit(1)
    except Exception as err:
        print(f"Could not read source: {err}")
        sys.exit(1)

    if not isinstance(data, dict):
        print("Unexpected JSON shape: top-level JSON value must be an object")
        sys.exit(1)

    ids, player_count = extract_item_ids(data)

    print(f"Source: {args.source}")
    print(f"Players parsed: {player_count}")
    print(f"Total selected item IDs: {len(ids)}")
    print()
    print("Selected item IDs:")
    for item_id in ids:
        print(".add", item_id)


if __name__ == "__main__":
    main()
