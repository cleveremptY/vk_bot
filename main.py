#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '../')

from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import vk_api
from datetime import datetime
import random
import send_mail
import users_information


users_information.load_users()


#Набор ответов для команды "Расскажи анекдот"
jokes = ['Энергосберегающие лампочки не застревают во рту!',
         'Конец света близок! Покайтесь и покупайте приборы ночного видения!',
         'В детстве я боялся темноты. Теперь же, когда я вижу свой счет за электроэнергию, я боюсь света.',
         'После того как слеповатая бабуля включила на кухне свет, наглый таракан не убежал, а мяукнул и потёрся о ногу старушки.',
         'Учиться никогда не поздно! А если поздно, то можно включить лампу.']

#Набор ответов для неизвестных команд
notUnderstand = ['Простите, я Вас не понял :(',
                 'Ничего не понял :(. Попробуйте использовать клавиатуру.',
                 'Я не понимаю :(. Попробуйте команду "помощь", если хотите получить список команд.',
                 'Мой разум не в состоянии опознать это сообщение.',
                 'О нет, эта команда неизвестна!']

bot_name = "Владимир"

try:
    f = open('settings.cb')
    line = f.readline()
    while line:
        print(line),
        if 'Bot name' in line:
            bot_name = f.readline()
            print(bot_name)
            print('Имя бота загружено')
        if 'Jokes count' in line:
            n = int((f.readline()).replace(' ', ''))
            print(n)
            jokes.clear()
            for counter in range(1, n+1):
                print(f.readline())
                jokes.append(f.readline())
        line = f.readline()
    f.close()
    if len(jokes) == 0:
        raise Exception('Не найдены шутки')
except Exception as ex:
    print('Не удалось загрузить файл-настроек. Применены стандартные настройки.')
    print(ex)

#Ключ доступа к группе
token = 'GROUP_TOKEN'
vk_session = vk_api.VkApi(token=token)

session_api = vk_session.get_api()

longpoll = VkLongPoll(vk_session)

message = ""

