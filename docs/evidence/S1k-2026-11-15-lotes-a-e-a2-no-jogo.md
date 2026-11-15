# Evidência S1k — lotes A e A2 da enciclopédia no jogo (single player, 2026-11-15)

**Gate:** etapa 4 do plano de conhecimento (testes reais), SPEC-008/009, CR-2026-013 a CR-2026-016.
**Resultado:** com as correções desta evidência, Bernard respondeu com fidelidade ao pacote sobre:
- o bairro onde está;
- o governo de Amn;
- uma cidade vizinha (Murann);
- a história antiga (Maztica, a Praga da Costa).

A tooltip do nome deixou de seguir o cursor. A ausência tipada respondeu por código. **APROVADO no laboratório ARM64/VM**, com os ajustes registrados abaixo.
**Executado por:** mantenedor no jogo (cópia `BG2EE-P1`, campanha `lab-s1f`) e Claude Code via SSH (serviço no Mac).

## Preparação

- **Pacote:** 49 entradas (lotes A e A2). Pin refeito na `lab-s1f` a cada ramo novo, com as revisões `sha256:77c6c0ad4486` e, depois da correção do bairro, `sha256:25c53d5635ef`.
- **Caixa:** reinstalada três vezes com `talk_poc.py --deploy`.
- **Manifestos:** a cada instalação, a comparação mostrou a mesma build, com só os arquivos da caixa diferentes. Ficaram fora do repositório: `s1j-manifest-2026-11-15c`, `-15d` e `-15e-pinned.json`.
- **Serviço:** `dialogue_service.py --voice`, com a ausência tipada aplicada por cima da main (PR separado).

## Achados e correções

| Achado no jogo | Causa | Correção |
|---|---|---|
| "Que bairro é esse?" casou com "Portões" | o bairro (Favelas, AR0400) não contava como "o lugar onde está" a partir da Coroa de Cobre (AR0406) | as Favelas passam a incluir AR0406; o lugar mais específico é "o estabelecimento" e o que contém mais áreas é "o bairro" (alias "bairro/distrito") |
| Os Magos Encapuzados saíram do prompt | cidades vizinhas e a entrada "Faerûn" ocupavam vagas na alternância | regiões fora da cadeia de onde a pessoa está e o continente vão para o fim da fila |
| "É o bairro da Ponte" | a frase de localização não dizia o bairro, e o modelo chutou | "está na Coroa de Cobre, nas Favelas" |
| Primeira tentativa recusada por "Favela" | o verificador só conhecia "Favelas" | um nome conhecido vale no singular e no plural |
| "Como é o dinheiro aqui?" disparou suborno (e um YIELD) | o gatilho casava com qualquer menção a moeda, ouro ou dinheiro | suborno exige uma oferta ("te pago", "pegue estas moedas", "20 peças de ouro") |
| Murann: "não sei" | Bernard tem o núcleo popular, mas a entrada não cabia nas 12 vagas | CR-2026-016: o que a pergunta nomeia, entre o que ele sabe, sobe na fila |
| Nome da criatura seguindo o cursor na caixa | a tooltip já estava aberta no clique e o jogo pausado não a fechava | gancho do EEex para suprimir, mais o fechamento da tooltip aberta, como no B3EffMen do EEex; também uma camada invisível na tela toda |

## Respostas finais (Bernard, reação cautelosa, camada comum)

- **Bairro:** as Favelas, o bairro mais pobre e mal-afamado de Athkatla. Fonte: `place:slums`, camada POPULAR.
- **Quem manda em Amn:** o Conselho dos Seis, sem saber quem são. Fonte: `org:council-of-six`.
- **Murann:** só o núcleo popular (o porto dos marinheiros de Amn). Fonte: `region:murann`, pelo CR-2026-015.
- **Maztica e Praga da Costa:** as camadas POPULAR das entradas.
- **"Você tem filhos?":** resposta neutra pela ausência tipada (`ABSENCE:NOT_DEFINED`), sem chamar o modelo.
- **Vínculo de gerente:** ficou retido o tempo todo (`CAUTIOUS`), como manda a divulgação (ADR-0131).

## Reação (ADR-0125)

- **Rolagens:** duas seguidas deram ameaçador (total 16); com a disposição fechada, tudo ficou retido. Depois de um carregamento dentro do jogo, saiu cauteloso (13).
- **Dados:** a distribuição foi conferida em 1.000 rolagens e segue a curva de 2d10.

## Pendências registradas

- **Moedas:** o modelo afirmou detalhes de moedas que contradizem a camada, como prata e ouro "raro" e o preço da bebida. Falta uma checagem de contradição de detalhe.
- **Sessão:** o contador de sessão da caixa volta a 0 quando o jogo é reaberto. A reação de uma sessão anterior no mesmo save é reaproveitada.
- **Aprendizado em conversa:** o núcleo popular calculado (cidades vizinhas) não passa adiante (`SPEAKER_DOES_NOT_KNOW`).
- **Pin defasado:** carregar um save antigo abre um ramo com o pin anterior, e o serviço não avisa ninguém.

## O que não entrou no repositório

Saves, texto ou áudio do jogo, manifestos e o banco da campanha ficaram fora do repositório. As falas acima são resumos, e o log registra só ids de entrada e códigos.
