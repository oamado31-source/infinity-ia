# Domain — Glossário controlado

| Termo | Definição normativa |
|---|---|
| BG2:EE | Baldur's Gate II: Enhanced Edition; primeiro jogo-alvo, não distribuído no repositório |
| Infinity Engine | Motor original proprietário dos jogos clássicos, distinto de GemRB |
| EEex | Extensor executável externo do motor Enhanced Edition; capability por build |
| GemRB | Reimplementação aberta, motor alternativo e referência técnica, não base inicial do Infinity AI |
| Bridge | Adaptador de leitura/comunicação entre motor/EEex e backend |
| Capability | Operação suportada e **comprovada** para build/modpack/bridge e configuração |
| Host | Autoridade mecânica da sessão; não equivale a todos os jogadores |
| PC | Personagem controlado por jogador |
| NPC | Personagem não jogador, sujeito a ACL e memória falível |
| ADR | Registro arquitetural imutável após aprovação; substituições via novo ADR |
| DEC | Decisão rastreável de produto/arquitetura |
| SPEC | Contrato de comportamento observável versionado por feature |
| CR | Solicitação de mudança, com diff, riscos, migração e aprovação |
| Receipt | Evidência autenticada pelo host de ação realizada; texto de LLM não conta |
| Epoch | Versão causal/temporal de sessão ou checkpoint; isola restores e branches |
| Knowledge Pack | Dados curados/canon, por ano DR e fontes |
| DR | Dalereckoning, calendário usado em Forgotten Realms |
| ACL | Política de acesso por audiência, finalidade, momento e titular |
| UNKNOWN | Dado insuficiente; não implica false nem autorização |
| Push-to-talk | Abertura do microfone apenas enquanto o jogador aciona controle intencional |
| STT | Speech-to-text, reconhecimento/transcrição da fala do jogador |
| TTS | Text-to-speech, síntese de voz do NPC, opcional |
| LLM | Modelo de linguagem; não é fonte de autoridade mecânica ou canônica |
| Fork | Cópia Git de projeto em outro namespace; upstream separado |
| Pull Request | Proposta de integração submetida à revisão, sem alteração automática do `main` |
