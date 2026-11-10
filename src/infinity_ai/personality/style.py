# SPDX-License-Identifier: Apache-2.0
"""SPEC-006: how a personality profile shapes speech (style lines and alignment orientation).

Pure functions over a profile snapshot; no dialogue or storage imports, so both the encounter
dialogue and the resident context (ADR-0116) can use them.
"""
from __future__ import annotations

ETHICS = {"LAWFUL": "valoriza regras e compromissos", "NEUTRAL": "avalia regras pelo contexto",
          "CHAOTIC": "preza autonomia e liberdade"}
MORALITY = {"GOOD": "tende a se preocupar com o bem alheio",
            "NEUTRAL": "equilibra interesses e consequências",
            "EVIL": "costuma priorizar seus próprios interesses"}


def style_from_profile(profile: dict) -> tuple[str, ...]:
    h = profile["hexaco"]
    return (
        "fala de modo reservado" if h["extraversion"] < 40 else
        "fala de modo expansivo" if h["extraversion"] > 60 else "fala com naturalidade",
        "prefere franqueza" if h["honesty_humility"] > 60 else
        "é diplomático e protege seus interesses",
        "é metódico" if h["conscientiousness"] > 60 else "é espontâneo",
        "é curioso" if h["openness"] > 60 else "prefere situações conhecidas",
        "paciente e conciliador" if h["agreeableness"] > 60 else
        "impaciente com quem o contraria" if h["agreeableness"] < 40 else "cordial na medida",
        "deixa transparecer preocupação" if h["emotionality"] > 60 else
        "mantém a calma diante do risco" if h["emotionality"] < 40 else "contido nas emoções",
    )


def orientation_from_profile(profile: dict) -> str:
    alignment = profile["alignment_initial"]
    return f'{ETHICS[alignment["ethical"]]}; {MORALITY[alignment["moral"]]}'
