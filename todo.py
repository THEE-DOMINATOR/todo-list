#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from typing import Any

TODO_FILE = Path(__file__).with_name("todos.json")


def load_todos() -> list[dict[str, Any]]:
    if not TODO_FILE.exists():
        return []
    try:
        data = json.loads(TODO_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    if not isinstance(data, list):
        return []
    todos: list[dict[str, Any]] = []
    for item in data:
        if isinstance(item, dict) and isinstance(item.get("title"), str):
            todos.append({"title": item["title"], "done": bool(item.get("done", False))})
    return todos


def save_todos(todos: list[dict[str, Any]]) -> None:
    TODO_FILE.write_text(json.dumps(todos, indent=2), encoding="utf-8")


def add_todo(todos: list[dict[str, Any]], title: str) -> None:
    title = title.strip()
    if not title:
        raise ValueError("Task cannot be empty.")
    todos.append({"title": title, "done": False})
    save_todos(todos)
    print(f'Added: "{title}"')


def list_todos(todos: list[dict[str, Any]]) -> None:
    if not todos:
        print("No tasks yet.")
        return

    for idx, item in enumerate(todos, start=1):
        status = "[x]" if item["done"] else "[ ]"
        print(f"{idx}. {status} {item['title']}")


def update_todo(todos: list[dict[str, Any]], index: int, *, done: bool | None = None, remove: bool = False) -> None:
    if index < 1 or index > len(todos):
        raise IndexError("Task number is out of range.")

    idx = index - 1
    if remove:
        removed = todos.pop(idx)
        save_todos(todos)
        print(f'Removed: "{removed["title"]}"')
        return

    if done is not None:
        todos[idx]["done"] = done
        save_todos(todos)
        action = "Completed" if done else "Marked as not done"
        print(f'{action}: "{todos[idx]["title"]}"')


def clear_todos() -> None:
    save_todos([])
    print("Cleared all tasks.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Simple to-do list")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("title", help="Task title")

    subparsers.add_parser("list", help="List tasks")

    done_parser = subparsers.add_parser("done", help="Mark a task as done")
    done_parser.add_argument("index", type=int, help="Task number")

    undone_parser = subparsers.add_parser("undone", help="Mark a task as not done")
    undone_parser.add_argument("index", type=int, help="Task number")

    remove_parser = subparsers.add_parser("remove", help="Remove a task")
    remove_parser.add_argument("index", type=int, help="Task number")

    subparsers.add_parser("clear", help="Remove all tasks")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    todos = load_todos()

    try:
        if args.command == "add":
            add_todo(todos, args.title)
        elif args.command == "list":
            list_todos(todos)
        elif args.command == "done":
            update_todo(todos, args.index, done=True)
        elif args.command == "undone":
            update_todo(todos, args.index, done=False)
        elif args.command == "remove":
            update_todo(todos, args.index, remove=True)
        elif args.command == "clear":
            clear_todos()
    except (ValueError, IndexError) as exc:
        print(f"Error: {exc}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
