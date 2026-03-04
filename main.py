from fastapi import FastAPI, Request
import uvicorn    #сервер для запуска питон приложений
from fastapi.responses import HTMLResponse, RedirectResponse       #1 - отправление html страниц, 2 - перенаправление юзера по разным страницам
from database import get_clients_page, get_total_count, get_contract_id, update_par, search_dog, get_dog_payments, verify_windows_login
from starlette.middleware.sessions import SessionMiddleware     #созданий сессий, запоминание что пользователь вошел
from starlette.middleware.base import BaseHTTPMiddleware         #проверка авторизации перед каждым запросом

#создание веб-приложения
app = FastAPI()

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):    #функция выполняется для каждого запроса
        #список путей доступных без авторизации - в нашем случае это только страница входа, иначе бы перед каждым запросом кидал страницу входа
        public_paths = ["/login"]

        #если путь не в списке публичных, то проверяем есть ли пользователь в сессии, если да - то проходим, если нет - то отправка на логиниться
        if request.url.path not in public_paths:
            user = request.session.get("user")
            if not user:
                return RedirectResponse("/login", status_code=303)

        response = await call_next(request)
        return response

#добавляет класс работу каждый раз перед запросом
app.add_middleware(AuthMiddleware)

#для создания сесии юзера, для сохранения данных между запросами
app.add_middleware(
    SessionMiddleware,
    secret_key="arenkovaan",
    max_age=60,  #время работы сессии - пока не закроется браузер
    session_cookie="session",
    same_site="strict",
    https_only=False
)

