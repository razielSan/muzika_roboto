from typing import List


def build_pages_to_step(current: int, total: int) -> List[int]:
    if total <= 1:  # если исполнитель один
        return []
    pages = {1, total}
    middle_page = total // 2

    pages.add(current)
    pages.add(middle_page)
    if current - 1 > 0:
        pages.add(current - 1)

    if current + 1 < total:
        pages.add(current + 1)

    if current + 10 < total:
        pages.add(current + 20)

    return sorted(pages)


def build_pages(current: int, total: int) -> List[int]:
    if total <= 1:  # если исполнитель один
        return []
    pages = {1, total}
    middle_page = total // 2

    pages.add(current)
    pages.add(middle_page)

    if current + 20 < total:
        pages.add(current + 20)

    return sorted(pages)
