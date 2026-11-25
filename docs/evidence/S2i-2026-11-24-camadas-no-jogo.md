# Evidência S2i — ADR-0147, fase 2: as camadas das falas no jogo (2026-11-24)

**Gate:** etapa 1, single player, save descartável, Coroa de Cobre.
**Resultado:** **aprovado no laboratório ARM64/VM.** Cada fala saiu pela camada que a regra manda: o código, o Ollama ou o Claude.

**Executado por:**
- mantenedor, no jogo (cópia `BG2EE-P1`, campanha `lab-s1f`);
- Claude Code: serviço reiniciado com `--claude`, teto de US$ 5 por mês e a chave no ambiente do anfitrião. Nada mudou na VM: só o serviço do Mac.

## As falas

O log de cada fala diz a reação, SAB, INT e quem respondeu (`fala_por=`).

| # | NPC | Reação | SAB / INT | Fala do jogador | Quem respondeu | Por quê |
|---|---|---|---|---|---|---|
| 1 | Bernard | ameaçadora | 9 / 9 | pergunta aberta | Ollama | reação negativa nunca vai para o Claude; com a quest do broche oferecida, nem as perguntas simples vão para o código |
| 2 | Salvanas | amistosa | 7 / 9 | "Qual é o seu nome?" | **código** ("Salvanas.") | pergunta simples, sem chamar modelo |
| 3 | Salvanas | amistosa | 7 / 9 | "O que você sabe sobre os Ladrões das Sombras?" | **Claude Haiku** | reação amistosa (D6), mesmo com SAB e INT medianas; mantenedor: "bem elaborada a resposta" |
| 4 | Garoll | ameaçadora | 9 / 9 | "Qual é o seu nome?" | Ollama ("Garoll... tá vendo? Garoll, rá, rá.") | jeito de falar curado (bêbado): a pergunta simples fica com o modelo para não perder a voz dele |
| 5 | Lehtinan | cautelosa | 6 / 9 | insultos | Ollama, curto ("Não entendo isso.") | reação negativa: nunca Claude |

**Custo no mês:** US$ 0,0004, no arquivo local de gasto, que só guarda o valor.

## O que apareceu no caminho

1. **Salvanas não conhece os Ladrões das Sombras.**
   - A resposta é honesta: a entrada não está no que ele sabe pelas regras de conhecimento.
   - Para um frequentador da Coroa em Athkatla, porém, é estranho não conhecer.
   - Fica para a curadoria dos NPCs (frente 2).
2. **Lehtinan tem SAB 6 no jogo.**
   - Isso dá a ele o nível rudimentar (ADR-0117), que manda dizer "não entendo disso" diante de assunto complicado.
   - O dono da Coroa falar assim mostra por que a curadoria pode corrigir INT e SAB (D2), como no caso de Hendak.
   - Fica para a frente 2.
3. **A reação ao insulto saiu cautelosa, não hostil.**
   - A frase misturava ameaça ("merece perder a cabeça") e insulto.
   - A regra de conduta da ADR-0125 leu primeiro a ameaça.
   - Não é das camadas: fica anotado.

## A bateria com as camadas

`run_eval.py --camadas --provider claude --runs 3`:
- **67 de 68 casos:** 188 falas pelo Ollama e 16 pelo Claude, por US$ 0,003;
- **o caso que falhou** foi o do nobre de INT 17 (as décadas do Conselho dos Seis): o Claude disse "não sei" depois de a primeira resposta ser recusada por citar número sobre terceiros;
- **rodado de novo**, passou 5 de 5 com as camadas e 4 de 5 só com o Claude: é variação. A primeira resposta desse caso costuma ser recusada, e a regra do número sobre terceiros merece revisão à parte;
- **sem camadas**, a bateria segue 68 de 68: a troca no motor não mudou nada para o Ollama.

## Verificação do ramo

- Suíte com 671 testes OK, também com `lupa` e `jsonschema`; `pyflakes` sem avisos.
- `check_historical_adrs` e `check_public_files` OK.
- **Testes novos** (`tests/test_layers.py`):
  - a camada por INT, SAB e reação;
  - as perguntas simples sem modelo;
  - a descida para o Ollama;
  - a subida por refinamento, que nunca acontece com reação negativa;
  - nada vai para o Claude sem ele ligado;
  - o Claude recebe o mesmo texto já filtrado que o Ollama receberia;
  - o teto mensal;
  - a correção de INT e SAB na curadoria.
- Arquivos copiados para o checkout do laboratório e conferidos byte a byte.
- **Limite:** os companheiros ainda não têm confiança registrada; por enquanto seguem só INT e SAB.
