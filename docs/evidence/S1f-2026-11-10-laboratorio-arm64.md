# Evidência S1f — conhecimento relacional e caixa com companheiros (single player, 2026-11-10)

**Gate:** S1 (etapa 1, ADR-0113), parte "f": ADR-0119 / SPEC-007 sobre ADR-0114, 0116 e 0117.
**Resultado:** conhecimento relacional (público e restrito) e caixa para companheiros com a matriz de Sabedoria/Inteligência **APROVADOS no laboratório ARM64/VM** (CR-2026-001). O frequentador `REGULAR` curado **ainda não foi testado**. Single player.
**Executado por:** o mantenedor, no jogo (cópia `BG2EE-P1`); Claude Code, via SSH.

## Preparação

- **Campanha:** nova e isolada, `lab-s1f`, com banco próprio. Não reutiliza a `lab-s1e` nem o banco padrão.
- **Pacote:** pin do 1369 DR com revisão `sha256:29bd32029a6c1916a50d0a8fdc2fd075d99158340d3838dc8c3b873e94dc9e83`, 13 entradas, incluindo `place:copper-coronet` e as duas relações da Coroa de Cobre.
- **Manifesto:** refeito a cada troca da caixa (`M_INFAIT.lua`). Em todos os inícios do serviço, "live matches pinned: True".
- **Modelo:** Ollama local `qwen3:8b`.

## Roteiro e resultado

| Passo | Observado |
|---|---|
| Bernard (curado, `STAFF`): quem é você, quem é o dono | Disse ser o taverneiro da Coroa de Cobre e que Lehtinan é o dono; usou a relação restrita sobre si. |
| Lehtinan, sem curadoria | Antes da regra das partes: não conhecia Bernard e citou um id inventado. Depois: disse ser o dono e que Bernard cuida da casa para ele. |
| Cliente sem afiliação (`npc:cre-mtown6`) | Conhece o dono (público). Não conhece a função de Bernard (restrita). |
| INQUIRY | 9 eventos `KnowledgeShared`. A relação pública e o lugar chegaram a Imoen, Jaheira e Minsc. A relação restrita `rel:bernard-manages-copper-coronet` **não aparece em nenhum** deles. |
| Caixa com companheiro (clique direito em Jaheira), antes do Conselho | Não sabia quem governa Amn. Correto: só tinha aprendido o dono e o lugar. |
| Bernard fala do Conselho dos Seis | `org:council-of-six` foi aprendido por INQUIRY pelos três companheiros. |
| Caixa com Minsc (Sab. 6 / Int. 8, `rudimentar`) | Só o núcleo popular ("governam Amn, ninguém sabe quem são"), com a voz dele. |
| Caixa com Jaheira (Sab. 14 / Int. 10, `atento`) | Núcleo popular mais o detalhe informado: é perigoso falar deles. Sem as três décadas nem os títulos (camada de estudo). |
| Caixa com Imoen (Sab. 11 / Int. 17, `atento` + estudo completo) | Tem todas as camadas. A resposta foi vaga porque a pergunta foi vaga. |

## Problemas encontrados e corrigidos durante o teste

1. **Pin numa campanha vazia:** o tempo de ancoragem era nulo. Passa a usar o primeiro evento com tempo depois do pin.
2. **Lehtinan não conhecia a relação que o envolve:** as partes de uma relação (`subject_id` e `object_id`) passam a conhecê-la (ADR-0119, item 3).
3. **Id inventado ("F6") numa fala sobre si:** os itens sobre o próprio NPC recebem a marca "(sobre você)". A regra 8 pede o id exato, e o `SELF_CLAIM` aceita o que está nesses itens.
4. **Companheiro sem a matriz:** no primeiro teste, Minsc citou "há décadas", que pertence à camada de estudo. A caixa passou a enviar Sabedoria e Inteligência da criatura. A primeira tentativa leu campos inexistentes da ficha e mandou 0. A correção usa `EEex_Sprite_GetActiveStats` (`m_nWIS` e `m_nINT`).
5. **Pedido de companheiro respondido de novo** depois de reiniciar o serviço: os ids atendidos passam a ficar num arquivo local ao lado do banco.

## Achados para depois

- **Atributos de terceiros inventados:** o cliente descreveu Lehtinan com um traço de caráter que não está no pacote. O validador só confere nomes e afirmações sobre si.
- **Exemplos nas regras 2, 7 e 8:** os exemplos de prompt removidos nesta branch fazem falta. A recomendação é restaurá-los com exemplos fora do mundo do jogo.
- **Frequentador `REGULAR` curado:** falta uma curadoria conferida pelo mantenedor para fechar o roteiro da SPEC-007.
- **Carregar o save não recarrega a caixa:** o motor só lê o módulo quando o jogo abre. Depois de enviar a caixa, é preciso fechar e abrir o jogo.
