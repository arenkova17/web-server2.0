from fastapi import FastAPI, Request
import uvicorn  # сервер для запуска питон приложений
from fastapi.responses import HTMLResponse, \
    RedirectResponse  # 1 - отправление html страниц, 2 - перенаправление юзера по разным страницам
from database import get_clients_page, get_total_count, get_contract_id, update_par, search_dog, get_dog_payments, \
    verify_windows_login, get_user_otd, add_dog_payment, delete_dog_payments, get_dog_payments1С, get_ds_data
from starlette.middleware.sessions import SessionMiddleware  # созданий сессий, запоминание что пользователь вошел
from starlette.middleware.base import BaseHTTPMiddleware  # проверка авторизации перед каждым запросом

# создание веб-приложения
app = FastAPI()


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):  # функция выполняется для каждого запроса
        # список путей доступных без авторизации - в нашем случае это только страница входа, иначе бы перед каждым запросом кидал страницу входа
        public_paths = ["/login", "/logout"]

        # если путь не в списке публичных, то проверяем есть ли пользователь в сессии, если да - то проходим, если нет - то отправка на логиниться
        if request.url.path not in public_paths:
            user = request.session.get("user")
            if not user:
                return RedirectResponse("/login", status_code=303)

        response = await call_next(request)
        return response


# добавляет класс работу каждый раз перед запросом
app.add_middleware(AuthMiddleware)

# для создания сесии юзера, для сохранения данных между запросами
app.add_middleware(
    SessionMiddleware,
    secret_key="arenkovaan",
    max_age=None,  # время работы сессии в секундах
    session_cookie="session",
    same_site="strict",
    https_only=False
)


