# ADR-0109 — Assets legítimos, escopo canônico por ano e mapa BG2:EE

**Estado:** APROVADA COMO POLÍTICA / ESCOPO em 2026-11-07, com base no questionário Q01–Q28 ratificado pelo idealizador.  
**Decisões:** DEC-017 / Q14=B, Q16=B, Q19=B, Q27=B. **Baseline:** Discovery v10.6 → SDD v11.0.  
**Referências anteriores:** DEC-009/010/017/023–026/050/060–063/099–104; Q14, Q16, Q19, Q27.  
**Gate:** documentação é política aprovada, **não uma capability comprovada no BG2:EE/EEex**.

## Contexto e alternativas

O questionário consolidado registrou escolhas explícitas para evitar bloqueio indefinido do Discovery. A opção escolhida não elimina mecanismos de segurança nem substitui ADRs anteriores: ela restringe a estratégia de implementação do MVP e da V1.

## Decisão vinculante

1. Não redistribuir arquivos binários, diálogos, sprites, saves ou recursos protegidos de BG2:EE, EET ou mods sem licença expressa; referenciar instalação legítima local.
2. Bibliotecas externas somente mediante inventário de licença, origem, versão, hash e compatibilidade; sem vendoring automático de EEex/GemRB.
3. Primeiro pacote canônico: ano-base 1369 DR (DEC-023) como hipótese fixada para teste; regiões exploráveis e efetivamente confirmadas na build inicial de **BG2:EE**, começando pelo recorte Athkatla/área acessível; a segunda região será escolhida após inventário de mapas e fontes.
4. Quest original: mapear **uma** quest curada após read-only validado; não vasculhar flags genericamente nem antecipar spoilers.
5. Eventos pessoais e paralelos opcionais N1/N2 antes de N3; o usuário poderá fornecer enredo de teste, sujeito a autorização de impactos e proveniência. 

## Consequências

- Requisitos nas SPECs devem citar este ADR e a pergunta de origem, com critério de aceite observável.
- Recursos mecânicos dependem de capability verificada na build do host, consentimento, idempotência e recibos; caso contrário `UNKNOWN` ou `BLOCKED_CAPABILITY`.
- Qualquer modificação material desta política deverá criar um ADR novo, mantendo este arquivo inalterado.
- Testes unitários sintéticos nunca serão descritos como validação de bridge, jogo ou multiplayer real.
