# Evidência S1e — perguntar a habitantes na caixa do jogo (INQUIRY, SPEC-006) (single player, 2026-11-09/10)

**Gate:** S1 (etapa 1, ADR-0113), parte "e": ADR-0116 sobre SPEC-003/004/005/006. **Resultado:** caixa de diálogo no jogo, habitantes pelos dados do jogo, INQUIRY e alternativa no overlay **APROVADOS no laboratório ARM64/VM** (CR-2026-001). O perfil temporário da SPEC-006 ainda **não foi exercitado** no jogo, porque as duas pessoas consultadas têm script name. Single player.
**Executado por:** mantenedor no jogo (cópia `BG2EE-P1`, campanha nova `lab-s1e`) e Claude Code via SSH.

## Preparação

- Inventário de habitantes (`build_area_inventory.py --residents`), gravado fora do repositório: 13 áreas do pacote e 358 criaturas identificadas por script name ou CRE. São 309 habitantes, contando só humanoides não hostis; 47 estão na Coroa de Cobre (`AR0406`), entre eles Bernard (`npc:cre-bernard`), Rumar e Priss.
- Caixa `M_INFAIT.lua` + `INFAITLK.menu` copiadas para `override`. O manifesto fixado foi refeito, porque os dois arquivos novos mudam o modpack (a diferença foi conferida: só eles, com hash igual ao do repositório).
- Pin do pacote 1369 DR na campanha nova. Os habitantes receberam o conhecimento comum (1092 registros `RESIDENCE`, estabelecidos); os companheiros não receberam nada.

## Roteiro e resultado

| Passo | Observado |
|---|---|
| Jaheira no overlay, "quem governa Amn?" | "Não sei dizer. Não faço ideia de quem governa Amn." (`fatos=0`, `nao_sabe=True`) |
| F9 sobre Rumar, mesma pergunta | Rumar: "O Conselho dos Seis…". Perfil `CANONICAL` (tem script name, sem sorteio). Ouvintes: Imoen, Jaheira e Minsc (alcance e linha de visão). |
| INQUIRY | Os três companheiros receberam `org:council-of-six` com base `INQUIRY`. |
| Jaheira de novo | "O Conselho dos Seis. Não pergunte quem são, é proibido saber." (`fatos=1`), sem dizer que viu. |
| Priss, "Conhece o Conselho dos Seis?" | "Conselho dos Seis? Ouvi falar. É um grupo de poder lá em Amn." |

## Problemas encontrados e corrigidos durante o teste

1. **F9 não abria:** o foco do teclado estava no overlay e havia um diálogo nativo aberto. No Mac é preciso Fn+F9. O módulo ganhou diagnóstico no log (`INFAI-TALK-DEBUG`).
2. **Resposta não aparecia na caixa:**
   - O motor só acha arquivos do `override` presentes ao abrir o jogo, e guarda em cache o conteúdo lido na primeira vez.
   - Correção:
     - `INFAIRSP.lua` passou a existir sempre, com resposta vazia, e fica fora do hash do modpack;
     - antes de cada leitura, a caixa descarta o recurso do cache (`EEex_Resource_Fetch` + `dimmDump`).
   - Depois disso, cinco trocas seguidas apareceram na caixa, sem nenhum aviso de resposta perdida no log do jogo.
3. **CRE trocado no save:** o jogo grava `*UMAR` em vez de `RUMAR`. Criaturas sem script name passaram a ser identificadas pelo resto do nome entre os habitantes da área.
4. **Aprendizado do que não foi dito:**
   - Rumar respondeu "Acha? Eu não acho nada…", e o modelo declarou ter usado `org:cowled-wizards`.
   - Com isso, os três companheiros receberam a entrada sem ouvi-la.
   - Correção: só conta entrada nomeada na fala (`NOT_SPOKEN`). Os registros indevidos ficam no banco `lab-s1e` (append-only) como evidência do defeito.
5. **Alternativa:** o overlay passou a repetir as trocas da caixa ("[no jogo] Rumar: …").

## Achados para depois

- **Fala além do fato:** Jaheira, perguntada sobre sua opinião, disse que o Conselho é "uma gangue de velhos…". A opinião combina com a persona, mas "velhos" é um atributo que não está no resumo. O validador só barra nomes desconhecidos; atributos inventados passam (tarefa de validação na SPEC-004).
- **Perfil da SPEC-006 sem teste no jogo:** Rumar e Priss têm script name, então nenhum perfil foi sorteado. Falta testar com Bernard ou outra pessoa sem script name.
- **Tempo de jogo no pedido:** a caixa enviou `game_time: null`; o serviço usa o tempo da observação, então não houve impacto.
- **Prova completa ainda pendente:** o laboratório faz no máximo uma troca por request, com 1 a 8 s de modelo mais cerca de 2 s de SSH. Falta medir a latência ponta a ponta.
