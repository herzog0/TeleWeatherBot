# vai_chover_bot

Bot para o [Telegram](https://telegram.org/) com funcionalidades especiais relacionadas ao clima local dx usuárix.

## Objetivo

O projeto tem por meta avisar as pessoas de forma rápida sobre mudanças no clima, além de tratar de questões em torno de como as pessoas executam suas tarefas diárias dependendo de como o clima está onde vivem.

Boa parte das pessoas hoje possuem um smartphone e neste ao menos um aplicativo de mensagem. Uma premissa estabelecida é a de que as pessoas tendem a dar grande importância para o uso destes aplicativos de mensagens e a usá-los para compartilhar informações diversas. Assim, elaboramos um bot de Telegram que avisa os usuários sobre o clima local dx usuárix.

## Dados Abertos

Para tanto, usamos a [Open Weather Map](https://openweathermap.org/), API aberta para consultas sobre o clima.

## Execução

### Configurando ambiente

Recomendamos a criação de um ambiente virtual do python 3 para rodar e trabalhar com o bot, basta rodar os comandos (no terminal):

```bash
virtualenv -p python3 ~/.bot_environment
source ~/.bot_environment/bin/activate
```

Agora que estamos em um ambiente seguramente separado do ambiente pessoal, podemos instalar os pacotes necessários listados em "requirements.txt".

```bash
pip install <pacote 1> 
pip install <pacote 2>
pip install <etc...>
```

Para sair deste ambiente virtual, basta digitar:

```bash
deactivate
```

### Rodando

Para rodar são necessários os tokens de acesso ao [Telegram](https://core.telegram.org/bots) e ao [OpenWeatherMap](https://openweathermap.org/api). Essa variáveis serão recuperadas de um arquivo que deve se chamar "TOKENS_HERE" e estar contido na pasta raiz do projeto, o formato dos tokens escritos no arquivo deve seguir o formato:

```
TELEGRAM_TOKEN=123456789:abcdef_GHIJKLMNOPQ-rstuvwxyz0123456
OWM_TOKEN=0123456789abcdefghijklmnopqrstuvwxy
GOOGLEMAPSTOKEN=0123456789abcdefghijklmnopqrstuvwxyz123
PASSWORD=<opcional>
```

E, só então, considerando o ambiente virtual ativado na sessão "configuração do ambiente", podemos rodar o bot com:

```bash
python3 run.py
```

Obs: note que os tokens utilizados aqui são falsos, servindo apenas como exemplo.

## Modo developer

Para ativar as funcionalidades de developer dentro do bot (poder executar funções administrativas), 
o arquivo TOKENS_HERE deve conter uma chave no seguinte formato:

```TOKENS_HERE
PASSWORD=<senha>
```

Se esta chave existir, o modo developer pode ser ativado por qualquer pessoa,
 enviando uma mensagem ao bot com o seguinte conteúdo:

```On chat
/set_dev_functions_on <senha>
```

Para desativar o modo developer, envie esta mensagem:

```On chat
/set_dev_functions_off
```

Para receber uma lista com os comandos de developer, primeiro você deve ativar o modo developer.
Em seguida, envie a mensagem:

```On chat
/devhelp
```


## Próximas funcionalidades

- Previsão do tempo
- Agendamento de tarefas que dependem do clima
- Alerta de mudanças bruscas no clima.

## Arquitetura
![Arquitetura Vai Chover Bot](https://i.imgur.com/Rt6o1zI.jpg)

## Deploy no Cloud (v1)
Abra o cloud console

Entre no compute engine e abra a maquina vai-chover-vm por ssh

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
nohup python3 run.py &
```

Aperte enter para receber de volta o terminal e feche a janela.
