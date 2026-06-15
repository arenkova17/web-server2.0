from database import get_dogs_ch, get_dog_ch, get_dog_tab2, dogs_for_klient, obj_for_klient, payment_for_dog, \
    search_dog_ch, nach_for_dog, get_podryadchik, get_actual_equipment, obj_for_dog, get_user_connection_ch, \
    get_actual_equipment_by_year
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
                <td>{dog['addr']}</td>
                <td>{dog['id_dog']}</td>
                <td>{dog['num_dog_txt']}</td>
                <td>{dog['name_type']}</td>
                <td>{dog['d_dog'].strftime('%Y-%m-%d')}</td>
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

        <div style="position: sticky; top: 10px; z-index: 100; background: #e4f0fb; padding: 8px 15px; display: flex; justify-content: space-between; align-items: center;">
            <h1 style="margin: 0; color: #0952a0; font-size: 28px;">Список договоров</h1>
            <div style="display: flex; gap: 12px;">
                <button class="button-searchdog" onclick="openSearchDialog()">Найти договор</button>
                <button class="button-switch" onclick="goToChoose()">Сменить программу</button>
                <button class="button-exit" onclick="logout()">Выйти</button>
            </div> 
        </div>
        <style>
            /* Таблица */
            .table_ch {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 0px;
            }}
            
            /* Заголовки */
            
            .table_ch thead tr {{
                position: sticky;
                top: 0;
                z-index: 10;
                background-color: #f5f5f5;
                font-weight: bold;
            
            }}
            .table_ch thead tr th {{
                border: 1px solid #ddd;
            }}
            
            /* Ячейки */
            .table_ch td {{
                border: 1px solid #ddd;
                padding: 10px;
                padding: 10px 12px;
            }}
            
            /* Строки при наведении */
            .table_ch tr:hover {{
                background-color: #f5f5f5;
                cursor: pointer;
            }}
            .table-container {{
                position: fixed;
                top: 70px;
                bottom: 6px;
                left: 8px;
                right: 8px;
                max-height: calc(100vh - 80px);
                overflow-y: auto;
                overflow-x: auto;
                border: 1px solid #ddd;
                background: #fff;
            }}
            /* Контейнер для скролла (только горизонтальный) */
            .table-wrapper {{
                overflow-x: auto;
            }}
        </style>

        <div class="table-container">
            <table class="table_ch">
                <thead>
                    <tr>
                        <th>№ ЛС ГРО</th>
                        <th>ФИО</th>
                        <th>Адрес оборудования</th>
                        <th>ID договора</th>
                        <th>Номер договора</th>
                        <th>Тип договора</th>
                        <th>Дата договора</th>
                        <th>Статус</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>

        <!-- Диалог для поиска -->
        <dialog id="searchDialog" style="width: 400px; border: 2px solid #1073b7; border-radius: 8px; padding: 0;">

            <div style="background: #1073b7; padding: 10px 15px;">
                <p style="color: white; font-size: 18px; margin: 0; font-weight: bold;">Поиск договора</p>
            </div>

            <div style="padding: 15px;">

                <div style="margin-bottom: 12px;">
                    <label style="display: block; margin-bottom: 4px;">Номер лицевого счёта</label>
                    <input type="text" id="search_idklient" placeholder="Введите номер" style="width: 100%; padding: 6px; border: 1px solid #ccc; border-radius: 4px;">
                </div>
                
                <div style="margin-bottom: 20px;">
                    <label style="display: block; margin-bottom: 4px;">ФИО</label>
                    <input type="text" id="search_fio" placeholder="Введите ФИО" style="width: 100%; padding: 6px; border: 1px solid #ccc; border-radius: 4px;">
                </div>

                <div style="margin-bottom: 12px;">
                    <label style="display: block; margin-bottom: 4px;">ID договора</label>
                    <input type="text" id="search_iddog" placeholder="Введите ID" style="width: 100%; padding: 6px; border: 1px solid #ccc; border-radius: 4px;">
                </div>

                <div style="margin-bottom: 12px;">
                    <label style="display: block; margin-bottom: 4px;">Номер договора</label>
                    <input type="text" id="search_numdog" placeholder="Введите номер" style="width: 100%; padding: 6px; border: 1px solid #ccc; border-radius: 4px;">
                </div>

                <div style="margin-bottom: 12px;">
                    <label style="display: block; margin-bottom: 4px;">Улица</label>
                    <input type="text" id="search_street" placeholder="Введите улицу" style="width: 100%; padding: 6px; border: 1px solid #ccc; border-radius: 4px;">
                </div>
                
                <div style="display: flex; justify-content: flex-start; align-items: flex-start; gap: 20px;">
                    <div style="margin-bottom: 12px;">
                        <label style="display: block; margin-bottom: 4px;">Дом</label>
                        <input type="text" id="search_house" placeholder="Введите номер дома" style="width: 100%; padding: 6px; border: 1px solid #ccc; border-radius: 4px;">
                    </div>
                    
                    <div style="margin-bottom: 12px;">
                        <label style="display: block; margin-bottom: 4px;">Квартира</label>
                        <input type="text" id="search_flat" placeholder="Введите номер квартиры" style="width: 100%; padding: 6px; border: 1px solid #ccc; border-radius: 4px;">
                    </div>
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
                const fio = document.getElementById('search_fio').value;
                const street = document.getElementById('search_street').value;
                const house = document.getElementById('search_house').value;
                const flat = document.getElementById('search_flat').value;

                let url = '/search/dogs?';
                let params = [];

                if (idklient) params.push('idklient=' + encodeURIComponent(idklient));
                if (iddog) params.push('iddog=' + encodeURIComponent(iddog));
                if (numdog) params.push('numdog=' + encodeURIComponent(numdog));
                if (fio) params.push('fio=' + encodeURIComponent(fio));
                if (street) params.push('street=' + encodeURIComponent(street));
                if (house) params.push('house=' + encodeURIComponent(house));
                if (flat) params.push('flat=' + encodeURIComponent(flat))
    
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
                        contentDiv.innerHTML = '<div style="color: black;">Нет записей</div>';
                    });
            }

            function closeContractDialog() {{
                document.getElementById('contractDialog').close();
            }}

            var activeTab = 'Equipment'; 

            function openTab(evt, tabName) {
                activeTab = tabName;
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

            function loadDogData(newDogId) {
                fetch(`/api/dogs/${newDogId}/dialog?partial=true&actual_only=${document.getElementById('actualOnlyCheckbox')?.checked ? 1 : 0}`)
                    .then(response => response.json())
                    .then(data => {
                        // Начисления
                        var nachTable = document.querySelector('#nachTableBody');
                        if (nachTable) nachTable.innerHTML = data.table_nach;

                        // ✅ Даты работ ВДГО
                        var objTable = document.querySelector('#objTableBody');
                        if (objTable) objTable.innerHTML = data.table_obj_klient;

                        // Оплаты
                        var paymentTable = document.querySelector('#paymentTableBody');
                        if (paymentTable) paymentTable.innerHTML = data.table_payment;

                        // История договора
                        var historyTable = document.querySelector('#historyTableBody');
                        if (historyTable) historyTable.innerHTML = data.table_rows_tab2;

                        // Заголовок истории (опционально)
                        var historyTitle = document.querySelector('#historyTitle');
                        if (historyTitle) historyTitle.innerHTML = 'История договора ' + newDogId;
                    })
                    .catch(error => console.error('Ошибка:', error));
            }

            function showChartsDialog(dogId, year) {
                const dialog = document.getElementById('chartsDialog');
                const contentDiv = document.getElementById('chartsDialogContent');
                contentDiv.innerHTML = '<div style="text-align: center; padding: 40px;">Загрузка...</div>';
                dialog.showModal();

                fetch(`/api/dogs/${dogId}/charts?year=${year}`)
                    .then(response => response.text())
                    .then(html => {
                        contentDiv.innerHTML = html;
                    })
                    .catch(error => {
                        contentDiv.innerHTML = '<div style="color: red; text-align: center;">Нет записей</div>';
                        console.error('Ошибка:', error);
                    });
            }

            function closeChartsDialog() {
                document.getElementById('chartsDialog').close();
            }

function loadGraff(obId, dogId, year) {
    const container = document.getElementById('graffContainer');
    container.innerHTML = '<div style="text-align: center; padding: 40px;">Загрузка графика...</div>';

    fetch(`/api/dogs/${dogId}/graff?ob_id=${obId}&year=${year}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                container.innerHTML = '<div style="color: red; text-align: center;">Нет данных</div>';
                return;
            }

            const months = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 
                           'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'];

            let html = `<h4>График работ по оборудованию за ${year} год</h4>`;
            html += '<table style="width: 100%; border-collapse: collapse;">';

            // Заголовки
            html += '<thead>';
            html += '<tr style="background-color: #e4f0fb;">';
            html += '<th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Год</th>';
            for (var i = 0; i < months.length; i++) {
                html += `<th style="border: 1px solid #ddd; padding: 8px; text-align: center;">${months[i]}</th>`;
            }
            html += '<th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Год прайса</th>';
            html += '</tr></thead>';

            // Данные
            html += '<tbody>';
            html += '<tr>';
            html += `<td style="border: 1px solid #ddd; padding: 8px; text-align: center; font-weight: bold;">${data.god || year}</td>`;
            for (var m = 0; m < 12; m++) {
                var work = data.months[m] || 0;
                html += `<td style="border: 1px solid #ddd; padding: 8px; text-align: center;">${work}</td>`;
            }
            html += `<td style="border: 1px solid #ddd; padding: 8px; text-align: center; font-weight: bold;">${data.price_god || 0}</td>`;
            html += '</tr>';
            html += '</tbody>';
            html += '</tr>';

            container.innerHTML = html;
        })
        .catch(error => {
            console.error('Ошибка:', error);
            container.innerHTML = '<div style="color: red; text-align: center;">Ошибка загрузки</div>';
        });
}

// Добавь эту функцию для выделения строки оборудования
function selectEquipmentRow(element, obId) {
    // Убираем выделение со всех строк
    const allRows = document.querySelectorAll('#equipmentGraffTable tr');
    allRows.forEach(row => {
        row.style.backgroundColor = '';
        row.style.fontWeight = 'normal';
    });
    
    // Выделяем выбранную строку
    const selectedRow = element.closest('tr');
    if (selectedRow) {
        selectedRow.style.backgroundColor = '#e4f0fb';
        selectedRow.style.fontWeight = 'bold';
    }
    
    // Сохраняем ID выбранного оборудования (опционально)
    window.selectedObId = obId;
}

        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


# ИНФОРМАЦИЯ ДИАЛОГОВОГО ОКНА
@router.get("/api/dogs/{id_dog}/dialog")
async def dog_dialog_api(request: Request, id_dog: int, actual_only: int = 1, partial: bool = False):
    dog = get_dog_ch(request, id_dog)
    if not dog:
        if partial:
            return {"error": "Договор не найден"}
        return "<h1>Договор не найден</h1>"

    id_klient = dog.get('id_klient')

    if partial:
        # Начисления
        nach = nach_for_dog(request, id_dog)
        if nach:
            table_nach = ""
            for row in nach:
                table_nach += f"""
                    <tr>
                        <td style="border: 1px solid #1073b7; padding: 6px; text-align: center;">{row.get('god', '-')}</td>
                        <td style="border: 1px solid #1073b7; padding: 6px; text-align: right;">{row.get('m1', 0):,.2f}</td>
                        <td style="border: 1px solid #1073b7; padding: 6px; text-align: right;">{row.get('m2', 0):,.2f}</td>
                        <td style="border: 1px solid #1073b7; padding: 6px; text-align: right;">{row.get('m3', 0):,.2f}</td>
                        <td style="border: 1px solid #1073b7; padding: 6px; text-align: right;">{row.get('m4', 0):,.2f}</td>
                        <td style="border: 1px solid #1073b7; padding: 6px; text-align: right;">{row.get('m5', 0):,.2f}</td>
                        <td style="border: 1px solid #1073b7; padding: 6px; text-align: right;">{row.get('m6', 0):,.2f}</td>
                        <td style="border: 1px solid #1073b7; padding: 6px; text-align: right;">{row.get('m7', 0):,.2f}</td>
                        <td style="border: 1px solid #1073b7; padding: 6px; text-align: right;">{row.get('m8', 0):,.2f}</td>
                        <td style="border: 1px solid #1073b7; padding: 6px; text-align: right;">{row.get('m9', 0):,.2f}</td>
                        <td style="border: 1px solid #1073b7; padding: 6px; text-align: right;">{row.get('m10', 0):,.2f}</td>
                        <td style="border: 1px solid #1073b7; padding: 6px; text-align: right;">{row.get('m11', 0):,.2f}</td>
                        <td style="border: 1px solid #1073b7; padding: 6px; text-align: right;">{row.get('m12', 0):,.2f}</td>
                    </tr>
                """
        else:
            table_nach = '<tr><td colspan="14" style="text-align: center;">Нет записей</td></tr>'

        # Даты работ ВДГО
        obj_klient = obj_for_dog(request, id_klient)
        table_obj_klient = ""
        if obj_klient:
            for row in obj_klient:
                table_obj_klient += (f"""
                    <tr>
                        <td style='border:1px solid #ddd; padding:8px;'>{row.get('id_object', '-')}</td>
                        <td style='border:1px solid #ddd; padding:8px;'>{row.get('date_action', '-').strftime('%Y-%m-%d')}</td>
                    </tr>
                """)
        else:
            table_obj_klient = "<tr><td colspan='2' style='text-align: center;'>Нет записей</td></tr>"

        # Оплаты
        payment = payment_for_dog(request, id_dog)
        table_payment = ""
        if payment:
            for row in payment:
                table_payment += f"""
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 8px;">{row['id_dog']}</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">{row['dn'].strftime('%Y-%m-%d')}</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">{row['s']}</td>
                    </tr>
                """
        else:
            table_payment = '<tr><td colspan="3" style="text-align: center;">Нет записей</td></tr>'

        # История договора
        dogs_tab2 = get_dog_tab2(request, id_dog)
        table_rows_tab2 = ""
        for row in dogs_tab2:
            year = row['dat_n'].strftime('%Y') if row['dat_n'] else ''
            table_rows_tab2 += f"""
                <tr ondblclick="showChartsDialog({row['id_dog']}, '{year}')" style="cursor: pointer;">
                    <td style="border: 1px solid #ddd; padding: 8px;">{row['dat_n'].strftime('%d.%m.%Y')}</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">{row['dat_k'].strftime('%d.%m.%Y')}</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">{row['s400']}</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">{row['s500']}</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">{row['s1431']}</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">{row['sal_n']}</td>
                </tr>
            """

        return {
            "table_nach": table_nach,
            "table_obj_klient": table_obj_klient,
            "table_payment": table_payment,
            "table_rows_tab2": table_rows_tab2
        }

    podryadchik = get_podryadchik(request, id_klient)
    num_dog_txt = dog.get('num_dog_txt', '')

    # История договора
    dogs_tab2 = get_dog_tab2(request, id_dog)
    table_rows_tab2 = ""
    for row in dogs_tab2:
        year = row['dat_n'].strftime('%Y') if row['dat_n'] else ''
        table_rows_tab2 += f"""
            <tr ondblclick="showChartsDialog({row['id_dog']}, '{year}')" style="cursor: pointer;">
                <td style="border: 1px solid #ddd; padding: 8px;">{row['dat_n'].strftime('%d.%m.%Y')}</td>
                <td style="border: 1px solid #ddd; padding: 8px;">{row['dat_k'].strftime('%d.%m.%Y')}</td>
                <td style="border: 1px solid #ddd; padding: 8px;">{row['s400']}</td>
                <td style="border: 1px solid #ddd; padding: 8px;">{row['s500']}</td>
                <td style="border: 1px solid #ddd; padding: 8px;">{row['s1431']}</td>
                <td style="border: 1px solid #ddd; padding: 8px;">{row['sal_n']}</td>
            </tr>
        """

    # Договоры клиента
    dogs_kl = dogs_for_klient(request, id_klient)
    if dogs_kl:
        table_dogs_kl = ""
        for row in dogs_kl:
            table_dogs_kl += f"""
            <tr onclick="loadDogData({row['id_dog']})" style="cursor: pointer;">
                <td style="border: 1px solid #ddd; padding: 8px;">{row['id_dog']}</td>
                <td style="border: 1px solid #ddd; padding: 8px;">{row.get('num_dog_txt', '-')}</td>
                <td style="border: 1px solid #ddd; padding: 8px;">{row['d_dog'].strftime('%d.%m.%Y')}</td>
                <td style="border: 1px solid #ddd; padding: 8px;">{row.get('name_type', '-')}</td>
                <td style="border: 1px solid #ddd; padding: 8px;">{row.get('name_st', '-')}</td>
                <td style="border: 1px solid #ddd; padding: 8px;">{row.get('saldo_now', '-')}</td>
            </tr>
            """
    else:
        table_dogs_kl = '<tr><td colspan="6" style="text-align: center; padding: 20px;">Нет записей</td></tr>'

    # Даты работ ВДГО
    obj_klient = obj_for_klient(request, id_klient)
    if obj_klient:
        table_obj_klient = ""
        for row in obj_klient:
            table_obj_klient += f"""
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px;">{row.get('id_object', '-')}</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">{row.get('date_action', '-').strftime('%Y-%m-%d')}</td>
                </tr>
            """
    else:
        table_obj_klient = '<tr><td colspan="2" style="text-align: center; padding: 20px;">Нет записей</td></tr>'

    month_names = {1: 'Январь', 2: 'Февраль', 3: 'Март', 4: 'Апрель',
                   5: 'Май', 6: 'Июнь', 7: 'Июль', 8: 'Август',
                   9: 'Сентябрь', 10: 'Октябрь', 11: 'Ноябрь', 12: 'Декабрь'}
    mesobc = dog.get('месобс', 0)
    mesobc_name = month_names.get(int(mesobc), '-') if mesobc else '-'

    # СУММА ОПЛАТ
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

    # Начисления
    nach = nach_for_dog(request, id_dog)
    if nach:
        table_nach = ""
        for row in nach:
            table_nach += f"""
                <tr>
                    <td style="border: 1px solid #1073b7; padding: 6px; text-align: center;">{row.get('god', '-')}</td>
                    <td style="border: 1px solid #1073b7; padding: 6px; text-align: right;">{row.get('m1', 0):,.2f}</td>
                    <td style="border: 1px solid #1073b7; padding: 6px; text-align: right;">{row.get('m2', 0):,.2f}</td>
                    <td style="border: 1px solid #1073b7; padding: 6px; text-align: right;">{row.get('m3', 0):,.2f}</td>
                    <td style="border: 1px solid #1073b7; padding: 6px; text-align: right;">{row.get('m4', 0):,.2f}</td>
                    <td style="border: 1px solid #1073b7; padding: 6px; text-align: right;">{row.get('m5', 0):,.2f}</td>
                    <td style="border: 1px solid #1073b7; padding: 6px; text-align: right;">{row.get('m6', 0):,.2f}</td>
                    <td style="border: 1px solid #1073b7; padding: 6px; text-align: right;">{row.get('m7', 0):,.2f}</td>
                    <td style="border: 1px solid #1073b7; padding: 6px; text-align: right;">{row.get('m8', 0):,.2f}</td>
                    <td style="border: 1px solid #1073b7; padding: 6px; text-align: right;">{row.get('m9', 0):,.2f}</td>
                    <td style="border: 1px solid #1073b7; padding: 6px; text-align: right;">{row.get('m10', 0):,.2f}</td>
                    <td style="border: 1px solid #1073b7; padding: 6px; text-align: right;">{row.get('m11', 0):,.2f}</td>
                    <td style="border: 1px solid #1073b7; padding: 6px; text-align: right;">{row.get('m12', 0):,.2f}</td>
                </tr>
            """
    else:
        table_nach = '<tr><td colspan="14" style="text-align: center; font-size: 16px;">Нет записей</td></tr>'

    # Оборудование
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
        table_equipment = '<tr><td colspan="8" style="text-align: center; padding: 20px;">Нет записей</td></tr>'

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

        <!-- ЛЕВЫЙ СТОЛБЕЦ -->
        <div style="flex: 1; max-width: 30%;">

            <div class="personal_info">
                <h3>Личные данные</h3>
                <div style="font-size: 16px;">
                    <p style="margin: 0;"><strong>№ лицевого счета ГРО:</strong> {dog.get('айди', '-')}</p>
                    <p style="margin: 0;"><strong>№ лицевого счета РГК:</strong> {dog.get('РГК', '-')}</p>
                    <p style="margin: 0;"><strong>№ ЕЛС:</strong> {dog.get('ЕЛС', '-')}</p>
                    <p style="margin: 0;"><strong>ФИО заказчика:</strong> {dog.get('фио', '-')}</p>
                    <p style="margin: 0;"><strong>Адрес расположения оборудования:</strong> {dog.get('адрес', '-')}, {dog.get('индекс', '-')}</p>
                    <p style="margin: 0;"><strong>Номер телефона:</strong> {dog.get('телефон', '-')}</p>
                    <p style="margin: 0;"><strong>Адрес электронной почты:</strong> {dog.get('почта', '-')}</p>
                    <p style="margin: 0;"><strong>Подрядчик:</strong> {podryadchik}</p>
                    <p style="margin: 0;"><strong>Месяц обслуживания:</strong> {mesobc_name}</p>
                </div>
            </div>

        </div>

        <!-- ПРАВЫЙ СТОЛБЕЦ -->
        <div style="flex: 1; max-width: 70%;">

            <!-- Договоры клиента (под личными данными) -->
            <div>
                <div class="table_dogs_for_klient">
                    <h3>Договоры клиента</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <thead>
                            <tr>
                                <th>ID договора</th>
                                <th>Номер договора</th>
                                <th>Дата начала</th>
                                <th>Тип</th>
                                <th>Статус</th>
                                <th>Нач. сальдо</th>
                            </tr>
                        </thead>
                        <tbody id="dogsKlBody">
                            {table_dogs_kl}
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- История договора -->
            <div class="table_ch_tab2">
                <h3 id="historyTitle">История договора {dog.get('id_dog')}</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr>
                            <th>Дата начала</th>
                            <th>Дата конца</th>
                            <th>400</th>
                            <th>500</th>
                            <th>1431</th>
                            <th>Начальное сальдо</th>
                        </tr>
                    </thead>
                    <tbody id="historyTableBody">{table_rows_tab2}</tbody>
                </table>
            </div>

            <!-- Диалог для графиков -->
            <dialog id="chartsDialog" style="width: 70%; height: 70%; border-radius: 8px; border: 2px solid #0952a0; padding: 0;">
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px; background: #1073b7; border-radius: 6px 6px 0 0;">
                    <h2 style="color: white; margin: 0;">Графики по договору</h2>
                    <button onclick="closeChartsDialog()" style="background: none; border: none; font-size: 24px; cursor: pointer; color: white;">✖</button>
                </div>
                <div id="chartsDialogContent" style="padding: 15px; overflow-y: auto; height: calc(100% - 60px);">
                    <div style="text-align: center; padding: 40px;">Загрузка...</div>
                </div>
            </dialog>

        </div>




</div>

        <div style="display: flex; justify-content: flex-start; align-items: flex-start; gap: 10px;">
            <div class="table_nach_tab2">
                <h3>Начисления</h3>
                <div style="overflow-x: auto;">
                    <table style="width: 100%; border-collapse: collapse; font-size: 11px;">
                        <thead>
                            <tr>
                                <th style="border: 1px solid #1073b7; padding: 6px;">Год</th>
                                <th style="border: 1px solid #1073b7; padding: 6px;">1</th>
                                <th style="border: 1px solid #1073b7; padding: 6px;">2</th>
                                <th style="border: 1px solid #1073b7; padding: 6px;">3</th>
                                <th style="border: 1px solid #1073b7; padding: 6px;">4</th>
                                <th style="border: 1px solid #1073b7; padding: 6px;">5</th>
                                <th style="border: 1px solid #1073b7; padding: 6px;">6</th>
                                <th style="border: 1px solid #1073b7; padding: 6px;">7</th>
                                <th style="border: 1px solid #1073b7; padding: 6px;">8</th>
                                <th style="border: 1px solid #1073b7; padding: 6px;">9</th>
                                <th style="border: 1px solid #1073b7; padding: 6px;">10</th>
                                <th style="border: 1px solid #1073b7; padding: 6px;">11</th>
                                <th style="border: 1px solid #1073b7; padding: 6px;">12</th>
                            </tr>
                        </thead>
                        <tbody id="nachTableBody">
                            {table_nach}
                        </tbody>
                    </table>
                </div>
            </div>

            <div class="data_vdgo">
                <h3>Даты работ ВДГО</h3>
                <table>
                    <thead>
                        <tr>
                            <th>ID объекта</th>
                            <th>Дата выполнения</th>
                        </tr>
                    </thead>
                    <tbody id="objTableBody">{table_obj_klient}</tbody>
                </table>
            </div>

            <div class="summ_payment">
                <h3>Сумма оплат</h3>
                <table>
                    <thead>
                        <tr>
                            <th>ID договора</th>
                            <th>Дата оплаты</th>
                            <th>Сумма к оплате</th>
                        </tr>
                    </thead>
                    <tbody id="paymentTableBody">
                        {table_payment}
                    </tbody>
                </table>
            </div>
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
    """
    html += """
    <script>
        var activeTab = 'PersonalData';

        function openTab(evt, tabName) {
            activeTab = tabName;
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
                })
                .catch(error => console.error('Ошибка:', error));
        }

        function loadDogData(newDogId) {
            fetch(`/api/dogs/${newDogId}/dialog?partial=true&actual_only=${document.getElementById('actualOnlyCheckbox')?.checked ? 1 : 0}`)
                .then(response => response.json())
                .then(data => {
                    // Начисления
                    var nachTable = document.querySelector('#nachTableBody');
                    if (nachTable) nachTable.innerHTML = data.table_nach;

                    // Даты работ ВДГО
                    var objTable = document.querySelector('#objTableBody');
                    if (objTable) objTable.innerHTML = data.table_obj_klient;

                    // Оплаты
                    var paymentTable = document.querySelector('#paymentTableBody');
                    if (paymentTable) paymentTable.innerHTML = data.table_payment;

                    // История договора
                    var historyTable = document.querySelector('#historyTableBody');
                    if (historyTable) historyTable.innerHTML = data.table_rows_tab2;

                    // Заголовок истории 
                    var historyTitle = document.querySelector('#historyTitle');
                    if (historyTitle) historyTitle.innerHTML = 'История договора ' + newDogId;
                })
                .catch(error => console.error('Ошибка:', error));
        }

        function showChartsDialog(dogId, year) {
            const dialog = document.getElementById('chartsDialog');
            const contentDiv = document.getElementById('chartsDialogContent');
            contentDiv.innerHTML = '<div style="text-align: center; padding: 40px;">Загрузка...</div>';
            dialog.showModal();

            fetch(`/api/dogs/${dogId}/charts?year=${year}`)
                .then(response => response.text())
                .then(html => {
                    contentDiv.innerHTML = html;
                })
                .catch(error => {
                    contentDiv.innerHTML = '<div style="color: black; text-align: center;">Нет записей</div>';
                    console.error('Ошибка:', error);
                });
        }

        function closeChartsDialog() {
            document.getElementById('chartsDialog').close();
        }

    </script>
    """
    return HTMLResponse(content=html)


@router.get("/search/dogs", response_class=HTMLResponse)
async def search_dog_page(
        request: Request,
        idklient: str = "",
        iddog: str = "",
        numdog: str = "",
        fio: str = "",
        street: str = "",
        house: str = "",
        flat: str = ""
):
    results = search_dog_ch(request, idklient, iddog, numdog, fio, street, house, flat)

    table_rows = ""
    for row in results:
        table_rows += f"""
            <tr onclick="showContractDialog({row['id_dog']})">
                <td>{row.get('id_klient', '-')}</td>
                <td>{row.get('FIO', '-')}</td>
                <td>{row.get('addr', '-')}</td>
                <td>{row.get('id_dog', '-')}</td>
                <td>{row.get('num_dog_txt', '-')}</td>
                <td>{row.get('name_type', '-')}</td>
                <td>{row.get('d_dog', '-').strftime('%Y-%m-%d') if row.get('d_dog') else '-'}</td>
                <td>{row.get('name_st', '-')}</td>
            </tr>
        """

    html = f"""
    <html>
    <head>
        <title style="font-size: 28px;" >Результаты поиска</title>
        <link rel="stylesheet" href="/static/css/style.css">
        <style>
            .table_ch {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
            }}
            .table_ch th, .table_ch td {{
                border: 1px solid #ddd;
                padding: 6px 8px;
                font-size: 16px;
            }}
            .table_ch th {{
                background-color: #e4f0fb;
                border-color: #1073b7;
            }}
            .table_ch tr:hover {{
                background-color: #f5f5f5;
                cursor: pointer;
            }}
            .button-back {{
                background: #1073b7;
                font-size: 14px;
                padding: 6px 15px;
                color: white;
                text-decoration: none;
                border: none;
                border-radius: 4px;
                display: inline-block;
            }}
            .button-back:hover {{
                background: #0952a0;
            }}
        </style>
    </head>
    <body>
        <div style="background: #e4f0fb; padding: 8px 15px; display: flex; justify-content: space-between; align-items: center;">
            <h1 style="color: #0952a0; margin: 0; font-size: 24px;">Результаты поиска</h1>
            <a href="/dogs" class="button-back">Назад к списку</a>
        </div>
        <div style="overflow-x: auto;">
            <table class="table_ch">
                <thead>
                    <tr>
                        <th>ID клиента</th>
                        <th>ФИО</th>
                        <th>Адрес оборудования</th>
                        <th>ID договора</th>
                        <th>Номер договора</th>
                        <th>Тип</th>
                        <th>Дата договора</th>
                        <th>Статус</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows if table_rows else '<tr><td colspan="8" style="text-align: center;">Договоры не найдены</td></tr>'}
                </tbody>
            </table>
        </div>

        <dialog id="contractDialog" style="width: 90%; height: 90%; border-radius: 8px; border: 2px solid #0952a0; padding: 0;">
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px; background: #1073b7; border-radius: 6px 6px 0 0;">
                <h2 style="color: white; margin: 0; font-size: 18px;">Информация по клиенту</h2>
                <button onclick="closeContractDialog()" style="background: none; border: none; font-size: 22px; cursor: pointer; color: white;">✖</button>
            </div>
            <div id="contractDialogContent" style="padding: 10px; overflow-y: auto; max-height: calc(90vh - 50px);"></div>
        </dialog>

        <dialog id="chartsDialog" style="width: 70%; height: 70%; border-radius: 8px; border: 2px solid #0952a0; padding: 0;">
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px; background: #1073b7; border-radius: 6px 6px 0 0;">
                <h2 style="color: white; margin: 0;">Графики по договору</h2>
                <button onclick="closeChartsDialog()" style="background: none; border: none; font-size: 24px; cursor: pointer; color: white;">✖</button>
            </div>
            <div id="chartsDialogContent" style="padding: 15px; overflow-y: auto; height: calc(100% - 60px);">
                <div style="text-align: center; padding: 40px;">Загрузка...</div>
            </div>
        </dialog>


        <script>
            var activeTab = 'PersonalData';

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
                    .then(html => {{
                        contentDiv.innerHTML = html;
                    }})
                    .catch(error => {{
                        contentDiv.innerHTML = '<div style="color: red; text-align: center;">Ошибка загрузки данных</div>';
                    }});
            }}

            function openTab(evt, tabName) {{
                activeTab = tabName;
                var i, tabcontent, tablinks;
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
                var isChecked = document.getElementById('actualOnlyCheckbox')?.checked ? 1 : 0;
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

            function loadDogData(newDogId) {{
                fetch(`/api/dogs/${{newDogId}}/dialog?partial=true&actual_only=${{document.getElementById('actualOnlyCheckbox')?.checked ? 1 : 0}}`)
                    .then(response => response.json())
                    .then(data => {{
                        var nachTable = document.querySelector('#nachTableBody');
                        if (nachTable) nachTable.innerHTML = data.table_nach;

                        var objTable = document.querySelector('#objTableBody');
                        if (objTable) objTable.innerHTML = data.table_obj_klient;

                        var paymentTable = document.querySelector('#paymentTableBody');
                        if (paymentTable) paymentTable.innerHTML = data.table_payment;

                        var historyTable = document.querySelector('#historyTableBody');
                        if (historyTable) historyTable.innerHTML = data.table_rows_tab2;

                        var historyTitle = document.querySelector('#historyTitle');
                        if (historyTitle) historyTitle.innerHTML = 'История договора ' + newDogId;
                    }})
                    .catch(error => console.error('Ошибка:', error));
            }}

            function showChartsDialog(dogId, year) {{
                console.log('=== showChartsDialog вызван ===');
                console.log('dogId:', dogId);
                console.log('year:', year);

                const dialog = document.getElementById('chartsDialog');
                console.log('dialog элемент:', dialog);

                if (!dialog) {{
                    console.error('❌ Диалог chartsDialog не найден в DOM!');
                    alert('Ошибка: диалог графиков не найден');
                    return;
                }}

                const contentDiv = document.getElementById('chartsDialogContent');
                console.log('contentDiv элемент:', contentDiv);

                contentDiv.innerHTML = '<div style="text-align: center; padding: 40px;">Загрузка...</div>';
                dialog.showModal();
                console.log('✅ Диалог открыт');

                const url = `/api/dogs/${{dogId}}/charts?year=${{year}}`;
                console.log('📡 Запрос к URL:', url);

                fetch(url)
                    .then(response => {{
                        console.log('📥 Ответ получен, статус:', response.status);
                        return response.text();
                    }})
                    .then(html => {{
                        console.log('✅ HTML получен, длина:', html.length);
                        console.log('📄 Первые 200 символов HTML:', html.substring(0, 200));
                        contentDiv.innerHTML = html;
                        console.log('✅ HTML вставлен в диалог');

                        const table = contentDiv.querySelector('.graff-table');
                        console.log('Таблица .graff-table найдена:', table ? 'да' : 'нет');

                        const equipmentRows = contentDiv.querySelectorAll('#equipmentGraffTable tr');
                        console.log('Количество строк с оборудованием:', equipmentRows.length);
                    }})
                    .catch(error => {{
                        console.error('❌ Ошибка загрузки:', error);
                        contentDiv.innerHTML = '<div style="color: red; text-align: center;">Ошибка загрузки данных</div>';
                    }});
            }}
function loadGraff(obId, dogId, year) {{
    const container = document.getElementById('graffContainer');
    container.innerHTML = '<div style="text-align: center; padding: 40px;">Загрузка графика...</div>';

    fetch(`/api/dogs/${{dogId}}/graff?ob_id=${{obId}}&year=${{year}}`)
        .then(response => response.json())
        .then(data => {{
            if (data.error) {{
                container.innerHTML = '<div style="color: red; text-align: center;">Нет данных</div>';
                return;
            }}

            const months = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 
                           'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'];

            let html = `<h4 style="margin-top: 5px;">График работ по оборудованию за ${{year}} год</h4>`;
            html += '<table style="width: 100%; border-collapse: collapse;">';

            // Заголовки
            html += '<thead>';
            html += '<tr style="background-color: #e4f0fb;">';
            html += '<th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Год</th>';
            for (var i = 0; i < months.length; i++) {{
                html += `<th style="border: 1px solid #ddd; padding: 8px; text-align: center;">${{months[i]}}</th>`;
            }}
            html += '<th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Год прайса</th>';
            html += '<tr></thead>';

            // Данные
            html += '<tbody>';
            html += '<tr>';
            html += `<td style="border: 1px solid #ddd; padding: 8px; text-align: center; font-weight: bold;">${{data.god || year}}</td>`;
            for (var m = 0; m < 12; m++) {{
                var work = data.months[m] || 0;
                html += `<td style="border: 1px solid #ddd; padding: 8px; text-align: center;">${{work}}</td>`;
            }}
            html += `<td style="border: 1px solid #ddd; padding: 8px; text-align: center; font-weight: bold;">${{data.price_god || 0}}</td>`;
            html += '</tr>';
            html += '</tbody>';
            html += '</table>';

            container.innerHTML = html;
        }})
        .catch(error => {{
            console.error('Ошибка:', error);
            container.innerHTML = '<div style="color: red; text-align: center;">Ошибка загрузки</div>';
        }});
}}

// Добавь эту функцию для выделения строки оборудования
function selectEquipmentRow(element, obId) {{
    // Убираем выделение со всех строк
    const allRows = document.querySelectorAll('#equipmentGraffTable tr');
    allRows.forEach(row => {{
        row.style.backgroundColor = '';
        row.style.fontWeight = 'normal';
    }});
    
    // Выделяем выбранную строку
    const selectedRow = element.closest('tr');
    if (selectedRow) {{
        selectedRow.style.backgroundColor = '#e4f0fb';
        selectedRow.style.fontWeight = 'bold';
    }}
    
    // Сохраняем ID выбранного оборудования (опционально)
    window.selectedObId = obId;
}}

            function closeChartsDialog() {{
                document.getElementById('chartsDialog').close();
            }}

        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@router.get("/api/dogs/{id_dog}/charts")
async def dog_charts_api(request: Request, id_dog: int, year: str = None):
    dog = get_dog_ch(request, id_dog)
    if not dog:
        return "<h1>Договор не найден</h1>"

    id_klient = dog.get('id_klient')

    # Получаем оборудование, актуальное для указанного года
    equipment = get_actual_equipment_by_year(request, id_klient, year)

    # Формируем таблицу оборудования
    table_equipment = ""
    if equipment:
        for row in equipment:
            table_equipment += f"""
                    <tr ondblclick="loadGraff({row['id_ob']}, {id_dog}, '{year}')" onclick="selectEquipmentRow(this, {row['id_ob']})" style="cursor: pointer;">
                    <td style="border: 1px solid #ddd; padding: 8px;">{row.get('name_ob', '-')}</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">{row.get('name_izg', '-')}</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">{row.get('name_model', '-')}</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">{row.get('kol_oborud', '-')}</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">{row.get('dol_ob', '-')}</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">{row.get('du', '-')[:10] if row.get('du') else '-'}</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">{row.get('do', '-')[:10] if row.get('do') else '-'}<td>
                </tr>
            """
    else:
        table_equipment = '<td><td colspan="7" style="text-align: center;">Нет оборудования за указанный период<\/td><\/tr>'
    html = f"""
    <style>
        .graff-table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }}
        .graff-table th, .graff-table td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: center;
        }}
        .graff-table th {{
            background-color: #e4f0fb;
        }}
        .graff-container {{
            margin-top: 20px;
            padding: 15px;
            border: 1px solid #1073b7;
            border-radius: 8px;
            background: #f9f9f9;
        }}
    </style>

    <h3>Договор №{dog.get('num_dog_txt', '-')}</h3>

    <h4>Оборудование по договору (двойной клик для просмотра графика)</h4>
    <table class="graff-table">
        <thead>
            <tr>
                <th>Оборудование</th>
                <th>Марка</th>
                <th>Модель</th>
                <th>Кол-во</th>
                <th>Доля</th>
                <th>Дата установки</th>
                <th>Дата отключения</th>
            </tr>
        </thead>
        <tbody id="equipmentGraffTable">
            {table_equipment}
        </tbody>
    </table>

    <div id="graffContainer" class="graff-container">
        <div style="text-align: center; padding: 40px; color: #666;">
            Выберите оборудование двойным кликом для просмотра графика работ
        </div>
    </div>
    """
    html += """
    <script>
function loadGraff(obId, dogId, year) {{
    const container = document.getElementById('graffContainer');
    container.innerHTML = '<div style="text-align: center; padding: 40px;">Загрузка графика...</div>';

    fetch(`/api/dogs/${{dogId}}/graff?ob_id=${{obId}}&year=${{year}}`)
        .then(response => response.json())
        .then(data => {{
            if (data.error) {{
                container.innerHTML = '<div style="color: red; text-align: center;">Нет данных</div>';
                return;
            }}

            const months = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 
                           'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'];

            let html = `<h4>График работ по оборудованию за ${{year}} год</h4>`;
            html += '<table style="width: 100%; border-collapse: collapse;">';

            // Заголовки
            html += '<thead>';
            html += '<tr style="background-color: #e4f0fb;">';
            html += '<th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Год</th>';
            for (var i = 0; i < months.length; i++) {{
                html += `<th style="border: 1px solid #ddd; padding: 8px; text-align: center;">${{months[i]}}</th>`;
            }}
            html += '<th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Год прайса</th>';
            html += '<tr></thead>';

            // Данные
            html += '<tbody>';
            html += '<tr>';
            html += `<td style="border: 1px solid #ddd; padding: 8px; text-align: center; font-weight: bold;">${{data.god || year}}</td>`;
            for (var m = 0; m < 12; m++) {{
                var work = data.months[m] || 0;
                html += `<td style="border: 1px solid #ddd; padding: 8px; text-align: center;">${{work}}</td>`;
            }}
            html += `<td style="border: 1px solid #ddd; padding: 8px; text-align: center; font-weight: bold; background-color: #e4f0fb;">${{data.price_god || 0}}</td>`;
            html += '</tr>';
            html += '</tbody>';
            html += '</table>';

            container.innerHTML = html;
        }})
        .catch(error => {{
            console.error('Ошибка:', error);
            container.innerHTML = '<div style="color: red; text-align: center;">Ошибка загрузки</div>';
        }});
}}


// Добавь эту функцию для выделения строки оборудования
function selectEquipmentRow(element, obId) {{
    // Убираем выделение со всех строк
    const allRows = document.querySelectorAll('#equipmentGraffTable tr');
    allRows.forEach(row => {{
        row.style.backgroundColor = '';
        row.style.fontWeight = 'normal';
    }});
    
    // Выделяем выбранную строку
    const selectedRow = element.closest('tr');
    if (selectedRow) {{
        selectedRow.style.backgroundColor = '#e4f0fb';
        selectedRow.style.fontWeight = 'bold';
    }}
    
    // Сохраняем ID выбранного оборудования (опционально)
    window.selectedObId = obId;
}}
    </script>
    """
    return HTMLResponse(content=html)

@router.get("/api/dogs/{id_dog}/graff")
async def get_graff_data(request: Request, id_dog: int, ob_id: int, year: str = None):
    try:
        connection = get_user_connection_ch(request)
        if not connection:
            return {"error": "Нет подключения"}

        cursor = connection.cursor()

        # Пытаемся получить данные из to_ch_jgraff
        cursor.execute("""
            SELECT m1, m2, m3, m4, m5, m6, m7, m8, m9, m10, m11, m12, god, price_god
            FROM to_ch_jgraff jg
            INNER JOIN to_ch_j j ON jg.id_j = j.id_j
            INNER JOIN to_ch_story s ON j.id_st = s.id_st
            WHERE j.id_dog = ? AND s.id_ob = ? AND jg.god = ?
        """, (id_dog, ob_id, year))

        rows = cursor.fetchall()

        # Если в первой таблице нет данных, пробуем вторую (to_ch_jgraf)
        if not rows:
            # Получаем id_j из to_ch_j
            cursor.execute("""
                SELECT j.id_j
                FROM to_ch_j j
                INNER JOIN to_ch_story s ON j.id_st = s.id_st
                WHERE j.id_dog = ? AND s.id_ob = ?
            """, (id_dog, ob_id))

            j_row = cursor.fetchone()
            if j_row:
                id_j = j_row[0]

                # Запрос к to_ch_jgraf (MSSQL через ClickHouse)
                cursor.execute("""
                    SELECT m1, m2, m3, m4, m5, m6, m7, m8, m9, m10, m11, m12, god, price_god
                    FROM to_ch_jgraf
                    WHERE id_j = ? AND god = ?
                """, (id_j, year))

                rows = cursor.fetchall()

        cursor.close()
        connection.close()

        if not rows:
            return {"error": "Нет данных для графика"}

        row = rows[0]

        # Формируем данные для таблицы
        months_data = []
        for i in range(12):
            val = row[i]
            months_data.append(1 if val and val > 0 else 0)

        return {
            "months": months_data,
            "god": row[12],
            "price_god": row[13] if len(row) > 13 and row[13] else 0
        }

    except Exception as e:
        return {"error": str(e)}