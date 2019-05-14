# Estratégia de testes

## Níveis de teste

Além de efetuar o teste de aceitação com algumas pessoas, teste para avaliar características mais técnicas do software serão realizados antes do deploy (teste de unidade, de integração e de sistema).

#### Teste de unidade
Para testar os módulos que estão dentro do projeto, pesquisaremos alguma ferramenta para testes unitários em Python3.
#### Teste de aceitação
Como não temos especificamente um cliente que pediu nosso software, nós do grupo escolheremos pessoas próximas que aceitariam testar nosso projeto e que possuem alguma relação com previsão de tempo. Versões alfa e beta previstas.

## Tipos de teste
Por conta de boa parte de nosso projeto usar software de terceiros (telegram, google API, Weather API), teste de desempenho, de segurança e configuração não serão realizados.
#### Teste Funcional
Para analisar se os requisitos do sistema estão se comportando tal como foram especificados.
#### Teste de Usabilidade
Por se tratar de aplicação mobile, a usabilidade se torna um item importante. A comunicação de bot com o usuário, bem como a disponibilização de suas funções, deve ser bem compreendida pelo usuário.

## Técnicas de teste

#### Caixa Branca
Para facilitar a inspeção de código e poder melhor localizar onde possíveis erros possam estar. Ajuda a melhor compreender a estrutura interna do projeto durante os testes.