#обработчик отправки логина и пароля
@app.post("/login")
async def login_post(request: Request):
    form = await request.form()    #забирает л/п
    username = form.get("username")      #достает логин
    password = form.get("password")     #достает пароль
    remote_host = "gazprosql"         #указывает на каком сервере проверять подключение

    if verify_windows_login(remote_host, username, password):       #проверяет по функции проверки из database л/п
        request.session["user"] = {"login": username}              #запомниает логин пользователя
        return RedirectResponse("/", status_code=303)        #и отправляет чувака на главную с таблицу
    else:             #если не входит чувак то по новой ввод л/п
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Вход в систему</title>
            <style>
                body { font-family: Arial; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
                .login-form { border: 2px solid #1073b7; padding: 30px; border-radius: 10px; width: 300px; }
                input { width: 100%; padding: 8px; margin: 10px 0; }
                button { background: #1073b7; color: white; border: none; padding: 10px; width: 100%; cursor: pointer; }
                .error { color: red; margin-top: 10px; text-align: center; }
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

#окно ввода логина и пароля
@app.get("/login", response_class=HTMLResponse)
def login_page():
    return """
    <html>
    <head>
        <title>Вход в систему</title>
        <style>
            body { font-family: Arial; display: flex; justify-content: center; align-items: center; height: 100vh; }
            .login-form { border: 2px solid #1073b7; padding: 30px; border-radius: 10px; width: 300px; }
            input { width: 100%; padding: 8px; margin: 10px 0; }
            button { background: #1073b7; color: white; border: none; padding: 10px; width: 100%; cursor: pointer; }
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
        } else {
            passwordField.type = 'password';
        }
    }
    </script>"""


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
    </style></head>
    <body>
        <h1 class="h1">Список договоров подлежащих публикации в ЕИС</h1>
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

    payments = get_dog_payments(request, contract_id)

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
        position: fixed;   /* фиксированное положение */
        bottom: 20px;     /* граница снизу для кнопки */
        right: 20px;      /* граница слева для кнопки */
        background: #1073b7;       /* фон кнопки */ 
        font-size: 18px;      /* размер текста */
        padding: 4px 20px;      /* отступы для текста внутри кнопки */
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
    .form-row {{
    display: flex;
    gap: 25px;
    margin-bottom: 15px;  /* одинаковый отступ между строками */
    }}
    </style>
    </head>

    <body>
        <h1 class="h1">Информация по договору {contract_id}</h1>

    <div class="info-container">

        <!-- СВЕРХУ СЛЕВА -------------------------->
        <p style="display: flex; gap: 90px;">
            <span><strong>№ договора:</strong> {contract.get('№ договора', 'Нет данных')}</span>
            <span><strong>№ контрагента:</strong> {contract.get('№ контрагента', 'Нет данных')}</span>
        </p>

        <div style="display: flex; gap: 50px; align-items: center; margin: 15px 0;">
            <div><strong>Дата регистрации:</strong> {str(contract.get('Дата регистрации', ''))[:10]}</div>
            <div><strong>Дата договора:</strong> {str(contract.get('Дата договора', ''))[:10]}</div>
            <div style="display: flex; align-items: center; gap: 10px;">
                <input type="checkbox" id="konkCheckbox" {is_checked}>
                <label for="konkCheckbox" style="cursor: pointer;"><strong>Конкурс</strong></label>
            </div>
        </div>

        <p><strong>Подразделение:</strong> {contract.get('Подразделение', 'Нет данных')}</p>
        <p style="width: 600px; word-wrap: break-word;"><strong>Предмет договора:</strong> {contract.get('Предмет договора', 'Нет данных')}</p>
        <p style="display: flex; gap: 40px;">
            <span><strong>Дата начала:</strong> {str(contract.get('Дата начала', ''))[:10]}</span>
            <span><strong>Дата конца:</strong> {str(contract.get('Дата конца', ''))[:10]}</span>
            <span><strong>Сумма договора:</strong> {contract.get('Сумма договора', 'Нет данных')} рублей</span>
        </p>

        <!-- КОНТРАГЕНТ ----------------------->
        <div style="width: 35%; border: 2px solid #1073b7; padding: 15px; border-radius: 8px; margin: 15px 0;">
            <h3 style="margin: 0 0 10px 0; color: #0952a0;">Контрагент</h3>

            <p><strong>Наименование:</strong> {contract.get('Наименование', 'Нет данных')}</p>

            <p style="display: flex; gap: 162px;">
                <span><strong style="width: 100px;">ИНН:</strong> {contract.get('ИНН', '')}</span>
                <span><strong>КПП:</strong> {contract.get('КПП', '')}</span>
            </p>

            <p style="display: flex; gap: 50px;">
                <span><strong style="width: 200px;">Расч.счет:</strong> {contract.get('Расч.счет', '')}</span>
                <span><strong>Телефон/факс:</strong> {contract.get('Телефон/факс', '')}</span>
            </p>

            <p><strong>БИК:</strong> {contract.get('БИК', 'Нет данных')}</p>
        </div>

        <!-- НИЖЕ КОНТРАГЕНТА ---------------->
        <div>
        <div class="form-row">
            <div><label><strong>№ закупки ЕИС</strong></label>
            <input type="text" id="num_z" value="{num_z_value}" size="15"></div>

            <div><label><strong>№ закуп. на эл.пл.</strong></label>
            <input type="text" id="numzalel" value="{numzalel_value}" size="15"></div>
        </div>

        <div class="form-row">
            <div><input type="checkbox" id="przakcheckbox" {przak_checked}>
            <label for="przakcheckbox" style="cursor: pointer;"><strong>Прямая закупка</strong></label></div>

            <div><label><strong>Основание</strong></label>
            <input type="text" id="osn" value="{osn_value}" size="15"></div>

            <div><label><strong>ГПЗ</strong></label>
            <input type="text" id="gpz" value="{gpz_value}" size="15"></div>
        </div>

        <div class="form-row">
            <div><label><strong>UID</strong></label>
            <input type="text" id="uid" value="{uid_value}" size="20"></div>

            <div><label><strong>ППЗ</strong></label>
            <input type="text" id="ppz" value="{ppz_value}" size="15"></div>
        </div>
        </div>

    </div>

    <!-- ДВЕ КНОПКИ -->
    <div style="position: fixed; bottom: 20px; right: 20px;">   
        <button id="saveButton" onclick="savepar()" class="button-save">Cохранить</button>
    </div>
    <p style="position: fixed; bottom: 20px; left: 20px;">
        <a href="/?page={from_page}" class="button-back"> Назад к списку</a>
    </p>      

    <!-- СВЕРХУ СПРАВА --> 
    <div style="position: fixed; top: 100px; right: 600px;">
        <div style="display: flex; gap: 30px; margin-bottom: 15px;">
            <div><input type="checkbox" id="prol" {prol_checked}>
            <label for="prol" style="cursor: pointer;"><strong>Пролонгация</strong></label></div>

            <div><input type="checkbox" id="beznds" {beznds_checked}>
            <label for="beznds" style="cursor: pointer;"><strong>Без НДС</strong></label></div>

            <div><strong>Код ОБД НСИ</strong> {contract.get('Код ОБД НСИ', 'Нет данных')}</div>
        </div>

        <div style=" display: flex; flex-direction: column;">
            <div><input type="checkbox" id="opl" {opl_checked}>
            <label for="opl" style="cursor: pointer;"><strong>Оплачено</strong></label></div>

            <div style="margin-bottom: 13px;"><input type="checkbox" id="eis" {eis_checked}>
            <label for="eis" style="cursor: pointer; "><strong>Публикация в ЕИС</strong></label></div>
        </div>

        <div style="margin-bottom: 10px;">
            <dr><label><strong>Дата заверш. договора</strong></label>
            <input type="date" id="d_end" value="{d_end_value}">
        </div>

        <div>
            <label for="statusD" style="margin-right: 10px"><strong>СТАТУС</strong></label>
            <select name="statusD" id="status">
            <option value="2">Подписан</option>
            <option value="4">Закрыт</option>
            </select>
        </div>
    </div>

<!-- РЕКВИЗИТЫ -->
<div style="width: 35%; border: 2px solid #1073b7; padding: 15px; border-radius: 8px; margin: 15px 0; position: fixed; top: 250px; left: 754px;">
    <h3 style="margin: 0 0 10px 0; color: #0952a0;">Реквизиты</h3>

<div style="display: flex; gap: 30px;">
    <div>
        <form action="#">
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

    <div>
        <form action="#">
            <label for="VIdZAK"><strong>Вид закупки</strong></label>
            <select name="VIdZAK" id="VIdZAK">
                <option value="001" {'selected' if VIdZAK_value == '001' else ''}>001</option>
                <option value="002" {'selected' if VIdZAK_value == '002' else ''}>002</option>
            </select>
        </form> 
    </div>
</div>

<div style="display: flex; gap: 30px;">
    <div>
        <label><strong>№ КЗ</strong></label>
        <input type="text" id="numzak" value="{numzak_value}" size="15">
    </div>

    <div>
        <form action="#">
            <label for="predlog"><strong>Формат закупки</strong></label>
        <select name="predlog" id="predlog">
            <option value="opened" {'selected' if predlog_value == 'opened' else ''}>Открытая</option>
            <option value="closed" {'selected' if predlog_value == 'closed' else ''}>Закрытая</option>
        </select>
        </form>
    </div>
</div>

<div style="display: flex; gap: 30px; margin-bottom: 15px;">
    <div>
        <label><strong>Дата док.осн.зак.</strong></label>
        <input type="date" id="dat_docosznak" value="{dat_docosznak_value}">
    </div>

    <div>
        <label><strong>СМСП</strong></label>
        <input type="text" id="smsp" value="{smsp_value}" size="15">
    </div>
</div>

    <div style="margin-bottom: 15px;">
        <label><strong>№ док.осн.зак.</strong></label>
        <input type="text" id="num_docosnzak" value="{num_docosnzak_value}" size="15">
    </div>

    <div style="margin-bottom: 15px;">
        <label><strong>Код основания некн.зак.</strong></label>
        <input type="text" id="OSTNEKONZAK" value="{OSTNEKONZAK_value}" size="15">
    </div>


<div style="display: flex; gap: 30px;">
    <div>
        <label><strong>ОКПД2</strong></label>
        <input type="text" id="okpd2" value="{okpd2_value}" size="15">
    </div>

    <div>
        <form action="#">
            <label for="subectzak"><strong>SUBECTZAK</strong></label>
            <select name="subectzak" id="subectzak">
                <option value="001" {'selected' if subectzak_value == '001' else ''}>001</option>
                <option value="002" {'selected' if subectzak_value == '002' else ''}>002</option>
            </select>
        </form> 
    </div>
</div>
</div>
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
        ppz: document.getElementById('ppz').value        
    }};

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
        konk_value = data.get('konk', 0)
        prol_value = data.get('prol', '')
        beznds_value = data.get('beznds', '')
        opl_value = data.get('opl', '')
        eis_value = data.get('eis', '')
        statusD_value = data.get('statusD', 1)
        d_end_value = data.get('d_end', None)

        num_z_value = data.get('num_z', '')
        num_z_el_value = data.get('num_z_el', '')
        pr_z_value = data.get('pr_z', 0)
        pr_z_osn_value = data.get('pr_z_osn', '')
        gpz_value = data.get('gpz', '')
        uid_value = data.get('uid', '')
        ppz_value = data.get('ppz', '')

        sposobzak_value = data.get('sposobzak', '')
        VIdZAK_value = data.get('VIdZAK', '')
        numzak_value = data.get('numzak', '')
        predlog_value = data.get('predlog', '')
        dat_docosznak = data.get('dat_docosznak', '')
        dat_docosznak_value = dat_docosznak[:10] if dat_docosznak else ''
        smsp_value = data.get('smsp', '')
        num_docosnzak_value = data.get('num_docosnzak', '')
        OSTNEKONZAK_value = data.get('OSTNEKONZAK', '')
        okpd2_value = data.get('okpd2', '')
        subectzak_value = data.get('subectzak', '')

        success = update_par(request,
                             contract_id=contract_id,
                             konk=konk_value,
                             prol=prol_value,
                             beznds=beznds_value,
                             opl=opl_value,
                             eis=eis_value,
                             statusD=statusD_value,
                             d_end=d_end_value,

                             sposobzak=sposobzak_value,
                             VIdZAK=VIdZAK_value,
                             numzak=numzak_value,
                             predlog=predlog_value,
                             dat_docosznak=dat_docosznak_value,
                             num_docosnzak=num_docosnzak_value,
                             smsp=smsp_value,
                             OSTNEKONZAK=OSTNEKONZAK_value,
                             okpd2=okpd2_value,
                             subectzak=subectzak_value,

                             num_z=num_z_value,
                             num_z_el=num_z_el_value,
                             pr_z=pr_z_value,
                             pr_z_osn=pr_z_osn_value,
                             gpz=gpz_value,
                             uid=uid_value,
                             ppz=ppz_value
                             )
        if success:
            return {"success": True, "message": "Статус сохранен"}
        else:
            return {"success": False, "message": "Ошибка сохранения"}

    except Exception as e:
        return {"success": False, "message": f"Ошибка: {str(e)}"}


if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000)   #ip aдрес 192.168.1.228