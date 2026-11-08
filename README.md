# Infinity AI

Infinity AI é um projeto experimental de extensão narrativa para campanhas cooperativas privadas de **Baldur’s Gate II: Enhanced Edition** (BG2:EE). A proposta é que o mundo reaja às escolhas e ao histórico dos personagens. Por exemplo, uma decisão do grupo pode gerar um rumor que chega a uma facção e muda a forma como ela recebe os personagens em um encontro futuro.

## Modos de jogo planejados

| Modo | Experiência |
| --- | --- |
| **Original** | Jogar a campanha clássica, preservando sua progressão. |
| **Living World** | Jogar em um mundo persistente em que rumores, reputações, facções e eventos evoluem com o tempo e com as ações do grupo. |

Cada modo terá seus próprios arquivos de campanha. No Living World, a cronologia de Forgotten Realms serve de referência. As consequências das intervenções dos jogadores ficam registradas para que o grupo possa entender como a campanha se desviou da história de referência.

## Como a integração foi pensada

- **BG2:EE no Windows.** A primeira prova de conceito parte de uma instalação limpa do jogo e acrescenta o EEex e uma ponte de integração. A meta é validar essa configuração em uma sessão cooperativa com dois clientes.
- **Autoridade dividida.** O host do jogo confirma mudanças mecânicas. O Infinity AI mantém a memória e o estado narrativo da campanha. A ponte valida as operações entre os dois.
- **Regras primeiro.** Código determinístico governa as regras e as mudanças de estado. Um modelo de linguagem local pode ser acionado sob demanda para tarefas narrativas, como formular um diálogo a partir dos fatos conhecidos por um NPC.

## Estado do projeto

O projeto está em fase de especificação e validação técnica. A integração multiplayer com EEex ainda precisa ser demonstrada de ponta a ponta. A próxima etapa é validar a sequência **BG2:EE limpo → EEex → ponte → sessão com dois clientes**. Este repositório ainda não oferece uma versão jogável.

## Acompanhar e contribuir

Use as [Issues](https://github.com/oamado31-source/infinity-ia/issues) para registrar problemas reproduzíveis ou propostas concretas e as [Discussions](https://github.com/oamado31-source/infinity-ia/discussions) para conversar sobre design e arquitetura. Para propor uma mudança no repositório, abra um pull request descrevendo o objetivo e os testes ou evidências de validação.

## Licença e dependências

O código, a documentação original e os exemplos sintéticos do Infinity AI que podem ser licenciados por seus titulares são distribuídos sob a [Apache License 2.0](LICENSE) (`Apache-2.0`), conforme [ADR-0112](docs/decisions/ADR-0112-licenca-apache-2.0-e-direitos-de-terceiros.md). Consulte também o [NOTICE](NOTICE) e a [política de licenciamento e terceiros](docs/architecture/licensing.md).

**A licença não cobre propriedade intelectual de terceiros.** Baldur’s Gate II: Enhanced Edition, Forgotten Realms, Infinity Engine, EEex, GemRB, marcas, recursos gráficos/sonoros, dados e mods externos permanecem sujeitos aos direitos e termos de seus respectivos titulares. O projeto é independente, não distribui esses componentes e não é afiliado ou endossado por seus proprietários. Para testes de integração, é necessária uma instalação própria e legitimamente obtida do jogo.
