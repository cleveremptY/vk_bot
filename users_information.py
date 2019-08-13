import MySQLdb
import user

#Описание глобальных переменных, необходимых для работы с группой пользователй
class USHelp:
    ex_counter = 0
    conn = MySQLdb.connect('localhost', 'root', '', 'chat-bot')
    cursor = conn.cursor()


users = []
ushelp = USHelp()
employersId = [] #ID людей, которым приходит уведомление о вызвове администратора. ID можно посмотреть по логам

#Загрузка пользователей из БД в локальный список
def load_users():
    ushelp.cursor.execute("SELECT * FROM users")
    rows = ushelp.cursor.fetchall()
    users.clear()
    ushelp.cursor = ushelp.conn.cursor()
    for row in rows:
        users.append(user.User(row[0]))
        get_user(row[0]).status = row[1]
        if row[2] == 'admin':
            employersId.append(row[0])
    print("Список пользователей загружен успешно")

#Получение экземплеря класса User
def get_user(vk_id):
    for val in users:
        if val.id == vk_id:
            return val
    return None

#Вывод пользователей в консоль
def print_users():
    print("Пользователи:")
    for val in users:
        print(val.id, " ", val.status)

#Добавление нового пользователя
def add_user(vk_id):
    try:
        if get_user(vk_id) == None:
            ushelp.cursor.execute("INSERT INTO users VALUES(" + str(vk_id) + ", 'Base')")
            ushelp.conn.commit()
            ushelp.cursor = ushelp.conn.cursor()
            users.append(user.User(vk_id))
            print("Пользователь ", str(vk_id) , "успешно добавлен")
            ushelp.ex_counter = 0
        else:
            print("Пользователь ", str(vk_id) , "уже есть в базе")
    except Exception as ex:
        print('Ошибка при попытке добавления пользователя в базу данных:' + str(ex))
        if ushelp.ex_counter < 11:
            ushelp.ex_counter += 1
            print('Повтор соединения №' + str(ushelp.ex_counter))
            ushelp.conn = MySQLdb.connect('localhost', 'root', '', 'chat-bot')
            ushelp.cursor = ushelp.conn.cursor()
            add_user(vk_id)
        else:
            print('Не удалось установить соединение с базой данных.')
            return ex

#Изменение статуса пользователя (написание письма, разговор с сотрудником)
def set_user_status(vk_id, status):

    try:
        currect_user = get_user(vk_id)
        if currect_user != None:
            currect_user.status = status
            ushelp.cursor.execute("UPDATE users SET status = '" + str(status) + "' WHERE id_user = " + str(vk_id) + "")
            ushelp.conn.commit()
            ushelp.cursor = ushelp.conn.cursor()
            ushelp.ex_counter = 0
        else:
            print("Пользователь ", vk_id, "отсутсвует в базе в базе")
    except Exception as ex:
        print('Ошибка при попытке соединения с базой данных:' + str(ex))
        if ushelp.ex_counter < 11:
            ushelp.ex_counter += 1
            print('Повтор соединения №' + str(ushelp.ex_counter))
            ushelp.conn = MySQLdb.connect('localhost', 'root', '', 'chat-bot')
            ushelp.cursor = ushelp.conn.cursor()
            set_user_status(vk_id, status)
        else:
            print('Не удалось установить соединение с базой данных.')
            return ex