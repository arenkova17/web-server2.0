from database import get_dogs_ch, get_dog_ch, get_dog_tab2, dogs_for_klient

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/dogs", response_class=HTMLResponse)
async def page_dogs(request: Request):
    dogs = get_dogs_ch(request)
    table_rows = ""
    for dog in dogs:
        table_rows+=f"""
            <tr onclick="window.location.href='/dogs/{dog['id_dog']}'">
                <td>{dog['id_dog']}</td>
                <td>{dog['name_type']}</td>
                <td>{dog['num_dog_txt']}</td>
                <td>{dog['d_dog']}</td>
                <td>{dog['saldo_now']}</td>
                <td>{dog['name_st']}</td>
            </tr>
        """

    html = f"""
    <head>
        <title>Список договоров</title>
        <link rel="stylesheet" href="/static/css/style.css">
    </head>
    <body>
        <div style="background: #e4f0fb; padding: 8px 15px; display: flex; justify-content: space-between; align-items: center;">
            <h1 style="margin: 0; color: #0952a0; font-size: 28px;">Список договоров</h1>
            <div style="display: flex; gap: 12px;">
                <button class="button-switch" onclick="goToChoose()">Сменить программу</button>
                <button class="button-exit" onclick="logout()">Выйти</button>
            </div>
        </div>
        
        
        <table class="table_ch">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Тип договора</th>
                    <th>Номер договора</th>
                    <th>Дата договора</th>
                    <th>Остаток</th>
                    <th>Статус</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
    </body>
    <script>
        function goToChoose() {{
            window.location.href = '/choose';
        }}
        function logout() {{
            window.location.href = '/logout';
        }}
    </script>
    </html>
    """
    return HTMLResponse(content=html)

@router.get("/dogs/{id_dog}")
async def page_one_dog(request: Request, id_dog: int):
    information = get_dog_ch(request, id_dog)
    if not information:
        return HTMLResponse(content="<h1>Договор не найден</h1>", status_code=404)
    dogs_tab = get_dog_tab2(request, id_dog)
    id_klient = information.get('айди')
    dogs_for_klient_data = dogs_for_klient(request, id_klient)

    table_rows_dog_tab2 = ""
    for dog in dogs_tab :
        table_rows_dog_tab2+=f"""
            <tr>
                <td>{dog['id_dog']}</td>
                <td>{dog['dat_n']}</td>
                <td>{dog['dat_k']}</td>
                <td>{dog['s400']}</td>
                <td>{dog['s500']}</td>
                <td>{dog['s1431']}</td>
                <td>{dog['sal_n']}</td>
            </tr>
        """

    table_rows_dogs_for_klient = ""
    for dog in dogs_for_klient_data:
        table_rows_dogs_for_klient += f"""
        <table>
            <td>{dog.get('айди', '—')}</td>
            <td>{dog.get('датадоговора', '—')}</td>
            <td>{dog.get('тип', '—')}</td>
            <td>{dog.get('статус', '—')}</td>
            <td>{dog.get('долг', '—')}</td>
            <td>{dog.get('сальдо', '—')}</td>
        </tr>
        """

    html = f"""
    <head>
        <title>Договор {id_dog}</title>
        <link rel="stylesheet" href="/static/css/style.css">
    </head>
    <body>
        <h1 class="h1">Информация по договору {id_dog}</h1>
        <div>
            <h5>Информация по клиенту</h5>
                <!-- Личные данные -->
                <p><strong>ФИО:</strong> {information.get('фио', 'Не указано')}</p>
                <p><strong>Айди клиента:</strong> {information.get('айди', 'Не указано')}</p>
                <p><strong>Телефон:</strong> {information.get('телефон', 'Не указан')}</p>
                <p><strong>Email:</strong> {information.get('почта', 'Не указан')}</p>
                <p><strong>Дата рождения:</strong> {information.get('датарождения', 'Не указана')}</p>
                
                <!-- Паспортные данные -->
                <p><strong>Серия паспорта:</strong> {information.get('серияпаспорта', 'Не указана')}</p>
                <p><strong>Номер паспорта:</strong> {information.get('номерпаспорта', 'Не указан')}</p>
                <p><strong>Дата выдачи:</strong> {information.get('датавыдачи', 'Не указана')}</p>
                <p><strong>Кем выдан:</strong> {information.get('кемвыдан', 'Не указано')}</p>
                
                <!-- Адрес -->
                <p><strong>Адрес:</strong> {information.get('адрес', 'Не указан')}</p>
            </div>
        </div>
        
        <div>
            <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Дата начала</th>
                    <th>Дата окончания</th>
                    <th>s400</th>
                    <th>s500</th>
                    <th>s1431</th>
                    <th>Начальное сальдо</th>
                </tr>
            </thead>
            <tbody>
                {table_rows_dog_tab2}
            </tbody>
        </table>
        </div>
        
        <div>
            <h3>Договоры клиента</h3>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Дата договора</th>
                        <th>Тип</th>
                        <th>Статус</th>
                        <th>Долг/Переплата</th>
                        <th>Сальдо</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows_dogs_for_klient}
                </tbody>
            </table>
        </div>
    </body>
    """
    return HTMLResponse(content=html)
