from __future__ import annotations

from pptx import Presentation


def delete_slide(prs: Presentation, index: int) -> None:
    """Delete slide at index from a Presentation.

    IMPORTANT: removing only the <p:sldId> entry leaves the slide part in the
    package. When we later add new slides, python-pptx can re-use partnames like
    ppt/slides/slide1.xml, resulting in duplicate ZIP members on save (PowerPoint
    repair prompt).

    So we:
    - drop the relationship from the presentation part (also releases the part)
    - remove the slide id element from the slide id list

    Uses internal python-pptx APIs; stable enough for our limited needs.
    """

    slide_id_list = prs.slides._sldIdLst  # type: ignore[attr-defined]
    sldId_elements = list(slide_id_list)
    sldId = sldId_elements[index]

    # rId is the relationship id from presentation.xml -> slideN.xml
    rId = sldId.rId  # type: ignore[attr-defined]

    # Drop the relationship first; this removes the target part from the package
    # when no longer referenced.
    prs.part.drop_rel(rId)  # type: ignore[attr-defined]

    # Remove the slide id from the presentation's slide list.
    slide_id_list.remove(sldId)
