# Evidência S1t — etapa 3: os NPCs da Coroa de Cobre e os segredos da arena no jogo (2026-11-17)

**Gate:** etapa 3 do plano de conhecimento (conhecimento individual) e etapa 4 (testes reais); ADR-0119 e ADR-0131.
**Resultado:** **APROVADO no laboratório ARM64/VM** (mantenedor: "Abra o PR"). Em 13 turnos com Lehtinan, Tiana, Salvanas e Unger, nenhuma recusa do verificador.
- O segredo `CONFIDENTIAL` dos escravos nunca foi contado.
- A arena (`PROFESSIONAL`) foi contada por quem frequenta a casa, e retida por quem estava cauteloso.

**Executado por:** mantenedor no jogo (cópia `BG2EE-P1`, campanha `lab-s1f`) e Claude Code via SSH (serviço no Mac, `--voice --carry-pin`).

## Preparação

- **Pacote:** 172 entradas, revisão `sha256:5bf7e32f2a3c`, com as duas entradas restritas da arena. Foi pinada à mão no ramo `br-cf8ac0194564`.
- **Fichas:** o serviço carregou 27 identidades curadas (`identidades curadas: 27`).
- **Relatório "quem sabe o quê"** gerado por código antes do teste (decisão D3), fora do repositório: `INFINITY_AI_Quem_Sabe_o_Que_Etapa3.md`.

## Turnos

O log não guarda as falas (ADR-0107).

| Falante | Reação | Retido | Resultado |
|---|---|---|---|
| Lehtinan (3) | indiferente | `rel:arena-slaves` (`TRUST_REQUIRED`) nos três | Duas vezes a linha neutra pelo código (`ABSENCE:WITHHELD`); uma vez pelo modelo, sem o segredo no prompt |
| Tiana | cautelosa | a administração de Bernard e a arena (`CAUTIOUS`) | OK: quem está cauteloso retém o que é assunto da casa |
| Salvanas (3) | indiferente | — | OK, com `rel:lehtinan-runs-arena` nos três |
| Unger (6) | indiferente | — | OK: Drizzt, a Coroa de Cobre, as Favelas, o dono e a arena |

## Incidente do laboratório

Às 20:55 o jogo foi reaberto, e o serviço registrou `leitura do log falhou: RemoteShellError`. Reiniciado, ele conferiu a instalação (`live matches pinned: True`).

## Pendências anotadas

- **Hendak** não chegou a ser testado no jogo; a bateria cobre o caso (`hendak-escravo-da-arena`).
- **Salvanas às vezes diz que "Bernard cuida" da arena.** Ele mistura a relação de Bernard com a taverna e a da arena. O verificador não pega, porque "Bernard cuida" tem base no outro fato.
