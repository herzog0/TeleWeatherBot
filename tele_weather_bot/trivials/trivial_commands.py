from tele_weather_bot.communication.send_to_user import markdown_message


def call_help(chat_id, text):

    args = text.lower().strip().split()

    main_help_message = u"""
Olá, você está usando o bot TeleWeather!
Usando dados abertos da API do OpenWeather, este bot te dá funcionalidades climáticas como:
*1 - Previsão do tempo*
*2 - Inscrição para notificações programadas (alertas)*
*3 - Cadastro e política de armazenamento de informações*
    
Para saber mais sobre alguma funcionalidade peça ajuda!
ex.: *ajuda 1* (isso dará ajuda sobre a previsão do tempo, pois é o item 1)
ou   *help previsao* (o mesmo que "ajuda 1")
"""

    help_msg_1 = u"""
*Previsão do tempo*
A previsão do tempo é calculada obtendo os dados requisitados da plataforma OpenWeather.

Atualmente suportamos as previsões das informações de:
*Temperatura*
*Umidade*
*Chuva*
*Nebulosidade*
*Pôr do sol*
*Nascer do sol*

*Para requisitar alguma informação destas você deve enviar uma mensagem ao bot seguindo o modelo abaixo:*
<requisição (lista acima)> <data (opcional)> <hora (opcional)> em <local>


*Exemplos:*
-tempo agora em Campinas
-temperatura amanhã as 17h em Shopping Center de São paulo
-umidade dia 5 em torre de pisa italia
-chuva hoje as 4h em hong kong
etc.

Note que a palavra "em" é necessária para determinar o local de pesquisa!

Caso deseje cadastrar um local de consulta fixo basta enviar a mensagem "cadastro" para o bot.
Para mais informações sobre o cadastro envie a mensagem "ajuda cadastro".

"""

    help_msg_2 = u"""
*Notificações programadas*

Para usar o serviço de alertas programados, envie a mensagem "alerta" ou "notificação" para o bot.

Com isto, você poderá configurar dois tipos de alertas: diários ou por gatilho.

*Os alertas diários funcionam da seguinte forma:*
Todos os dias, em um horário definido por você, enviaremos uma mensagem contendo um resumo do clima de um certo local.
O local é definido por você e será fixo para o alerta diário.

*Os alertas por gatilho funcionam da seguinte forma:*
Você definirá qual informação deseja colocar em estado de alerta (temperatura, chuva, etc.).
Para esta informação específica, você definirá uma condição como "temperatura menor que 17 graus".
A cada 3 horas o serviço do bot irá buscar na previsão do tempo se a sua condição foi satisfeita.
Em caso positivo, você receberá um alerta a cada 3 horas a partir de 9 horas antes do evento ocorrer.

Para descadastrar algum alerta existente basta invocar novamente o serviço e tocar o botão de descadastro.
"""

    help_msg_3 = u"""
*Cadastro*

O cadastro serve para facilitar algumas funcionalidades recorrentemente usadas.
Para usá-lo, envie a mensagem "cadastro" para o bot.

Será pedido seu nome, email e local de cadastro. 
Por enquanto, nome e email não causam nenhum efeito na personalização do seu uso, mas planejamos incluir melhorias!

Já o local de cadastro fará com que, ao pedir uma previsão, não seja mais necessário dizer o local de pesquisa. 
Supondo então que seu local de cadastro seja Nova Iorque, bastaria pedir a temperatura com a mensagem:
-Temperatura agora
ou
-Chuva amanhã as 12h

A resposta será a temperatura (ou chuva no exemplo abaixo) em Nova Iorque.

Caso deseje *apagar* completamente suas informações de cadastro envie o comando "apagar cadastro".
Assim, absolutamente todas as suas informações serão apagadas de nosso banco de dados.

Lembrando que apenas guardamos seus dados quando você requisita um cadastro ou criação de alertas.
"""
    helptype = None
    if args and len(args) > 1 and ('ajuda' in args or 'help' in args):
        for arg in args:
            if arg in ['1', 1, 'previsão', 'previsao', 'tempo', 'prever']:
                helptype = '1'
            elif arg in ['2', 2, 'inscrição', 'inscricao', 'inscriçao', 'inscricão', 'inscrever', 'notificar',
                         'notificação', 'alerta', 'alarme', 'gatilho']:
                helptype = '2'
            elif arg in ['3', 3, 'cadastro', 'cadastrar', 'cad']:
                helptype = '3'

    helps = {
        '1': help_msg_1,
        '2': help_msg_2,
        '3': help_msg_3
    }

    markdown_message(chat_id, helps.get(helptype, main_help_message))


def start(chat_id):
    initial_response_text = """
Seja bem vind@ ao bot TeleWeather!

Digite 'ajuda' para conhecer os comandos disponíveis ou já comece o uso do bot requisitando uma informação climática.

*Exemplo:* 
tempo agora em campinas

Não deixe de conferir o menu de ajuda. O bot possui funções muito interessantes para seu uso diário!

"""
    markdown_message(chat_id, initial_response_text)
