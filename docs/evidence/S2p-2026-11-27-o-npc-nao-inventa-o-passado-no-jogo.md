# Evidência S2p — CR-2026-037: o NPC não inventa o passado, no jogo (2026-11-27)

**Gate:** etapa 1, single player, save descartável, Coroa de Cobre (AR0406).
**Resultado:** **aprovado no laboratório ARM64/VM.**

**Executado por:** mantenedor, no jogo (cópia `BG2EE-P1`, campanha `lab-s1f`), e Claude Code.

**Preparação:**
- o código e a quest do broche foram copiados para o checkout do laboratório e conferidos byte a byte;
- o serviço foi reiniciado sem quest local de teste;
- o jogo partiu do save da S2o, em que o broche estava só oferecido e Bernard tinha conversas anteriores.

## O que passou

| # | Fala | Log | No jogo |
|---|---|---|---|
| 1 | Bernard, "Tem trabalho para nós?" | `lembra=5`, `bernard-brooch=OFERECIDA` | Oferece o trabalho e manda perguntar a Unger, "um freguês antigo que não perde nada". Não diz que o broche foi resolvido, nem que já falou com alguém, nem confunde Unger com o ladrão. |
| 2 | Bernard, "ok, vou falar com ele" | `NarrativeQuestAccepted` | Aceita, com a linha do diário que manda falar com Unger |
| 3 | Unger, "Você viu quem roubou o broche do balcão?" | `NarrativeQuestStepDone` | Conta do rapaz novato e do receptador nas Docas, com a linha do diário |
| 4 | Bernard, "Unger viu o batedor que vendeu o broche nas Docas" | `NarrativeQuestResolved`, confiança `INTIMO/MILESTONE` | Agradece e manda alguém às Docas; o diário diz "Tarefa concluída" |

- Todas as falas saíram do modelo local (`qwen3:30b-a3b`).
- Nenhum erro de banco na sessão.

## O que apareceu no caminho

1. **Yarin era difícil de achar.**
   - O mantenedor não o achou no mapa: ele fica no canto de cima, a uns 725 px de Bernard.
   - A quest passou a mandar falar com **Unger Colinaescura**, que bebe ao lado do balcão (CR-2026-037, item 4).
2. **Na primeira rodada com Unger, Bernard o chamou de "o batedor de carteiras novato".**
   - Na oferta, o suspeito vinha logo antes do nome de Unger.
   - A oferta foi reescrita, separando o ladrão desconhecido da testemunha. A bateria ganhou a checagem dessa mistura, e nenhuma de 30 rodadas misturou. Na segunda rodada no jogo, passou.
3. **A checagem do contato passado não disparou no jogo.** Na bateria, ela pegou e corrigiu um "já falei com Yarin" e um "já falei com Unger".
4. **Detalhes pequenos, sem correção:**
   - logo depois do aceite, Bernard disse "ainda estou esperando a resposta dele";
   - na entrega, disse "mandei alguém", e não "vou mandar".

   A checagem do contato só vale para uma pessoa nomeada, por isso "mandei alguém" passa.

## Verificação do ramo

- A suíte passa inteira (767 testes, com `lupa` e `jsonschema`), e `pyflakes` não dá avisos.
- `check_historical_adrs` e `check_public_files` passam.
- **Bateria de diálogo:**
  - 70 de 70 casos, com Unger e a oferta nova;
  - os casos do broche passam 10 de 10 e 15 de 15.
- **O teste de concorrência da CR-2026-036** agora segura a trava de verdade, e confirma que a gravação espera.
