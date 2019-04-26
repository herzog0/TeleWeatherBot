# vai_chover_bot

Bot para o [Telegram](https://telegram.org/) com funcionalidades especiais relacionadas ao clima local dx usuárix.

## Objetivo

O projeto tem por meta avisar as pessoas de forma rápida sobre mudanças no clima, além de tratar de questões em torno de como as pessoas executam suas tarefas diárias dependendo de como o clima está onde vivem.

Boa parte das pessoas hoje possuem um smartphone e neste ao menos um aplicativo de mensagem. Uma premissa estabelecida é a de que as pessoas tendem a dar grande importância para o uso destes aplicativos de mensagens e a usá-los para compartilhar informações diversas. Assim, elaboramos um bot de Telegram que avisa os usuários sobre o clima local dx usuárix.

## Dados Abertos

Para tanto, usamos a [Open Weather Map](https://openweathermap.org/), API aberta para consultas sobre o clima.

## Execução

### Rodando

Para rodar são necessários os tokens de acesso ao [Telegram](https://core.telegram.org/bots) e ao [OpenWeatherMap](https://openweathermap.org/api). Essa variáveis serão recuperadas do ambiente com os nomes `TELEGRAM_TOKEN` e `OWM_TOKEN`. Elas podem ser marcadas com:

```bash
export TELEGRAM_TOKEN=123456789:abcdef_GHIJKLMNOPQ-rstuvwxyz0123456
export OWM_TOKEN=0123456789abcdefghijklmnopqrstuvwxy
```

Ou fazendo um arquivo `.env` com o seguinte conteúdo:

```dotenv
TELEGRAM_TOKEN=123456789:abcdef_GHIJKLMNOPQ-rstuvwxyz0123456
OWM_TOKEN=0123456789abcdefghijklmnopqrstuvwxy
```

E, só então, podemos rodar o bot com:

```bash
make run
```

Obs: note que os tokens utilizados aqui são falsos, servindo apenas como exemplo.

### Build

```bash
make
```

Isso instala as dependências pelo `pip` e compila o byte code para próximas execuções (apesar não ser necessário). Essa etapa não é necessária, já que `make run` já executa o build.

## Desenvolvimento

Para as funções de desenvolvimento, a instalação local do bot é necessária, porém essa etapa já é executada sempre que preciso.

### Testes

```bash
make tests
```

### Instalação

```bash
make install
```

## Próximas funcionalidades

- Previsão do tempo
- Agendamento de tarefas que dependem do clima
- Alerta de mudanças bruscas no clima.

## Arquitetura
![Arquitetura Vai Chover Bot](https://imgur.com/Rt6o1zI)

## Deploy no Cloud (v1)
Abra o cloud console

Entre no cumpute engine e abra a maquina vai-chover-vm por ssh

```bash
cd vai_chover_bot
```

```bash
git fetch
git checkout <tag da nova versão>
```

```bash
htop
```

Ache e mate o processo da versão atual

```bash
nohup make run &
```

Aperte entrer para receber devolta o terminal e feche a janela
