# TeleWeather Bot


Bot para o [Telegram](https://telegram.org/) com funcionalidades climáticas de fácil utilização e customização.

## Objetivo

O projeto tem por meta avisar as pessoas de forma rápida e eficiente sobre mudanças no clima,
 oferecendo funcionalidades de alerta por gatilho facilmente configuráveis.  

Boa parte das pessoas hoje possuem um smartphone e neste ao menos um aplicativo 
de mensagem. Uma premissa estabelecida é a de que as pessoas tendem a dar grande 
importância para o uso destes aplicativos de mensagens e a usá-los para 
compartilhar informações diversas.

O público alvo é justamente aquele que precisa de um sistema conciso de informações climáticas.
Os aplicativos oferecidos hoje em dia costumam oferecer uma interface pouco comunicativa, tornando 
difíceis as tarefas mais simples e que tanto costumamos precisar, como:  
- Informações climáticas em um local que não seja o seu necessariamente, em uma data qualquer.
- Configuração de gatilhos de alerta.
- Configuração de avisos periódicos programados.  

Além disso, o uso do TeleWeather Bot não requer a instalação de nenhum outro aplicativo além do 
próprio mensageiro Telegram, poupando dados de internet
e facilitando muito a requisição de informações através de uma comunicação verbal com o Bot. 

## Uso

No mensageiro Telegram, procure pelo chat `@TeleWeatherBot`.  
Este nome de usuário é
 único, já o nick do chat não necessariamente. Para desambiguações, abra o bot 
 encontrado e confira se o nome de usuário corresponde ao dito aqui (isto é semelhante
 ao caso de possuirmos dois nomes de contato iguais para números de telefone diferentes).

## Coleta de informações

Apenas coletamos dados fornecidos por você durante um cadastro opcional, como sua localização, nome, e-mail e endereço 
(explicitamente fornecidos a seu gosto, ou seja, essas informações não precisam ser verdadeiras).

As localizações enviadas para requisições de informação climática, que não estejam associadas ao cadastro, não são armazenadas.

Quando você apaga seu cadastro, todas as suas informações são apagadas de nosso banco de dados de forma irrecuperável.



## Dados Abertos

A fonte de dados climáticos é a plataforma [Open Weather](https://openweathermap.org/), API aberta para consultas sobre o clima.

# Sessão para developers

Se sua intenção é apenas utilizar as funcionalidades do bot, pode ignorar totalmente 
este documento a partir daqui.  
Caso tenha interesse em desenvolver seu próprio bot baseado neste, os tópicos abaixo 
podem ajudar.

## Execução 

### Configurando ambiente

Recomendamos a criação de um ambiente virtual do python 3 para rodar e trabalhar com o bot, basta rodar os comandos 
(requer a instalação do virtualenv):

```bash
virtualenv -p python3 ~/.bot_environment
source ~/.bot_environment/bin/activate
```

Agora que estamos em um ambiente seguramente separado do ambiente pessoal, podemos instalar os pacotes necessários listados em "requirements.txt".


Você pode instalá-los com o comando a seguir:

```bash
pip3 install -r /path/to/requirements.txt
```

Ou, tente configurar um caminho para 'requirements.txt' no seu software de desenvolvimento.

Para sair deste ambiente virtual, basta digitar:

```bash
deactivate
```

### Rodando

Atualmente o bot funciona através de requisições HTTP feitas pelo próprio telegram (há 
ótimas informações sobre isso na documentação do telepot).  
Um webhook é configurado usando um endereço gerado pelo GCloud Functions.

Para rodar são necessários os tokens de acesso ao [Telegram](https://core.telegram.org/bots), 
[OpenWeatherMap](https://openweathermap.org/api) e [Google Geolocation api](https://developers.google.com/maps/documentation/geolocation/get-api-key).  
Essas variáveis serão recuperadas de um arquivo (que deve se chamar ".env.yaml" e estar na raiz do projeto) 
em tempo de execução da função no GCloud Functions.
  
As variáveis contidas no arquivo devem ter estes mesmos nomes:

```
TELEGRAM_TOKEN: "123456789:abcdef_GHIJKLMNOPQ-rstuvwxyz0123456"
OWM_TOKEN: "0123456789abcdefghijklmnopqrstuvwxy"
GOOGLEMAPS_TOKEN: "0123456789abcdefghijklmnopqrstuvwxyz123"
```

Atenção: a autenticação do banco de dados do firebase não é necessária no caso deste projeto 
pois, pelo fato de a execução do bot ser feita na própria plataforma do google, ele reconhece 
que o cliente do firebase utilizado é aquele pertencente ao próprio projeto. Caso este bot não seja 
utilizado no GCloud Functions a implementação da autenticação do firebase deve ser feita no arquivo `database/userDAO.py`.

Obs.: note que os tokens utilizados aqui são falsos, servindo apenas como exemplo.  
Obs.[2]: o GCloud Functions interpreta que variáveis de ambiente são pouco manipuladas. Portanto,
 ao fazer o deploy deste arquivo uma vez, os deploys subsequentes do programa não necessitam do arquivo 
 novamente.

### Padrões do projeto e reciclagem de variáveis

De acordo com as informações de performance do [GCloud Docs](https://cloud.google.com/functions/docs/bestpractices/tips#functions-graceful-termination-python) 
é recomendado que o projeto _utilize_ variáveis globais. Já que, pela natureza 
de funcionamento das chamadas do código, variáveis globais podem 
ser ocasionalmente salvas em cache, reduzindo o tempo de processamento 
da função.  
  
A outra recomendação relacionada é que, destas variáveis globais, aquelas que 
não precisam ser sempre executadas (por exemplo a inicialização de um objeto de API sendo que 
a chamada da função requisita algo não relacionado à API) sejam declaradas 
no escopo global como `var_global = None` mas que sejam inicializadas somente 
dentro da função que a utiliza.

## Próximas funcionalidades

- Agendamento de tarefas que dependem do clima
- Alerta de mudanças bruscas no clima.

## Arquitetura
![Arquitetura Vai Chover Bot](https://i.imgur.com/EEu3XAh.png)

## Deploy no Cloud Functions

Caso deseje fazer o deploy manual através de um pacote zip, use o comando abaixo:
```bash
make build
```

Um pacote .zip será gerado na pasta "package" contendo todos os arquivos necessários para a execução da função.

A alternativa é o deploy através do comando abaixo:
```bash
make deploy_gcloud
```

O comando acima requer a prévia instalação do SDK do Google. Use o comando abaixo para
 instalá-lo e siga as instruções da documentação do [Cloud SDK](https://cloud.google.com/sdk/) 
 para sua autenticação local.

```bash
curl https://sdk.cloud.google.com | bash
```

O uso do comando `make deploy_gcloud` pressupõe o uso do GCloud Repositories, utilizando o link de referência 
da branch de deploy. Caso prefira automatizar o deploy de outra forma, edite o comando no `Makefile`.

## Pós-desenvolvimento

Caso precise elaborar um novo arquivo de requisitos para o projeto, recomendamos o uso do `pipreqs`.  

```bash
pip3 install pipreqs
pipreqs path/to/project
```

O programa busca recursivamente no diretório passado como argumento e anota quais são as bibliotecas utilizadas para o projeto 
em um arquivo `requirements.txt`.

## Brainstorm

![Primeira rodada](https://i.imgur.com/snds7ff.jpg)

![Segunda rodada](https://i.imgur.com/ZXSTDGb.jpg)
