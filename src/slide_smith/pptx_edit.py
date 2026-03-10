from __future__ import annotations

from pptx import Presentation


def delete_slide(prs: Presentation, index: int) -> None:
    """Delete slide at index from a Presentation.

    Uses internal python-pptx APIs; stable enough for our limited needs.
    """
    slide_id_list = prs.slides._sldIdLst  # type: ignore[attr-defined]
    slides = list(slide_id_list)
    slide_id_list.remove(slides[index])
