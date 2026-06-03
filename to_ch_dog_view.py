from database import get_dogs_ch, get_dog_ch, get_dog_tab2, dogs_for_klient, obj_for_klient, payment_for_dog, \
    search_dog_ch, nach_for_dog, get_podryadchik, get_actual_equipment
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
import json

router = APIRouter()


@router.get("/dogs", response_class=HTMLResponse)
async def page_dogs(request: Request):
    dogs = get_dogs_ch(request)
    table_rows = ""
    for dog in dogs:
        table_rows += f"""
            <tr onclick="showContractDialog({dog['id_dog']})">
                <td>{dog['id_klient']}</td>
                <td>{dog['FIO']}</td>
                <td>{dog['id_dog']}</td>
                <td>{dog['num_dog_txt']}</td>
                <td>{dog['name_type']}</td>
                <td>{dog['d_dog'].strftime('%Y-%m-%d')}</td>
                <td>{dog['saldo_now']}</td>
                <td>{dog['name_st']}</td>
            </tr>
        """

    html = f"""
    <html>
    <head>
        <title>Список договоров</title>
        <link rel="stylesheet" href="/static/css/style.css">
    </head>
    <body>
        <div style="background: #e4f0fb; padding: 8px 15px; display: flex; justify-content: space-between; align-items: center;">
            <h1 style="margin: 0; color: #0952a0; font-size: 28px;">Список договоров</h1>
            <div style="display: flex; gap: 12px;">
                <button class="button-searchdog" onclick="openSearchDialog()">Найти договор</button>
                <button class="button-switch" onclick="goToChoose()">Сменить программу</button>
                <button class="button-exit" onclick="logout()">Выйти</button>
            </div>
        </div>

        <table class="table_ch">
            <thead>
                <tr>
                    <th>Лицевой счет</th>
                    <th>ФИО</th>
                    <th>ID договора</th>
                    <th>Номер договора</th>
                    <th>Тип договора</th>
                    <th>Дата договора</th>
                    <th>Сальдо</th>
                    <th>Статус</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>

        <!-- Диалог для поиска -->
        <dialog id="searchDialog" style="width: 400px; border: 2px solid #1073b7; border-radius: 8px; padding: 0;">

            <div style="background: #1073b7; padding: 10px 15px;">
                <p style="color: white; font-size: 18px; margin: 0; font-weight: bold;">Поиск договора</p>
            </div>

            <div style="padding: 15px;">

                <div style="margin-bottom: 12px;">
                    <label style="display: block; margin-bottom: 4px;">ID клиента</label>
                    <input type="text" id="search_idklient" placeholder="Введите ID" style="width: 100%; padding: 6px; border: 1px solid #ccc; border-radius: 4px;">
                </div>

                <div style="margin-bottom: 12px;">
                    <label style="display: block; margin-bottom: 4px;">ID договора</label>
                    <input type="text" id="search_iddog" placeholder="Введите ID" style="width: 100%; padding: 6px; border: 1px solid #ccc; border-radius: 4px;">
                </div>

                <div style="margin-bottom: 12px;">
                    <label style="display: block; margin-bottom: 4px;">Номер договора</label>
                    <input type="text" id="search_numdog" placeholder="Введите номер" style="width: 100%; padding: 6px; border: 1px solid #ccc; border-radius: 4px;">
                </div>

                <div style="margin-bottom: 20px;">
                    <label style="display: block; margin-bottom: 4px;">Адрес</label>
                    <input type="text" id="search_address" placeholder="Введите адрес" style="width: 100%; padding: 6px; border: 1px solid #ccc; border-radius: 4px;">
                </div>

                <div style="display: flex; justify-content: flex-end; gap: 10px;">
                    <button onclick="closeSearchDialog()" style="background: #6c757d; color: white; border: none; padding: 6px 15px; border-radius: 4px; cursor: pointer;">Отмена</button>
                    <button onclick="searchContracts()" style="background: #1073b7; color: white; border: none; padding: 6px 15px; border-radius: 4px; cursor: pointer;">Найти</button>
                </div>

            </div>
        </dialog>

        <!-- Диалог для информации о договоре -->
        <dialog id="contractDialog" class="dialog_window">
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px; background: #1073b7; border-radius: 6px 6px 0 0;">
                <h2 style="color: white; margin: 0;">Информация по клиенту</h2>
                <button onclick="closeContractDialog()" style="background: none; border: none; font-size: 24px; cursor: pointer; color: white;">✖</button>
            </div>
            <div id="contractDialogContent" style="padding-top: 10px; overflow-y: auto;"></div>
        </dialog>
        """
    html += """
        <script>
            function goToChoose() {{
                window.location.href = '/choose';
            }}
            function logout() {{
                window.location.href = '/logout';
            }}

            function openSearchDialog() {{
                document.getElementById('searchDialog').showModal();
            }}
            function closeSearchDialog() {{
                document.getElementById('searchDialog').close();
            }}

            function searchContracts() {{
                const idklient = document.getElementById('search_idklient').value;
                const iddog = document.getElementById('search_iddog').value;
                const numdog = document.getElementById('search_numdog').value;
                const address = document.getElementById('search_address').value;

                let url = '/search/dogs?';
                let params = [];

                if (idklient) params.push('idklient=' + encodeURIComponent(idklient));
                if (iddog) params.push('iddog=' + encodeURIComponent(iddog));
                if (numdog) params.push('numdog=' + encodeURIComponent(numdog));
                if (address) params.push('address=' + encodeURIComponent(address));

                window.location.href = url + params.join('&');
            }}

            function showContractDialog(dogId) {
                const dialog = document.getElementById('contractDialog');
                const contentDiv = document.getElementById('contractDialogContent');
                contentDiv.innerHTML = '<div style="text-align: center; padding: 40px;">Загрузка...</div>';
                dialog.showModal();

                fetch(`/api/dogs/${dogId}/dialog`)
                    .then(response => response.text())
                    .then(html => {
                        contentDiv.innerHTML = html;

                        const btnPersonal = contentDiv.querySelector('#btnPersonal');
                        const btnEquipment = contentDiv.querySelector('#btnEquipment');
                        const personalBlock = contentDiv.querySelector('#personalBlock');
                        const equipmentBlock = contentDiv.querySelector('#equipmentBlock');

                        if (btnPersonal) {
                            btnPersonal.onclick = () => {
                                personalBlock.style.display = 'block';
                                equipmentBlock.style.display = 'none';
                            };
                        }
                        if (btnEquipment) {
                            btnEquipment.onclick = () => {
                                personalBlock.style.display = 'none';
                                equipmentBlock.style.display = 'block';
                            };
                        }
                    })
                    .catch(error => {
                        contentDiv.innerHTML = '<div style="color: red;">Ошибка загрузки данных</div>';
                    });
            }

            function closeContractDialog() {{
                document.getElementById('contractDialog').close();
            }}

            var activeTab = 'Equipment';  // по умолчанию "Оборудование"

            function openTab(evt, tabName) {
                activeTab = tabName;  // ← ДОБАВЬ ЭТУ СТРОКУ
                var i, tabcontent, tablinks;
                tabcontent = document.getElementsByClassName("tabcontent");
                for (i = 0; i < tabcontent.length; i++) {
                    tabcontent[i].style.display = "none";
                }
                tablinks = document.getElementsByClassName("tablinks");
                for (i = 0; i < tablinks.length; i++) {
                    tablinks[i].className = tablinks[i].className.replace(" active", "");
                }
                document.getElementById(tabName).style.display = "block";
                evt.currentTarget.className += " active";
            }

            function applyFilter(dogId) {
                var isChecked = document.getElementById('actualOnlyCheckbox').checked ? 1 : 0;
                fetch(`/api/dogs/${dogId}/dialog?actual_only=${isChecked}`)
                    .then(response => response.text())
                    .then(html => {
                        document.getElementById('contractDialogContent').innerHTML = html;

                        // Восстанавливаем активную вкладку
                        var i, tabcontent, tablinks;
                        tabcontent = document.getElementsByClassName("tabcontent");
                        for (i = 0; i < tabcontent.length; i++) {
                            tabcontent[i].style.display = "none";
                        }
                        tablinks = document.getElementsByClassName("tablinks");
                        for (i = 0; i < tablinks.length; i++) {
                            tablinks[i].className = tablinks[i].className.replace(" active", "");
                        }
                        document.getElementById(activeTab).style.display = "block";

                        // Находим кнопку с нужной вкладкой и добавляем ей класс active
                        var buttons = document.getElementsByClassName("tablinks");
                        for (i = 0; i < buttons.length; i++) {
                            if (buttons[i].getAttribute('onclick') && buttons[i].getAttribute('onclick').includes(activeTab)) {
                                buttons[i].className += " active";
                                break;
                            }
                        }
                    })
                    .catch(error => {
                        console.error('Ошибка:', error);
                    });
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


# ИНФОРМАЦИЯ ДИАЛОГОВОГО ОКНА
@router.get("/api/dogs/{id_dog}/dialog")
async def dog_dialog_api(request: Request, id_dog: int, actual_only: int = 1):
    dog = get_dog_ch(request, id_dog)
    if not dog:
        return "<h1>Договор не найден</h1>"
    id_klient = dog.get('id_klient')
    podryadchik = get_podryadchik(request, id_klient)
    num_dog_txt = dog.get('num_dog_txt', '')

    dogs_tab2 = get_dog_tab2(request, id_dog)
    table_rows_tab2 = ""
    for row in dogs_tab2:
        table_rows_tab2 += f"""
            <tr>
                <td>{row['id_dog']}</td>
                <td>{row['dat_n'].strftime('%Y-%m-%d')}</td>
                <td>{row['dat_k'].strftime('%Y-%m-%d')}</td>
                <td>{row['s400']}</td>
                <td>{row['s500']}</td>
                <td>{row['s1431']}</td>
                <td>{row['sal_n']}</td>
            </tr>
        """

    dogs_kl = dogs_for_klient(request, id_klient)
    if dogs_kl:
        table_dogs_kl = ""
        for row in dogs_kl:
            table_dogs_kl += f"""
                <tr>
                    <td>{row['id_dog']}</td>
                    <td>{row['d_dog'].strftime('%Y-%m-%d')}</td>
                    <td>{row['name_type']}</td>
                    <td>{row['name_st']}</td>
                    <td>{row['saldo_now']}</td>
                    <td>{row['sal_n']}</td>
                </tr>
            """
    else:
        table_dogs_kl = '<tr><td colspan="6" style="text-align: center; padding: 20px;">Нет записей</td></tr>'

    obj_klient = obj_for_klient(request, id_klient)
    if obj_klient:
        table_obj_klient = ""
        for row in obj_klient:
            table_obj_klient += f"""
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px;">{row.get('id_object', '-')}</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">{row.get('id_dog', '-')}</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">{row.get('date_action', '-')}</td>
                </tr>
            """
    else:
        table_obj_klient = '<tr><td colspan="3" style="text-align: center; padding: 20px;">Нет записей</td></tr>'

    month_names = {1: 'Январь', 2: 'Февраль', 3: 'Март', 4: 'Апрель',
                   5: 'Май', 6: 'Июнь', 7: 'Июль', 8: 'Август',
                   9: 'Сентябрь', 10: 'Октябрь', 11: 'Ноябрь', 12: 'Декабрь'}
    mesobc = dog.get('месобс', 0)
    mesobc_name = month_names.get(int(mesobc), '-') if mesobc else '-'

    payment = payment_for_dog(request, id_dog)
    if payment:
        table_payment = ""
        for row in payment:
            table_payment += f"""
                <tr>
                    <td>{row['id_dog']}</td>
                    <td>{row['dn'].strftime('%Y-%m-%d')}</td>
                    <td>{row['s']}</td>
                </tr>
            """
    else:
        table_payment = '<tr><td colspan="3" style="text-align: center; padding: 20px;">Нет записей</td></tr>'

    nach = nach_for_dog(request, id_dog)
    if nach:
        table_nach = ""
        for row in nach:
            table_nach += f"""
                <tr>
                    <td>{row['id_dog']}</td>
                    <td>{str(row['s'])[:7]}</td>
                    <td>{row['god']}</td>
                    <td>{row['m']}</td>
                </tr>
            """
    else:
        table_nach = '<tr><td colspan="4" style="text-align: center; padding: 20px;">Нет записей</td></tr>'

    equipment = get_actual_equipment(request, id_klient, actual_only)
    if equipment:
        table_equipment = ""
        for row in equipment:
            table_equipment += f"""
                <tr>
                    <td>{row['name_ob']}</td>
                    <td>{row['name_izg']}</td>
                    <td>{row['name_model']}</td>
                    <td>{row['kol_oborud']}</td>
                    <td>{row['dol_ob']}</td>
                    <td>{row['du'][:10] if row['du'] else '-'}</td>
                    <td>{row['do'][:10] if row['do'] else '-'}</td>
                    <td>{row['id_kl']}</td>
                </tr>
            """
    else:
        table_equipment = '<td><td colspan="8" style="text-align: center; padding: 20px;">Нет записей</td></tr>'

    html = f"""
    <link rel="stylesheet" href="/static/css/style.css">
    <style>
        .tab {{
            display: flex;
            gap: 8px;
            border-bottom: 2px solid #1073b7;
            margin-bottom: 10px;
            padding-bottom: 0;
        }}
        .tab button {{
            background: none;
            border: none;
            padding: 5px 15px;
            font-size: 16px;
            font-weight: 500;
            color: #787878;
            cursor: pointer;
            border-radius: 20px 20px 0 0;
            transition: all 0.2s ease;
            font-family: inherit;
        }}
        .tab button:hover {{
            background: #f0f7ff;
            color: #0952a0;
        }}
        .tab button.active {{
            background: #1073b7;
            color: white;
            box-shadow: 0 -2px 5px rgba(0,0,0,0.05);
        }}
        .tabcontent {{
            display: none;
            padding: 10px 0;
            animation: fadeIn 0.3s ease;
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(5px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        

        /*таблица актуальный оборудований*/
        .table_equipment {{      /*рамка для таблицы*/
            max-height: 300px;
            overflow-y: auto;
            width: 98%;
            border: 1px solid #1073b7;
            padding: 10px;
            border-radius: 8px;
        }}
        .table_equipment h3 {{  /*заголовок*/
            margin: 0px;
            color: #0952a0;
            margin-bottom: 5px;
        }}
        .table_equipment table{{       /*сама таблица*/
            width: 100%;
            border-collapse: collapse;
        }}
        .table_equipment thead th {{
            border: 1px solid #1073b7;
            background-color: #e4f0fb;
            font-size: 14px;
            font-weight: bold;
            text-align: center;
            vertical-align: middle;
            padding: 5px;
        }}
        .table_equipment td {{
            padding: 8px;
            border: 1px solid #ddd;
            text-align: left;
            vertical-align: top;
        }}
        .table_equipment td:last-child {{
            width: 60px;
            text-align: center;
        }}
    </style>
    
    <div class="tab">
        <button class="tablinks active" onclick="openTab(event, 'PersonalData')">Личные данные</button>
        <button class="tablinks" onclick="openTab(event, 'Equipment')">Оборудование</button>
    </div>

    <div id="PersonalData" class="tabcontent" style="display: block;">
    
        <div style="display: flex; justify-content: flex-start; align-items: flex-start; gap: 20px;">
            <div style="border: 1px solid #1073b7; padding: 10px; border-radius: 8px; width: 40%;">
                <h3 style="margin: 0 0 10px 0; color: #0952a0;">Личные данные</h3>
                <div style="font-size: 16px;">
                    <p style="margin: 0;"><strong>Лицевой счет:</strong> {dog.get('айди', '-')}</p>
                    <p style="margin: 0;"><strong>ФИО заказчика:</strong> {dog.get('фио', '-')}</p>
                    <p style="margin: 0;"><strong>Адрес расположения оборудования:</strong> {dog.get('адрес', '-')}</p>
                    <p style="margin: 0;"><strong>Почтовый адрес:</strong> {dog.get('индекс', '-')}</p>
                    <p style="margin: 0;"><strong>Номер телефона:</strong> {dog.get('телефон', '-')}</p>
                    <p style="margin: 0;"><strong>Адрес электронной почты:</strong> {dog.get('почта', '-')}</p>
                    <p style="margin: 0;"><strong>Подрядчик:</strong> {podryadchik}</p>
                    <p style="margin: 0;"><strong>Месяц обслуживания:</strong> {mesobc_name}</p>
                </div>
            </div>

            <div class="table_dogs_for_klient">
                <h3>Договоры клиента</h3>
                <table>
                    <thead>
                        <tr><th>ID договора</th><th>Дата начала</th><th>Тип</th><th>Статус</th><th>Сальдо</th><th>Начальное сальдо</th></tr>
                    </thead>
                    <tbody>{table_dogs_kl}</tbody>
                </table>
            </div>
        </div>

        <p style="font-size: 20px; margin: 10px 0 5px 0;">Договор <strong>№{dog.get('номердог', '-')}</strong> от {dog.get('датадог', '-').strftime('%d.%m.%Y')}</p>
        <p style="font-size: 20px; margin: 0 0 5px 0;">Тип договора: <strong>{dog.get('типдог')}</strong></p>

        <div style="display: flex; justify-content: flex-start; align-items: flex-start; gap: 10px;">

            <div class="table_nach_tab2">        
                <h3>Начисления</h3>
                <table>
                    <thead>
                        <tr>
                            <th>ID договора</th>
                            <th>Сумма</th>
                            <th>Год</th>
                            <th>Месяц</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_nach}
                    </tbody>
                </table>
            </div>

            <div class="table_nach_tab2">
                <h3>Даты работ ВДГО</h3>
                <table>
                    <thead>
                        <thead>
                            <tr>
                                <th>ID объекта</th>
                                <th>ID договора</th>
                                <th>Дата выполнения</th>
                            </tr>
                        </thead>
                    <tbody>
                        {table_obj_klient}
                    </tbody>
                </table>
            </div>

            <div class="table_nach_tab2">
                <h3>Сумма оплат</h3>
                <table>
                    <thead>
                        <thead>
                            <tr>
                                <th>ID договора</th>
                                <th>Дата оплаты</th>
                                <th>Сумма к оплате</th>
                            </tr>
                        </thead>
                    <tbody>
                        {table_payment}
                    </tbody>
                </table>
            </div>

        </div>

        <div class="table_ch_tab2">
            <h3>История договора {dog.get('id_dog')}</h3>
            <table>
                <thead><tr><th>ID договора</th><th>Дата начала</th><th>Дата конца</th><th>s400</th><th>s500</th><th>s1431</th><th>Начальное сальдо</th></tr></thead>
                <tbody>{table_rows_tab2}</tbody>
            </table>
        </div>
    </div>

    <div id="Equipment" class="tabcontent">
    
        <div style="margin-bottom: 10px;">
            <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
                <input type="checkbox" id="actualOnlyCheckbox" onchange="applyFilter({dog.get('id_dog')})" {'checked' if actual_only == 1 else ''}>
                <strong>Только актуальное оборудование</strong>
            </label>
        </div>
        
        <div class="table_equipment">
            <table>
                <thead><tr><th>Оборудование</th><th>Марка</th><th>Модель</th><th>Кол-во</th><th>Доля</th><th>Дата установки</th><th>Дата отключения</th><th>ID клиента</th></tr></thead>
                <tbody>{table_equipment}</tbody>
            </table>
        </div>
        
    </div>

    <script>
        function openTab(evt, tabName) {{
            var i, tabcontent, tablinks;
            activeTab = tabName;
            tabcontent = document.getElementsByClassName("tabcontent");
            for (i = 0; i < tabcontent.length; i++) {{
                tabcontent[i].style.display = "none";
            }}
            tablinks = document.getElementsByClassName("tablinks");
            for (i = 0; i < tablinks.length; i++) {{
                tablinks[i].className = tablinks[i].className.replace(" active", "");
            }}
            document.getElementById(tabName).style.display = "block";
            evt.currentTarget.className += " active";
        }}

        function applyFilter(dogId) {{
            var isChecked = document.getElementById('actualOnlyCheckbox').checked ? 1 : 0;
            fetch(`/api/dogs/${{dogId}}/dialog?actual_only=${{isChecked}}`)
                .then(response => response.text())
                .then(html => {{
                    document.getElementById('contractDialogContent').innerHTML = html;
                    var i, tabcontent, tablinks;
                    tabcontent = document.getElementsByClassName("tabcontent");
                    for (i = 0; i < tabcontent.length; i++) {{
                        tabcontent[i].style.display = "none";
                    }}
                    tablinks = document.getElementsByClassName("tablinks");
                    for (i = 0; i < tablinks.length; i++) {{
                        tablinks[i].className = tablinks[i].className.replace(" active", "");
                    }}
                    document.getElementById(activeTab).style.display = "block";
                    var buttons = document.getElementsByClassName("tablinks");
                    for (i = 0; i < buttons.length; i++) {{
                        if (buttons[i].getAttribute('onclick') && buttons[i].getAttribute('onclick').includes(activeTab)) {{
                            buttons[i].className += " active";
                            break;
                        }}
                    }}
                }})
                .catch(error => console.error('Ошибка:', error));
        }}
    </script>
    """
    return HTMLResponse(content=html)


@router.get("/search/dogs", response_class=HTMLResponse)
async def search_dog_page(
        request: Request,
        idklient: str = "",
        iddog: str = "",
        numdog: str = "",
        address: str = ""
):
    results = search_dog_ch(request, idklient, iddog, numdog, address)

    table_rows = ""
    for row in results:
        table_rows += f"""
            <tr onclick="showContractDialog({row['id_dog']})">
                <td>{row.get('id_klient', '-')}</td>
                <td>{row.get('FIO', '-')}</td>
                <td>{row.get('id_dog', '-')}</td>
                <td>{row.get('num_dog_txt', '-')}</td>
                <td>{row.get('name_type', '-')}</td>
                <td>{row.get('d_dog', '-').strftime('%Y-%m-%d') if row.get('d_dog') else '-'}</td>
                <td>{row.get('saldo_now', '-')}</td>
                <td>{row.get('name_st', '-')}</td>
                <td>{row.get('addr', '-')}</td>
            </tr>
        """

    html = f"""
    <html>
    <head>
        <title>Результаты поиска</title>
        <link rel="stylesheet" href="/static/css/style.css">
    </head>
    <body>
        <div style="background: #e4f0fb; padding: 8px 15px; display: flex; justify-content: space-between; align-items: center;">
            <h1 style="color: #0952a0; margin: 0;">Результаты поиска</h1>
            <a href="/dogs" class="button-back">Назад к списку</a>
        </div>
        <table class="table_ch">
            <thead>
                <tr>
                    <th>ID клиента</th>
                    <th>ФИО</th>
                    <th>ID договора</th>
                    <th>Номер договора</th>
                    <th>Тип</th>
                    <th>Дата договора</th>
                    <th>Сальдо</th>
                    <th>Статус</th>
                    <th>Адрес</th>
                </tr>
            </thead>
            <tbody>
                {table_rows if table_rows else '<tr><td colspan="9">Договоры не найдены</td></tr>'}
            </tbody>
        </table>

        <dialog id="contractDialog" style="width: 90%; height: 90%; border-radius: 8px; border: 2px solid #0952a0; padding: 10px;">
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px; background: #1073b7; border-radius: 6px 6px 0 0;">
                <h2 style="color: white; margin: 0;">Информация по клиенту</h2>
                <button onclick="closeContractDialog()" style="background: none; border: none; font-size: 24px; cursor: pointer; color: white;">✖</button>
            </div>
            <div id="contractDialogContent" style="padding-top: 10px; overflow-y: auto;"></div>
        </dialog>

        <script>
            function closeContractDialog() {{
                document.getElementById('contractDialog').close();
            }}

            function showContractDialog(dogId) {{
                const dialog = document.getElementById('contractDialog');
                const contentDiv = document.getElementById('contractDialogContent');
                contentDiv.innerHTML = '<div style="text-align: center; padding: 40px;">Загрузка...</div>';
                dialog.showModal();
                fetch(`/api/dogs/${{dogId}}/dialog`)
                    .then(response => response.text())
                    .then(html => {{ contentDiv.innerHTML = html; }})
                    .catch(error => {{ contentDiv.innerHTML = '<div style="color: red;">Ошибка загрузки данных</div>'; }});
            }}
            
            function openTab(evt, tabName) {{
                var i, tabcontent, tablinks;
                activeTab = tabName;
                tabcontent = document.getElementsByClassName("tabcontent");
                for (i = 0; i < tabcontent.length; i++) {{
                    tabcontent[i].style.display = "none";
                }}
                tablinks = document.getElementsByClassName("tablinks");
                for (i = 0; i < tablinks.length; i++) {{
                    tablinks[i].className = tablinks[i].className.replace(" active", "");
                }}
                document.getElementById(tabName).style.display = "block";
                evt.currentTarget.className += " active";
            }}
    
            function applyFilter(dogId) {{
                var isChecked = document.getElementById('actualOnlyCheckbox').checked ? 1 : 0;
                fetch(`/api/dogs/${{dogId}}/dialog?actual_only=${{isChecked}}`)
                    .then(response => response.text())
                    .then(html => {{
                        document.getElementById('contractDialogContent').innerHTML = html;
                        var i, tabcontent, tablinks;
                        tabcontent = document.getElementsByClassName("tabcontent");
                        for (i = 0; i < tabcontent.length; i++) {{
                            tabcontent[i].style.display = "none";
                        }}
                        tablinks = document.getElementsByClassName("tablinks");
                        for (i = 0; i < tablinks.length; i++) {{
                            tablinks[i].className = tablinks[i].className.replace(" active", "");
                        }}
                        document.getElementById(activeTab).style.display = "block";
                        var buttons = document.getElementsByClassName("tablinks");
                        for (i = 0; i < buttons.length; i++) {{
                            if (buttons[i].getAttribute('onclick') && buttons[i].getAttribute('onclick').includes(activeTab)) {{
                                buttons[i].className += " active";
                                break;
                            }}
                        }}
                    }})
                    .catch(error => console.error('Ошибка:', error));
            }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)