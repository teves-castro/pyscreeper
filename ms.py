import random
from typing import Set, Tuple

from pydantic import BaseModel

Position = Tuple[int, int]


class MineSweeper(BaseModel):
    width: int
    height: int
    mines: Set[Position] = set()
    open_cells: Set[Position] = set()
    flags: Set[Position] = set()
    lost: bool = False
    won: bool = False


def get_neighbors(position: Position, board: MineSweeper) -> Set[Position]:
    x, y = position
    neighbors = {
        (i, j)
        for i in range(x - 1, x + 2)
        for j in range(y - 1, y + 2)
        if (i, j) != position and 0 <= i < board.width and 0 <= j < board.height
    }
    return neighbors


def get_surrounding_mines(position: Position, board: MineSweeper) -> int:
    return len(get_neighbors(position, board) & board.mines)


def open(position: Position, board: MineSweeper) -> MineSweeper:
    if board.lost or board.won or position in board.flags:
        return board

    board.open_cells.add(position)

    neighbors = get_neighbors(position, board)
    surrounding_mines = get_neighbors(position, board) & board.mines
    console.debug(f"Surrounding mines: {surrounding_mines}")
    console.debug(f"neighbors: {neighbors}")

    if position in board.mines:
        board.lost = True
        return board

    if (
        board.flags == board.mines
        and len(board.open_cells | board.flags) == board.width * board.height
    ):
        board.won = True
        return board

    if surrounding_mines == set() or (
        position in board.open_cells
        and len(surrounding_mines) == len(neighbors & board.flags)
    ):
        print("Expanding")
        for neighbor in neighbors - board.open_cells:
            open(neighbor, board)

    return board


def toggle_flag(position: Position, board: MineSweeper) -> MineSweeper:
    if position in board.open_cells:
        return board

    if position in board.flags:
        board.flags.remove(position)
    else:
        board.flags.add(position)
    return board


# noinspection PyUnresolvedReferences,PyPackageRequirements
from js import Element, console, document


def render_cell(
    root: Element, pos: Position, cell_text: str, board: MineSweeper
) -> Element:
    def on_click(e):
        e.preventDefault()
        console.log(f"Clicked {pos}")
        open(pos, board)
        render_board(root, board)

    def on_context(e):
        e.preventDefault()
        toggle_flag(pos, board)
        render_board(root, board)

    x, y = pos
    cell = document.createElement("a")
    cell.href = "#"
    cell.className = "cell"
    cell.id = f"{x}-{y}"
    cell.innerHTML = cell_text
    cell.onclick = on_click
    cell.oncontextmenu = on_context
    root.appendChild(cell)
    return cell


def render_board(root: Element, board: MineSweeper) -> None:
    root.style.display = "inline-grid"
    root.style.gridTemplate = (
        f"repeat({board.width}, auto) / repeat({board.height}, auto)"
    )
    root.innerHTML = ""
    for x in range(board.width):
        for y in range(board.height):
            pos = (x, y)
            cell_text = "⬜"
            if pos in board.flags:
                cell_text = "🚩"
            elif pos in board.mines and pos in board.open_cells:
                cell_text = "💣"
            elif pos in board.open_cells:
                mine_count = get_surrounding_mines(pos, board)
                if mine_count > 0:
                    cell_text = str(mine_count)
                else:
                    cell_text = " "
            render_cell(root, pos, cell_text, board)

    result = document.getElementById("result")
    if board.won:
        result.innerHTML = "You won!"
        return

    if board.lost:
        result.innerHTML = "You lost!"
        return


def restart(e):
    e.preventDefault()
    run()


result = document.getElementById("result")
result.onclick = restart


def random_board():
    width = 20
    height = 20
    mines = set()
    for i in range(50):
        mines.add((random.randint(0, width - 1), random.randint(0, height - 1)))
    return MineSweeper(width=width, height=height, mines=mines)


def run():
    ms = random_board()
    root = document.getElementById("root")
    result = document.getElementById("result")
    result.innerHTML = ""
    render_board(root, ms)


run()
