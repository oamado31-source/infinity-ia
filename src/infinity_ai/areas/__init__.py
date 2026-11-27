# SPDX-License-Identifier: Apache-2.0
"""SPEC-014 / ADR-0149: the files of a new area, written by us from a recipe.

Every file of an area of ours is written here from scratch, following the public documentation
of the formats (IESDP): the picture (TIS V2 and its PVRZ pages), the plan with its walls (WED
V1.3), the search, height and light maps (BMP), the minimap (MOS V1) and the content (ARE V1.0).
Standard library only. No game byte is needed to build an area from a procedural recipe.
"""
from __future__ import annotations


class AreaError(ValueError):
    """A named refusal (the code is what tests and the checker report)."""

    def __init__(self, code: str, detail: str = '') -> None:
        super().__init__(f'{code}: {detail}' if detail else code)
        self.code = code
        self.detail = detail
