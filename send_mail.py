import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

#Данные для входа на почту
server = smtplib.SMTP_SSL('smtp.mail.ru', 465)
user = 'sample_company@mail.ru'
password = 'password'

#Отправитель и получатель письма
recipients = 'sample_company@mail.ru'
sender = 'sample_company@mail.ru'

#Базовый метод отправки сообщения
def send(message_subject, message_text):
    try:
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = recipients
        msg['Subject'] = message_subject
        body = message_text
        msg.attach(MIMEText(body, 'html'))
        #message = msg.as_string()
        message = msg.as_string()
        server.login(user, password)
        server.sendmail(sender, recipients, message)
        server.quit()
    except Exception as ex:
        print('Ошибка при отправке сообщения: ' + str(ex))
        return ex

#Шаблон произвольного письма
def send_custom_mail(user_id, message_subject, message_content):
    ulink = "vk.com/id" + user_id
    message_text = """\
        <html>
          <head></head>
          <body>
            <h2>Сообщение</h2>
            <p> Сообщение из группы <a href = "vk.com/smirby">СветомирБай</a> от пользователя <a hreft = '""" + ulink + """'>""" + ulink + """</a>
            <hr>
            """ + message_content + """ <br>
          </body>
        </html>
        """
    send(message_subject, message_text)

#Шаблон заказа из каталога
def send_catalog_order(user_id, message_subject, message_name, message_count, message_params, message_client, message_others):
    ulink = "vk.com/id" + user_id
    message_text = """\
        <html>
          <head></head>
          <body>
            <h2>Заказ из каталога</h2>
            <p> Заказ из группы <a href = "vk.com/smirby">СветомирБай</a> от пользователя <a hreft = '""" + ulink + """'>""" + ulink + """</a>
            <hr>
            <b>Название:</b> """ + message_name + """ <br>
            <b>Количество:</b> """ + message_count + """ <br>
            <b>Характеристики:</b> """ + message_params + """ <br>
            <b>Контактные данные клиента:</b> """ + message_client + """ <br>
            <b>Примечания:</b> """ + message_others + """ <br>
          </body>
        </html>
        """
    send(message_subject, message_text)

#Шаблон заказа вывески
def send_order(user_id, message_subject, message_orderType, message_orderSize, message_orderColor, message_orderContent,
               message_orderClient, message_orderOthers):
    ulink = "vk.com/id" + user_id
    message_text = """\
    <html>
      <head></head>
      <body>
        <h2>Заявка на вывеску</h2>
        <p> Заявка из группы <a href = "vk.com/smirby">СветомирБай</a> от пользователя <a hreft = '""" + ulink + """'>""" + ulink + """</a>
        <hr>
        <b>Тип:</b> """ + message_orderType + """ <br>
        <b>Размер:</b> """ + message_orderSize + """ <br>
        <b>Цвет:</b> """ + message_orderColor + """ <br>
        <b>Содержание:</b> """ + message_orderContent + """ <br>
        <b>Контактные данные клиента:</b> """ + message_orderClient + """ <br>
        <b>Примечания:</b> """ + message_orderOthers + """ <br>
      </body>
    </html>
    """
    send(message_subject, message_text)