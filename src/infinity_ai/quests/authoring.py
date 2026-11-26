# SPDX-License-Identifier: Apache-2.0
"""SPEC-013: the quest checker — every problem of a quest file by name, instead of a silent drop.

`check_quest(doc, context)` returns the errors (the loader would refuse the quest, or the lab
could never run it) and the warnings (it loads, but something is likely wrong). The format part
mirrors `narrative.parse_quest`; a quest the loader refuses with no named error still gets one
("FORMAT"), so the two never disagree in silence. The context part, when given, checks the quest
against what exists: curated people, the build's areas and our installed creature templates.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

from .narrative import (
    END_RESOLVED, LEAVE_DESPAWN, LEAVE_ESCAPE, MAX_FACT, MAX_GOLD, MAX_JOURNAL, MAX_XP,
    QUEST_SCHEMA, START_ACCEPTED, START_BEGIN, WHEN_ANY, WHEN_NIGHT, _AREA, _CRE, _GAME_NAME, _ID,
    _NPC, _OUR_AREA, _OWN_NAME, parse_quest,
)

MAX_CUE = 40
MIN_ACCEPT_CUES = 4
COMMON_CUES = frozenset({
    'a', 'o', 'e', 'é', 'de', 'do', 'da', 'que', 'sim', 'não', 'nao', 'ok', 'eu', 'você', 'voce',
    'um', 'uma', 'me', 'se', 'em', 'no', 'na', 'pra', 'para', 'com', 'por', 'isso', 'aqui',
})
PASSAGE_KEYS = {'passage_id', 'area', 'x', 'y', 'to', 'to_x', 'to_y', 'facing', 'after'}


@dataclass(frozen=True)
class Issue:
    code: str
    where: str
    message: str

    def __str__(self) -> str:
        return f'[{self.code}] {self.where}: {self.message}'


@dataclass
class Report:
    errors: list[Issue] = field(default_factory=list)
    warnings: list[Issue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    def error(self, code: str, where: str, message: str) -> None:
        self.errors.append(Issue(code, where, message))

    def warn(self, code: str, where: str, message: str) -> None:
        self.warnings.append(Issue(code, where, message))


@dataclass(frozen=True)
class AuthoringContext:
    """What exists, for the cross checks; None in a field skips that check."""
    curated: frozenset[str] | None = None        # npc ids with a checked curation
    areas: frozenset[str] | None = None          # area resrefs of the build
    templates: frozenset[str] | None = None      # our creature files installed (IA…)
    names: frozenset[str] | None = None          # proper names the world knows (pack, people)


def _plain(text: str) -> str:
    text = unicodedata.normalize('NFKD', text.lower())
    return ''.join(c for c in text if not unicodedata.combining(c))


def _is_int(v: object) -> bool:
    return isinstance(v, int) and not isinstance(v, bool)


def _text(r: Report, where: str, raw: object, limit: int) -> None:
    if not isinstance(raw, str) or not raw.strip():
        r.error('TEXT', where, 'falta o texto')
    elif len(raw.strip()) > limit:
        r.error('TEXT', where, f'{len(raw.strip())} caracteres; o limite é {limit}')


def _cues(r: Report, where: str, raw: object, common: frozenset[str] = COMMON_CUES) -> list[str]:
    if not isinstance(raw, list) or not raw:
        r.error('CUES', where, 'a lista de palavras-chave falta ou está vazia')
        return []
    out = []
    for c in raw:
        if not isinstance(c, str) or not c.strip():
            r.error('CUES', where, f'palavra-chave inválida: {c!r}')
        elif len(c) > MAX_CUE:
            r.error('CUES', where, f'palavra-chave com mais de {MAX_CUE} caracteres: {c!r}')
        else:
            out.append(c.strip())
            if _plain(c.strip().rstrip('*')) in common:
                r.warn('COMMON_CUE', where, f'palavra comum demais, dispara em qualquer fala: {c!r}')
    return out


def _area(r: Report, where: str, area: object, ctx: AuthoringContext | None) -> None:
    if not isinstance(area, str) or not _AREA.fullmatch(area):
        r.error('AREA', where, f'área inválida: {area!r}')
        return
    if _OUR_AREA.fullmatch(area):
        if not any(w.code == 'OUR_AREA' and area in w.message for w in r.warnings):
            r.warn('OUR_AREA', where, f'{area} é área nossa: confirme que foi instalada '
                                      '(build_area.py, com o jogo fechado)')
    elif ctx is not None and ctx.areas is not None and area not in ctx.areas:
        r.error('AREA', where, f'{area} não existe na build')


def _person(r: Report, where: str, npc: object, ctx: AuthoringContext | None) -> None:
    if not isinstance(npc, str) or not _NPC.fullmatch(npc):
        r.error('NPC', where, f'pessoa inválida: {npc!r}')
    elif ctx is not None and ctx.curated is not None and npc not in ctx.curated:
        r.error('NO_CURATION', where, f'{npc} não tem curadoria conferida (knowledge/npcs)')


def _names(r: Report, where: str, text: object, ctx: AuthoringContext | None) -> None:
    if ctx is None or ctx.names is None or not isinstance(text, str):
        return
    words = re.findall(r"(?<![.!?]\s)(?<!^)\b[A-ZÀ-Ý][\wÀ-ÿ'-]{2,}", text.strip())
    unknown = sorted({w for w in words if w not in ctx.names})
    if unknown:
        r.warn('UNKNOWN_NAME', where, 'nome que o mundo não conhece (pacote ou pessoas): '
                                      + ', '.join(unknown))


def _steps(r: Report, raw: object, ctx: AuthoringContext | None) -> list[dict]:
    if not isinstance(raw, list) or not raw:
        r.error('STEPS', 'steps', 'a quest precisa de pelo menos um passo')
        return []
    seen: list[str] = []
    before: dict[str, set[str]] = {}
    talks: dict[str, list[str]] = {}
    good = []
    for i, s in enumerate(raw):
        where = f'steps[{i}]'
        if not isinstance(s, dict):
            r.error('STEP', where, 'o passo não é um objeto')
            continue
        sid = s.get('step_id')
        if not isinstance(sid, str) or not _ID.fullmatch(sid):
            r.error('STEP_ID', where, f'step_id inválido: {sid!r}')
            continue
        where = f'passo {sid}'
        if sid in seen:
            r.error('STEP_ID', where, 'step_id repetido')
        after = s.get('after', [])
        if not isinstance(after, list):
            r.error('AFTER', where, '`after` precisa ser uma lista')
            after = []
        for a in after:
            if a not in seen:
                r.error('AFTER', where, f'`after` cita {a!r}, que não é um passo anterior '
                                        '(a ordem nunca pode dar volta)')
        before[sid] = set(a for a in after if a in before).union(
            *(before[a] for a in after if a in before))
        _text(r, f'{where}.journal', s.get('journal'), MAX_JOURNAL)
        kinds = [k for k in ('defeated', 'arrive') if k in s] + (['talk'] if 'npc_id' in s else [])
        if len(kinds) != 1:
            r.error('STEP_KIND', where, 'um passo é uma só coisa: conversa (npc_id, cues, fact), '
                                        'chegada (arrive) ou derrota (defeated)')
        elif kinds == ['defeated']:
            fell = s['defeated']
            if not isinstance(fell, dict) or set(fell) != {'presence'} \
                    or not isinstance(fell.get('presence'), str):
                r.error('DEFEATED', where, '`defeated` precisa ser {"presence": "<presence_id>"}')
        elif kinds == ['arrive']:
            where_to = s['arrive']
            if not isinstance(where_to, dict) or set(where_to) - {'area', 'night'}:
                r.error('ARRIVE', where, '`arrive` aceita só "area" e "night"')
            else:
                _area(r, f'{where}.arrive', where_to.get('area'), ctx)
                if not isinstance(where_to.get('night', False), bool):
                    r.error('ARRIVE', where, '`night` é verdadeiro ou falso')
        else:
            _person(r, where, s.get('npc_id'), ctx)
            _cues(r, f'{where}.cues', s.get('cues'))
            _text(r, f'{where}.fact', s.get('fact'), MAX_FACT)
            _names(r, f'{where}.fact', s.get('fact'), ctx)
            if 'area' in s:
                _area(r, f'{where}.area', s.get('area'), ctx)
            npc = s.get('npc_id')
            if isinstance(npc, str):
                for prev in talks.get(npc, []):
                    if prev not in before[sid]:
                        r.error('CHAIN', where, f'{npc} já tem a conversa {prev!r} aberta ao mesmo '
                                                'tempo: ponha a anterior em `after` (ADR-0144)')
                talks.setdefault(npc, []).append(sid)
        seen.append(sid)
        good.append(s)
    return good


def _presences(r: Report, raw: object, step_ids: list[str], steps: list[dict],
               ctx: AuthoringContext | None, told: tuple = ()) -> dict[str, dict]:
    if raw is None:
        return {}
    if not isinstance(raw, list):
        r.error('PRESENCE', 'presence', 'precisa ser uma lista')
        return {}
    starts, ends = {START_ACCEPTED, START_BEGIN, *step_ids}, {END_RESOLVED, *step_ids}
    found: dict[str, dict] = {}
    order = {sid: i for i, sid in enumerate(step_ids)}
    ids, names = set(), set()
    night_arrivals = {(s['arrive'].get('area')) for s in steps
                      if isinstance(s.get('arrive'), dict) and s['arrive'].get('night')}
    told_night = 'noite' in _plain(' '.join(str(v) for v in told))
    for i, p in enumerate(raw):
        where = f'presence[{i}]'
        if not isinstance(p, dict):
            r.error('PRESENCE', where, 'a presença não é um objeto')
            continue
        pid = p.get('presence_id')
        if isinstance(pid, str) and _ID.fullmatch(pid):
            where = f'presença {pid}'
            if pid in ids:
                r.error('PRESENCE', where, 'presence_id repetido')
            ids.add(pid)
            found[pid] = p
        else:
            r.error('PRESENCE', where, f'presence_id inválido: {pid!r}')
        cre, name = p.get('cre'), p.get('name')
        if not isinstance(cre, str) or not _CRE.fullmatch(cre):
            r.error('CRE', where, f'só criatura nossa (IA e até 6 letras ou números): {cre!r}')
        elif ctx is not None and ctx.templates is not None and cre not in ctx.templates:
            r.error('NO_TEMPLATE', where, f'{cre} não está instalado no laboratório '
                                          '(build_templates.py, com o jogo fechado)')
        if not isinstance(name, str) or not _OWN_NAME.fullmatch(name):
            r.error('NAME', where, f'nome de script precisa ser INFAI_…: {name!r}')
        elif name in names:
            r.error('NAME', where, f'nome de script repetido: {name}')
        names.add(name)
        _area(r, f'{where}.area', p.get('area'), ctx)
        start, end = p.get('from', START_ACCEPTED), p.get('until', END_RESOLVED)
        if start not in starts:
            r.error('WINDOW', where, f'`from` precisa ser START, ACCEPTED ou um passo: {start!r}')
        if end not in ends:
            r.error('WINDOW', where, f'`until` precisa ser RESOLVED ou um passo: {end!r}')
        if start == end:
            r.error('WINDOW', where, '`from` e `until` não podem ser o mesmo ponto')
        elif start in order and end in order and order[end] < order[start]:
            r.warn('WINDOW', where, f'`until` ({end}) vem antes de `from` ({start}) na lista')
        x, y, facing, copies = (p.get('x', -1), p.get('y', -1), p.get('facing', 0),
                                p.get('copies', 1))
        if not all(_is_int(n) for n in (x, y, facing, copies)):
            r.error('NUMBER', where, 'x, y, facing e copies são números inteiros')
        else:
            if not (-1 <= x <= 32767 and -1 <= y <= 32767) or (x < 0) != (y < 0):
                r.error('POINT', where, 'x e y vão de 0 a 32767, os dois juntos (ou nenhum)')
            if not 0 <= facing <= 15:
                r.error('FACING', where, '`facing` vai de 0 a 15')
            if not 1 <= copies <= 8:
                r.error('COPIES', where, '`copies` vai de 1 a 8')
        when = p.get('when', WHEN_ANY)
        if when not in (WHEN_ANY, WHEN_NIGHT):
            r.error('WHEN', where, f'`when` é {WHEN_ANY} ou {WHEN_NIGHT}')
        elif when == WHEN_NIGHT and p.get('area') not in night_arrivals and not told_night:
            r.warn('WHEN', where, 'presença só de noite, mas a quest nunca diz ao jogador que é '
                                  'de noite: ele pode chegar de dia e não achar ninguém')
        hostile = p.get('hostile_from')
        if hostile is not None and (hostile not in starts or hostile == START_BEGIN):
            r.error('HOSTILE', where, f'`hostile_from` precisa ser ACCEPTED ou um passo: {hostile!r}')
        walk = p.get('walk_to')
        if walk is not None:
            if not isinstance(walk, dict) or set(walk) != {'x', 'y'} or not all(
                    _is_int(walk.get(k)) and 0 <= walk.get(k) <= 32767 for k in ('x', 'y')):
                r.error('WALK', where, '`walk_to` é {"x": …, "y": …}, inteiros de 0 a 32767')
            elif not _is_int(x) or x < 0:
                r.error('WALK', where, 'para andar até um ponto, a presença precisa de x e y '
                                       '(onde nasce, por exemplo a porta) (ADR-0148)')
        if p.get('leave', LEAVE_DESPAWN) not in (LEAVE_DESPAWN, LEAVE_ESCAPE):
            r.error('LEAVE', where, f'`leave` é {LEAVE_DESPAWN} ou {LEAVE_ESCAPE}')
    return found


def _passages(r: Report, raw: object, step_ids: list[str], ctx: AuthoringContext | None) -> None:
    if raw is None:
        return
    if not isinstance(raw, list):
        r.error('PASSAGE', 'passages', 'precisa ser uma lista')
        return
    ids = set()
    for i, p in enumerate(raw):
        where = f'passages[{i}]'
        if not isinstance(p, dict):
            r.error('PASSAGE', where, 'a passagem não é um objeto')
            continue
        pid = p.get('passage_id')
        where = f'passagem {pid}' if isinstance(pid, str) else where
        if not isinstance(pid, str) or not _ID.fullmatch(pid) or pid in ids:
            r.error('PASSAGE', where, f'passage_id inválido ou repetido: {pid!r}')
        ids.add(pid)
        extra = set(p) - PASSAGE_KEYS
        if extra:
            r.error('PASSAGE', where, 'campos que não existem: ' + ', '.join(sorted(extra)))
        area, to = p.get('area'), p.get('to')
        _area(r, f'{where}.area', area, ctx)
        _area(r, f'{where}.to', to, ctx)
        if isinstance(area, str) and isinstance(to, str):
            if area == to:
                r.error('PASSAGE', where, 'origem e destino iguais')
            if not (_OUR_AREA.fullmatch(area) or _OUR_AREA.fullmatch(to)):
                r.error('PASSAGE', where, 'só de ou para uma área nossa (IA e quatro dígitos), '
                                          'nunca entre duas áreas do jogo (ADR-0146)')
        numbers = [p.get(k) for k in ('x', 'y', 'to_x', 'to_y')]
        if not all(_is_int(n) and 0 <= n <= 32767 for n in numbers):
            r.error('POINT', where, 'x, y, to_x e to_y são inteiros de 0 a 32767')
        facing = p.get('facing', 0)
        if not _is_int(facing) or not 0 <= facing <= 15:
            r.error('FACING', where, '`facing` vai de 0 a 15')
        after = p.get('after', [])
        if not isinstance(after, list) or any(a not in step_ids for a in after):
            r.error('AFTER', where, '`after` só cita passos da quest')


def _call(r: Report, raw: object, ctx: AuthoringContext | None,
          own: set[str] = frozenset()) -> None:
    if raw is None:
        return
    if not isinstance(raw, dict) or set(raw) != {'script_name', 'area', 'strref', 'every'}:
        r.error('CALL', 'call', 'precisa ter exatamente script_name, area, strref e every')
        return
    name, strref, every = raw['script_name'], raw['strref'], raw['every']
    if not isinstance(name, str) or not _GAME_NAME.fullmatch(name.upper()):
        r.error('CALL', 'call.script_name', 'nome de script inválido')
    elif name.upper().startswith('INFAI_') and name.upper() not in own:
        r.error('CALL', 'call.script_name', 'um chamado de criatura nossa só vale para uma '
                                            'presença desta quest (ADR-0148)')
    _area(r, 'call.area', raw['area'], ctx)
    if not _is_int(strref) or not 0 <= strref <= 999999:
        r.error('CALL', 'call.strref', 'número de uma frase que já existe no jogo (dialog.tlk)')
    if not _is_int(every) or not 300 <= every <= 108000:
        r.error('CALL', 'call.every', 'de 300 a 108000 (tempo do jogo; 4500 é uma hora)')


def _reward(r: Report, raw: object) -> None:
    """ADR-0148: `turn_in.reward` {gold, xp}."""
    if raw is None:
        return
    if not isinstance(raw, dict) or not raw or not set(raw) <= {'gold', 'xp'}:
        r.error('REWARD', 'turn_in.reward', 'só {"gold": …, "xp": …} (itens ainda não existem)')
        return
    gold, xp = raw.get('gold', 0), raw.get('xp', 0)
    if not _is_int(gold) or not _is_int(xp) or not 0 <= gold <= MAX_GOLD \
            or not 0 <= xp <= MAX_XP:
        r.error('REWARD', 'turn_in.reward', f'ouro de 0 a {MAX_GOLD} e XP de 0 a {MAX_XP}')
    elif gold + xp == 0:
        r.error('REWARD', 'turn_in.reward', 'a recompensa precisa de ouro ou XP')


# A fact is what the person knows, said to the model in the second person ("Você viu..."). Orders
# about the person's own speech work (Gregor's "Agradeça primeiro. Depois conte: ..."), but an
# order to make a request of the group comes back word for word as the answer: Doran said "Peça
# que o grupo dê uma olhada na rua". The request is written as a wish ("você quer que o grupo
# ...") or as the closing "Pergunte se o grupo aceita ..." (Garoll's lesson, SPEC-013 §2).
ORDER_VERBS = ('peça', 'mande', 'convide', 'chame', 'solicite', 'implore')


def _orders(r: 'Report', where: str, text: object) -> None:
    if not isinstance(text, str):
        return
    for sentence in re.split(r'(?<=[.!?;,])\s+|\s+e\s+', text):
        first = sentence.strip().split(' ', 1)[0].lower().strip('"\'“”')
        if first in ORDER_VERBS:
            r.warn('FACT_ORDER', where, f'"{first.capitalize()} ..." é uma ordem dentro do fato, e '
                                        'a pessoa a repete como fala; escreva como desejo '
                                        '("você quer que o grupo ...") ou feche com "Pergunte se o '
                                        'grupo aceita ..."')
            return


def check_quest(doc: object, context: AuthoringContext | None = None) -> Report:
    """Errors and warnings of one quest file (SPEC-013)."""
    r = Report()
    if not isinstance(doc, dict):
        r.error('FORMAT', 'arquivo', 'não é um objeto JSON')
        return r
    if doc.get('schema') != QUEST_SCHEMA:
        r.error('SCHEMA', 'schema', f'precisa ser {QUEST_SCHEMA}')
    check = doc.get('curation') or {}
    if check.get('status') != 'CHECKED' or not check.get('checked_by') \
            or not check.get('checked_at'):
        r.error('CURATION', 'curation', 'status CHECKED, checked_by e checked_at: a quest só '
                                        'carrega depois da sua conferência')
    qid = doc.get('quest_id')
    if not isinstance(qid, str) or not _ID.fullmatch(qid):
        r.error('QUEST_ID', 'quest_id', 'letras minúsculas, números e hífen, até 48')
    elif doc.get('milestone') != f'quest:{qid}:RESOLVED':
        r.error('MILESTONE', 'milestone', f'precisa ser quest:{qid}:RESOLVED')
    _text(r, 'title', doc.get('title'), 80)
    if doc.get('area') is not None:
        _area(r, 'area', doc.get('area'), context)
    steps = _steps(r, doc.get('steps'), context)
    step_ids = [s['step_id'] for s in steps]
    giver = doc.get('giver')
    if not isinstance(giver, dict):
        r.error('GIVER', 'giver', 'falta quem dá a quest')
    else:
        _person(r, 'giver', giver.get('npc_id'), context)
        if giver.get('npc_id') in {s.get('npc_id') for s in steps}:
            r.error('GIVER', 'giver', 'quem dá a quest não pode ter um passo de conversa: a '
                                      'entrega já volta a ele')
        _cues(r, 'giver.offer_cues', giver.get('offer_cues'))
        # "sim" is how one accepts, and accept cues only count after the offer
        accept = _cues(r, 'giver.accept_cues', giver.get('accept_cues'),
                       COMMON_CUES - {'sim', 'ok'})
        if 0 < len(accept) < MIN_ACCEPT_CUES:
            r.warn('ACCEPT_CUES', 'giver.accept_cues', f'só {len(accept)} formas de aceitar: o '
                                                       'jogador pode aceitar com outras palavras')
        for key, limit in (('offer_fact', MAX_FACT), ('waiting_fact', MAX_FACT),
                           ('accept_journal', MAX_JOURNAL)):
            _text(r, f'giver.{key}', giver.get(key), limit)
        _names(r, 'giver.offer_fact', giver.get('offer_fact'), context)
        for key in ('offer_fact', 'waiting_fact'):
            _orders(r, f'giver.{key}', giver.get(key))
    turn_in = doc.get('turn_in')
    if not isinstance(turn_in, dict):
        r.error('TURN_IN', 'turn_in', 'falta a entrega')
    else:
        _cues(r, 'turn_in.cues', turn_in.get('cues'))
        _text(r, 'turn_in.fact', turn_in.get('fact'), MAX_FACT)
        _orders(r, 'turn_in.fact', turn_in.get('fact'))
        _text(r, 'turn_in.journal', turn_in.get('journal'), MAX_JOURNAL)
        _reward(r, turn_in.get('reward'))
    for s in steps:
        _orders(r, f"passo {s.get('step_id')}", s.get('fact'))
    told = [s.get('fact', '') for s in steps] + [s.get('journal', '') for s in steps]
    if isinstance(giver, dict):
        told += [giver.get('offer_fact', ''), giver.get('accept_journal', '')]
    found = _presences(r, doc.get('presence'), step_ids, steps, context, tuple(told))
    presences = set(found)
    giver_id = giver.get('npc_id') if isinstance(giver, dict) else None
    if isinstance(giver_id, str) and giver_id.startswith('npc:infai_') and not any(
            str(p.get('name', '')).lower() == giver_id[4:] and p.get('from') == START_BEGIN
            for p in found.values()):
        r.warn('GIVER_PRESENCE', 'giver', f'{giver_id} é uma pessoa nossa: sem uma presença '
                                          '`from: START` com o nome dela, ela não está no mundo '
                                          'para oferecer a quest (ADR-0148)')
    fallen = [s['defeated'].get('presence') for s in steps if isinstance(s.get('defeated'), dict)]
    for f in fallen:
        if f not in presences:
            r.error('DEFEATED', f'derrota de {f}', 'a presença não existe na quest')
    if len(fallen) != len(set(fallen)):
        r.error('DEFEATED', 'steps', 'a mesma presença tem dois passos de derrota')
    _call(r, doc.get('call'), context,
          {str(p.get('name', '')).upper() for p in found.values()})
    _passages(r, doc.get('passages'), step_ids, context)
    if r.ok and parse_quest(doc) is None:
        r.error('FORMAT', 'arquivo', 'o carregador recusou a quest por um motivo que o '
                                     'verificador não nomeou; avise para incluí-lo')
    return r




def rejected_quests(base) -> dict[str, list[str]]:
    """SPEC-013: the quest files of a folder that the loader drops, each with its named errors,
    so the service can say why a quest did not load (the loader itself stays silent)."""
    import json
    from pathlib import Path
    out: dict[str, list[str]] = {}
    for path in sorted(Path(base).glob('*.json')):
        try:
            doc = json.loads(path.read_text(encoding='utf-8'))
        except (OSError, ValueError) as exc:
            out[path.name] = [f'[JSON] arquivo: não abre ({exc})']
            continue
        if parse_quest(doc) is None:
            out[path.name] = [str(e) for e in check_quest(doc).errors] or ['[FORMAT] arquivo: recusada']
    return out


__all__ = ['AuthoringContext', 'Issue', 'Report', 'check_quest', 'rejected_quests']
