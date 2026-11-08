# Architecture — Dependências externas e licenças

| Projeto | Papel | Estratégia | Situação |
|---|---|---|---|
| Baldur's Gate II: Enhanced Edition | Jogo proprietário instalado pelo usuário | Instalação separada e legítima | Binários/assets não distribuídos |
| EEex (Bubb13/EEex) | Extensão executável de BG2:EE | Referenciar release fixa e documentação, sem copiar código sem checar licença | Hooks a comprovar |
| GemRB (gemrb/gemrb) | Engine alternativo GPL-2.0 | Referência técnica e possível adapter/fork futuro isolado | Não base do MVP |
| WeiDU | Tooling para mods Infinity Engine | Uso como ferramenta externa, observar GPL e avisos | Instalação separada |
| Python / SQLite / STT / TTS | Orquestração e áudio local-first | Escolha por benchmark e licença | Binários/vozes/modelos a selecionar |

**Proposta de estratégia de repositório — pendente de decisão explícita:** projeto novo independente `infinity-ai`, integrações por adaptadores; não fork principal de GemRB/EEex. Se houver código derivado de projeto GPL, revisar obrigações de redistribuição e isolá-lo em projeto compatível. A ausência de licença própria não permite chamar o projeto de open source em sentido jurídico; escolher SPDX permissiva/copyleft antes de incentivar reutilização.