# обработчик отправки логина и пароля
@app.post("/login")
async def login_post(request: Request):
    form = await request.form()  # забирает л/п
    username = form.get("username")  # достает логин
    password = form.get("password")  # достает пароль
    remote_host = "gazprosql"  # указывает на каком сервере проверять подключение

    if verify_windows_login(remote_host, username, password):  # проверяет по функции проверки из database л/п
        otd = get_user_otd(username)  # запоминает номер отдела у логина который ввели
        request.session["user"] = {"login": username, "otd": otd}  # запомниает логин пользователя
        print(f"otd из функции: {otd}")
        return RedirectResponse("/", status_code=303)  # и отправляет чувака на главную с таблицу
    else:  # если не входит чувак то по новой ввод л/п
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Вход в систему</title>
            <style>
                body { 
                    font-family: Arial; 
                    display: flex; 
                    justify-content: center; 
                    align-items: center; 
                    height: 100vh; 
                    margin: 0; 
                }
                .login-form { 
                    border: 2px solid #1073b7; 
                    padding: 30px; 
                    border-radius: 10px; 
                    width: 300px; 
                }
                input { 
                    width: 100%; 
                    padding: 8px; 
                    margin: 10px 0; 
                }
                button { 
                    background: #1073b7; 
                    color: white; 
                    border: none; 
                    padding: 10px; 
                    width: 100%; 
                    cursor: pointer; `
                }
                .error { 
                    color: red; 
                    margin-top: 
                    10px; 
                    text-align: center; 
                }
            </style>
        </head>

        <body>
            <div class="login-form">
                <h2 style="color: #0952a0;">Вход в систему</h2>
                <form method="post" action="/login">
                    <input type="text" name="username" placeholder="Логин" required>
                    <div style="position: relative;">
                        <input type="password" name="password" id="password" placeholder="Пароль" required style="width: 100%; padding: 8px; margin: 10px 0; padding-right: 40px;">
                        <span onclick="togglePassword()" style="position: absolute; right: 10px; top: 50%; transform: translateY(-50%); cursor: pointer;">Показать</span>
                    </div>
                    <button type="submit">Войти</button>
                </form>
                <p class="error">Неверный логин или пароль</p>
            </div>

            <script>
            function togglePassword() {
                var passwordField = document.getElementById('password');
                passwordField.type = passwordField.type === 'password' ? 'text' : 'password';
            }
            </script>
        </body>
        </html>
        """)


# окно ввода логина и пароля
@app.get("/login", response_class=HTMLResponse)
def login_page():
    return """
    <html>
    <head>
        <title>Вход в систему</title>
        <style>
            body {        
                font-family: Arial; 
                display: flex; 
                justify-content: center; 
                align-items: center; 
                height: 100vh;
            }
            .login-form {      /* рамка */  
                border: 2px solid #1073b7; 
                padding: 30px; 
                border-radius: 10px; 
                width: 300px; 
            }
            input {          /* два инпута */
                width: 100%; 
                padding: 8px; 
                margin: 10px 0; 
            }
            button {           /* для кнопок */
                background: #1073b7; 
                color: white; 
                border: none; 
                padding: 10px; 
                width: 100%; 
                cursor: pointer; 
            }
        </style>
    </head>

    <body>
    <div class="login-form">
        <h2 style="color: #0952a0;">Вход в систему</h2>
        <form method="post" action="/login">
            <input type="text" name="username" placeholder="Логин" required style="width: 100%; padding: 8px; margin: 10px 0;">

            <div style="position: relative;">
                <input type="password" name="password" id="password" placeholder="Пароль" required style="width: 100%; padding: 8px; margin: 10px 0; padding-right: 40px;">
                <span onclick="togglePassword()" style="position: absolute; right: 10px; top: 50%; transform: translateY(-50%); cursor: pointer; font-size: 12px;">Показать</span>
            </div>

            <button type="submit" style="background: #1073b7; color: white; border: none; padding: 10px; width: 100%; cursor: pointer; margin-top: 10px;">Войти</button>
        </form>
    </div>

    <!-- функция для нажатия кнопки показать и пароль станет видимым. если при нажатии кнопки звездочки, то будут буквы и наоборот -->
    <script>
    function togglePassword() {
        var passwordField = document.getElementById('password');
        if (passwordField.type === 'password') {
            passwordField.type = 'text';
        } 
        else {
            passwordField.type = 'password';
        }
    }
    </script>"""


@app.get("/logout")
async def logout(request: Request):
    # очищаем сессию
    request.session.clear()
    # отправляем на страницу входа
    return RedirectResponse("/login", status_code=303)


# функция главного экрана с пагинацией
@app.get("/", response_class=HTMLResponse)
def home(request: Request, page: int = 1, page_size: int = 4000):
    contracts = get_clients_page(request, page, page_size)  # занесение списка из строк которые будем выводить
    total_count = get_total_count(request)  # занесение общего числа строк

    # расссчитывает сколько всего должно быть страниц на всё количество с округлением вверх
    total_pages = (total_count + page_size - 1) // page_size
    html = """  
    <html>
    <head><title>Договора в ЕИС</title>  
    <style>
    .table-columns {
        width: 100%;     /* ширина таблицы */
        max-width: 100%;    /* максимально занимаемая ширина таблицы */
        table-layout: fixed;     /* фиксированные размеры столбцов */
        border-collapse: collapse;    /* делает двойные границы одной линией */
    }

.table-columns th:nth-child(1),
.table-columns td:nth-child(1) { width: 5%; }
.table-columns th:nth-child(2),
.table-columns td:nth-child(2) { width: 15%; }
.table-columns th:nth-child(3),
.table-columns td:nth-child(3) { width: 10%; }
.table-columns th:nth-child(4),
.table-columns td:nth-child(4) { width: 10%; }
.table-columns th:nth-child(5),
.table-columns td:nth-child(5) { width: 25%; }
.table-columns th:nth-child(6),
.table-columns td:nth-child(6) { width: 35%; }

    th, td {    /* th - заголовкисвойства самих ячеек */
        white-space: normal;
        word-wrap: break-word;
        overflow-wrap: break-word;
    }
    .h1 {
        background: #e4f0fb; /* Цвет фона под заголовком */
        color: #0952a0; /* Цвет текста */
        padding: 8px; /* Поля вокруг текста */
    }
    .column-names {
        color: #0952a0; /* Цвет текста */
    }
    tr:hover {
        background-color: #f5f5f5; /* цвет при наведении */
        cursor: pointer;           /* курсор в виде руки */
    }
    .pagination {      /* стиль для одной иконки страницы */
        margin: 20px 0;
        text-align: center;
    }  
    .pagination a {        /* стиль для всех иконок страниц */
        display: inline-block;
        padding: 5px 10px;
        margin: 0 2px;
        border: 1px solid #ddd;
        text-decoration: none;
    }
    .pagination a.active {     /* стиль для активной страницы, которая нажата */
        background: #032c57;
        color: white;
    }
    .button-searchdog {
        padding: 10px 20px;
        background-color: #1073b7;
        color: white;
        border: none;
        cursor: pointer;
        font-size: 16px;
        position: absolute; top: 16px; right: 20px;
    }
    .button-in-window {
        background-color: #1073b7;
        color: white;
        border: none;
        cursor: pointer;
        font-size: 14 px;
        padding: 5px 10px;
    }
    .button-exit {      /*кнопка выхода из ученой записи*/
        background-color: #1073b7;
        color: white;
        border: none;
        cursor: pointer;
        font-size: 16px;
        padding: 10px 20px;
        position: absolute; top: 16px; right: 180px;
        text-decoration: none;
    }
    </style>
    </head>

    <body>
        <h1 class="h1">Список договоров подлежащих публикации в ЕИС</h1>
        <button class="button-exit" onclick="logout()">Выйти</button>
        <button class="button-searchdog" onclick="opendialogwindow()" >Найти договор</button>
        <dialog id="dialogwindow" style="border: 2px solid black;">
            <p style="color: #1073b7; font-size: 20px;"><strong>Поиск договора</strong></p>
            <div style="margin-bottom: 10px">
                <label>№ договора(числовой)</label>
                <input type="text" id="numberdog" placeholder="Введите номер договора">
            </div>
            <div style="margin-bottom: 10px">
                <label>№ контрагента</label>
                <input type="text" id="numberkontr" placeholder="Введите номер контрагента">
            </div>
            <div style="gap: 20px;">
                <button class="button-in-window" onclick="searchdog()">Найти</button>
                <button class="button-in-window" onclick="goback()">Отмена</button>
            </div>
        </dialog>

        <table border="1" class="table-columns">
    """
    html += '<table border="1" class="table-columns">'
    if contracts:  # если список получен
        html += "<tr style='background-color: #f2f2f2;'>"  # 1 строка - заголовки. цвет - серый
        for key in contracts[0].keys():  # цикл прохода по первой строчке таблицы - заголовкам
            html += f"<th style='padding: 10px; border: 1px solid;'>{key}</th>"  # оформление текста заголовков столбцов
        html += "</tr>"
        for contract in contracts:  # проход по строчкам договоров
            contract_id = contract['ID договора']  # присваиваем id переменной
            html += f"<tr ondblclick='showContract({contract_id}, {page})'>"  # делаем строчку кликабельной
            for value in contract.values():  # проход по значениям одной строчки договора + оформление
                html += f"<td style='padding: 5px; border: 1px solid #ddd;'>{value}</td>"
            html += "</tr>"
    html += """</table> 

<script>
// функция для перехода на страницу договора при двойном клике по списку 
function showContract(id, page) {
    window.location.href = '/contract/' + id + '?from_page=' + page;
    }

// функция откытия диалогового окна после того как нажали на кнопку найти договор 
// document - главная страница, getElementById('dialogwindow') - найти элемент по id, showModal() - открыть поверх станицы, затемняя фон  
function opendialogwindow() {
    document.getElementById('dialogwindow').showModal()      
    }

// функция закрытия окна через кнопку отмена, close() - закрыть окно 
function goback() {
    document.getElementById('dialogwindow').close();
    }

// const - переменная в дальнейшем не меняется, пишем когда не объявляли переменную ранее, value - взять то что написано в элементе
function searchdog() {
    const numberdog = document.getElementById('numberdog').value
    const numberkontr = document.getElementById('numberkontr').value

    let url = '/search?';
    if (numberdog) {url += 'numberdog=' + encodeURIComponent(numberdog);}
    if (numberdog && numberkontr) {url += '&';}
    if (numberkontr) {url += 'numberkontr=' + encodeURIComponent(numberkontr);}

    window.location.href = url
    document.getElementById('dialogwindow').close()
    }

function logout() {
    window.location.href = '/logout';
}
</script>

    <div class="pagination">
    """
    for i in range(1,
                   total_pages + 1):  # рассчитывает сколько кнопок пагинации надо создать. если total_pages = 4, то кнопок 4
        active_class = "active" if i == page else ""  # определяет активную кнопку. если i равняется номеру открытой страницы, то применяется к ней стиль active_class
        html += f'<a href="/?page={i}&page_size={page_size}" class="{active_class}">{i}</a>'  # создание самой кнопки страницы

    html += """
    </div>
    </body>
    </html>
    """
    return html


# функция перехода на старницу договора когда нашли 1 договор через кнопку найти договор
@app.get("/search", response_class=HTMLResponse)
def search_page(request: Request, numberdog: str = "", numberkontr: str = ""):
    results = search_dog(request, numberdog, numberkontr)
    if len(results) == 1:
        contract_id = results[0]['ID договора']
        return HTMLResponse(f"""
            <script>
                window.location.href = '/contract/{contract_id}'
            </script>
            """)

    html = f"""
    <html>
    <head><title>Результаты поиска</title></head>
    <style>
    </style>
    <body>
    <h1>Результаты поиска</h1>
    <p>Договор: {numberdog if numberdog else 'не указан'}</p>
    <p>Контрагент: {numberkontr if numberkontr else 'не указан'}</p>
    <a href="/">Назад к списку</a>
    <table border="1" style="border-collapse: collapse; width: 100%;">
    """

    if results:
        html += "<tr style='background-color: #f2f2f2'>"
        for key in results[0].keys():
            html += f"<th style='padding: 10px; border: 1px solid;'>{key}</th>"
        html += "</tr>"

        for contract in results:
            contract_id = contract['ID договора']
            html += f"<tr ondblclick='window.location.href=\"/contract/{contract_id}\"'>"
            for value in contract.values():
                html += f"<td style='padding: 5px; border: 1px solid #ddd;'>{value}</td>"
            html += "</tr>"
    else:
        html += f"<tr><td colspan='6' style='padding: 20px; text-align: center;'>Договоры не найдены</td></tr>"

    html += "</table></body></html>"
    return html


# функция для показа информации клиента
@app.get("/contract/{contract_id}", response_class=HTMLResponse)
def contract_page(request: Request, contract_id: int, from_page: int = 1):
    # присваивание результата функции в переменную
    contract = get_contract_id(request, contract_id)
    if not contract:
        return "<h1>Договор не найден</h1>"
    ds_data = get_ds_data(request, contract_id)

    payments = get_dog_payments(request, contract_id)
    payments1C = get_dog_payments1С(request, contract_id)
    total_sum_1c = 0  # подсчет общей суммы
    if payments1C:
        for payment in payments1C:
            total_sum_1c += float(payment.get('s_opl', 0))

    konk_value = contract.get('Конкурс', 0)  # берем значение из столбца Конкурс, если значения нет - 0
    is_checked = 'checked' if konk_value == 1 else ''

    num_z_value = contract.get('№ закупки ЕИС', '')
    numzalel_value = contract.get('№ закупю на эл.пл.', '')

    przak_value = contract.get('Прямая закупка', 0)
    przak_checked = 'checked' if przak_value == 1 else ''

    beznds_value = contract.get('Без НДС', 0)
    beznds_checked = 'checked' if beznds_value == 1 else ''

    opl_value = contract.get('Оплачено', 0)
    opl_checked = 'checked' if opl_value == 1 else ''

    eis_value = contract.get('Публикация в ЕИС', 0)
    eis_checked = 'checked' if eis_value == 1 else ''

    osn_value = contract.get('Основание', '')
    gpz_value = contract.get('ГПЗ', '')
    uid_value = contract.get('UID', '')
    ppz_value = contract.get('ППЗ', '')

    prol_value = contract.get('Пролонгация', 0)
    prol_checked = 'checked' if prol_value == 1 else ''

    d_end_raw = contract.get('Дата заверш. договора', '')
    d_end_value = d_end_raw.strftime('%Y-%m-%d') if d_end_raw else ''

    sposobzak_value = contract.get('Способ закупки', '')
    VIdZAK_value = contract.get('Вид закупки', '')
    numzak_value = contract.get('№ КЗ', '')
    predlog_value = contract.get('Формат закупки', '')
    dat_docosznak = contract.get('Дата дог.осн.закупки', '')
    dat_docosznak_value = dat_docosznak.strftime('%Y-%m-%d') if dat_docosznak else ''
    smsp_value = contract.get('СМСП', '')
    num_docosnzak_value = contract.get('№ дог.осн.закупки', '')
    OSTNEKONZAK_value = contract.get('Код основания некн.зак.', '')
    okpd2_value = contract.get('ОКПД2', '')
    subectzak_value = contract.get('SUBECTZAK', '')

    s_dog_okz_value = contract.get('Сумма договора ОКЗ', '')
    s_ds_value = contract.get('Сумма с ДС', '')
    date_izv_value = contract.get('Дата извещения', '')

    agent_value = contract.get('Агентский договор', 0)
    agent_checked = 'checked' if agent_value == 1 else ''

    smsp_okz_value = contract.get('Загрузка среди СМСП', 0)
    smsp_okz_checked = 'checked' if smsp_okz_value == 1 else ''

    sysnum_value = contract.get('Системный номер', '')
    d_work_value = contract.get('Рабочая дата', '')

    predlog_txt_value = contract.get('№ предложения', '')

    # оформление страницы договора
    html = f"""
    <html>
    <head><title>Договор {contract_id}</title>
    <style>
    .button-back {{
        background: #1073b7; /* Цвет фона */
        font-size: 18px; /* Размер текста */
        padding: 5px 20px; /* Поля вокруг текста */
        color: white;
        text-decoration: none;
        border-radius: 4px; 
    }}
    .button-back:hover {{
        background: #0952a0;
        border-radius: 4px; 
    }}
    .h1 {{
        background: #e4f0fb; /* Цвет фона под заголовком */
        color: #0952a0; /* Цвет текста */
        padding: 8px; /* Поля вокруг текста */
    }}
    .info-container {{    /* фон под информацией */
        background: #f8f9fa;  /* Светло-серый фон */
        padding-top: 10px;
        padding-left: 20px;
        padding-right: 20px;
        padding-bottom: 10px; 
        border-radius: 10px;
        margin: 20px 0;
        display: flow-root; 
    }}
    .konk-Сheckbox {{   /* квадратик с галочкой */
        width: 24px;
        height: 24px;
        cursor: pointer;
    }}
    .button-save {{
        background: #1073b7;       /* фон кнопки */ 
        font-size: 18px;      /* размер текста */
        padding: 5px 20px;      /* отступы для текста внутри кнопки */
        color: white;    /* цвет текста */
        text-decoration: none;      /* убирает подчерквание */
        cursor: pointer;     /* курсор руки при наведении */
        border-radius: 4px;     /* сруление углов кнопки */
        font-family: inherit;    /* наследование */
        border: 1px solid #1073b7;
    }}
    .button-save:hover {{
        background: #0952a0;    /* темно синий при наведении мыши */
        border: 1px solid #1073b7
    }}

    .button-adddeletepayment {{
        width: 30px; 
        height: 30px; 
        background: #1073b7; 
        color: white; 
        border: none; 
        border-radius: 3px; 
        cursor: pointer; 
        font-size: 20px;
    }}
    </style>
    </head>

    <body>
    <h1 class="h1">Информация по договору {contract_id}</h1>

    <div class="info-container">

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 0px; width: 80%">   <!--начало двух столбцов-->
        <div>    <!--контейнер левого столбца-->
        <!-- СВЕРХУ СЛЕВА -------------------------->
        <div style="line-height: 24px; width: 100%;">
            <div style="width: 100%; display: flex; gap: 90px;">
                <span><strong>№ договора:</strong> {contract.get('№ договора', 'Нет данных')}</span>
                <span><strong>№ контрагента:</strong> {contract.get('№ контрагента', 'Нет данных')}</span>
            </div>

            <div style="display: flex; gap: 50px; align-items: center; width: 100%">
                <div><strong>Дата регистрации:</strong> {str(contract.get('Дата регистрации', ''))[:10]}</div>
                <div><strong>Дата договора:</strong> {str(contract.get('Дата договора', ''))[:10]}</div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <input type="checkbox" id="konkCheckbox" {is_checked}>
                    <label for="konkCheckbox" style="cursor: pointer;"><strong>Конкурс</strong></label>
                </div>
            </div>

            <div style="width: 100%"><strong>Подразделение:</strong> {contract.get('Подразделение', 'Нет данных')}</div>
            <div style="width: 100%; word-wrap: break-word;"><strong>Предмет договора:</strong> {contract.get('Предмет договора', 'Нет данных')}</div>
            <div style="display: flex; gap: 40px; width: 100%">
                <span><strong>Дата начала:</strong> {str(contract.get('Дата начала', ''))[:10]}</span>
                <span><strong>Дата конца:</strong> {str(contract.get('Дата конца', ''))[:10]}</span>
                <span><strong>Сумма договора:</strong> {contract.get('Сумма договора', 'Нет данных')} рублей</span>
            </div>
        </div>
        <!--КОНЕЦ СВЕРХУ СЛЕВА--------------------->

        <!-- КОНТРАГЕНТ ----------------------->
        <div style="border: 2px solid #1073b7; padding: 15px; border-radius: 8px; margin: 15px 0 10px 0;">
            <h3 style="margin: 0 0 10px 0; color: #0952a0;">Контрагент</h3>

            <div style="line-height: 25px;">
                <div><strong>Наименование:</strong> {contract.get('Наименование', 'Нет данных')}</div>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 0px;">

                        <div style="line-height: 25px;">
                            <div><strong>ИНН:</strong> {contract.get('ИНН', '')}</div>
                            <div><strong>Расч.счет:</strong> {contract.get('Расч.счет', '')}</div>
                        </div>

                        <div style="line-height: 25px;">
                            <div><strong>КПП:</strong> {contract.get('КПП', '')}</div>
                            <div><strong>Телефон/факс:</strong> {contract.get('Телефон/факс', '')}</div>
                        </div>
                </div>

                <div><strong>БИК:</strong> {contract.get('БИК', 'Нет данных')}</div>
            </div>
        </div>
        <!--КОНЕЦ КОНТРАГЕНТА--------------------->

        <!-- НИЖЕ КОНТРАГЕНТА ---------------->
        <div style="line-height: 28px;">
            <div style="display: flex; gap: 25px;">
                <div><label><strong>№ закупки ЕИС</strong></label>
                <input type="text" id="num_z" value="{num_z_value}" size="15"></div>

                <div><label><strong>№ закуп. на эл.пл.</strong></label>
                <input type="text" id="numzalel" value="{numzalel_value}" size="15"></div>
            </div>

            <div style="display: flex; gap: 25px;">
                <div><input type="checkbox" id="przakcheckbox" {przak_checked}>
                <label for="przakcheckbox" style="cursor: pointer;"><strong>Прямая закупка</strong></label></div>

                <div><label><strong>Основание</strong></label>
                <input type="text" id="osn" value="{osn_value}" size="15"></div>

                <div><label><strong>ГПЗ</strong></label>
                <input type="text" id="gpz" value="{gpz_value}" size="15"></div>
            </div>

            <div style="display: flex; gap: 25px;">
                <div><label><strong>UID</strong></label>
                <input type="text" id="uid" value="{uid_value}" size="20"></div>

                <div><label><strong>ППЗ</strong></label>
                <input type="text" id="ppz" value="{ppz_value}" size="15"></div>
            </div>
        </div>
        <!--КОНЕЦ НИЖЕ КОНТРАГЕНТА------------------>
        </div>     <!-- закрытие левого столбца-->

        <div>       <!-- открытие правого столбца -->
        <!-- СВЕРХУ СПРАВА-----------------> 
        <div style="">
            <div style="display: flex; gap: 30px; margin-bottom: 10px;">
                <div><input type="checkbox" id="prol" {prol_checked}>
                <label for="prol" style="cursor: pointer;"><strong>Пролонгация</strong></label></div>

                <div><input type="checkbox" id="beznds" {beznds_checked}>
                <label for="beznds" style="cursor: pointer;"><strong>Без НДС</strong></label></div>

                <div><strong>Код ОБД НСИ</strong> {contract.get('Код ОБД НСИ', 'Нет данных')}</div>
            </div>

            <div style=" display: flex; flex-direction: column;">
                <div><input type="checkbox" id="opl" {opl_checked}>
                <label for="opl" style="cursor: pointer;"><strong>Оплачено</strong></label></div>

                <div style="margin-bottom: 10px;"><input type="checkbox" id="eis" {eis_checked}>
                <label for="eis" style="cursor: pointer; "><strong>Публикация в ЕИС</strong></label></div>
            </div>

            <div style="margin-bottom: 10px;">
                <label><strong>Дата заверш. договора</strong></label>
                <input type="date" id="d_end" value="{d_end_value}">

                <div>
                    <label for="statusD"><strong>СТАТУС</strong></label>
                    <select name="statusD" id="status">
                    <option value="2">Подписан</option>
                    <option value="4">Закрыт</option>
                    </select>
                </div>
            </div>
        </div>
        <!--КОНЕЦ СВЕРХУ СПРАВА----------------->

        <!-- РЕКВИЗИТЫ------------------->
        <div style="width: 100%; border: 2px solid #1073b7; padding: 15px 15px 5px 20px; border-radius: 8px; margin: 10px 0;">
            <h3 style="margin: 0 0 10px 0; color: #0952a0;">Реквизиты</h3>

            <div style="line-height: 28px;">
                <div style="display: flex; gap: 50px;">
                    <div><form action="#" style="margin-bottom: 0;">
                        <label for="sposobzak"><strong>Способ закупки</strong></label>
                        <select name="sposobzak" id="sposobzak">
                        <option value="001" {'selected' if sposobzak_value == '001' else ''}>001</option>
                        <option value="002" {'selected' if sposobzak_value == '002' else ''}>002</option>
                        <option value="003" {'selected' if sposobzak_value == '003' else ''}>003</option>
                        <option value="004" {'selected' if sposobzak_value == '004' else ''}>004</option>
                        <option value="005" {'selected' if sposobzak_value == '005' else ''}>005</option>
                        <option value="006" {'selected' if sposobzak_value == '006' else ''}>006</option>
                        <option value="007" {'selected' if sposobzak_value == '007' else ''}>007</option>
                        <option value="008" {'selected' if sposobzak_value == '008' else ''}>008</option>
                        <option value="009" {'selected' if sposobzak_value == '009' else ''}>009</option>
                        <option value="010" {'selected' if sposobzak_value == '010' else ''}>010</option>
                        <option value="011" {'selected' if sposobzak_value == '011' else ''}>011</option>
                        <option value="012" {'selected' if sposobzak_value == '012' else ''}>012</option>
                        <option value="013" {'selected' if sposobzak_value == '013' else ''}>013</option>
                        <option value="014" {'selected' if sposobzak_value == '014' else ''}>014</option>
                        <option value="015" {'selected' if sposobzak_value == '015' else ''}>015</option>
                        <option value="016" {'selected' if sposobzak_value == '016' else ''}>016</option>
                        <option value="017" {'selected' if sposobzak_value == '017' else ''}>017</option>
                        <option value="018" {'selected' if sposobzak_value == '018' else ''}>018</option>
                        </select>
                    </form> 
                    </div>

                    <div >
                        <form action="#" style="margin-bottom: 0;">
                            <label for="VIdZAK"><strong>Вид закупки</strong></label>
                            <select name="VIdZAK" id="VIdZAK">
                                <option value="001" {'selected' if VIdZAK_value == '001' else ''}>001</option>
                                <option value="002" {'selected' if VIdZAK_value == '002' else ''}>002</option>
                            </select>
                        </form> 
                    </div>
                </div>

                <div style="display: flex; gap: 50px;">
                    <div style="margin-bottom: 0;">
                        <label><strong>№ КЗ</strong></label>
                        <input type="text" id="numzak" value="{numzak_value}" size="15">
                    </div>

                    <div>
                        <form action="#" style="margin-bottom: 0;">
                            <label for="predlog"><strong>Формат закупки</strong></label>
                        <select name="predlog" id="predlog">
                            <option value="opened" {'selected' if predlog_value == 'opened' else ''}>Открытая</option>
                            <option value="closed" {'selected' if predlog_value == 'closed' else ''}>Закрытая</option>
                        </select>
                        </form>
                    </div>
                </div>

                <div style="display: flex; gap: 50px;">
                    <div>
                        <label><strong>Дата док.осн.зак.</strong></label>
                        <input type="date" id="dat_docosznak" value="{dat_docosznak_value}">
                    </div>

                    <div>
                        <label><strong>СМСП</strong></label>
                        <input type="text" id="smsp" value="{smsp_value}" size="15">
                    </div>
                </div>

                <div>
                    <label><strong>№ док.осн.зак.</strong></label>
                    <input type="text" id="num_docosnzak" value="{num_docosnzak_value}" size="15">
                </div>

                <div>
                    <label><strong>Код основания некн.зак.</strong></label>
                    <input type="text" id="OSTNEKONZAK" value="{OSTNEKONZAK_value}" size="15">
                </div>

                <div style="display: flex; gap: 50px;">
                    <div>
                        <label><strong>ОКПД2</strong></label>
                        <input type="text" id="okpd2" value="{okpd2_value}" size="15">
                    </div>

                    <div>
                        <form action="#" style="margin-bottom: 0">
                            <label for="subectzak"><strong>SUBECTZAK</strong></label>
                            <select name="subectzak" id="subectzak">
                                <option value="001" {'selected' if subectzak_value == '001' else ''}>001</option>
                                <option value="002" {'selected' if subectzak_value == '002' else ''}>002</option>
                            </select>
                        </form> 
                    </div>
                </div>
            </div>
        </div>
        <!--КОНЕЦ РЕКВИЗИТОВ-------------->
        </div>       <!-- закрытие правого столбца-->
        </div>       <!--закрытие таблицы-->


        <div style="display: flex; justify-content: flex-start; align-items: flex-start; gap:20px;">        <!--открытие контейнера с нижней частью-->
        <!-- ТАБЛИЦА ОПЛАТ -->
        <div style="max-height: 200px; overflow-y: auto; width: 20%; border: 2px solid #1073b7; padding: 15px; border-radius: 8px; margin: 15px 0;">
            <div style="margin-bottom: 5px; display: flex; justify-content: space-between; align-items: center;">
                <h3 style="margin: 0px; color: #0952a0;">Оплаты по договору</h3>
                <div style="display: flex; gap: 15px; align-items: center;">
                    <button onclick="showAddPaymentForm()" class="button-adddeletepayment"><strong>+</strong></button>
                    <button onclick="deleteSelectedPayment()" class="button-adddeletepayment"><strong>-</strong></button>
                </div>
            </div>

            <div id="addPaymentForm" style="display: none; margin-bottom: 0px; padding: 10px; background: #f8f9fa; border-radius: 4px;">
                <input type="text" id="newPaymentSum" placeholder="Сумма" style="width: 45%; padding: 5px; margin-right: 5px;">
                <input type="date" id="newPaymentDate" style="width: 45%; padding: 5px; margin-right: 5px;">
                <div style="margin-top: 3px;"><button onclick="saveNewPayment({contract_id})" style="background: #1073b7; color: white; border: none; padding: 5px 10px; border-radius: 4px;">Сохранить</button>
                <button onclick="hideAddPaymentForm()" style="background: #6c757d; color: white; border: none; padding: 5px 10px; border-radius: 4px;">Отмена</button></div>
            </div>

            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="background-color: #e4f0fb;">
                        <th style="padding: 8px; border: 1px solid #1073b7;">✓</th>
                        <th style="padding: 8px; border: 1px solid #1073b7;">Сумма</th>
                        <th style="padding: 8px; border: 1px solid #1073b7;">Дата</th>
                    </tr>
                </thead>
                <tbody>
        """
    if payments:
        for payment in payments:
            html += f"""
                    <tr>
                        <td style="padding: 5px; border: 1px solid #ddd; text-align: center;">
                            <input type="checkbox" class="payment-checkbox" value="{payment['id_opl']}">
                        </td>
                        <td style="padding: 5px; border: 1px solid #ddd;">{payment['s_opl']}</td>
                        <td style="padding: 5px; border: 1px solid #ddd;">{payment['d_opl'].strftime('%Y-%m-%d') if payment['d_opl'] else ''}</td>
                    </tr>
                """
    else:
        html += """
                    <tr>
                        <td colspan="3" style="padding: 20px; text-align: center; color: #666;">Оплаты по договору отсутствуют</td>
                    </tr>
            """
    html += """
                </tbody>
            </table>
        </div>       

        <script>
        function showAddPaymentForm() {
            document.getElementById('addPaymentForm').style.display = 'block';
        }

        function hideAddPaymentForm() {
            document.getElementById('addPaymentForm').style.display = 'none';
            document.getElementById('newPaymentSum').value = '';
            document.getElementById('newPaymentDate').value = '';
        }

        function saveNewPayment(contractId) {
            const sum = document.getElementById('newPaymentSum').value;
            const date = document.getElementById('newPaymentDate').value;

            if (!sum || !date) {
                alert('Заполните сумму и дату');
                return;
            }

            fetch(`/api/contract/${contractId}/add_payment`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ summa: sum, date: date })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert('Ошибка при добавлении оплаты');
                }
            });
        }

        function deleteSelectedPayment() {
            const checkboxes = document.querySelectorAll('.payment-checkbox:checked');
            const selectedIds = Array.from(checkboxes).map(cb => cb.value);

            if (selectedIds.length === 0) {
                alert('Выберите оплаты для удаления');
                return;
            }

            if (confirm(`Удалить ${selectedIds.length} запись(ей)?`)) {
                fetch('/api/contract/delete_payments', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ payment_ids: selectedIds })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        location.reload();
                    } else {
                        alert('Ошибка при удалении');
                    }
                });
            }
        }
        </script>
        <!-- КОНЕЦ ТАБЛИЦЫ ОПЛАТ--------------------->
        """

    html += f"""
        <!-- ПОЛЯ МЕЖДУ ТАБЛИЦАМИ---------------------->
        <div style="line-height: 23px; margin-top: 25px;">
            <div style="display: flex; gap: 5px; align-items: center; margin-top: 0px;">
                <input type="checkbox" id="smsp_okz" {smsp_okz_checked}>
                <label for="smsp_okz"><strong>Загрузка среди СМСП</strong></label>
            </div>
            
            <div style="display: flex; gap: 5px; justify-content: space-between; margin-bottom: 5px;">
                <label for="summaokz"><strong>Сумма договора ОКЗ</strong></label>
                <input type="text" id="summaokz" value="{s_dog_okz_value}" size="15">
            </div>

            <div style="display: flex; gap: 5px; justify-content: space-between; margin-bottom: 5px;">
                <label for="summasds"><strong>Сумма c ДС</strong></label>
                <input type="text" id="summasds" value="{s_ds_value}" size="15">
            </div>
            
            <div style="display: flex; gap: 5px; justify-content: space-between; margin-bottom: 5px;">
                <label for="dateizv"><strong>Дата извещения</strong></label>
                <input type="date" id="dateizv" value="{date_izv_value}" size="15">
            </div>
            
            <div style="display: flex; gap: 5px; align-items: center; margin-bottom: 5px;">
                <input type="checkbox" id="agent" {agent_checked}>
                <label for="agent"><strong>Агентский договор</strong></label>
            </div>
            
            <div style="display: flex; gap: 5px; align-items: center; margin-bottom: 5px;">
                <label for="sysnum"><strong>Системный номер</strong></label>
                <input type="text" id="sysnum" value="{sysnum_value}">    
            </div>
           
            <div style="display: flex; gap: 5px; align-items: center; margin-bottom: 5px;">
                <label for="d_work"><strong>Рабочая дата</strong></label>
                <input type="date" id="d_work" value="{d_work_value}">    
            </div>
            
            <div style="display: flex; gap: 5px; align-items: center; margin-bottom: 5px;">
                <label for="predlog_txt"><strong>№ предложения</strong></label>
                <input type="text" id="predlog_txt" value="{predlog_txt_value}">    
            </div>
        </div>
        <!-- ПОЛЯ МЕЖДУ ТАБЛИЦАМИ---------------------->

        <!-- ТАБЛИЦА ИЗ DSPROC -->
        <div style="max-height: 200px; overflow-y: auto; width: 30%; border: 2px solid #1073b7; padding: 15px; border-radius: 8px; margin: 15px 0;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <h3 style="margin: 0; color: #0952a0;">Дополнительные соглашения</h3>
            </div>

            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="background-color: #e4f0fb;">
                        <th style="padding: 8px; border: 1px solid #1073b7;">№ дс</th>
                        <th style="padding: 8px; border: 1px solid #1073b7;">Дата рег.</th>
                        <th style="padding: 8px; border: 1px solid #1073b7;">Дата нач.</th>
                        <th style="padding: 8px; border: 1px solid #1073b7;">Дата оконч.</th>
                        <th style="padding: 8px; border: 1px solid #1073b7;">azec_ds</th>
                    </tr>
                </thead>
                <tbody>
        """
    if ds_data:
        for item in ds_data:
            html += f"""
                    <tr>
                        <td style="padding: 5px; border: 1px solid #ddd;">{item.get('numds', '')}</td>
                        <td style="padding: 5px; border: 1px solid #ddd;">{item.get('drds', '')}</td>
                        <td style="padding: 5px; border: 1px solid #ddd;">{item.get('dnds', '')}</td>
                        <td style="padding: 5px; border: 1px solid #ddd;">{item.get('dkds', '')}</td>
                        <td style="padding: 5px; border: 1px solid #ddd;">{item.get('azes_ds', '')}</td>
                    </tr>
                """
    else:
        html += """
                    <tr>
                        <td colspan="5" style="padding: 20px; text-align: center; color: #666;">Данные отсутствуют</td>
                    </tr>
            """
    html += """
                </tbody>
            </table>
        </div>
        <!-- КОНЕЦ ТАБЛИЦЫ ИЗ DSPROC -->

        """
    html += f"""

        <!-- ДВЕ КНОПКИ -->
        <div style="display: flex; width: 97%; justify-content: space-between; position: fixed; bottom: 20px;">
            <div>
                <a href="/?page={from_page}" class="button-back"> Назад к списку</a>
            </div> 
            <div>   
                <button id="saveButton" onclick="savepar()" class="button-save">Cохранить</button>
            </div>
        </div>


        <!-- ТАБЛИЦА ОПЛАТ ИЗ 1С -->
        <div style="max-height: 200px; overflow-y: auto; width: 20%; padding: 15px; margin: 15px 0; border: 2px solid #1073b7; border-radius: 8px;">
            <h3 style="margin: 0 0 10px 0; color: #0952a0;">Оплаты из 1С на сумму {total_sum_1c:.2f}</h3>

            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="background-color: #e4f0fb;">
                        <th style="padding: 8px; border: 1px solid #1073b7;">Сумма</th>
                        <th style="padding: 8px; border: 1px solid #1073b7;">Дата</th>
                    </tr>
                </thead>
                <tbody>
        """
    if payments1C:
        for payment in payments1C:
            html += f"""
                    <tr>
                        <td style="padding: 5px; border: 1px solid #ddd;">{payment.get('s_opl', '')}</td>
                        <td style="padding: 5px; border: 1px solid #ddd;">{payment['d_opl'].strftime('%Y-%m-%d') if payment['d_opl'] else ''}</td>
                    </tr>
                """
    else:
        html += """
                    <tr>
                        <td colspan="2" style="padding: 20px; text-align: center; color: #666;">Оплаты из 1С отсутствуют</td>
                    </tr>
                </tbody>
            </table>
        </div>
        <!-- КОНЕЦ ТАБЛИЦЫ ОПЛАТ ИЗ 1С -->

        </div>           <!--закрытие контейнера с нижней частью-->

    </div>             <!-- закрытие общего контейнера с фоном -->



</body>
</html>


<script>
function savepar() {{
    const saveButton = document.getElementById('saveButton')    //ищется кнопка сохранить 
    saveButton.textContent = "Сохранение...";   //смена текста после нажатия кнопки 
    saveButton.disabled = true;    //не дает второй раз надать пока не загорится снова синим 

    const data = {{      //сбор всех полей которые изменили и не изменили для дальнейшего сохранения 
        konk: document.getElementById('konkCheckbox').checked ? 1 : 0,
        prol: document.getElementById('prol').checked ? 1 : 0,      
        beznds: document.getElementById('beznds').checked ? 1 : 0,  
        opl: document.getElementById('opl').checked ? 1 : 0,        
        eis: document.getElementById('eis').checked ? 1 : 0,      
        statusD: document.getElementById('status').value, 
        d_end: document.getElementById('d_end').value,

        sposobzak: document.getElementById('sposobzak').value,
        VIdZAK: document.getElementById('VIdZAK').value,
        numzak: document.getElementById('numzak').value,
        predlog: document.getElementById('predlog').value === 'opened' ? 1 : 0,
        dat_docosznak: document.getElementById('dat_docosznak').value,
        num_docosnzak: document.getElementById('num_docosnzak').value,
        smsp: document.getElementById('smsp').value,
        OSTNEKONZAK: document.getElementById('OSTNEKONZAK').value,
        okpd2: document.getElementById('okpd2').value,
        subectzak: document.getElementById('subectzak').value,

        num_z: document.getElementById('num_z').value,
        num_z_el: document.getElementById('numzalel').value,
        pr_z: document.getElementById('przakcheckbox').checked ? 1 : 0,
        pr_z_osn: document.getElementById('osn').value, 
        gpz: document.getElementById('gpz').value,
        uid: document.getElementById('uid').value,
        ppz: document.getElementById('ppz').value,    
        
        s_dog_okz: document.getElementById('summaokz').value, 
        s_ds: document.getElementById('summasds').value,
        date_izv: document.getElementById('dateizv').value, 
        
        agent: document.getElementById('agent').checked ? 1 : 0,
        smsp_okz: document.getElementById('smsp_okz').checked ? 1 : 0,
        d_work: document.getElementById('d_work').value,
        predlog_txt: document.getElementById('predlog_txt').value
        
    }};
    console.log('Данные для отправки:', data);

    //отправляем запрос на сервер, method: 'POST' - отправить данные
    fetch('/api/contract/{contract_id}/update', {{      //fetch - функция для отправление запросов на сервер, в нашем случае на адрес которые делает сохранение полей 
        method: 'POST',       //метод post - отправление/обновление данных. есть ещё get - он для получения данных
        headers: {{ 'Content-Type': 'application/json' }},   //пищет что мы отправляем. в нашем случае json строку
        body: JSON.stringify(data)     //изменяет js в json
    }})

    .then(response => response.json())    //меняем json строку в js объект 
    .then(data => {{
        if (data.success) {{     //если успешно поменялось поле в таблице изменяем текст и цвет кнопки
            saveButton.textContent = "Сохранено";
            saveButton.style.background = "#28a745";
        }} else {{
            saveButton.textContent = "Ошибка"; 
            saveButton.style.background = "#dc3545";
        }}

        setTimeout(() => {{     //функция позволяет запустить код с задержкой, в нашем случае изменить текст и цвет кнопки 
            saveButton.textContent = "Сохранить";
            saveButton.style.background = "#1073b7";
            saveButton.disabled = false;        //чтобы второй раз не нажал на сохранение иначе второй раз запрос будет проходить 
        }}, 4000);
    }});
}}
</script>
    </body>
    </html>
    """
    return html


@app.post("/api/contract/{contract_id}/update")
async def update_contract_api(contract_id: int, request: Request):
    # собирает параметры перед нажатием кнопки сохранить
    try:
        data = await request.json()

        konk = data.get('konk', 0)
        prol = data.get('prol', 0)
        beznds = data.get('beznds', 0)
        opl = data.get('opl', 0)
        eis = data.get('eis', 0)
        statusD = data.get('statusD', 1)
        d_end = data.get('d_end', None)

        num_z = data.get('num_z', '')
        num_z_el = data.get('num_z_el', '')
        pr_z = data.get('pr_z', 0)
        pr_z_osn = data.get('pr_z_osn', '')
        gpz = data.get('gpz', '')
        uid = data.get('uid', '')
        ppz = data.get('ppz', '')

        sposobzak = data.get('sposobzak', '')
        VIdZAK = data.get('VIdZAK', '')
        numzak = data.get('numzak', '')
        predlog = data.get('predlog', 0)
        dat_docosznak = data.get('dat_docosznak', '')
        smsp = data.get('smsp', '')
        num_docosnzak = data.get('num_docosnzak', '')
        OSTNEKONZAK = data.get('OSTNEKONZAK', '')
        okpd2 = data.get('okpd2', '')
        subectzak = data.get('subectzak', '')

        s_dog_okz = data.get('s_dog_okz', '')
        s_ds = data.get('s_ds', '')
        date_izv = data.get('date_izv', '')

        agent = data.get('agent', 0)
        smsp_okz = data.get('smsp_okz', 0)
        d_work = data.get('d_work', '')
        sysnum = data.get('sysnum', '')
        predlog_txt = data.get('predlog_txt', '')

        success = update_par(
            request,
            contract_id=contract_id,

            konk=konk,
            prol=prol,
            beznds=beznds,
            opl=opl,
            eis=eis,
            statusD=statusD,
            d_end=d_end,

            sposobzak=sposobzak,
            VIdZAK=VIdZAK,
            numzak=numzak,
            predlog=predlog,
            dat_docosznak=dat_docosznak,
            num_docosnzak=num_docosnzak,
            smsp=smsp,
            OSTNEKONZAK=OSTNEKONZAK,
            okpd2=okpd2,
            subectzak=subectzak,

            num_z=num_z,
            num_z_el=num_z_el,
            pr_z=pr_z,
            pr_z_osn=pr_z_osn,
            gpz=gpz,
            uid=uid,
            ppz=ppz,

            s_dog_okz=s_dog_okz,
            s_ds=s_ds,
            date_izv=date_izv,

            agent=agent,
            smsp_okz=smsp_okz,
            d_work=d_work,
            sysnum=sysnum,
            predlog_txt=predlog_txt
        )

        if success:
            return {"success": True, "message": "Статус сохранен"}
        else:
            return {"success": False, "message": "Ошибка сохранения"}

    except Exception as e:
        print(f"Error in update_contract_api: {e}")
        return {"success": False, "message": f"Ошибка: {str(e)}"}


#для добавления оплаты
@app.post("/api/contract/{contract_id}/add_payment")
async def add_payment(contract_id: int, request: Request):
    try:
        data = await request.json()
        summa = data.get('summa')
        date = data.get('date')

        success = add_dog_payment(request, contract_id, summa, date)

        return {"success": success}
    except Exception as e:
        print(f"Error adding payment: {e}")
        return {"success": False, "message": str(e)}

#для удаления оплаты
@app.post("/api/contract/delete_payments")
async def delete_payments(request: Request):
    try:
        data = await request.json()
        payment_ids = data.get('payment_ids', [])

        success = delete_dog_payments(request, payment_ids)

        return {"success": success}
    except Exception as e:
        print(f"Error deleting payments: {e}")
        return {"success": False, "message": str(e)}


if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8000)  # ip aдрес моего компьютера 192.168.1.228, по умолчанию 127.0.0.1, http://192.168.1.228:8000
