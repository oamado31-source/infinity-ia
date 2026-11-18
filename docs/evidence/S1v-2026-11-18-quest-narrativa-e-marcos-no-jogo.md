# Evidência S1v — SPEC-011 e ADR-0134/0135: a quest narrativa e a confiança por marco no jogo (2026-11-18)

**Gate:** etapa 1, single player; SPEC-011, ADR-0134 (marcos e regra `MILESTONE`) e ADR-0135 (quests narrativas curadas).
**Resultado:** **APROVADO no laboratório ARM64/VM** (mantenedor: "Respondeu corretamente, revelando que são escravos comprados de traficantes").
- A quest "O broche de Bernard" foi feita inteira pela caixa, sem escrever nada no jogo.
- O marco da quest deixou Bernard `ÍNTIMO`, e ele passou a contar o segredo dos escravos da arena, que antes retinha.

**Executado por:** mantenedor no jogo (cópia `BG2EE-P1`, campanha `lab-s1f`) e Claude Code via SSH (serviço no Mac, `--voice --carry-pin --watch-probes`).

## Preparação

- **Caixa nova** instalada com o jogo fechado (`talk_poc.py --deploy`).
- **Manifesto fixado de novo:** `s1v-manifest-2026-11-17-pinned.json`. Mesma build (`sha256:c05b2b973695`); o hash dos mods mudou só pela caixa (`M_INFAIT.lua`). O arquivo da lista (`INFAIQST.lua`) é transitório.
- **Pacote:** 172 entradas, revisão `sha256:5bf7e32f2a3c`, levado aos ramos novos (`--carry-pin`).
- **Catálogo local de variáveis** (fora do repositório): `REVIEW_PENDING`, só observação.
- **Troca no laboratório:** o mantenedor não achou Yarin no save e pediu Anomen no lugar, só para o teste. A troca foi feita só na cópia do laboratório; o repositório continua com Yarin.

## Turnos

O log não guarda as falas (ADR-0107); as falas citadas vêm das capturas do mantenedor.

| Hora (UTC) | Falante | Reação | Confiança | Quest | Resultado |
|---|---|---|---|---|---|
| 01:46:39 | Bernard | ameaçadora | `NEUTRO` | nova | Escravos: linha neutra (`ABSENCE:WITHHELD`, `TRUST_REQUIRED`) |
| 01:47:19 | Bernard | indiferente | `NEUTRO` | oferecida | "Sim, há um trabalho. Descubram quem roubou um broche do meu balcão…" |
| 01:48:20 | Bernard | indiferente | `NEUTRO` | aceita | "Ótimo. Aguardo a resposta dele." e a linha de diário |
| 01:53:08 | — | — | — | — | Save antigo carregado: ramo novo, a quest volta a nova |
| 01:53:59 a 02:03:19 | Bernard | indiferente e amistosa | `NEUTRO` | oferecida e aceita | Refeita no ramo novo; vários turnos sem as palavras de aceite |
| 02:08:20 | Anomen | cautelosa | `NEUTRO` | passo feito | O fato do passo e a linha de diário |
| 02:09:25 | Bernard | amistosa | **`INTIMO/MILESTONE`** | **resolvida** | Agradeceu, vai mandar alguém às Docas; diário de tarefa concluída |
| 02:10:44 | Bernard | amistosa | `INTIMO/MILESTONE` | resolvida | Escravos: contou que são comprados de traficantes (`rel:arena-slaves`, nada retido) |

Nenhum turno teve recusa do verificador.

## Achados e correções

1. **Pessoa fechada não move a quest.**
   - Na primeira sessão, Bernard rolou reação ameaçadora. Pedir trabalho ali marcaria a oferta, mas ele, irritado, não a diria.
   - Correção: com reação ameaçadora, hostil ou de fuga, a quest não avança e a pessoa não recebe fatos dela (`advance(..., closed=True)`). Teste em `tests/test_narrative_quests.py`.
2. **Quem viu e quem roubou.**
   - Na volta, Bernard disse "Anomen? O batedor novato que passou pelo meu balcão…", confundindo a testemunha com o ladrão. O fato começava com "o que Anomen viu: um batedor novato…".
   - Correção: "O grupo voltou com a resposta de Yarin, o ladrão aposentado: quem furtou o broche foi um batedor de carteiras novato…". O caso da bateria foi atualizado.
3. **Aceite por palavras.** Vários turnos não registraram o aceite, porque o texto não tinha as palavras curadas. O motor fez o que devia; a lista pode crescer conforme o uso.
4. **Save antigo.** A quest voltou ao estado do ponto do save, como previsto na SPEC (REQ-QUEST-008).

## Leitura de variáveis (ADR-0134)

- Em todas as perguntas, a caixa mandou as 5 variáveis da lista; as quatro da quest de Hendak e a inexistente vieram `null`. Isso mostra que a caixa lê só a lista e que a variável ausente não é criada nem vira 0.
- **Limitação achada:** com o jogo aberto, a caixa não relê a lista depois que o serviço a reescreve. Por enquanto, trocar o catálogo pede reabrir o jogo.
- **Prova de leitura com valor:** com o jogo reaberto (02:16:46), a caixa mandou as 7 variáveis da lista nova. A variável global do capítulo, posta no catálogo local só para a prova, veio `1` nas duas grafias do nome; as outras seguiram `null`. Logo:
  - a leitura devolve o valor de uma variável que existe;
  - a ausente vem `null`, não `0`, e não é criada (segue `null` em todas as leituras);
  - o nome não diferencia maiúsculas e minúsculas.

## Verificação do ramo

- Suíte: OK, também com `lupa` e `jsonschema`; `pyflakes` sem avisos.
- `check_historical_adrs` e `check_public_files` OK.
- Bateria de diálogo: 64/64.
