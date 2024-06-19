import hashlib
import sqlite3
import wx
import random
import string
import smtplib
import wx.lib.filebrowsebutton as filebrowse
from tensorflow.keras.preprocessing import image
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import numpy as np
from tensorflow import keras
from datetime import datetime

#Хеширование пароля:
def hash_password(password):
    salt = b'mysalt'
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return key

def hash_name(name):
    salt = b'mysalt'
    key = hashlib.pbkdf2_hmac('sha256', name.encode('utf-8'), salt, 100000)
    return key
#Класс авторизации:
class LoginWindow(wx.Frame):
    def __init__(self, *args, **kw):
        super(LoginWindow, self).__init__(*args, **kw)
        self.SetSize(wx.Size(340, 315))

        loc = wx.IconLocation(r'C:\Users\SystemX\.vscode\Ptoject\Icon.jpg', 0)
        self.SetIcon(wx.Icon(loc))
        
        self.InitUI()
#Окно авторизации:
    def InitUI(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.wellcom_label = wx.StaticText(panel, label="Распознование заболеваний головного мозга человека")
        vbox.Add(self.wellcom_label, flag=wx.LEFT | wx.TOP, border=10)
        self.wellcom_label = wx.StaticText(panel, label=" ")
        vbox.Add(self.wellcom_label, flag=wx.LEFT | wx.TOP, border=10)

        self.wellcom_label = wx.StaticText(panel, label="Введите данные от личного кабинета")
        vbox.Add(self.wellcom_label, flag=wx.LEFT | wx.TOP, border=10)

        self.username_label = wx.StaticText(panel, label="Имя пользователя:")
        vbox.Add(self.username_label, flag=wx.LEFT | wx.TOP, border=10)
        self.username_input = wx.TextCtrl(panel)
        vbox.Add(self.username_input, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        self.password_label = wx.StaticText(panel, label="Пароль:")
        vbox.Add(self.password_label, flag=wx.LEFT | wx.TOP, border=10)
        self.password_input = wx.TextCtrl(panel, style=wx.TE_PASSWORD)
        vbox.Add(self.password_input, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        self.login_button = wx.Button(panel, label="Войти")
        self.login_button.Bind(wx.EVT_BUTTON, self.login)
        vbox.Add(self.login_button, flag=wx.ALIGN_CENTER | wx.TOP, border=10)

        vbox.Add(hbox, flag=wx.EXPAND  | wx.TOP, border=10)

        self.wellcom_label = wx.StaticText(panel, label="Забыли пароль?")
        hbox.Add(self.wellcom_label, flag=wx.LEFT | wx.TOP, border=10)

        hbox.AddStretchSpacer()

        self.register_button = wx.Button(panel, label="Восстановить")
        self.register_button.Bind(wx.EVT_BUTTON, self.recover_password,)
        hbox.Add(self.register_button, flag=wx.RIGHT | wx.BOTTOM, border=10)

        panel.SetSizer(vbox)
        self.SetTitle('Авторизация')
        self.Centre()
#Генерация кода
    def generate_code(self):
        """Генерация уникального кода"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=8))
#Функция создания письма для восстановления
    def send_email(self, email, code):
        """Отправка электронного письма с кодом восстановления"""
        sender = 'tw1nkltap@mail.ru'
        password = 'MUmywtYY4y1VyYmq0PdX'
        subject = 'Восстановление пароля'
        body = f'Ваш код для восстановления пароля: {code}'

        message = MIMEMultipart()
        message['From'] = sender
        message['To'] = email
        message['Subject'] = subject

        message.attach(MIMEText(body, 'plain', 'utf-8'))

        try:
            server = smtplib.SMTP('smtp.mail.ru', 587)
            server.starttls()
            server.login(sender, password)
            server.send_message(message)
            server.quit()
            wx.MessageBox('Код восстановления отправлен на вашу почту.', 'Информация', wx.OK | wx.ICON_INFORMATION)
        except Exception as e:
            wx.MessageBox(f'Ошибка при отправке письма: {str(e)}', 'Ошибка', wx.OK | wx.ICON_ERROR)
#Функция отправки письма для восстановления 
    def recover_password(self, event):
        global recovery_code
        email = 'tap885@mail.ru'
        if email:
            recovery_code = self.generate_code()
            self.send_email(email, recovery_code)
            self.open_code_verification_window()
    
    def open_code_verification_window(self):
        code_verification_window = CodeVerificationWindow(None)
        code_verification_window.Show()

#Проверка правильности авторизации:
    def login(self, event):
        username = self.username_input.GetValue()
        password = self.password_input.GetValue()
        password1 = hash_password(password)
        conn = sqlite3.connect('databases.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE login=? AND password=?", (username, password1))
        result = cursor.fetchone()

        if result:
            wx.MessageBox("Добро пожаловать!", "Успешная авторизация", wx.OK | wx.ICON_INFORMATION)
            self.user_dashboard = UserDashboardWindow(None, title="РЗГМ.24", username=username)
            self.user_dashboard.Show()
            self.Close()
        else:
            wx.MessageBox("Неверное имя пользователя или пароль", "Ошибка авторизации", wx.OK | wx.ICON_WARNING)

        conn.close()

#Окно заполнения шаблона:
class TemplatesWindow(wx.Frame):
    def __init__(self, *args, username, **kw):
        super(TemplatesWindow, self).__init__(*args, **kw)
        self.SetSize(wx.Size(750, 810))
        loc = wx.IconLocation(r'C:\Users\SystemX\.vscode\Ptoject\Icon.jpg', 0)
        self.SetIcon(wx.Icon(loc))

        self.username = username

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)


        # Предварительно заполненный текст для шаблона:
        initial_text = (
            "Пациент:\n"
            "Адрес проживания:\n"
            "Дата и время посещения:\n"
            "Профиль: нейрохирург.\n""\n"
            "Жалобы:\n""\n"
            "Анамнез заболевания:\n""\n""\n""\n"
            "Диагноз:\n""\n"
            "\n"
            "Рекомендации, назначения:\n"
            "\n""\n""\n""\n""\n""\n""\n""\n""\n""\n""\n""\n""\n""\n""\n""\n""\n""\n""\n""\n""\n""\n"
            "Подпись врача:        __________________        Расшифровка:        __________________        Дата:        __________________"
        )

        # Добавление текстового поля для ввода шаблона с предварительно заполненным текстом
        self.text_ctrl = wx.TextCtrl(panel, value=initial_text, style=wx.TE_MULTILINE, size=(750, 700))
        vbox.Add(self.text_ctrl, flag=wx.EXPAND | wx.ALL, border=10)

        vbox.Add(hbox, flag=wx.EXPAND  | wx.TOP, border=10)

        self.print_btn = wx.Button(panel, label="Печать")
        self.print_btn.Bind(wx.EVT_BUTTON, self.OnPrint)
        hbox.Add(self.print_btn, flag=wx.LEFT | wx.TOP, border=10)

        hbox.AddStretchSpacer()

        self.temp = wx.Button(panel, label="Назад")
        self.temp.Bind(wx.EVT_BUTTON, self.Returnn)
        hbox.Add(self.temp, flag=wx.RIGHT | wx.TOP, border=10)

        panel.SetSizer(vbox)

        self.SetTitle('Шаблон РЗГМ.24')
        self.Centre()
#Выход обратно в основное окно:
    def Returnn(self, event):
        username = self.temp.GetName()
        self.user_dashboard = UserDashboardWindow(None, title="РЗГМ.24", username=username)
        self.user_dashboard.Show()
        self.Close()
#функция для печати готового шаблона:
    def OnPrint(self, event):
        # Получение текста из текстового поля
        text = self.text_ctrl.GetValue()
        print(f"Отладка: текст для печати - \n{text}")

        # Создаём объект PrintData для настройки параметров печати
        print_data = wx.PrintData()
        print_data.SetPaperId(wx.PAPER_A4)
        print_data.SetPrintMode(wx.PRINT_MODE_PRINTER)

        # Создаём объект PrintDialogData и передаем ему PrintData
        print_dialog_data = wx.PrintDialogData()
        print_dialog_data.SetPrintData(print_data)

        printer = wx.Printer(print_dialog_data)
        printout = MyPrintout("Печать документа", text)

        if not printer.Print(self, printout, True):
            wx.MessageBox("Ошибка печати", "Ошибка", wx.OK | wx.ICON_ERROR)
        else:
            printout.Destroy()
#Отладка печати:
class MyPrintout(wx.Printout):
    def __init__(self, title, text):
        super(MyPrintout, self).__init__(title)
        self.text = text
        print(f"Отладка: текст в MyPrintout - \n{text}")

    def OnBeginDocument(self, startPage, endPage):
        if not super(MyPrintout, self).OnBeginDocument(startPage, endPage):
            return False
        return True

    def OnPrintPage(self, page):
        dc = self.GetDC()
        if not dc:
            return False

        # Установка шрифта большего размера
        font = wx.Font(42, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        dc.SetFont(font)

        # Печать текста, введенного пользователем
        lines = self.text.split('\n')
        y = 10
        for line in lines:
            dc.DrawText(line, 10, y)
            y += 75  # Отступ между строками

        return True

    def HasPage(self, page):
        return page == 1

    def GetPageInfo(self):
        return (1, 1, 1, 1)
#Класс основного окна:
class UserDashboardWindow(wx.Frame):
    def __init__(self, *args, username, **kw):
        super(UserDashboardWindow, self).__init__(*args, **kw)
        self.SetSize(wx.Size(400, 500))
        loc = wx.IconLocation(r'C:\Users\SystemX\.vscode\Ptoject\Icon.jpg', 0)
        self.SetIcon(wx.Icon(loc))
        
        self.username = username
        self.InitUI()
#Основное окно:
    def InitUI(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hhbox = wx.BoxSizer(wx.HORIZONTAL)

        self.lbl2 = wx.StaticText(panel, label="Распознование заболеваний головного мозга человека.")
        vbox.Add(self.lbl2, flag=wx.LEFT | wx.TOP, border=10)

        vbox.Add(hbox, flag=wx.ALIGN_LEFT | wx.TOP, border=10)

        self.temp = wx.Button(panel, label="Подготовить шаблон")
        self.temp.Bind(wx.EVT_BUTTON, self.OnOpenTemplatesWindow)
        hbox.Add(self.temp, flag=wx.LEFT | wx.RIGHT, border=10)

        self.patient = wx.Button(panel, label="База данных")
        self.patient.Bind(wx.EVT_BUTTON, self.OnOpenPatientsWindow)
        hbox.Add(self.patient, flag=wx.LEFT | wx.RIGHT, border=10)

        self.image_path_label = wx.StaticText(panel, label="Путь к изображению:")
        vbox.Add(self.image_path_label, flag=wx.LEFT | wx.TOP, border=10)

        vbox.Add(hhbox, flag=wx.ALIGN_RIGHT | wx.TOP, border=10)

        self.image_path_input = wx.TextCtrl(panel, size=wx.Size(290, -1))
        hhbox.Add(self.image_path_input, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)
        self.browse_button = wx.Button(panel, label="Обзор")
        self.browse_button.Bind(wx.EVT_BUTTON, self.browseImage)
        hhbox.Add(self.browse_button, flag=wx.RIGHT | wx.TOP, border=10)

        self.upload_button = wx.Button(panel, label="Определить заболевание мозга")
        self.upload_button.Bind(wx.EVT_BUTTON, self.uploadImage)
        vbox.Add(self.upload_button, flag=wx.LEFT | wx.TOP, border=10)

        self.image_label = wx.StaticBitmap(panel)
        vbox.Add(self.image_label, flag=wx.LEFT | wx.TOP, border=10)

        self.prr = wx.StaticText(panel)
        vbox.Add(self.prr, flag=wx.LEFT | wx.TOP, border=10)
        self.prr = wx.StaticText(panel)
        vbox.Add(self.prr, flag=wx.LEFT | wx.TOP, border=10)
        self.prr = wx.StaticText(panel)
        vbox.Add(self.prr, flag=wx.LEFT | wx.TOP, border=10)
        self.prr = wx.StaticText(panel)
        vbox.Add(self.prr, flag=wx.LEFT | wx.TOP, border=10)
        self.prr = wx.StaticText(panel)
        vbox.Add(self.prr, flag=wx.LEFT | wx.TOP, border=10)
        self.prr = wx.StaticText(panel)
        vbox.Add(self.prr, flag=wx.LEFT | wx.TOP, border=10)
        self.prr = wx.StaticText(panel)
        vbox.Add(self.prr, flag=wx.LEFT | wx.TOP, border=10)
        self.prr = wx.StaticText(panel)
        vbox.Add(self.prr, flag=wx.LEFT | wx.TOP, border=10)

        self.massopr = wx.StaticText(panel)
        vbox.Add(self.massopr, flag=wx.LEFT | wx.TOP, border=10)

        self.lexit = wx.Button(panel, label="Выйти")
        self.lexit.Bind(wx.EVT_BUTTON, self.OnExit)
        vbox.Add(self.lexit, flag=wx.ALIGN_CENTER | wx.BOTTOM, border=10)

        panel.SetSizer(vbox)

        self.mmem = [-1, -1, -1]
        self.kz = 0
#Переход в окно шаблона:
    def OnOpenTemplatesWindow(self, event):
        username = self.temp.GetName()
        templates_window = TemplatesWindow(None, title="Шаблон РЗГМ.24", username=username)
        templates_window.Show()
        self.Close()
#Переход в окно базы данных пациентов:
    def OnOpenPatientsWindow(self, event):
        username = self.temp.GetName()
        patients_window = PatientsWindow(None, title="База данных РЗГМ.24", username=username)
        patients_window.Show()
        self.Close()
#Выбор изображения для распознавания заболевания:
    def browseImage(self, event):
        with wx.FileDialog(self, "Выберите изображение", wildcard="Image files (*.png;*.jpg;*.jpeg)|*.png;*.jpg;*.jpeg",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            pathname = fileDialog.GetPath()
            self.image_path_input.SetValue(pathname)
            image = wx.Image(pathname, wx.BITMAP_TYPE_ANY)
            self.image_label.SetBitmap(wx.Bitmap(image.Scale(200, 200)))
#Запуск нейросети для выбранного изображения:
    def uploadImage(self, event):
    # Проверяем, выбрано ли изображение
        if not self.image_path_input.GetValue():
            wx.MessageBox("Выберите другое изображение!", "Ошибка", wx.OK | wx.ICON_ERROR)
            return

        model = keras.models.load_model('tumor11.h5')
        path = self.image_path_input.GetValue()

        def predict_image(img_path, model):
            img = image.load_img(img_path, target_size=(224, 224))
            img_array = image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)
            img_array /= 255.0

            prediction = model.predict(img_array)

            labels = ["Гипофиз", "Глиома", "Здоровый мозг", "Менингиома"]

            self.predicted_class_index = np.argmax(prediction)
            self.prr.SetLabel("На изображении: " + labels[self.predicted_class_index])

        predict_image(path, model)

        if self.mmem[self.kz] == -1:
            self.mmem[self.kz] = self.predicted_class_index
            labels = ["Гипофиз", "Глиома", "Здоровый мозг", "Менингиома"]
            self.mmem[self.kz] = labels[self.predicted_class_index]

    def OnExit(self, event):
        self.Close()

#Изменения пароля
class CodeVerificationWindow(wx.Frame):
    def __init__(self, *args, **kw):
        self.email = kw.pop('email', None)
        super(CodeVerificationWindow, self).__init__(*args, **kw)
        self.SetSize(wx.Size(340, 215))
        loc = wx.IconLocation(r'C:\Users\SystemX\.vscode\Ptoject\Icon.jpg', 0)
        self.SetIcon(wx.Icon(loc))

        self.InitUI()
#Окно изменения пароля
    def InitUI(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.code_label = wx.StaticText(panel, label="Код восстановления:")
        vbox.Add(self.code_label, flag=wx.LEFT | wx.TOP, border=10)
        self.code_input = wx.TextCtrl(panel)
        vbox.Add(self.code_input, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        self.new_password_label = wx.StaticText(panel, label="Новый пароль:")
        vbox.Add(self.new_password_label, flag=wx.LEFT | wx.TOP, border=10)
        self.new_password_input = wx.TextCtrl(panel, style=wx.TE_PASSWORD)
        vbox.Add(self.new_password_input, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        self.verify_button = wx.Button(panel, label="Подтвердить")
        self.verify_button.Bind(wx.EVT_BUTTON, self.verify_code)
        vbox.Add(self.verify_button, flag=wx.ALIGN_CENTER | wx.TOP, border=10)

        panel.SetSizer(vbox)
        self.SetTitle('Восстановление пароля')
        self.Centre()

    def verify_code(self, event):
        global recovery_code
        entered_code = self.code_input.GetValue()
        new_password = self.new_password_input.GetValue()

        if entered_code == recovery_code:
            if self.update_password(self.email, new_password):
                wx.MessageBox('Код подтвержден. Пароль успешно изменен.', 'Успех', wx.OK | wx.ICON_INFORMATION)
                self.Close()
            else:
                wx.MessageBox('Ошибка при обновлении пароля.', 'Ошибка', wx.OK | wx.ICON_ERROR)
        else:
            wx.MessageBox('Неверный код восстановления. Попробуйте снова.', 'Ошибка', wx.OK | wx.ICON_ERROR)

    def update_password(self, email, new_password):
        """Обновление пароля пользователя в базе данных"""
        email = 'tap885@mail.ru'
        try:
            conn = sqlite3.connect('databases.db')
            cursor = conn.cursor()
            # Расшифровываем старый пароль перед обновлением
            cursor.execute("SELECT password FROM users WHERE email=?", (email,))
            result = cursor.fetchone()
            if result:
                old_encrypted_password = result[0]
                old_password = decrypt_password(old_encrypted_password)
                # Хэшируем новый пароль перед сохранением в базу данных
                new_encrypted_password = hash_password(new_password)
                cursor.execute("UPDATE users SET password = ? WHERE email = ?", (new_encrypted_password, email))
                conn.commit()
                conn.close()
                return True
            else:
                print("Пользователь с таким email не найден.")
                return False
        except Exception as e:
            print(f'Ошибка при обновлении пароля: {e}')
            return False
        
def decrypt_password(encrypted_password):
    """Расшифровка пароля."""
    return encrypted_password

#Класс окна администрирования:
class PatientsWindow(wx.Frame):
    def __init__(self, *args, username, **kw):
        super(PatientsWindow, self).__init__(*args, **kw)
        self.SetSize(wx.Size(600, 500))
        loc = wx.IconLocation(r'C:\Users\SystemX\.vscode\Ptoject\Icon.jpg', 0)
        self.SetIcon(wx.Icon(loc))
        
        self.username = username
        self.InitUI()
#Окно администрирования:
    def InitUI(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.table_widget = wx.ListCtrl(panel, style=wx.LC_REPORT)
        vbox.Add(self.table_widget, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

        self.lbl2 = wx.StaticText(panel, label="Напишите данные паниента:")
        vbox.Add(self.lbl2, flag=wx.LEFT | wx.TOP, border=10)

        self.idaddd = wx.TextCtrl(panel)
        vbox.Add(self.idaddd, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        self.add_button = wx.Button(panel, label="Добавить")
        self.add_button.Bind(wx.EVT_BUTTON, self.addd)
        vbox.Add(self.add_button, flag=wx.ALIGN_CENTER | wx.TOP, border=10)

        self.lbl3 = wx.StaticText(panel, label="Напишите id пациента, которого ходите удалить:")
        vbox.Add(self.lbl3, flag=wx.LEFT | wx.TOP, border=10)

        self.iddell = wx.TextCtrl(panel)
        vbox.Add(self.iddell, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        self.del_button = wx.Button(panel, label="Удалить")
        self.del_button.Bind(wx.EVT_BUTTON, self.delll)
        vbox.Add(self.del_button, flag=wx.ALIGN_CENTER | wx.TOP, border=10)

        vbox.Add(hbox, flag=wx.EXPAND | wx.TOP, border=10)

        self.shh_button = wx.Button(panel, label="Обновить")
        self.shh_button.Bind(wx.EVT_BUTTON, self.ref)
        hbox.Add(self.shh_button, flag=wx.LEFT | wx.BOTTOM, border=10)

        hbox.AddStretchSpacer()
        self.temp = wx.Button(panel, label="Назад")
        self.temp.Bind(wx.EVT_BUTTON, self.Returnn)
        hbox.Add(self.temp, flag=wx.RIGHT | wx.BOTTOM, border=10)

        panel.SetSizer(vbox)
#Выход обратно в основное окно:
    def Returnn(self, event):
        username = self.temp.GetName()
        self.user_dashboard = UserDashboardWindow(None, title="РЗГМ.24", username=username)
        self.user_dashboard.Show()
        self.Close()
#Обновлении базы данных:
    def ref(self, event):
        conn = sqlite3.connect('databases.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients")
        rows = cursor.fetchall()

        self.table_widget.ClearAll()
        columns = [description[0] for description in cursor.description]
        for col, column in enumerate(columns):
            self.table_widget.InsertColumn(col, column)

        for row in rows:
            self.table_widget.Append(row)

        conn.close()
#Добавление в базу данных
    def addd(self, event):
        idd = self.idaddd.GetValue()
        parts = idd.split(',')

        if len(parts) != 5:
            wx.MessageBox("Введите данные в формате: Порядковый номер, ФИО, Возвраст, Диагноз, Дата", "Ошибка", wx.OK | wx.ICON_ERROR)
            return

        id, name, age, diagnosis, data = parts
        id = id.strip()
        name = name.strip()
        age = age.strip()
        diagnosis = diagnosis.strip()
        data = data.strip()

        if not id or not name or not age or not diagnosis or not data:
            wx.MessageBox("Все поля должны быть заполнены!", "Ошибка", wx.OK | wx.ICON_ERROR)
            return

        try:
            age = int(age)
        except ValueError:
            wx.MessageBox("Возраст должен быть числом!", "Ошибка", wx.OK | wx.ICON_ERROR)
            return

        data = datetime.now().strftime('%d.%m.%Y')

        conn = sqlite3.connect('databases.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO patients (id, name, age, diagnosis, date) VALUES(?, ?, ?, ?, ?)", (id, name, age, diagnosis, data))
        conn.commit()
        conn.close()

        self.ref(None)
        self.input_field.SetValue("")
#Удаление из базы данных
    def delll(self, event):
        idd = self.iddell.GetValue()
        conn = sqlite3.connect('databases.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM patients WHERE id = ?", (idd,))
        conn.commit()
        conn.close()
        self.ref(None)

    def OnExit(self, event):
        self.Close()
#Запуск приложения:
if __name__ == '__main__':
    app = wx.App()
    login_window = LoginWindow(None, title="Авторизация")
    login_window.Show()
    app.MainLoop()
