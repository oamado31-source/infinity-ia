# Evidência S2j — CR-2026-035: a persona dos NPCs no jogo (2026-11-25)

**Gate:** etapa 1, single player, save descartável, Coroa de Cobre.
**Resultado:** **aprovado no laboratório ARM64/VM.** Mantenedor: "Fiz vários testes, gostei dos resultados".

**Executado por:** mantenedor, no jogo (cópia `BG2EE-P1`, campanha `lab-s1f`), e Claude Code. Preparação:
- pacote refixado no ramo `br-687011c034ee`: `REVISION_CHANGED` → `MATCH`, revisão `sha256:9bfb43a57bf8`, 172 entradas;
- serviço reiniciado com `--claude`: 30 identidades curadas carregadas.

## As falas

Do log: reação, quem respondeu e motivo.

| # | NPC | Reação | Quem respondeu | Resultado |
|---|---|---|---|---|
| 1 | Lehtinan, sobre os escravos | cautelosa | código (`ABSENCE:WITHHELD`) | "Disso eu não falo.": o segredo confidencial da arena é cortado antes do modelo. Agora com SAB 12 e INT 13, nível "atento" (antes, SAB 6: "não entendo isso") |
| 2 | Lehtinan, "Você é um velho avarento!" | cautelosa | Ollama | "Taverna não é para quem não tem grana. Quer beber? Pague ou saia.": a persona (desdém por quem não tem dinheiro) no tom |
| 3 | Salvanas, sobre os Ladrões das Sombras | indiferente | Ollama | usou `org:shadow-thieves` ("São os que mandam na cidade"): antes, dizia que não conhecia |
| 4 | Rumar, "Você trabalha aqui?" | amistosa | Claude | nega trabalhar ali, pomposo ("não sou de servir a ninguém nesta taverna") |
| 5 | Priss, "Você trabalha aqui?" | indiferente | Ollama | "Não, só estou aqui com Rumar." |
| 6 | Leão de Chácara, "Como é trabalhar aqui?" | indiferente | Ollama | "Mantenho a ordem, nada mais. Se quiser ficar, fique quieto.": intimidador e calado, como na persona |
| 7 | Surly, "Como é trabalhar aqui?" | indiferente | Ollama | "Só bebo e deixo a cabeça em paz.": rabugento, como na persona |
| 8 | Nalia e Anomen | ameaçadora / amistosa | Ollama / Claude | sem curadoria (fora deste lote); a camada seguiu a reação |

**Custo do Claude no mês até aqui:** US$ 0,0012.

## O que apareceu no caminho

1. **Respostas de segredo (ausência tipada) apareciam no log como fala do Ollama**, porque não marcavam "código". Corrigido: `model='code'`.
2. **Rumar disse estar "só de passagem" e ficar "um pouco nas Favelas".** Pela curadoria, ele é habitante de Athkatla, escondido da esposa na Coroa. Foi uma leitura livre do modelo sobre onde ele está, e não violou nenhuma regra do validador. Fica anotado para a curadoria dele.
3. **"Grana" (fala 2)** é gíria moderna para Faerûn. Se repetir, cabe uma regra de vocabulário de época.
4. **Hendak, Madame Nin, Unger e Zaviera** não foram testados nesta rodada. Suas personas seguem como aprovadas na proposta; Unger e Zaviera continuam marcados para conferir.

## Verificação do ramo

- Suíte com 676 testes OK, também com `lupa` e `jsonschema`; `pyflakes` sem avisos.
- `check_historical_adrs` e `check_public_files` OK.
- **Bateria:** 69/69, com o caso novo `salvanas-ladroes-das-sombras`.
  - Alguns casos demoraram até 11 s nessa rodada; rodados de novo, voltaram a 1,3–1,8 s (lentidão passageira do Ollama).
- Arquivos copiados para o checkout do laboratório e conferidos byte a byte.
