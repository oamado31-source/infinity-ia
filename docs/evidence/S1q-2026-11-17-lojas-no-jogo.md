# Evidência S1q — quem vende não nega o que vende (ADR-0132) no jogo (single player, 2026-11-17)

**Gate:** ADR-0132.
**Resultado:** **APROVADO no laboratório ARM64/VM** (mantenedor: "Ótimo, agora podemos fechar com o teste aprovado"). Bernard confirmou quartos, cervejas e espadas com os preços da loja da Coroa de Cobre, sem negar nada e sem recusa do verificador, em três rodadas. As duas primeiras mostraram problemas, corrigidos antes da terceira.
**Executado por:** mantenedor no jogo (cópia `BG2EE-P1`, campanha `lab-s1f`) e Claude Code via SSH (serviço no Mac, `--voice --carry-pin`).

## Preparação

- **Pacote:** sem mudança (147 entradas, `sha256:dd158cc00b9d`, lote H).
- **Inventário de lojas:** `build_area_inventory.py --stores` leu a cópia do jogo da VM só em memória e gravou o resultado fora do repositório, em `~/.infinity-ai/knowledge/install-…/stores.pt_BR.json`. Encontrou 19 vendedores entre os 358 habitantes.
  - **Diálogo de Bernard:** abre as lojas `BERNARD` e `BERNARD2`, as duas do tipo estalagem e com o nome "Coroa de Cobre".
  - **Quartos:** os dois que a loja aluga.
  - **Bebidas:** cinco.
  - **Itens:** armas, armaduras, escudos, joias, poções e pergaminhos.
- **Serviço:** a linha de partida mostra `vendedores: 19`.

## Turnos

Bernard, reação amistosa, 109 assuntos. O log não guarda as falas (ADR-0107); elas vêm das capturas de tela do mantenedor. Todos os sete turnos saíram com status `OK` e sem recusas.

| Rodada | O que mostrou | Ajuste feito |
|---|---|---|
| 1 (16:31) | **Bebidas:** leu a lista inteira. **Espadas:** "Sim, vendo espadas", mas citou munição (Bala, Flecha…) "a preço a combinar" e nenhuma espada. | O plural "espadas" passa a achar "Espada Longa". Itens de preço zero saem da lista. "1 peça de ouro" no singular. O vendedor ganha uma regra no prompt: citar só o que foi perguntado. |
| 2 (16:36) | **Espadas:** citou três espadas com os preços da loja e disse que "as +1 são mais caras". **Quartos:** "Sim, temos quartos", com os dois preços por noite da loja. Os preços conferem com o inventário local e não são copiados aqui (REQ-CANON-004). | O mantenedor pediu que o vendedor não fale em "+1". O bônus de jogo nunca chega ao NPC: os itens com bônus viram "peças especiais, encantadas e de alta qualidade, bem mais caras", com o menor preço do tipo perguntado. |
| 3 (16:42) | Respondeu de primeira, já com as peças especiais. | Teste aprovado. |

## Pendências anotadas

- **A lista de bebidas:** perguntado sobre cerveja, Bernard ainda pode citar todas as bebidas. Os preços estão certos, mas a fala fica longa.
- **Escolha da loja pelo capítulo:** Bernard tem duas lojas, e a primeira versão usa a união das duas, pela menor margem.
- **Ajuste de preço** por carisma e reputação fica de fora.