#Определние и вывод корректной клавиатуры
def create_keyboard(response):
    keyboard = VkKeyboard(one_time=False)
    if response == 'заявка':
            keyboard.add_button('Неоновая вывеска', color=VkKeyboardColor.POSITIVE)
            keyboard.add_button('Объёмные буквы', color=VkKeyboardColor.POSITIVE)
            keyboard.add_button('Вывеска-короб', color=VkKeyboardColor.POSITIVE)
            keyboard.add_line()
            keyboard.add_button('Отменить', color=VkKeyboardColor.NEGATIVE)
            
    elif response == 'позвать администратора группы' or response == 'отправить заказ на почту':
        keyboard.add_button('Отменить', color=VkKeyboardColor.NEGATIVE)

    elif response == 'тест':

        keyboard.add_button('Белая кнопка', color=VkKeyboardColor.DEFAULT)
        keyboard.add_button('Зелёная кнопка', color=VkKeyboardColor.POSITIVE)

        keyboard.add_line()  # Переход на вторую строку
        keyboard.add_button('Красная кнопка', color=VkKeyboardColor.NEGATIVE)

        keyboard.add_line()
        keyboard.add_button('Синяя кнопка', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('Привет', color=VkKeyboardColor.PRIMARY)

    elif response == 'закрыть':
        return keyboard.get_empty_keyboard()

    elif response == 'хочу связаться с вами':

        keyboard.add_button('Написать на почту', color=VkKeyboardColor.PRIMARY)

        keyboard.add_line()
        keyboard.add_button('Позвать администратора группы', color=VkKeyboardColor.PRIMARY)

    elif response == 'написать на почту':
        keyboard.add_button('Отправить', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('Отменить', color=VkKeyboardColor.NEGATIVE)

    elif response == 'хочу сделать заказ':
        keyboard.add_button('Каталог', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('Заявка', color=VkKeyboardColor.PRIMARY)
        
    elif response == 'каталог':
        keyboard.add_button('Отправить заказ на почту', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('Вернуться', color=VkKeyboardColor.PRIMARY)
        
    else:

        keyboard.add_button('Хочу сделать заказ', color=VkKeyboardColor.PRIMARY)

        keyboard.add_line()
        keyboard.add_button('Кто вы?', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('Хочу связаться с вами', color=VkKeyboardColor.PRIMARY)

        keyboard.add_line()
        keyboard.add_button('Расскажи анекдот', color=VkKeyboardColor.PRIMARY)
    keyboard = keyboard.get_keyboard()

    return keyboard

#Функция отправки сообщения
def send_message(vk_session, id_type, id, message=None, attachment=None, keyboard=None):
    vk_session.method('messages.send',{id_type: id, 'message': message, 'random_id': random.randint(-2147483648, +2147483648), "attachment": attachment, 'keyboard': keyboard})

#Отслеживание сообщений
while True:
    #Просмотр событий
    for event in longpoll.listen():
        #Выбираем из всех событий новые сообщения
        if event.type == VkEventType.MESSAGE_NEW:
            print('Сообщение от ' + str(event.user_id) + ' пришло в: ' + str(datetime.strftime(datetime.now(), "%H:%M:%S")))
            print('Текст сообщения: ' + str(event.text))
            response = event.text.lower()
            keyboard = create_keyboard(response)

            if event.from_user and not event.from_me:
                #Получение информации о пользователе
                profile_info = session_api.users.get(user_ids=event.user_id, fields='first_name, last_name')
                profile_name = profile_info[0]['first_name']
                profile_lastname = profile_info[0]['last_name']
                #Проверка пользователя на наличие в БД
                if users_information.get_user(event.user_id) == None:
                    print('Добавление пользователя', event.user_id)
                    users_information.add_user(event.user_id)
                    send_message(vk_session, 'user_id', event.user_id,
                                 message='Привет, ' + profile_name + '! Меня зовут ' + bot_name + '. Я местный бот, чьей целью является помочь всем всем интересующимся покупателям. Итак, какие у вас есть вопросы?',
                                 keyboard=keyboard)
                elif response == "отменить":
                    if users_information.get_user(event.user_id).status != 'Base':
                        users_information.get_user(event.user_id).message = ""
                        users_information.set_user_status(event.user_id, 'Base')
                        users_information.get_user(event.user_id).writeOrder = 0
                        users_information.get_user(event.user_id).orderType = ""
                        users_information.get_user(event.user_id).orderSize = ""
                        users_information.get_user(event.user_id).orderColor = ""
                        users_information.get_user(event.user_id).orderContent = ""
                        users_information.get_user(event.user_id).orderClient = ""
                        users_information.get_user(event.user_id).orderOthers = ""

                        users_information.get_user(event.user_id).catalogOrderName = ""
                        users_information.get_user(event.user_id).catalogOrderCount = ""
                        users_information.get_user(event.user_id).catalogOrderParamss = ""
                        users_information.get_user(event.user_id).catalogOrderClient = ""
                        users_information.get_user(event.user_id).catalogOrderOthers = ""
                        send_message(vk_session, 'user_id', event.user_id,
                                     message='Операция отменена. Могу я помочь чем-либо ещё?', keyboard=keyboard)
                    else:
                        send_message(vk_session, 'user_id', event.user_id,
                                     message='Ни одна из операций не находится в состоянии выполнения в данный момент.', keyboard=keyboard)
                elif users_information.get_user(event.user_id).status == 'Write message':

                    if response == "отправить":
                        if send_mail.send_custom_mail(str(event.user_id), "Обращение из группы ВК", users_information.get_user(event.user_id).message) == None:
                            send_message(vk_session, 'user_id', event.user_id,
                                         message='Ваше сообщение успешно отправлено! Чем ещё могу помочь?',
                                         keyboard=keyboard)
                        else:
                            send_message(vk_session, 'user_id', event.user_id,
                                         message='При отправке сообщения возникла ошибка. Попробуйте снова или воспользуйтесь альтернативными способами связи с нами.',
                                         keyboard=keyboard)
                        users_information.get_user(event.user_id).message = ""
                        users_information.set_user_status(event.user_id, 'Base')
                    else:
                        users_information.get_user(event.user_id).message = users_information.get_user(event.user_id).message + "\n" + response
                elif users_information.get_user(event.user_id).status == 'Write catalog order':
                    keyboard_s = VkKeyboard(one_time=False)
                    keyboard_s.add_button('Отменить', color=VkKeyboardColor.NEGATIVE)
                    keyboard_s = keyboard_s.get_keyboard()
                    if users_information.get_user(event.user_id).writeOrder == 1:
                        users_information.get_user(event.user_id).catalogOrderName = response
                        users_information.get_user(event.user_id).writeOrder = 2
                        send_message(vk_session, 'user_id', event.user_id,
                                     message='Сколько единиц товара вам нужно?', keyboard=keyboard_s)
                    elif users_information.get_user(event.user_id).writeOrder == 2:
                        users_information.get_user(event.user_id).catalogOrderCount = response
                        users_information.get_user(event.user_id).writeOrder = 3
                        send_message(vk_session, 'user_id', event.user_id,
                                     message='Опишите требуемые вам характеристики товара в одном сообщении. Если товар их не предусматривает, то так и укажите.', keyboard=keyboard_s)
                    elif users_information.get_user(event.user_id).writeOrder == 3:
                        users_information.get_user(event.user_id).catalogOrderParamss = response
                        users_information.get_user(event.user_id).writeOrder = 4
                        send_message(vk_session, 'user_id', event.user_id,
                                     message='Как можно с вами связаться? Можете написать свой Email или номер телефона.', keyboard=keyboard_s)
                    elif users_information.get_user(event.user_id).writeOrder == 4:
                        users_information.get_user(event.user_id).catalogOrderClient = response
                        users_information.get_user(event.user_id).writeOrder = 5
                        send_message(vk_session, 'user_id', event.user_id,
                                     message='Можете оставить другие примечания к заказу. Если таких нет, то так и укажите.', keyboard=keyboard_s)
                    elif users_information.get_user(event.user_id).writeOrder == 5:
                        users_information.get_user(event.user_id).catalogOrderOthers = response
                        send_mail.send_catalog_order(str(event.user_id),
                                                     'Заказ из группы ВК',
                                                     users_information.get_user(event.user_id).catalogOrderName,
                                                     users_information.get_user(event.user_id).catalogOrderCount,
                                                     users_information.get_user(event.user_id).catalogOrderParamss,
                                                     users_information.get_user(event.user_id).catalogOrderClient,
                                                     users_information.get_user(event.user_id).catalogOrderOthers)
                        users_information.get_user(event.user_id).catalogOrderName = ""
                        users_information.get_user(event.user_id).catalogOrderCount = ""
                        users_information.get_user(event.user_id).catalogOrderParamss = ""
                        users_information.get_user(event.user_id).catalogOrderClient = ""
                        users_information.get_user(event.user_id).catalogOrderOthers = ""
                        users_information.get_user(event.user_id).writeOrder = 0
                        users_information.set_user_status(event.user_id, 'Base')
                        send_message(vk_session, 'user_id', event.user_id,
                                     message='Ваш закаp успешно отправлен! Ожидайте ответа. Что ещё я могу для вас сделать?', keyboard=keyboard)
                elif users_information.get_user(event.user_id).status == 'Write order':
                    keyboard_s = VkKeyboard(one_time=False)
                    keyboard_s.add_button('Отменить', color=VkKeyboardColor.NEGATIVE)
                    keyboard_s = keyboard_s.get_keyboard()
                    if users_information.get_user(event.user_id).writeOrder == 1:
                        users_information.get_user(event.user_id).orderType = response
                        users_information.get_user(event.user_id).writeOrder = 2
                        send_message(vk_session, 'user_id', event.user_id,
                                     message='Каких размеров должна быть вывеска? В одном сообщении укажите длину, высоту и, при необходимости, другие размеры.', keyboard=keyboard_s)
                    elif users_information.get_user(event.user_id).writeOrder == 2:
                        users_information.get_user(event.user_id).orderSize = response
                        users_information.get_user(event.user_id).writeOrder = 3
                        send_message(vk_session, 'user_id', event.user_id,
                                     message='Какого цвета должна быть вывеска? При наличии нескольких цветов, опишите в одном сообщение элементы вывески и соответсвующие им цвета.', keyboard=keyboard_s)
                    elif users_information.get_user(event.user_id).writeOrder == 3:
                        users_information.get_user(event.user_id).orderColor = response
                        users_information.get_user(event.user_id).writeOrder = 4
                        send_message(vk_session, 'user_id', event.user_id,
                                     message='Что должно быть изображено на вывеске? Опишите одним сообщением.', keyboard=keyboard_s)
                    elif users_information.get_user(event.user_id).writeOrder == 4:
                        users_information.get_user(event.user_id).orderContent = response
                        users_information.get_user(event.user_id).writeOrder = 5
                        send_message(vk_session, 'user_id', event.user_id,
                                     message='Как можно с вами связаться? Можете написать свой Email или номер телефона.', keyboard=keyboard_s)
                    elif users_information.get_user(event.user_id).writeOrder == 5:
                        users_information.get_user(event.user_id).orderClient = response
                        users_information.get_user(event.user_id).writeOrder = 6
                        send_message(vk_session, 'user_id', event.user_id,
                                     message='Можете оставить другие примечания к заказу. Если таких нет, то так и укажите.', keyboard=keyboard_s)
                    elif users_information.get_user(event.user_id).writeOrder == 6:
                        users_information.get_user(event.user_id).orderOthers = response
                        send_mail.send_order(str(event.user_id),
                                             'Заявка на вывеску из группы ВК',
                                             users_information.get_user(event.user_id).orderType,
                                             users_information.get_user(event.user_id).orderSize,
                                             users_information.get_user(event.user_id).orderColor,
                                             users_information.get_user(event.user_id).orderContent,
                                             users_information.get_user(event.user_id).orderClient,
                                             users_information.get_user(event.user_id).orderOthers)
                        users_information.get_user(event.user_id).orderType = ""
                        users_information.get_user(event.user_id).orderSize = ""
                        users_information.get_user(event.user_id).orderColor = ""
                        users_information.get_user(event.user_id).orderContent = ""
                        users_information.get_user(event.user_id).orderClient = ""
                        users_information.get_user(event.user_id).orderOthers = ""
                        users_information.get_user(event.user_id).writeOrder = 0
                        users_information.set_user_status(event.user_id, 'Base')
                        send_message(vk_session, 'user_id', event.user_id,
                                     message='Ваша заявка успешно отправлена! Ожидайте ответа. Что ещё я могу для вас сделать?', keyboard=keyboard)
                elif users_information.get_user(event.user_id).status == 'Base':
                    if (response == "привет") or (response == 'начать'):
                        send_message(vk_session, 'user_id', event.user_id, message='Привет ' + profile_name + '! Меня зовут ' + bot_name + '. Я местный бот, чьей целью является помочь всем всем интересующимся покупателям. Итак, какие у вас есть вопросы?', keyboard=keyboard)
                    elif response == "тест":
                        users_information.add_user(event.user_id)
                        users_information.get_user(event.user_id)
                        users_information.print_users()
                        #send_message(vk_session, 'user_id', event.user_id, message= 'Тестовые команды', keyboard=keyboard)
                    elif response == 'команды' or response == 'помощь':
                        send_message(vk_session, 'user_id', event.user_id, message='Список команд бота: \n \n 1)Привет/Начать - Вывод приветственного сообщения \n 2)Команды/Помощь - Вывод списка команд \n 3)Кто вы? - Вывод информации об ООО "Зеленоглазое Такси" \n 4)Написать на почту - Активация режима составления письма на почту компании ООО "Моя оборона" \n 5) Позвать администратора группы - отправить в личные сообщения администратора группы уведомление о вызове \n 6) Заявка - активация режима составления заявки на товар, и последующей отправки её на почту')
                    elif response == "кто вы?":
                        send_message(vk_session, 'user_id', event.user_id,
                                     message='Компания - это магазин светотехники. Мы работаем с 2015 года и с тех пор мы успели осветить немалую часть домов, квартир, офисов, улиц, заведений и других мест. \n \n В нашем ассортименте вы найдёте как обычные виды ламп, так и светодиодную и неоновую продукцию, световые рекламные панели, массу декоративного освещения и комплектующие к ним. ',
                                     keyboard=keyboard)
                    elif response == "хочу связаться с вами":
                        send_message(vk_session, 'user_id', event.user_id, message='Вы можете связаться с нами по телефону 88005553535 (городской). \n \n Также вы можете выбрать другой способ связи при помощи кнопок или введя одну из команд: \n \n "Написать на почту" \n "Позвать администратора группы"', keyboard=keyboard)
                    elif response == "написать на почту":
                        send_message(vk_session, 'user_id', event.user_id, message='Напишите ваше сообщение. Для подтверждения отправки введите команду "Отправить" или нажмите на соотвутсвующую кнопку. В этом случае на нашу почту будут отправлены все ваши сообщения, написанные вами после моего сообщения.  \n \n Для отмены отправки сообщения введите комнаду "Отменить" или нажмите на соотвутсвующую конпку.', keyboard=keyboard)
                        users_information.set_user_status(event.user_id, 'Write message')
                    elif response == "позвать администратора группы":
                        for emp_id in users_information.employersId:
                            send_message(vk_session, 'user_id', emp_id,
                                         message='Пользователь @id' + str(event.user_id) + ' (' + profile_name + ' ' + profile_lastname + ') (' + str(event.user_id) + ') ожидает администратора группы.',
                                         keyboard=keyboard)
                        send_message(vk_session, 'user_id', event.user_id,
                                     message='Администратору отправлео уведомление. Ожидайте.  \n \n Для отмены введите комнаду "Отменить" или нажмите на соотвутсвующую конпку.',
                                     keyboard=keyboard)
                        users_information.set_user_status(event.user_id, 'Wait admin')
                    elif response == "расскажи анекдот":
                        send_message(vk_session, 'user_id', event.user_id,
                                     message=random.choice(jokes))
                    elif response == "хочу сделать заказ":
                        send_message(vk_session, 'user_id', event.user_id,
                                     message='Желаете просмотреть каталог или отправить индивидуальную заявку? \n \n Через каталог вы можете выбрать и заказать конкретный товар (команда "Каталог). \n \n При помощи индивидуальной заявки вы можете отправить нам запрос на изготовление индивидуальной вывески (неон, объёмные буквы) (команда "Заявка).',
                                     keyboard=keyboard)
                    elif response == "заявка":
                        users_information.get_user(event.user_id).writeOrder = 1
                        users_information.set_user_status(event.user_id, 'Write order')
                        send_message(vk_session, 'user_id', event.user_id,
                                     message='Для составления заявки ответьте на несколько вопросов. Их ответы будут отправлены нам на почту. \n \n Какого типа вывеску вы хотите? \n \n Неоновая вывеска \n Объёмные буквы \n Другой вариант (написать самому) \n \n Для отмены составления заявки используйте команду "Отменить".',
                                     keyboard=keyboard)
                    elif response == "каталог":
                        send_message(vk_session, 'user_id', event.user_id,
                                     message='Каталог доступен на сайте по ссылке company.by/katalog \n \n Желаете оформить заказ или вернуться в главное меню?',
                                     keyboard=keyboard)
                    elif response == "отправить заказ на почту":
                        users_information.get_user(event.user_id).writeOrder = 1
                        users_information.set_user_status(event.user_id, 'Write catalog order')
                        send_message(vk_session, 'user_id', event.user_id,
                                     message='Для составления заказа ответьте на несколько вопросов. Их ответы будут отправлены нам на почту. \n \n Укажите название товара. При желании можете приложить к своему сообщение ссылку на товар из нашего каталога. \n \n Для отмены составления заказа используйте команду "Отменить".',
                                     keyboard=keyboard)
                    elif response == "вернуться":
                        send_message(vk_session, 'user_id', event.user_id,
                                     message='Возвращаю вас в главное меню. \n \n Могу я вам чем-либо помочь?',
                                     keyboard=keyboard)
                    elif response == 'закрыть':
                        send_message(vk_session, 'user_id', event.user_id, message='Закрыть', keyboard=keyboard)
                    else:
                        send_message(vk_session, 'user_id', event.user_id,
                                     message=random.choice(notUnderstand))