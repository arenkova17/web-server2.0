from database import get_dogs_ch, get_dog_ch, dogs_for_klient,\
    search_dog_ch, get_podryadchik, get_actual_equipment, get_user_connection_ch, \
    get_tabl_for_TOADO, get_tabl_for_VDGO, get_tabl_for_CHSEK, obj_for_dog
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
import json
from datetime import datetime
router = APIRouter()


@router.get("/dogs", response_class=HTMLResponse)
async def page_dogs(request: Request):
    current_date = datetime.now().strftime('%d.%m.%Y')
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
                <td>{dog['d_dog'].strftime('%d.%m.%Y')}</td>
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
                top: -1;
                z-index: 10;
                background-color: #f5f5f5;
                font-weight: bold;
            }}
            .table_ch thead tr th {{
                border: 1px solid #ddd;
                padding: 7px;
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
                    <label style="display: block; margin-bottom: 4px;">№ лицевого счёта ГРО</label>
                    <input type="text" id="search_idklient" placeholder="Введите номер" style="width: 100%; padding: 6px; border: 1px solid #ccc; border-radius: 4px;">
                </div>
                
                <div style="margin-bottom: 12px;">
                    <label style="display: block; margin-bottom: 4px;">№ Единого лицевого счета</label>
                    <input type="text" id="search_els" placeholder="Введите ЕЛС" style="width: 100%; padding: 6px; border: 1px solid #ccc; border-radius: 4px;">
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
                    <label style="display: block; margin-bottom: 4px;">Город, село, поселок, район</label>
                    <input type="text" id="search_town" placeholder="Введите город, село, поселок, район" style="width: 100%; padding: 6px; border: 1px solid #ccc; border-radius: 4px;">
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

        <dialog id="contractDialog" class="dialog_window">
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px; background: #1073b7; border-radius: 6px 6px 0 0;">
                <h2 style="color: white; margin: 0; font-size: 22px;">Информация по клиенту на {current_date}</h2>
                <button onclick="closeContractDialog()" style="background: none; border: none; font-size: 24px; cursor: pointer; color: white;">✖</button>
            </div>
            
            <div id="contractDialogContent" style="padding: 10px; overflow-y: auto; flex: 1;"></div>
            
            <div class="tooltip_on_dialog_page" onclick="openTooltipDialogPage()">
                <span class="tip_text_dialog" id="tip_text_dialog_page">
                    1. <strong>Личные данные</strong> — информация о клиенте.<br>
                    2. <strong>Договоры клиента</strong> — список всех договоров.<br>
                    3. <strong>Нажмите на договор</strong> — откроется информация по нему.<br>
                </span>
                <span class="circle_dialog">?</span>
            </div>
            
            
        </dialog>
        
        
        <div class="tooltip_on_page_dog" onclick="openTooptipPage()">
            <span class="circle_page">?</span>
            <span class="tip_text_page" id="tip_text_page_dog">
                1. <strong>"Найти договор"</strong> — открывает форму для поиска по договорам.<br>
                2. <strong>«Выбор модуля»</strong> — возвращает на страницу выбора программы.<br>
                3. <strong>«Выйти»</strong> — завершает сессию и выходит из системы.<br>
                4. Двойной "клик" по строке — открывает карточку клиента со списком договоров.
            </span>
        </div>
        

        """

    html += """
        <script>
            function openTooptipPage() {
                const tip = document.getElementById('tip_text_page_dog');
                if (tip.style.display === 'block') {
                    tip.style.display = 'none';
                } else {
                    tip.style.display = 'block';
                }
            }
            
            function openTooltipDialogPage() {
                const tip = document.getElementById('tip_text_dialog_page');
                if (tip.style.display === 'block') {
                    tip.style.display = 'none';
                } else {
                    tip.style.display = 'block';
                }
            }

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
                const town = document.getElementById('search_town').value;
                const street = document.getElementById('search_street').value;
                const house = document.getElementById('search_house').value;
                const flat = document.getElementById('search_flat').value;
                const els = document.getElementById('search_els').value;

                let url = '/search/dogs?';
                let params = [];

                if (idklient) params.push('idklient=' + encodeURIComponent(idklient));
                if (iddog) params.push('iddog=' + encodeURIComponent(iddog));
                if (numdog) params.push('numdog=' + encodeURIComponent(numdog));
                if (fio) params.push('fio=' + encodeURIComponent(fio));
                if (town) params.push('town=' + encodeURIComponent(town));
                if (street) params.push('street=' + encodeURIComponent(street));
                if (house) params.push('house=' + encodeURIComponent(house));
                if (flat) params.push('flat=' + encodeURIComponent(flat));
                if (els) params.push('els=' + encodeURIComponent(els));
    
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
    podryadchik = get_podryadchik(request, id_klient)

    from datetime import datetime

    month_names = {1: '01', 2: '02', 3: '03', 4: '04',
                   5: '05', 6: '06', 7: '07', 8: '08',
                   9: '09', 10: '10', 11: '11', 12: '12'}

    mesobc = dog.get('месобс', 0)
    current_year = datetime.now().year

    if mesobc:
        mesobc_name = f"{month_names.get(int(mesobc), '-')}.{current_year}"
    else:
        mesobc_name = '-'

    # Получаем договоры клиента
    dogs_kl = dogs_for_klient(request, id_klient)

    # Таблица договоров клиента
    table_dogs_kl = ""
    if dogs_kl:
        for row in dogs_kl:
            table_dogs_kl += f"""
            <tr style="cursor: pointer;">
                <td>{row['id_dog']}</td>
                <td>{row.get('num_dog_txt', '-')}</td>
                <td>{row['d_dog'].strftime('%d.%m.%Y')}</td>
                <td>{row.get('name_type', '-')}</td>
                <td>{row.get('name_st', '-')}</td>
            </tr>
            """
    else:
        table_dogs_kl = '<tr><td colspan="5" style="text-align: center; padding: 20px;">Нет записей</td></tr>'

    # ОБОРУДОВАНИЕ
    equipment = get_actual_equipment(request, id_klient, actual_only)
    if equipment:
        table_equipment = ""
        for row in equipment:
            table_equipment += f"""
                <tr>
                    <td>{row['name_ob']}</td>
                    <td>{row['dol_ob']}</td>
                    <td>{row['kol_oborud']}</td>
                </tr>
            """
    else:
        table_equipment = '<tr><td colspan="3" style="text-align: center; padding: 20px;">Нет записей</td></tr>'


    all_tables_html = ""

    if dogs_kl:
        for dog_row in dogs_kl:
            dog_id = dog_row['id_dog']
            name_type = dog_row.get('name_type', '')
            dog_num = dog_row.get('num_dog_txt', dog_id)

            # 1. ТО100%+АДО100%
            if name_type == 'ТО100%+АДО100%':
                toado_data = get_tabl_for_TOADO(request, dog_id)
                table_rows = ""
                if toado_data:
                    for row in toado_data:
                        table_rows += f"""
                            <tr>
                                <td>{row.get('id_dog', '-')}</td>
                                <td>{row.get('god', '-')}</td>
                                <td>{row.get('nach400', '-') if row.get('nach400') is not None else '-'}</td>
                                <td>{row.get('nach1431', '-') if row.get('nach1431') is not None else '-'}</td>
                                <td>{row.get('summanach', '-') if row.get('summanach') is not None else '-'}</td>
                                <td>{row.get('s', '-') if row.get('s') is not None else '-'}</td>
                                <td>{row.get('dn', '-') if row.get('dn') is not None else '-'}</td>
                            </tr>
                        """
                else:
                    table_rows = '<tr><td colspan="7" style="text-align: center;">Нет данных</td></tr>'

                all_tables_html += f"""
                <details style="border-radius: 8px; padding: 10px; border: 1px solid #1073b7; margin: 10px 0 10px 0;">
                    <summary style="cursor: pointer; font-weight: bold; font-size: 18px; padding: 5px;">
                        Информация по договору <span style="color: #0952a0;">{name_type}</span> №{dog_num} <span style="color: #0952a0;">(ID договора {dog_id})</span>
                    </summary>
                    
                    <div class="table_nach_opl" style="margin-top: 15px;">
                        <h4>Начисления и оплата</h4>
                        <table style="width: 100%; border-collapse: collapse;">
                            <thead>
                                <tr>
                                    <th>ID договора</th>
                                    <th>Год</th>
                                    <th>ТО начисление (ТО)</th>
                                    <th>АДО начисления (1431)</th>
                                    <th>ИТОГО</th>
                                    <th>Оплата</th>
                                    <th>Дата оплаты</th>
                                </tr>
                            </thead>
                            <tbody id="TOADOTableBody_{dog_id}">
                                {table_rows}
                            </tbody>
                        </table>
                    </div>
                </details>
                """

            # 2. ВДГО факт / ВДГО 100%
            elif name_type in ['ВДГО факт', 'ВДГО 100%', 'ВДГО (100%) стар.']:
                vdgo_data = get_tabl_for_VDGO(request, dog_id)
                work_dates = obj_for_dog(request, dog_id)

                table_rows = ""
                if vdgo_data:
                    for row in vdgo_data:
                        table_rows += f"""
                            <tr>
                                <td>{row.get('id_dog', '-')}</td>
                                <td>{row.get('period', '-')}</td>
                                <td>{row.get('nach500', '-') if row.get('nach500') is not None else '-'}</td>
                                <td>{row.get('opl', '-') if row.get('opl') is not None else '-'}</td>
                                <td>{row.get('dn', '-') if row.get('dn') is not None else '-'}</td>
                            </tr>
                        """
                else:
                    table_rows = '<tr><td colspan="5" style="text-align: center;">Нет данных</td></tr>'

                work_dates_rows = ""
                if work_dates:
                    for wd in work_dates:
                        date_action = wd.get('date_action')
                        date_str = date_action.strftime('%d.%m.%Y') if date_action else '-'
                        work_dates_rows += f"""
                            <tr>
                                <td>{wd.get('id_object', '-')}</td>
                                <td>{date_str}</td>
                            </tr>
                        """
                else:
                    work_dates_rows = '<tr><td colspan="2" style="text-align: center;">Нет данных</td></tr>'

                all_tables_html += f"""
                <details style="border-radius: 8px; padding: 10px; border: 1px solid #1073b7; margin: 10px 0 10px 0;">
                    <summary style="cursor: pointer; font-weight: bold; font-size: 18px; padding: 5px;">
                        Информация по договору <span style="color: #0952a0;">{name_type}</span> №{dog_num} <span style="color: #0952a0;">(ID договора {dog_id})</span>
                    </summary>
                    <div style="display: flex; justify-content: flex-start; align-items: flex-start; gap: 20px; margin-top: 15px;">
                        <div class="table_obj" style="flex: 0 0 250px;">
                            <h4>Даты выполнения работ ВДГО</h4>
                            <table style="width: 100%; border-collapse: collapse;">
                                <thead>
                                    <tr>
                                        <th>ID объекта</th>
                                        <th>Дата выполнения</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {work_dates_rows}
                                </tbody>
                            </table>
                        </div>
                        <div class="table_vdgo" style="flex: 1;">
                            <h4>Начисления и оплата</h4>
                            <table style="width: 100%; border-collapse: collapse;">
                                <thead>
                                    <tr>
                                        <th>ID договора</th>
                                        <th>Период</th>
                                        <th>Начислено ВДГО (500)</th>
                                        <th>Сумма оплат</th>
                                        <th>Дата оплат</th>
                                    </tr>
                                </thead>
                                <tbody id="VDGOTableBody_{dog_id}">
                                    {table_rows}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </details>
                """

            # 3. Ч/сектор
            elif name_type == 'Ч/сектор':
                chsek_data = get_tabl_for_CHSEK(request, dog_id)
                work_dates = obj_for_dog(request, dog_id)

                table_rows = ""
                if chsek_data:
                    for row in chsek_data:
                        table_rows += f"""
                            <tr>
                                <td>{row.get('id_dog', '-')}</td>
                                <td>{row.get('period', '-')}</td>
                                <td>{row.get('nach400', '-') if row.get('nach400') is not None else '-'}</td>
                                <td>{row.get('nach1431', '-') if row.get('nach1431') is not None else '-'}</td>
                                <td>{row.get('nach500', '-') if row.get('nach500') is not None else '-'}</td>
                                <td>{row.get('summanach', '-') if row.get('summanach') is not None else '-'}</td>
                                <td>{row.get('opl', '-') if row.get('opl') is not None else '-'}</td>
                                <td>{row.get('dn', '-') if row.get('dn') is not None else '-'}</td>
                            </tr>
                        """
                else:
                    table_rows = '<tr><td colspan="8" style="text-align: center;">Нет данных</td></tr>'

                # Даты работ
                work_dates_rows = ""
                if work_dates:
                    for wd in work_dates:
                        date_action = wd.get('date_action')
                        date_str = date_action.strftime('%d.%m.%Y') if date_action else '-'
                        work_dates_rows += f"""
                            <tr>
                                <td>{wd.get('id_object', '-')}</td>
                                <td>{date_str}</td>
                            </tr>
                        """
                else:
                    work_dates_rows = '<tr><td colspan="2" style="text-align: center;">Нет данных</td></tr>'

                all_tables_html += f"""
                <details style="border-radius: 8px; padding: 10px; border: 1px solid #1073b7; margin: 10px 0 10px 0;">
                    <summary style="cursor: pointer; font-weight: bold; font-size: 18px; padding: 5px;">
                        Информация по договору <span style="color: #0952a0;">{name_type}</span> №{dog_num} <span style="color: #0952a0;">(ID договора {dog_id})</span>
                    </summary>
                    <div style="display: flex; justify-content: flex-start; align-items: flex-start; gap: 20px; margin-top: 15px;">
                        <div class="table_obj" style="flex: 0 0 250px;">
                            <h4>Даты выполнения работ ВДГО</h4>
                            <table style="width: 100%; border-collapse: collapse;">
                                <thead>
                                    <tr>
                                        <th>ID объекта</th>
                                        <th>Дата выполнения</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {work_dates_rows}
                                </tbody>
                            </table>
                        </div>
                        <div class="table_vdgo" style="flex: 1;">
                            <h4>Начисления и оплата</h4>
                            <table style="width: 100%; border-collapse: collapse;">
                                <thead>
                                    <tr>
                                        <th>ID договора</th>
                                        <th>Период</th>
                                        <th>ТО начислено (400)</th>
                                        <th>АДО начислено (1431)</th>
                                        <th>ВДГО начислено (500)</th>
                                        <th>ИТОГО начислено</th>
                                        <th>Сумма оплат</th>
                                        <th>Дата оплат</th>
                                    </tr>
                                </thead>
                                <tbody id="CHSEKTableBody_{dog_id}">
                                    {table_rows}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </details>
                """

    html = """
    <link rel="stylesheet" href="/static/css/style.css">
    <style>
        .tab {
            display: flex;
            gap: 8px;
            border-bottom: 2px solid #1073b7;
            margin-bottom: 10px;
            padding-bottom: 0;
        }
        .tab button {
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
        }
        .tab button:hover {
            background: #f0f7ff;
            color: #0952a0;
        }
        .tab button.active {
            background: #1073b7;
            color: white;
            box-shadow: 0 -2px 5px rgba(0,0,0,0.05);
        }
        .tabcontent {
            display: none;
            padding: 10px 0;
            animation: fadeIn 0.3s ease;
        }
        @keyframes fadeIn {
            from {opacity: 0; transform: translateY(5px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .table_equipment {
            max-height: 300px;
            overflow-y: auto;
            width: 98%;
            border: 1px solid #1073b7;
            padding: 10px;
            border-radius: 8px;
        }
        .table_equipment h3 {
            margin: 0px;
            color: #0952a0;
            margin-bottom: 5px;
        }
        .table_equipment table{
            width: 100%;
            border-collapse: collapse;
        }
        .table_equipment thead th {
            border: 1px solid #1073b7;
            background-color: #e4f0fb;
            font-size: 14px;
            font-weight: bold;
            text-align: center;
            vertical-align: middle;
            padding: 5px;
        }
        .table_equipment td {
            padding: 8px;
            border: 1px solid #ddd;
            text-align: left;
            vertical-align: top;
        }

        .table_equipment th:nth-child(1) { width: 40%; }
        .table_equipment th:nth-child(2) { width: 15%; }
        .table_equipment th:nth-child(3) { width: 15%; }
        .table_equipment th:nth-child(4) { width: 15%; }
        .table_equipment th:nth-child(5) { width: 15%; }
        
        
        
/*таблицы ТО АДО */
.table_nach_opl{      /*рамка для таблицы*/
    overflow-y: auto;
    width: 98%;
    border: 1px solid #1073b7;
    padding: 10px;
    border-radius: 8px;
    margin: 0 0 5px 0;
}
.table_nach_opl h4 {    /*заголовок*/
    margin: 0px;
    color: #0952a0;
    margin-bottom: 5px;
}
.table_nach_opl table{       /*сама таблица*/
    width: 100%;
    border-collapse: collapse;
}
.table_nach_opl thead th {
    border: 1px solid #1073b7;
    background-color: #e4f0fb;
    font-size: 14px;
    font-weight: bold;
    text-align: center;
    vertical-align: middle;
    padding: 5px;
}
.table_nach_opl td {
    padding: 8px;
    border: 1px solid #ddd;
    text-align: left;
    vertical-align: top;
}
.table_nach_opl td:last-child {
    width: 60px;
    text-align: center;
}
.table_nach_opl th:nth-child(1) { width: 5%; }
.table_nach_opl th:nth-child(2) { width: 16%; }
.table_nach_opl th:nth-child(3) { width: 12%; }
.table_nach_opl th:nth-child(4) { width: 13%; }
.table_nach_opl th:nth-child(5) { width: 20%; }
.table_nach_opl th:nth-child(6) { width: 9%; }


/*таблица вдго И Ч/СЕКТОР*/
.table_vdgo{      /*рамка для таблицы*/
    overflow-y: auto;
    width: 70%;
    border: 1px solid #1073b7;
    padding: 10px;
    border-radius: 8px;
    margin: 0 0 5px 0;
}
.table_vdgo h4 {    /*заголовок*/
    margin: 0px;
    color: #0952a0;
    margin-bottom: 5px;
}
.table_vdgo table{       /*сама таблица*/
    width: 100%;
    border-collapse: collapse;
}
.table_vdgo thead th {
    border: 1px solid #1073b7;
    background-color: #e4f0fb;
    font-size: 14px;
    font-weight: bold;
    text-align: center;
    vertical-align: middle;
    padding: 5px;
}
.table_vdgo td {
    padding: 8px;
    border: 1px solid #ddd;
    text-align: left;
    vertical-align: top;
}
.table_vdgo td:last-child {
    width: 60px;
    text-align: center;
}
.table_vdgo th:nth-child(1) { width: 5%; }
.table_vdgo th:nth-child(2) { width: 16%; }
.table_vdgo th:nth-child(3) { width: 12%; }
.table_vdgo th:nth-child(4) { width: 13%; }
.table_vdgo th:nth-child(5) { width: 20%; }
.table_vdgo th:nth-child(6) { width: 9%; }


/*таблица дата работ вдго*/
.table_obj{      /*рамка для таблицы*/
    overflow-y: auto;
    border: 1px solid #1073b7;
    padding: 10px;
    border-radius: 8px;
    margin: 0 0 5px 0;
    width: 30%;
}
.table_obj h4 {    /*заголовок*/
    margin: 0px;
    color: #0952a0;
    margin-bottom: 5px;
}
.table_obj table{       /*сама таблица*/
    width: 100%;
    border-collapse: collapse;
}
.table_obj thead th {
    border: 1px solid #1073b7;
    background-color: #e4f0fb;
    font-size: 14px;
    font-weight: bold;
    text-align: center;
    vertical-align: middle;
    padding: 5px;
}
.table_obj td {
    padding: 8px;
    border: 1px solid #ddd;
    text-align: left;
    vertical-align: top;
}
.table_obj td:last-child {
    width: 60px;
    text-align: center;
}

    </style>
"""
    html+=f"""
    <div class="tab">
        <button class="tablinks active" onclick="openTab(event, 'PersonalData')">Личные данные</button>
        <button class="tablinks" onclick="openTab(event, 'Equipment')">Оборудование</button>
    </div>

    <div id="PersonalData" class="tabcontent" style="display: block;">
        <div style="display: flex; justify-content: flex-start; align-items: flex-start; gap: 20px;">

            <!-- ЛЕВЫЙ СТОЛБЕЦ -->
            <div style="flex: 1; max-width: 40%;">
                <div class="personal_info">
                    <h3>Личные данные</h3>
                    <div style="font-size: 16px;">
                        <div style="display: flex; justify-content: flex-start; align-items: flex-start; gap: 20px;" >
                            <p style="margin: 0;"><strong>№ лицевого счета ГРО:</strong> {dog.get('айди', '-')}</p>
                            <p style="margin: 0;"><strong>№ лицевого счета РГК: </strong> {dog.get('РГК') if dog.get('РГК') and dog.get('РГК') != '-' else 'Не указан'}</p>
                        </div>
                        <p style="margin: 0;"><strong>№ ЕЛС: </strong> {dog.get('ЕЛС') if dog.get('ЕЛС') and dog.get('ЕЛС') != '-' else 'Не указан'}</p>
                        <p style="margin: 0;"><strong>ФИО заказчика:</strong> {dog.get('фио', '-')}</p>
                        <p style="margin: 0;"><strong>Адрес расположения оборудования:</strong> <br>{dog.get('адрес', '-')}, {dog.get('индекс', '-')}</p>
                        <p style="margin: 0;"><strong>Адрес проживания клиента:</strong> <br>{dog.get('адресклиента', '-')}, {dog.get('индекс', '-')}</p>
                        <p style="margin: 0;"><strong>Номер телефона:</strong> {dog.get('телефон') if dog.get('телефон') and dog.get('телефон') != '-' else 'Не указан'}</p>
                        <p style="margin: 0;"><strong>Адрес электронной почты:</strong> {dog.get('почта') if dog.get('почта') and dog.get('почта') != '-' and dog.get('почта') != 'не_указан' else 'Не указан'}</p>
                        <p style="margin: 0;"><strong>Подрядчик:</strong> {podryadchik}</p>
                        <p style="margin: 0;"><strong>Месяц обслуживания ВДГО:</strong> {mesobc_name}</p>
                    </div>
                </div>
            </div>

            <!-- ПРАВЫЙ СТОЛБЕЦ -->
            <div style="flex: 1; max-width: 70%;">
                <div class="table_dogs_for_klient">
                    <h3>Договоры клиента</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <thead>
                            <tr>
                                <th>ID договора</th>
                                <th>Номер договора</th>
                                <th>Дата договора</th>
                                <th>Тип</th>
                                <th>Статус</th>
                            </tr>
                        </thead>
                        <tbody>
                            {table_dogs_kl}
                        </tbody>
                    </table>
                </div>
            </div>

        </div>

        {all_tables_html}
        
    
    </div>

    <!-- ВКЛАДКА ОБОРУДОВАНИЕ -->
    <div id="Equipment" class="tabcontent">
        <div style="margin-bottom: 10px;">
            <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
                <input type="checkbox" id="actualOnlyCheckbox" onchange="applyFilter({dog.get('id_dog')})" {'checked' if actual_only == 1 else ''}>
                <strong>Только актуальное оборудование</strong>
            </label>
        </div>
        <div class="table_equipment">
            <table>
                <thead>
                    <tr>
                        <th>Оборудование</th>
                        <th>Доля</th>
                        <th>Кол-во</th>
                    </tr>
                </thead>
                <tbody>
                    {table_equipment}
                </tbody>
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
        town: str = "",
        street: str = "",
        house: str = "",
        flat: str = "",
        els: str = ""
):
    current_date = datetime.now().strftime('%d.%m.%Y')
    results = search_dog_ch(request, idklient, iddog, numdog, fio, town, street, house, flat, els)

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
                <td>{row.get('d_dog', '-').strftime('%d.%m.%Y') if row.get('d_dog') else '-'}</td>
                <td>{row.get('name_st', '-')}</td>
            </tr>
        """

    html = f"""
    <html>
    <head>
        <title style="font-size: 28px;">Результаты поиска</title>
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
                padding: 10px 20px;
                background-color: #1073b7;
                color: white;
                border: none;
                cursor: pointer;
                font-size: 16px;
                border-radius: 4px;
            }}
            .button-back:hover {{
                background: #0952a0;
            }}                
        </style>
    </head>
    <body>
        <div style="background: #e4f0fb; padding: 8px 15px; display: flex; justify-content: space-between; align-items: center;">
            <h1 style="color: #0952a0; margin: 0; font-size: 28px;">Результаты поиска</h1>
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

        <dialog id="contractDialog" style="width: 90%; height: 90%; border-radius: 8px; border: 2px solid #0952a0; padding: 0; padding: 0px; overflow: hidden; flex-direction: column;">
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px; background: #1073b7; border-radius: 6px 6px 0 0;">
                <h2 style="color: white; margin: 0; font-size: 22px;">Информация по клиенту на {current_date}</h2>
                <button onclick="closeContractDialog()" style="background: none; border: none; font-size: 22px; cursor: pointer; color: white;">✖</button>
            </div>
            <div id="contractDialogContent" style="padding: 10px; overflow-y: auto; max-height: calc(90vh - 50px);"></div>
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
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)
