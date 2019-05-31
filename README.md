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

Atenção: para que a identificação de textos seja feita de forma mais natural, é necessária a instalação do pacote "myspell-pt-br". Usano linux, você pode obtê-lo através do comando:

bash
sudo apt-get install myspell-pt-br


Você pode instalá-los com o comando a seguir:

```bash
pip install -r /path/to/requirements.txt
```

Ou, tente configurar um caminho para 'requirements.txt' no seu software de desenvolvimento.

Para sair deste ambiente virtual, basta digitar:

```bash
deactivate
```

### Rodando

Para rodar são necessários os tokens de acesso ao [Telegram](https://core.telegram.org/bots) e ao [OpenWeatherMap](https://openweathermap.org/api).   
Essas variáveis serão recuperadas de um arquivo que deve se chamar "TOKENS_HERE.py" e estar contido na pasta raiz do projeto.  
As variáveis contidas no arquivo devem ter estes mesmos nomes:

```
TELEGRAM_TOKEN = "123456789:abcdef_GHIJKLMNOPQ-rstuvwxyz0123456"
OWM_TOKEN = "0123456789abcdefghijklmnopqrstuvwxy"
GOOGLEMAPS_TOKEN = "0123456789abcdefghijklmnopqrstuvwxyz123"
PASSWORD = "<opcional>"

FIREBASE_CERTIFICATE = {<dicionário que contém os dados do certificado do firebase>}
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
![Arquitetura Vai Chover Bot](https://i.imgur.com/EEu3XAh.png)

## Deploy no Cloud Functions

Rodar o comando abaixo na pasta do projeto:
```bash
make build
```

Um pacote .zip será gerado na pasta "package"

Subir este pacote para a função no cloud
