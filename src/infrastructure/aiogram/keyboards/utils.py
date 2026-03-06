from typing import List


def build_pages(current: int, total: int) -> List[int]:
    pages = {1, total}
    middle_page = total // 2

    pages.add(current)
    pages.add(middle_page)

    if current - 1 > 1:
        pages.add(current - 1)

    if current + 1 < total:
        pages.add(current + 1)

    if current + 10 < total:
        pages.add(current + 10)

    return sorted(pages)
