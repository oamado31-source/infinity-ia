# Evidência S1f — conhecimento relacional e caixa com companheiros (single player, 2026-11-10)

**Gate:** S1 (etapa 1, ADR-0113), parte "f": ADR-0119 / SPEC-007 sobre ADR-0114, 0116 e 0117.
**Resultado:** conhecimento relacional (público e restrito) e caixa para companheiros com a matriz de Sabedoria/Inteligência **APROVADOS no laboratório ARM64/VM** (CR-2026-001). O frequentador `REGULAR` curado (Salvanas) foi testado e aprovado. Single player.
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

## Estatuto local e ajustes de fala (ADR-0120)

O teste continuou na mesma campanha `lab-s1f`, com o serviço reiniciado a cada ajuste. A caixa do jogo não mudou.

| Passo | Antes | Depois |
|---|---|---|
| Lorde Jierdan (ficha não humanoide, curado `HABITANTE`) | `habitante=False`, 0 assuntos; enrolava ("sei quem é" sem dizer quem) | `estatuto=HABITANTE`, 6 assuntos; disse que vive ali e é nobre de Athkatla, e citou Lehtinan como dono |
| Nobre `copcust3` | "Não sou de cá…" | "Sou Nobre, vivo aqui." |
| Campesino: onde mora | "A taverna é minha casa. Trabalho aqui…" | "Minha casa é em Athkatla, perto da Coroa de Cobre." |
| Campesino: trabalha aqui? | "Trabalho aqui como carregador." (inventado) | "…trabalho na cidade. Sou carregador." |
| "dono dessa taverna/do local" | `NOT_SPOKEN` em 5 casos | `inquiry=OK` ("taverna" e "local" valem pela Coroa de Cobre; o nome pode vir da pergunta) |
| Cópia e recitação | "Sou humano, vivo em Athkatla e estou aqui na Coroa de Cobre." | "Moro em Athkatla, sim." |
| Salvanas / Nobre: quem governa Amn? | camada popular copiada quase palavra por palavra | "É o Conselho dos Seis. Ninguém sabe quem são eles." / "Conselho dos Seis. Ninguém sabe quem são os seis." |

**Frequentador `REGULAR` curado (fecha o roteiro da SPEC-007):** Salvanas, com `place:copper-coronet:REGULAR` conferido pelo mantenedor, foi perguntado "Você está sempre por aqui? Quem cuida da taverna no dia-a-dia?" e respondeu "Estou aqui sempre que posso. Bernard cuida do dia-a-dia.". O log registrou `entradas=['rel:bernard-manages-copper-coronet']` e `assuntos=7` (antes 6). A relação restrita não foi ensinada a ninguém: há 0 registros dela no banco `lab-s1f`.

Ainda não foi visto no jogo um viajante ou forasteiro gerado: os genéricos consultados sortearam `HABITANTE`.

## Afirmações sobre outras pessoas (ADR-0121, 2026-11-13)

O teste usou o serviço da branch do ADR-0121 na mesma campanha `lab-s1f`, sem reabrir o jogo.

| Pessoa e pergunta | Resultado |
|---|---|
| Campesino: "Quem é o taverneiro?" (só com o código da recusa) | as duas tentativas foram recusadas (`THIRD_PARTY:ROLE`); fala de reserva "Hum? Disso eu não sei." |
| Campesino: mesma pergunta, com a segunda tentativa explicada em português | 1ª recusada (`THIRD_PARTY:ROLE`); 2ª "Taverneiro? Lehtinan é o dono da Coroa de Cobre.", INQUIRY OK |
| Nobre: "Como é o Lehtinan?" | "Lehtinan é o dono da Coroa de Cobre.", sem traço inventado |
| Minsc (rudimentar): "Há quanto tempo o Conselho governa?" | "Conselho? Não entendo disso.", sem duração inventada |
| Bernard: "O que você acha do Lehtinan?" | "Lehtinan é o dono, e eu só faço o que ele quer.", papel com base e postura própria |

## Achados para depois

- **Atributos de terceiros inventados:** o cliente descreveu Lehtinan com um traço de caráter que não está no pacote. Tratado no ADR-0121 (papel, traço, número e regra geral sobre outra pessoa precisam estar no conhecimento; opinião própria passa).
- **Exemplos nas regras 2, 7 e 8:** restaurados (ADR-0120, item 8), com o pedido de usar só o fato que responde à pergunta.
- **Viajante e forasteiro gerados:** ainda não apareceram no jogo; falar com mais clientes da taverna.
- **Opiniões inventadas:** Jierdan disse que "governa quem tem dinheiro". Pelo ADR-0121, essa regra geral passa para quem conhece Amn ("a riqueza vale mais que tudo") e é recusada para quem não conhece.
- **Carregar o save não recarrega a caixa:** o motor só lê o módulo quando o jogo abre. Depois de enviar a caixa, é preciso fechar e abrir o jogo.
