# Proposta (a confirmar) — Novo repositório independente versus fork de engine

**Pergunta do usuário:** seria melhor aproveitar repo 'original do Infinity' por fork ou iniciar repo novo e importar só o relevante?

## Recomendação: repo novo independente

1. O **código-fonte do motor proprietário BG2:EE** não é um repositório aberto que possamos clonar e publicar.
2. **GemRB** é uma reimplementação GPL-2.0 distinta, com arquitetura e compatibilidade próprias, não a base do BG2:EE/EEex inicialmente aprovado. Forká-lo agora cria uma migração de motor não prevista.
3. **EEex** é um extensor externo, utilizado como dependência do BG2:EE Windows, não uma fundação de produto que deveríamos incorporar integralmente; verificar licença antes de copiar código.
4. Um projeto independente concentra os ADRs/SPECs, memória, rede privada, voz, Quest bridge e adaptadores. O motor fica fora, versionado por manifesto.
5. Caso uma mudança real do EEex ou GemRB seja imprescindível, criar fork técnico separado e enviar PR upstream, documentando compatibilidade e licença.
6. Nunca redistribuir binários, saves, assets, diálogos originais, mapas ou sprites protegidos da Beamdog/FR.

**Status:** RECOMENDAÇÃO EM ANÁLISE. A escolha pela estratégia de repositório não deve ser marcada 'aprovada' sem confirmação do usuário.

## Próxima ação após a escolha

Se a recomendação for ratificada, abrir novo ADR sobre autonomia do repositório e pinagem de upstream, sem transformar GemRB/EEex em dependências copiadas. Se for escolhido fork, exige nova análise de qual upstream, compatibilidade, licença e migração da arquitetura atual.
