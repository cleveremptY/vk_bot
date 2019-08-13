class User:

    status = 'Base'
    message = ''

    #Параметры для заявки на вывеску
    writeOrder = 0
    orderType = ""
    orderSize = ""
    orderColor = ""
    orderContent = ""
    orderClient = ""
    orderOthers = ""

    #Параметры для заявки по каталогу
    catalogOrderName = ""
    catalogOrderCount = ""
    catalogOrderParamss = ""
    catalogOrderClient = ""
    catalogOrderOthers = ""

    # конструктор
    def __init__(self, id):
        self.id = id


    def display_info(self):
        print("Для пользователя ", self.id, "установлен статус ", self.status)

    def set_status(self, status):
        self.status = status
        self.display_info()