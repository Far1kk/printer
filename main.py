import os
import urllib.request
from itertools import permutations
from random import randint
import vk
import win32api
import win32print
from PyPDF2 import PdfReader
from docx2pdf import convert
# from pyqiwip2p import QiwiP2P
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
import json
import keyboards
from config import main_folder, paid_folder
from keyboards import *
import traceback
import shutil
from threading import Timer
import datetime
from config import token as tkn

today = datetime.datetime.today()
print(today)
print(main_folder)


class printer_db():
    """Запросы базы данных"""

    def __init__(self):
        self.data = 'printer_db.json'

    def readstate(self, printer_point):
        '''Возврат колличества бумаги, тонера и состояния принтера'''
        with open(self.data, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        state = {'paper': raw_data[str(printer_point)]['printer']['paper'],
                 'toner': raw_data[str(printer_point)]['printer']['toner'],
                 'status': raw_data[str(printer_point)]['printer']['status'],
                 'connection': raw_data[str(printer_point)]['printer']['connection']}
        return state

    def updatepaper(self, printer_point, count):
        '''Изменение и возврат колличества бумаги и тонера'''
        with open(self.data, 'r', encoding='utf-8') as f:
            old_data = json.load(f)
        old_data[str(printer_point)]['printer']['paper'] = old_data[str(printer_point)]['printer']['paper'] - count
        old_data[str(printer_point)]['printer']['toner'] = old_data[str(printer_point)]['printer']['toner'] - count
        paper = old_data[str(printer_point)]['printer']['paper']
        toner = old_data[str(printer_point)]['printer']['toner']
        old_data = json.dumps(old_data)
        new_data = json.loads(str(old_data))
        with open(self.data, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=4)
        return paper, toner

    def restocking(self, printer_point, user_id, paper=None, toner=None, status=None):
        '''Пополнение запасов'''
        if paper:
            with open(self.data, 'r', encoding='utf-8') as f:
                old_data = json.load(f)
            old_data[str(printer_point)]['printer']['paper'] = paper
            paper_info = old_data[str(printer_point)]['printer']['paper']
            toner_info = old_data[str(printer_point)]['printer']['toner']
            status_info = old_data[str(printer_point)]['printer']['status']
            connection_info = old_data[str(printer_point)]['printer']['connection']
            printer_info = {'paper': paper_info, 'toner': toner_info, 'status': status_info,
                            'connection': connection_info}
            old_data = json.dumps(old_data)
            new_data = json.loads(str(old_data))
            with open(self.data, 'w', encoding='utf-8') as f:
                json.dump(new_data, f, indent=4)
            send_message(user_id, 'Бумага успешно пополнена')
            return printer_info
        elif toner:
            with open(self.data, 'r', encoding='utf-8') as f:
                old_data = json.load(f)
            old_data[str(printer_point)]['printer']['toner'] = toner
            paper_info = old_data[str(printer_point)]['printer']['paper']
            toner_info = old_data[str(printer_point)]['printer']['toner']
            status_info = old_data[str(printer_point)]['printer']['status']
            connection_info = old_data[str(printer_point)]['printer']['connection']
            printer_info = {'paper': paper_info, 'toner': toner_info, 'status': status_info,
                            'connection': connection_info}
            old_data = json.dumps(old_data)
            new_data = json.loads(str(old_data))
            with open(self.data, 'w', encoding='utf-8') as f:
                json.dump(new_data, f, indent=4)
            send_message(user_id, 'Тонер успешно обновлен')
            return printer_info
        elif status:
            with open(self.data, 'r', encoding='utf-8') as f:
                old_data = json.load(f)
            old_data[str(printer_point)]['printer']['status'] = status
            paper_info = old_data[str(printer_point)]['printer']['paper']
            toner_info = old_data[str(printer_point)]['printer']['toner']
            status_info = old_data[str(printer_point)]['printer']['status']
            connection_info = old_data[str(printer_point)]['printer']['connection']
            printer_info = {'paper': paper_info, 'toner': toner_info, 'status': status_info,
                            'connection': connection_info}
            old_data = json.dumps(old_data)
            new_data = json.loads(str(old_data))
            with open(self.data, 'w', encoding='utf-8') as f:
                json.dump(new_data, f, indent=4)
            send_message(user_id, 'Статус успешно обновлен')
            return printer_info
        else:
            with open(self.data, 'r', encoding='utf-8') as f:
                old_data = json.load(f)
            paper_info = old_data[str(printer_point)]['printer']['paper']
            toner_info = old_data[str(printer_point)]['printer']['toner']
            status_info = old_data[str(printer_point)]['printer']['status']
            connection_info = old_data[str(printer_point)]['printer']['connection']
            printer_info = {'paper': paper_info, 'toner': toner_info, 'status': status_info,
                            'connection': connection_info}
            return printer_info

    def SelectAdmins(self, point):
        """Выбрать админов точки"""
        with open(self.data, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        admin_list = list()
        for admins in raw_data[str(point)]['admins'].keys():
            admin_list.append(raw_data[str(point)]['admins'][str(admins)])
        return admin_list

    def SelectLocations(self):
        """Выбрать локацию точки"""
        with open(self.data, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        location_list = list()
        for points in raw_data.keys():
            location_list.append(raw_data[str(points)]['location'])
        return location_list

    def SelectPointOfLocation(self, user_location):
        """Выбрать id локации точки"""
        with open(self.data, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        for point in raw_data.keys():
            if user_location == raw_data[str(point)]['location']:
                return point
        return False

    def SelectPrice(self, point):
        """Цена точки"""
        with open(self.data, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        price = raw_data[str(point)]['price']
        return price

    def SelectPrinterName(self, point):
        """Выбрать название принтера точки"""
        with open(self.data, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        printer_name = raw_data[str(point)]['printer']['printer_name']
        return printer_name

    def StatusChange(self, printer_point, status=None):
        """Смена состояния работоспособности"""
        if status == 1:
            with open(self.data, 'r', encoding='utf-8') as f:
                old_data = json.load(f)
            old_data[str(printer_point)]['printer']['status'] = 1
            old_data = json.dumps(old_data)
            new_data = json.loads(str(old_data))
            with open(self.data, 'w', encoding='utf-8') as f:
                json.dump(new_data, f, indent=4)
        elif status == 0:
            with open(self.data, 'r', encoding='utf-8') as f:
                old_data = json.load(f)
            old_data[str(printer_point)]['printer']['status'] = 0
            old_data = json.dumps(old_data)
            new_data = json.loads(str(old_data))
            with open(self.data, 'w', encoding='utf-8') as f:
                json.dump(new_data, f, indent=4)
        else:
            with open(self.data, 'r', encoding='utf-8') as f:
                old_data = json.load(f)
            old_data[str(printer_point)]['printer']['status'] = 1
            old_data = json.dumps(old_data)
            new_data = json.loads(str(old_data))
            with open(self.data, 'w', encoding='utf-8') as f:
                json.dump(new_data, f, indent=4)


l = printer_db()
locations = l.SelectLocations()  # Разобраться с классами
for loc in locations:
    keyboard_location.add_button(str(loc), color=vk_api.keyboard.VkKeyboardColor.POSITIVE)
    if loc == locations[-1]:
        break
    keyboard_location.add_line()

vk_session = vk_api.VkApi(
    token=str(tkn))
longpoll = VkBotLongPoll(vk_session, 216283433)  # 213072407
vk = vk_session.get_api()
Lslongpoll = VkLongPoll(vk_session)
Lsvk = vk_session.get_api()


def send_message(user_id, msg):
    vk.messages.send(
        user_id=user_id,
        message=msg,
        random_id=get_random_id()
    )
def send_keyboard(user_id, msg, keyboard):
    vk.messages.send(
        user_id=user_id,
        message=msg,
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard()
    )
def delete_files(user):
    user = str(user)
    for file in os.listdir(main_folder + user):
        os.remove(main_folder + user + '/' + file)

def print_files(user_id, point):
    """Функция печати файлов на удаленном принтере. На входе принимает id пользователя и id точки"""
    try:
        # Настройки по-умолчанию принтера
        printdefaults = {"DesiredAccess": win32print.PRINTER_ALL_ACCESS}
        # Выбираем принтер по переданному idшнику
        printer_name = printer_db()
        printer_name = printer_name.SelectPrinterName(point)
        print(printer_name)
        # Настраиваем принтер для печати
        handle = win32print.OpenPrinter(printer_name, printdefaults)
        level = 2
        attributes = win32print.GetPrinter(handle, level)
        print(attributes)
        win32print.SetPrinter(handle, level, attributes, 0)
        # Выбираем файлы для печати из нужно директории
        inputs_print = next(os.walk(main_folder + 'paid/' + str(user_id) + '/'))[2]
        print(inputs_print)
        # Печатаем документы
        for input_print in inputs_print:
            input_print = main_folder + 'paid/' + str(user_id) + '/' + input_print
            attributes = win32print.GetPrinter(handle, level)
            print(attributes)
            win32api.ShellExecute(2, "print", input_print, '.', None, 0)
            attributes = win32print.GetPrinter(handle, level)
            print(attributes)
        #Закрываем принтер
        win32print.ClosePrinter(handle)
    except Exception as e:
        with open("log.txt", "a") as f:
            f.write(str(e))

recover_key = False

def recover_user_data(user):
    '''Если скрипт был перезапущен на сервере, и у пользователя остались оплаченные файлы.'''
    user_data.update({str(user): {'user_id': user, 'stage': 3, 'sheets': 0,
                                  'paper': 0, 'point': str(), 'status_pay': False,
                                  'attributes': list(), 'location': str(), 'admins': list(),
                                  'pay_link': str(), 'pdf': list()}})
    recover_key = True
    return recover_key


def PageCount(pdf_files_dir):
    """Функция подсчета страниц"""
    sheets = 0
    for path in pdf_files_dir:
        reader = PdfReader(path)
        num_of_sheets = len(reader.pages)
        sheets += num_of_sheets
    print('ok')
    return sheets


def FilterFiles(user_folder):
    """ Функция фильтрации """
    for file in next(os.walk(user_folder))[2]:
        if file.endswith('docx') and not file.startswith('~'):
            def converting(file):
                """ Функция конвертирования"""
                file = user_folder + file
                file_pdf = file.replace('.docx', '.pdf')
                user_data[str(event.user_id)]['pdf'].append(file_pdf)
                convert(file)  # convert создает новый файл в формате PDF.
                os.remove(file)  # Удаляем старый файл DOC(X).

            converting(file)
        elif file.endswith('pdf') and not file.startswith('~'):
            file = user_folder + file
            user_data[str(event.user_id)]['pdf'].append(file)
        else:
            send_message(event.user_id, f'{file} Я не могу прочитать файл c таким расширением.')
        print('ok')


p2p = True
is_options = False
permutation = ['1', '2', '3', '4', '5']
for h in range(2, 5 + 1):
    permutation += [''.join(i) for i in permutations('12345', h)]
link_pay = ''
bill = ''
user_data = dict()

while True:
    try:
        for event in Lslongpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:

                if not str(event.user_id) in user_data.keys():
                    """Если юзера нет в базе, то его номер и данные вносятся"""
                    print(user_data.keys())
                    user_data.update({str(event.user_id): {'user_id': event.user_id, 'stage': 0, 'sheets': 0,
                                                           'paper': 0, 'point': str(), 'status_pay': False,
                                                           'attributes': list(), 'location': str(), 'admins': list(),
                                                           'pay_link': str(), 'pdf': list(), 'limit': int(0)}})


                def iters_func():
                    """Фильтрует файлы и скачивает в папку пользователя в printer"""
                    attachmentsLen = len(items["items"][0]["attachments"])
                    attachList = []
                    attributes = []

                    for i in range(attachmentsLen):
                        if items["items"][0]["attachments"][i]["type"] == 'photo':
                            # attachList.append(items["items"][0]["attachments"][i]["photo"]["sizes"][4]["url"])
                            # attributes.append(i)
                            send_message(event.user_id, 'Я пока не умею печатать фото(')
                        elif items["items"][0]["attachments"][i]["type"] == 'doc' and user_data[str(event.user_id)][
                            'stage'] == 1:
                            attachList.append(items["items"][0]["attachments"][i]["doc"]["url"])
                            attributes.append(i)
                        elif items["items"][0]["attachments"][i]["type"] == 'doc' and user_data[str(event.user_id)][
                            'stage'] == 0:
                            user_data[str(event.user_id)]['stage'] = 1
                            print(user_data[str(event.user_id)]['stage'])
                            attachList.append(items["items"][0]["attachments"][i]["doc"]["url"])
                            attributes.append(i)
                            send_keyboard(event.user_id,
                                          'Файл сохранен, нажмите готово после отправки всех файлов. Если кнопки пропали, нажмите на четыре квадрата снизу, возле поля сообщения',
                                          keyboards.keyboard1)

                    for value, i in zip(attachList, attributes):
                        print(value)
                        print(i)
                        path = main_folder + str(event.user_id) + '/'
                        # if items["items"][0]["attachments"][i]['type'] == 'photo':
                        #    fullfilename = os.path.join(path, str(randint(0, 999999)) + ".jpg")
                        #    urllib.request.urlretrieve(value, fullfilename)
                        if items["items"][0]["attachments"][i]['type'] == 'doc':
                            ext = str(items["items"][0]["attachments"][i]["doc"]["ext"])
                            fullfilename = os.path.join(path, str(randint(0, 999999)) + '.' + ext)
                            urllib.request.urlretrieve(value, fullfilename)
                    # if attachmentsLen == 0:
                    #    open('C:/Users/bogdan/Desktop/printer/' + str(event.user_id) + '/' + str(randint(0,999999)) + '.doc', "w").write(event.text)
                    return attributes


                """При отправке сообщения на этапах 0 и 1, выполняется функция проверки на наличие файлов"""
                if (user_data[str(event.user_id)]['stage'] in [0, 1]) and not (
                        event.text.lower() in ['готово', 'назад', 'распечатать']):
                    items = vk.messages.getById(message_ids=event.message_id)
                    user_data[str(event.user_id)]['attributes'] = iters_func()

                """ 0 этап. Сброс файлов """
                if (event.text.lower() == 'сбросить') \
                        or (event.text.lower() == 'назад' and user_data[str(event.user_id)]['stage'] == 1) \
                        or (event.text.lower() not in ['готово', 'назад', 'печатать', 'да']
                            and user_data[str(event.user_id)]['stage'] == 0):

                    if os.path.isdir(main_folder + str(event.user_id)):
                        delete_files(event.user_id)
                    else:
                        os.mkdir(main_folder + str(event.user_id))

                    send_keyboard(event.user_id, 'Все файлы удалены. Начать заново?', keyboards.keyboard4)
                    user_data[str(event.user_id)]['stage'] = 0

                """ 1 этап. Удаление старых файлов и отправка пользователем новых"""
                if (event.text.lower() == 'начать') \
                        or (event.text.lower() == 'назад' and user_data[str(event.user_id)]['stage'] == 3) \
                        or (event.text.lower() == 'да' and user_data[str(event.user_id)]['stage'] == 0) \
                        or (event.text.lower() == 'начать заново'):

                    if os.path.isdir(main_folder + str(event.user_id)):
                        pass
                    else:
                        os.mkdir(main_folder + str(event.user_id))
                    send_keyboard(event.user_id, 'Отправьте файлы '
                                                 ' и нажмите готово. Если кнопки пропали, нажмите на четыре квадрата снизу, возле поля сообщения',
                                  keyboards.keyboard1)
                    user_data[str(event.user_id)]['stage'] = 1

                """ 2 этап. Конвертирование файлов в pdf и подсчет страниц"""
                if event.text.lower() == 'готово' and user_data[str(event.user_id)]['stage'] == 1 and \
                        user_data[str(event.user_id)]['attributes']:

                    send_message(event.user_id, 'Считаю страницы, подождите.')

                    # Конвертирование файлов
                    user_data[str(event.user_id)]['pdf'] = list()
                    FilterFiles(main_folder + str(event.user_id) + '/')

                    # Подсчет страниц PDF
                    user_data[str(event.user_id)]['sheets'] = PageCount(user_data[str(event.user_id)]['pdf'])

                    print(user_data[str(event.user_id)]['limit'])
                    print(type(user_data[str(event.user_id)]['limit']))

                    if user_data[str(event.user_id)]['sheets'] <= 0:
                        user_data[str(event.user_id)]['stage'] = 1
                        send_keyboard(event.user_id, 'Список файлов пуст, отправьте файлы и нажмите готово',
                                      keyboards.keyboard1)
                    elif user_data[str(event.user_id)]['sheets'] + user_data[str(event.user_id)]['limit'] > 10:
                        user_data[str(event.user_id)]['stage'] = 1
                        send_keyboard(event.user_id,
                                      f'К сожалению, я не могу печатать больше 10 листов на одного человека в день. Вы сегодня распечатали: {user_data[str(event.user_id)]["limit"]}',
                                      keyboards.keyboard1)
                    else:
                        user_data[str(event.user_id)]['stage'] = 2

                elif (event.text.lower() == 'готово'
                      and user_data[str(event.user_id)]['stage'] == 1
                      and not user_data[str(event.user_id)]['attributes']):
                    send_keyboard(event.user_id, 'Список файлов пуст, отправьте файлы и нажмите готово',
                                  keyboards.keyboard1)

                """ 3 этап. Выбор принтера"""
                if user_data[str(event.user_id)]['stage'] == 2 \
                        or (event.text.lower() == 'назад' and user_data[str(event.user_id)]['stage'] == 4):
                    print('ok')
                    user_data[str(event.user_id)]['stage'] = 3

                    if str(user_data[str(event.user_id)]["sheets"])[-1] == str(1):
                        gramma = 'cтраница'
                    elif str(user_data[str(event.user_id)]["sheets"])[-1] in [str(2), str(3), str(4)]:
                        gramma = 'cтраницы'
                    else:
                        gramma = 'страниц'
                    send_keyboard(event.user_id, f'Всего у вас {user_data[str(event.user_id)]["sheets"]} {gramma}. '
                                                 'Выберите принтер для печати из списка:'
                                  , keyboards.keyboard_location)

                """ 4 этап. Проверка работоспособности принтера и генерация платежного шлюза"""
                if (event.text in locations) and user_data[str(event.user_id)]['stage'] == 3:

                    print('Пользователь выбрал: ' + str(event.text))

                    user_data[str(event.user_id)]['location'] = str(event.text)
                    point = printer_db()
                    user_data[str(event.user_id)]['point'] = point.SelectPointOfLocation(
                        user_data[str(event.user_id)]['location'])


                    def PaperCheck(point, sheets):
                        """Проверка работоспособности и наличия бумаги и тонера принтера"""
                        pc = printer_db()
                        state = pc.readstate(point)
                        admins = printer_db()
                        user_data[str(event.user_id)]['admins'] = admins.SelectAdmins(
                            point)  # У каждого пользователя личные админы
                        printdefaults = {"DesiredAccess": win32print.PRINTER_ALL_ACCESS}
                        printer_name = printer_db()
                        printer_name = printer_name.SelectPrinterName(point)
                        print(printer_name)
                        if state['status'] != 1:
                            user_data[str(event.user_id)]['stage'] = 3
                            send_keyboard(event.user_id,
                                          'К сожалению, этим принтером сейчас занимаются разработчики, если есть другие принтера поблизости выберите их.',
                                          keyboards.keyboard_location)
                            for adminid in user_data[str(event.user_id)]['admins']:
                                send_message(adminid,
                                             f'Статус точки выставлен {state["status"]}. Проверить работоспособность и поменять значение.')
                            return False
                        else:
                            handle = win32print.OpenPrinter(printer_name, printdefaults)
                            attributes = win32print.GetPrinter(handle, 2)
                            win32print.ClosePrinter(handle)
                        if attributes['Status'] not in [0, 1]:
                            user_data[str(event.user_id)]['stage'] = 3
                            send_keyboard(event.user_id,
                                          'К сожалению, этот принтер сейчас не работает, если есть другие принтера поблизости выберите их.',
                                          keyboards.keyboard_location)
                            for adminid in user_data[str(event.user_id)]['admins']:
                                send_message(adminid,
                                             f'Статус принтера {attributes["Status"]}. Cбой проверки работоспособности')
                            return False
                        elif state['paper'] < sheets + 5 or state['toner'] < sheets + 5:
                            user_data[str(event.user_id)]['stage'] = 3
                            send_keyboard(event.user_id,
                                          'К сожалению, у этого принтера сейчас нет столько бумаги, если есть другие принтера поблизости выберите их',
                                          keyboards.keyboard_location)
                            for adminid in user_data[str(event.user_id)]['admins']:
                                send_message(adminid, f'Клиенту не хватило листов. Запрос: {sheets}. '
                                                      f'Бумаги: {state["paper"]}. Тонера: {state["toner"]}')
                            return False
                        elif state['connection'] != 1:
                            user_data[str(event.user_id)]['stage'] = 3
                            send_keyboard(event.user_id.user_id,
                                          'К сожалению, этот принтер сейчас не подключен к сети, если есть другие принтера поблизости выберите их',
                                          keyboards.keyboard_location)
                            for adminid in user_data[str(event.user_id)]['admins']:
                                send_message(adminid, f'Отсутствует сеть у {point}. Клиент не смог распечатать.')
                            return False
                        else:
                            def PayGen(sheets, point, recover_key=None):
                                """Генерация платежной ссылки и оформление стоимости"""
                                if recover_key == True:
                                    """Если сервер перезапускался, а в paid есть файлы, открывается востонавливающий ключ """
                                    user_data[str(event.user_id)]['status_pay'] = True
                                    for file in next(os.walk(paid_folder))[2]:
                                        user_data[str(event.user_id)]['pdf'].append(file)
                                    user_data[str(event.user_id)]['sheets'] = PageCount(
                                        user_data[str(event.user_id)]['pdf'])
                                    recover_key = False
                                    return recover_key
                                else:
                                    price = printer_db()
                                    price = price.SelectPrice(point)
                                    amount = sheets * price
                                    """ bill = p2p.bill(amount=sum, lifetime=15, comment=comment)
                                        send_keyboard(event.user_id, 'Отправь ' + str(
                                        sum) + ' рублей сюда: ' + bill.pay_url + 'Ссылка будет жить в течении 15 минут.', keyboard3)"""
                                    send_keyboard(event.user_id, f'Всего к оплате: {amount}.',
                                                  keyboards.keyboard_pay_link)
                                    send_keyboard(event.user_id, f'Нажмите на кнопку Оплатил(а)',
                                                  keyboards.keyboard3)

                            PayGen(user_data[str(event.user_id)]['sheets'], user_data[str(event.user_id)]['point'],
                                   recover_key)

                            user_data[str(event.user_id)]['stage'] = 4

                    PaperCheck(user_data[str(event.user_id)]['point'], user_data[str(event.user_id)]['sheets'])

                """ 4.1 этап. Проверка платежа. Платеж всегда True, так как НКО проект """
                if (user_data[str(event.user_id)]['stage'] == 4) and event.text.lower() == 'оплатил(а)':
                    def PayCheck(link):
                        status_pay = True
                        if status_pay:
                            pass
                        else:
                            send_message(event.user_id, 'Оплата еще не прошла')
                        return status_pay


                    user_data[str(event.user_id)]['status_pay'] = PayCheck(user_data[str(event.user_id)]['pay_link'])

                """ 5 этап. Сохранение файлов в paid """
                if (user_data[str(event.user_id)]['stage'] == 4) and user_data[str(event.user_id)]['status_pay']:

                    # status = p2p.check(bill).status
                    user_data[str(event.user_id)]['pay_link'] = str()  # Сброс платежной ссылки

                    if os.path.exists(paid_folder + str(event.user_id)):
                        get_files = os.listdir(main_folder + str(event.user_id))
                        for g in get_files:
                            print('Файл перемещен в paid: ' + str(g))
                            shutil.move(main_folder + str(event.user_id) + '/' + g,
                                        paid_folder + str(event.user_id))
                    else:
                        os.mkdir(paid_folder + str(event.user_id))
                        get_files = os.listdir(main_folder + str(event.user_id))
                        for g in get_files:
                            print(g)
                            shutil.move(main_folder + str(event.user_id) + '/' + g,
                                        paid_folder + str(event.user_id))

                    user_data[str(event.user_id)]['status_pay'] = False  # Сброс статуса платежа
                    user_data[str(event.user_id)]['stage'] = 5
                    send_keyboard(event.user_id,
                                  'Файлы сохраненны для печати. Подойдите в любое время к '
                                  'принтеру и нажмите или напишите печатать, также убедитесь, что принтер свободен.', keyboards.keyboard_start_print)
                    attempt = 0

                """ 5.1 этап. Печать файлов"""
                if event.text.lower() == 'печатать' and os.path.exists(paid_folder + str(event.user_id)) and \
                        user_data[str(event.user_id)]['point'] != '':

                    try:
                        # Подсчет всех страниц из папки paid
                        user_data[str(event.user_id)]['pdf'] = list()
                        FilterFiles(paid_folder + str(event.user_id) + '/')
                        user_data[str(event.user_id)]['paper'] = PageCount(user_data[str(event.user_id)]['pdf'])
                        print('Пользователь распечатал страниц:' + str(user_data[str(event.user_id)]['paper']))
                        attempt = + 1

                        # Функция печати
                        print_files(event.user_id, user_data[str(event.user_id)]['point'])

                        # Добавление страниц в лимит
                        user_data[str(event.user_id)]['limit'] = user_data[str(event.user_id)]['limit'] + \
                                                                 user_data[str(event.user_id)]['paper']
                        print('Распечатал за день: ' + str(user_data[str(event.user_id)]['limit']))

                    except Exception as e:
                        with open("log.txt", "a") as f:
                            f.write(str(e) + str(today.strftime("%Y-%m-%d-%H.%M.%S")))
                        for adminid in user_data[str(event.user_id)]['admins']:
                            send_message(adminid,
                                         f'Не получилось распечатать на {user_data[str(event.user_id)]["location"]}. Ошибка: {e}')
                        user_data[str(event.user_id)]['stage'] = 5
                        send_keyboard(event.user_id,
                                      'Что-то пошло не так, подождите несколько секунд и повторите попытку, нажав на '
                                      'кнопку печать',
                                      keyboards.keyboard_start_print)

                    else:
                        """При успешной печати, директория юзера удаляется из paid, cбрасываются некоторые данные"""
                        def remove_paid(user_id):
                            get_files = os.listdir(paid_folder + user_id)
                            print(get_files)
                            for g in get_files:
                                os.remove(paid_folder + str(user_id) + '/' + g)
                            os.rmdir(paid_folder + str(user_id))

                        # Обновление базы данных
                        up = printer_db()
                        paper, toner = up.updatepaper(user_data[str(event.user_id)]['point'],
                                                      user_data[str(event.user_id)]['paper'])
                        send_message(user_data[str(event.user_id)]['admins'][0],
                                     f'Клиент распечтал. Осталось: {paper} бумаги и {toner} тонера.')

                        # Доп. поток для отсчета времени для удаления файлов
                        t = Timer(user_data[str(event.user_id)]['paper'] * 5, remove_paid,
                                  args=(str(user_data[str(event.user_id)]['user_id']),))
                        t.start()

                        # Сброс данных юзера
                        user_data.update({str(event.user_id): {'user_id': event.user_id, 'stage': 1,
                                                               'paper': 0, 'point': str(), 'status_pay': False,
                                                               'attributes': list(), 'location': str(),
                                                               'admins': list(), 'pay_link': str(),
                                                               'limit': user_data[str(event.user_id)]['limit']}})

                        send_keyboard(event.user_id,
                                      'Я начинаю печатать, будьте возле меня, чтобы ваши листы никто случайно не взял.',
                                      keyboards.keyboard5)

                elif event.text.lower() == 'печатать' and os.path.exists(paid_folder + str(event.user_id)) == False:
                    send_message(event.user_id, 'У вас нет оплаченных файлов.')

                elif event.text.lower() == 'печатать' and os.path.exists(paid_folder + str(event.user_id)) and \
                        user_data[str(event.user_id)]['point'] == '':
                    # Восстонавливающий ключ при перезапуске сервера
                    recover_user_data(event.user_id)
                    send_keyboard(event.user_id, 'Сервер перезапускался, напомните мне, какой принтер выбрать:',
                                  keyboards.keyboard_location)

                """************Панель администратора************"""

                if event.text.lower() == '123' and (user_data[str(event.user_id)]['user_id'] in [328945905, 190355238]):
                    user_data[str(event.user_id)]['stage'] = 100
                    user_data[str(event.user_id)]['point'] = 'point1'
                    send_keyboard(event.user_id, 'Аутентификация прошла успешно, Выбери действие', keyboard7)
                    print('Админ подключился к принтеру')

                if event.text.lower() == 'пополнил бумагу(150)' and user_data[str(event.user_id)][
                    'stage'] == 100:
                    print('Админ пополнил бумагу')
                    a = printer_db()
                    stock = a.restocking(user_data[str(event.user_id)]['point'], event.user_id, paper=150)
                    send_keyboard(event.user_id,
                                  f'В принтере: Бумага: {stock["paper"]}\nТонер: {stock["toner"]}\nCтатус: {stock["status"]}\nПодключение: {stock["connection"]}\n\nВыбери действие',
                                  keyboard7)
                elif event.text.lower() == 'пополнил тонер(2900)' and user_data[str(event.user_id)][
                    'stage'] == 100:
                    print('Админ пополнил тонер')
                    a = printer_db()
                    stock = a.restocking(user_data[str(event.user_id)]['point'], event.user_id, toner=2900)
                    send_keyboard(event.user_id,
                                  f'В принтере: Бумага: {stock["paper"]}\nТонер: {stock["toner"]}\nCтатус: {stock["status"]}\nПодключение: {stock["connection"]}\n\nВыбери действие',
                                  keyboard7)
                elif event.text.lower() == 'остановить работу принтера' and user_data[str(event.user_id)][
                    'stage'] == 100:
                    print('Админ остановил работу')
                    a = printer_db()
                    stock = a.restocking(user_data[str(event.user_id)]['point'], event.user_id, status=-1)
                    send_keyboard(event.user_id,
                                  f'В принтере: Бумага: {stock["paper"]}\nТонер: {stock["toner"]}\nCтатус: {stock["status"]}\nПодключение: {stock["connection"]}\n\nВыбери действие',
                                  keyboard7)
                elif event.text.lower() == 'возобновить работу принтера' and user_data[str(event.user_id)][
                    'stage'] == 100:
                    print('Админ возобновил работу')
                    a = printer_db()
                    stock = a.restocking(user_data[str(event.user_id)]['point'], event.user_id, status=1)
                    send_keyboard(event.user_id,
                                  f'В принтере: Бумага: {stock["paper"]}\nТонер: {stock["toner"]}\nCтатус: {stock["status"]}\nПодключение: {stock["connection"]}\n\nВыбери действие',
                                  keyboard7)
                elif event.text.lower() == 'печать тестовой страницы' and user_data[str(event.user_id)]['stage'] == 100:
                    print('Админ распечатал тестовую страницу')
                    print_files(user_id='admin', point=user_data[str(event.user_id)]['point'])
                    send_message(event.user_id, 'Печатаю тестовую страницу...')
                    send_keyboard(event.user_id, 'Выбери действие', keyboard7)

                elif event.text.lower() == 'просмотр состояния принтера' and user_data[str(event.user_id)][
                    'stage'] == 100:
                    print('Админ просмотрел состояние принтера')
                    a = printer_db()
                    stock = a.restocking(user_data[str(event.user_id)]['point'], event.user_id)
                    send_keyboard(event.user_id,
                                  f'В принтере: Бумага: {stock["paper"]}\nТонер: {stock["toner"]}\nCтатус: {stock["status"]}\nПодключение: {stock["connection"]}\n\nВыбери действие',
                                  keyboard7)
                elif event.text.lower() == 'выход' and user_data[str(event.user_id)]['stage'] == 100:
                    print('Админ вышел из панели')
                    user_data[str(event.user_id)]['stage'] = 0
                    send_keyboard(event.user_id, 'Выход из панели администратора', keyboard1)

    except Exception as e:
        '''print(traceback.extract_stack()[-2].lineno)'''
        print(e)
        with open("log.txt", "a") as f:
            today = datetime.datetime.today()
            f.write(str(today.strftime("%Y-%m-%d-%H.%M.%S")) + str(e))
