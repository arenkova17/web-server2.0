"""
В этом файле database.py находятся функции с запросами к базе для получения/обновления/авторизации в программе
20-58 - подключение, авторизация
подключение к базе
подключние к tmp_dog
подключение к to_ch_dog
функция авторизации

81-776 строки - запросы для модуля Расходные договора и закупки
770-до конца - запросы для моделя Просмотр договоров с физ.лицами
"""


import pyodbc
import winrm
import os
from datetime import datetime

CONTRACTS_BASE_PATH = os.environ.get('CONTRACTS_PATH', '/mnt/oblgaz/system/contracts_archive')
pyodbc.pooling = False

# подключение к бд
driver = '{ODBC Driver 17 for SQL Server}'
server = 'gazprosql'
database = 'tmp_dog'
database_ch = 'to_ch_dog'
connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection=yes'

#подключение к базе tmp_dog
def get_user_connection(request):
    conn_str = (
        f'DRIVER={driver};'
        f'SERVER={server};'
        f'DATABASE={database};'
        f'Trusted_Connection=yes;'
    )
    return pyodbc.connect(conn_str)

#подключение к базе to_ch_dog
def get_user_connection_ch(request):
    conn_str = (
        f'DRIVER={driver};'
        f'SERVER={server};'
        f'DATABASE={database_ch};'
        f'Trusted_Connection=yes;'
    )
    return pyodbc.connect(conn_str)

#выбор ролей для админов и кассы - таблица с ролями админы/касса находится в to_ch_dog.user_roles_aren
def get_user_roles(request, username):
    try:
        conn = get_user_connection_ch(request)
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM user_roles_aren WHERE login = ?", username)
        roles = [row[0] for row in cursor.fetchall()]
        conn.close()
        return roles
    except Exception as e:
        print(f"Ошибка: {e}")
        return []

# функция вывода таблицы почастично ( первые 4000 клиентов. вторые 4000 клиентов и тд)
def get_clients_page(request, page: int = 1, page_size: int = 4000, pub: str = '1'):
    try:
        connection = get_user_connection(request)
        if not connection:
            return []

        user = request.session.get("user")
        if not user:
            return []

        id_user = user.get("id_user")

        cursor = connection.cursor()
        offset = (page - 1) * page_size

        # Базовый SQL
        sql = """
            SELECT 
                dog.id as 'ID договора', 
                dbo.dog_fGetNum(dog.id) as 'Номер договора',
                dog.n4 as '№ контрагента',
                CONVERT(varchar, dog.dd, 104) as 'Дата договора',
                klint.name as 'Контрагент', 
                dog.predmet as 'Предмет договора'
            FROM dog 
            LEFT JOIN klint ON dog.klient = klint.id
            LEFT JOIN dog_okz ON dog.id = dog_okz.id_dog
            LEFT JOIN dog_ident ON dog.kodpodr = dog_ident.otd 
                                OR dog_ident.opt <= 6 
                                OR dog.n2 = dog_ident.viddog
            WHERE dog.dohod = 3 AND dog_ident.id_user = ?
        """
        params = [id_user]

        if pub == '0':
            sql += " AND dog_okz.publ = 0 AND dog.eis = 1"

        sql += " ORDER BY dog.id OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
        params.extend([offset, page_size])

        cursor.execute(sql, params)

        columns = [column[0] for column in cursor.description]
        result = []

        for row in cursor.fetchall():
            result.append(dict(zip(columns, row)))

        cursor.close()
        connection.close()
        return result

    except Exception as e:
        print(f'Error in get_clients_page: {e}')
        return []

# функция для добычи одного договора по id, нужна для окошка с инфой клиента
def get_contract_id(request, contract_id: int):
    try:
        connection = get_user_connection(request)
        if not connection:
            print("Нет подключения к БД")
            return []

        user = request.session.get("user")
        if not user:
            print("Нет пользователя в сессии")
            return []

        cursor = connection.cursor()
        cursor.execute("""
            select 
                dog.id as 'ID договора',
                dbo.dog_fGetNum(dog.id) as '№ договора',
                n4 as '№ контрагента',
                dn as 'Дата начала',
                summa as 'Сумма договора',
                predmet as 'Предмет договора',
                dr as 'Дата регистрации',
                dd as 'Дата договора',
                spotd.namepodr as 'Подразделение',
                dk as 'Дата конца',
                klint.name as 'Наименование',
                klint.inn as 'ИНН',
                klint.rassh as 'Расч.счет',
                klint.bik as 'БИК',
                klint.KPP as 'КПП',
                klint.tel as 'Телефон/факс',
                dog.konk as 'Конкурс',

                dog.sposobzak as 'Способ закупки',
                dog.VIdZAK as 'Вид закупки',
                dog.numzak as 'Номер КЗ',
                dog.predlog as 'Формат закупки',
                dog.dat_docosznak as 'Дата основной закупки',
                dog.num_docosnzak as 'Номер основной закупки',
                dog.smsp as 'СМСП',
                dog.OSTNEKONZAK as 'Код основания',
                dog.okpd2 as 'ОКПД2',
                dog.subectzak as 'Субъектзак',

                dog_okz.num_z  as '№ закупки ЕИС', 
                dog_okz.num_z_el as '№ закупю на эл.пл.',
                dog_okz.pr_z as 'Прямая закупка',
                dog_okz.pr_z_osn as 'Основание',
                dog_okz.gpz as 'ГПЗ',
                dog.dog_uid as 'UID',
                dog_okz.ppz as 'ППЗ',

                dog.prol as 'Пролонгация',
                dog.beznds as 'Без НДС',
                klint.asbu as 'Код ОБД НСИ',
                dog.opl as 'Оплачено',
                dog.eis as 'Публикация в ЕИС',
                dog_status.name_st as 'СТАТУС',
                dog.d_end as 'Дата заверш. договора',

                dog_okz.s_dog_okz as 'Сумма договора ОКЗ',
                dog_okz.s_ds as 'Сумма с ДС',
                dog_okz.date_izv as 'Дата извещения', 
                dog_okz.agent as 'Агентский договор',
                dog_okz.smsp as 'Закупка среди СМСП',
                dog_okz.d_work as 'Рабочая дата',
                dog.predlog_txt as '№ предложения',
                dog.sysnum as 'Системный номер'

            from dog 
            left join klint on dog.klient = klint.id
            left join dog_okz on dog.id = dog_okz.id_dog
            inner join dog_status on dog.statusD  = dog_status.id_status
            left join spotd on dog.kodpodr = spotd.idpodr
             WHERE dog.id = ?
            """, contract_id)

        columns = [column[0] for column in cursor.description]
        row = cursor.fetchone()  # получение строки
        cursor.close()
        connection.close()
        # если строка получена, возвращаем её в виде {'id': 57, 'Дата начала': '2023-01-01', ...}
        if row:
            return dict(zip(columns, row))
        else:
            return None

    except Exception as e:
        print(f'Error: {e}')
        return None

# считает всех всех клиентов (нужно для просчета количества выводимых клиентов)
def get_total_count(request, pub: str = '1'):
    try:
        connection = get_user_connection(request)
        if not connection:
            return 0

        user = request.session.get("user")
        if not user:
            return 0

        id_user = user.get("id_user")

        sql = """
            SELECT COUNT(*) FROM dog 
            LEFT JOIN dog_okz ON dog.id = dog_okz.id_dog
            LEFT JOIN dog_ident ON dog.kodpodr = dog_ident.otd 
                                OR dog_ident.opt <= 6 
                                OR dog.n2 = dog_ident.viddog
            WHERE dog.dohod = 3 AND dog_ident.id_user = ?
        """
        params = [id_user]

        if pub == '0':
            sql += " AND dog_okz.publ = 0 AND dog.eis = 1"

        cursor = connection.cursor()
        cursor.execute(sql, params)
        count = cursor.fetchone()[0]

        cursor.close()
        connection.close()
        return count

    except Exception as e:
        print(f'Error in get_total_count: {e}')
        return 0

# обновление полей и чекбоксов
def update_par(request, contract_id: int, konk: int, prol: int, beznds: int, opl: int, eis: int, statusD: int,
               d_end: str, sposobzak: str, VIdZAK: int, numzak: str, predlog: int, dat_docosznak: str,
               num_docosnzak: int, smsp: str, OSTNEKONZAK: str, okpd2: str, subectzak: int, num_z: str, num_z_el: str,
               pr_z: int, pr_z_osn: str, gpz: str, uid: str, ppz: str, s_dog_okz: int, s_ds: int, date_izv: str,
               agent: int, smsp_okz: int, d_work: str, predlog_txt: str, publ: int = 0, publ_d: str = ''):
    try:
        connection = get_user_connection(request)
        if not connection:
            return []
        cursor = connection.cursor()
        cursor.execute("SELECT kodpodr FROM dog WHERE id = ?", contract_id)

        cursor.execute("""
            UPDATE dog 
            SET konk = ?,
            prol = ?,
            beznds = ?, 
            opl = ?, 
            eis = ?,
            statusD = ?,
            d_end = ?,

            sposobzak = ?,
            VIdZAK = ?,
            numzak = ?,
            predlog = ?,
            dat_docosznak = ?,
            num_docosnzak = ?,
            smsp = ?,
            OSTNEKONZAK = ?,
            okpd2 = ?,
            subectzak = ?, 

            predlog_txt = ?
            WHERE id = ?

        """, konk, prol, beznds, opl, eis, statusD, d_end, sposobzak, VIdZAK, numzak, predlog, dat_docosznak,
                       num_docosnzak, smsp, OSTNEKONZAK, okpd2, subectzak, predlog_txt, contract_id)

        cursor.execute("""
            UPDATE dog_okz 
            SET num_z = ?,
                num_z_el = ?,
                UID_dog_ = ?,
                pr_z = ?,
                pr_z_osn = ?,
                gpz = ?,
                ppz = ?,
                s_dog_okz = ?,
                s_ds = ?,
                date_izv = ?,
                agent = ?,
                d_work = ?,
                smsp = ?,
                publ = ?,
                publ_d = ?
            WHERE id_dog = ?
        """, num_z, num_z_el, uid, pr_z, pr_z_osn, gpz, ppz, s_dog_okz, s_ds, date_izv, agent, d_work, smsp_okz,
                       contract_id, publ, publ_d)

        connection.commit()
        cursor.close()
        connection.close()
        return True

    except Exception as e:
        print(f'Update error: {e}')
        return False


# функция поиска 1 или нескольких договоров после нажатия кнопки найти на диалоговом окне
def search_dog(request,
               numberdog: str = "",
               numberkontr: str = "",
               date_from: str = "",
               date_to: str = "",
               publ: str = "",
               sum_from: str = "",
               sum_to: str = "",
               podr: str = "",
               pr_dog: str = "",
               gazsrv: str = "",
               search_archive: str = ""
               ):
    try:
        connection = get_user_connection(request)
        if not connection:
            print("НЕТ ПОДКЛЮЧЕНИЯ К БД!")
            return []

        user = request.session.get("user")
        if not user:
            print("НЕТ ПОЛЬЗОВАТЕЛЯ В СЕССИИ!")
            return []

        cursor = connection.cursor()

        # Получаем id_user
        id_user = user.get("id_user")

        # Формируем базовый SQL в зависимости от архива
        if search_archive == '1':
            sql = """
                SELECT 
                    dog.id as 'ID договора',
                    dbo.dog_fGetNum(dog.id) as 'Номер договора',
                    dog.n4 as '№ контрагента',
                    dog.dd as 'Дата договора',
                    klint.name as 'Контрагент', 
                    dog.predmet as 'Предмет договора'
                FROM dog
                LEFT JOIN klint ON dog.klient = klint.id
                LEFT JOIN dog_okz ON dog.id = dog_okz.id_dog
                LEFT JOIN dog_ident ON dog.kodpodr = dog_ident.otd 
                                    OR dog_ident.opt <= 6 
                                    OR dog.n2 = dog_ident.viddog
                WHERE dog.dohod = 3
                    AND dog_ident.id_user = ?

                UNION ALL

                SELECT 
                    dog.id as 'ID договора',
                    dbo.dog_fGetNum(dog.id) as 'Номер договора',
                    dog.n4 as '№ контрагента',
                    dog.dd as 'Дата договора',
                    klint.name as 'Контрагент', 
                    dog.predmet as 'Предмет договора'
                FROM dogarh dog
                LEFT JOIN klint ON dog.klient = klint.id
                LEFT JOIN dog_okz ON dog.id = dog_okz.id_dog
                LEFT JOIN dog_ident ON dog.kodpodr = dog_ident.otd 
                                    OR dog_ident.opt <= 6 
                                    OR dog.n2 = dog_ident.viddog
                WHERE dog.dohod = 3
                    AND dog_ident.id_user = ?
            """
            params = [id_user, id_user]
        else:
            sql = """
                SELECT 
                    dog.id as 'ID договора',
                    dbo.dog_fGetNum(dog.id) as 'Номер договора',
                    dog.n4 as '№ контрагента',
                    dog.dd as 'Дата договора',
                    klint.name as 'Контрагент', 
                    dog.predmet as 'Предмет договора'
                FROM dog
                LEFT JOIN klint ON dog.klient = klint.id
                LEFT JOIN dog_okz ON dog.id = dog_okz.id_dog
                LEFT JOIN dog_ident ON dog.kodpodr = dog_ident.otd 
                                    OR dog_ident.opt <= 6 
                                    OR dog.n2 = dog_ident.viddog
                WHERE dog.dohod = 3
                    AND dog_ident.id_user = ?
            """
            params = [id_user]

        # Номер договора - поиск по ЛЮБОЙ части номера
        if numberdog:
            sql += "AND dog.n3 = ?"
            params.append(numberdog)

        # Номер контрагента
        if numberkontr:
            sql += " AND dog.n4 LIKE ?"
            params.append(f'%{numberkontr}%')

        # Дата с
        if date_from:
            sql += " AND dog.dd >= ?"
            params.append(date_from)

        # Дата по
        if date_to:
            sql += " AND dog.dd <= ?"
            params.append(date_to)

        # Сумма от
        if sum_from:
            try:
                sql += " AND dog.summa >= ?"
                params.append(float(sum_from))
            except ValueError:
                print(f"❌ Ошибка: сумма от '{sum_from}' не число")

        # Сумма до
        if sum_to:
            try:
                sql += " AND dog.summa <= ?"
                params.append(float(sum_to))
            except ValueError:
                print(f"❌ Ошибка: сумма до '{sum_to}' не число")

        # Предмет договора
        if pr_dog:
            sql += " AND dog.predmet LIKE ?"
            params.append(f'%{pr_dog}%')

        # Нижегородоблгаз Сервис
        if gazsrv == '1':
            sql += " AND dog.gazsrv = 1"

        # Только подлежащие публикации
        if publ and not search_archive:
            sql += " AND dog_okz.publ = 0 AND dog.eis = 1"

        # Сортировка
        sql += " ORDER BY dog.id"

        cursor.execute(sql, params)

        columns = [column[0] for column in cursor.description]
        result = []

        for row in cursor.fetchall():
            result.append(dict(zip(columns, row)))

        cursor.close()
        connection.close()
        return result

    except Exception as e:
        print(f'❌ Search error: {e}')
        import traceback
        traceback.print_exc()
        return []

# функция берёт результат процедуры (для таблицы оплат) - первая таблица
def get_dog_payments(request, contract_id: int):
    try:
        connection = get_user_connection(request)
        if not connection:
            return []
        cursor = connection.cursor()

        cursor.execute("EXEC dog_opl_proc ?", contract_id)

        columns = [column[0] for column in cursor.description]
        rows = cursor.fetchall()

        payments = []
        for row in rows:
            payment_dict = dict(zip(columns, row))
            payments.append(payment_dict)

        cursor.close()
        connection.close()
        return payments

    except Exception as e:
        print(f'Error getting payments: {e}')
        return []

# функция берёт процедуру dsproc для второй таблицы Дополнительные соглашения
def get_ds_data(request, contract_id: int):
    try:
        connection = get_user_connection(request)
        if not connection:
            return []
        cursor = connection.cursor()

        cursor.execute("EXEC dsproc ?", contract_id)

        columns = [column[0] for column in cursor.description]
        rows = cursor.fetchall()

        ds_data = []
        for row in rows:
            row_dict = dict(zip(columns, row))
            for key, value in row_dict.items():
                if value is None:
                    row_dict[key] = ''
            ds_data.append(row_dict)

        cursor.close()
        connection.close()
        return ds_data

    except Exception as e:
        print(f'Error getting ds data: {e}')
        return []

# функция берёт процедуру и вытаскивает результат процедуры (для таблицы оплат из 1C) - третья таблица
def get_dog_payments1С(request, contract_id: int):
    try:
        connection = get_user_connection(request)
        if not connection:
            return []
        cursor = connection.cursor()

        cursor.execute("EXEC dog_opl_l_proc ?", contract_id)

        columns = [column[0] for column in cursor.description]
        rows = cursor.fetchall()

        payments1C = []
        for row in rows:
            payment_dict = dict(zip(columns, row))
            payments1C.append(payment_dict)

        cursor.close()
        connection.close()
        return payments1C

    except Exception as e:
        print(f'Error getting payments: {e}')
        return []


# функция получения отдела зашедшего пользователя для того чтобы вывести только те договора которые относятся к его отделу
def get_user_otd(username: str):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("SELECT otd FROM dog_ident WHERE im_user = ?", username)
        row = cursor.fetchone()
        print(f"отдел из БД: {row[0] if row else None}")
        conn.close()
        # Если пользователя нет в БД - даем ему права видеть все отделы (0)
        return row[0] if row else 0
    except:
        return 0

def get_user_id(username: str):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("SELECT id_user FROM dog_ident WHERE im_user = ?", username)
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None
    except:
        return None

# функция добавления оплаты в таблицу
def add_dog_payment(request, contract_id: int, summa: float, date: str):
    try:
        connection = get_user_connection(request)
        cursor = connection.cursor()

        cursor.execute("SELECT klient FROM dog WHERE id = ?", contract_id)
        row = cursor.fetchone()
        if not row or not row[0]:
            print(f'Ошибка: не найден клиент для договора {contract_id}')
            return False

        klient_id = row[0]

        cursor.execute("""
            INSERT INTO dog_opl (id_dog, id_kl, s_opl, d_opl)
            VALUES (?, ?, ?, ?)
        """, contract_id, klient_id, summa, date)

        connection.commit()
        cursor.close()
        connection.close()
        return True
    except Exception as e:
        print(f'Error adding payment: {e}')
        return False

# функция удаления оплаты из таблицы
def delete_dog_payments(request, payment_ids: list):
    try:
        connection = get_user_connection(request)
        cursor = connection.cursor()

        placeholders = ','.join(['?'] * len(payment_ids))

        cursor.execute(f"""
            DELETE FROM dog_opl 
            WHERE id_opl IN ({placeholders})
        """, *payment_ids)

        connection.commit()
        cursor.close()
        connection.close()
        return True
    except Exception as e:
        print(f'Error deleting payments: {e}')
        return False


# взятие файлов договора из смонтированной папки
def get_contract_files(request, contract_num: str):
    try:
        base_path = CONTRACTS_BASE_PATH
        contract_folder = os.path.join(base_path, str(contract_num))

        if not os.path.exists(contract_folder):
            print(f"Папка не найдена: {contract_folder}")
            return []

        files = []

        # Проверяем подключение к БД
        connection = None
        cursor = None
        try:
            connection = get_user_connection(request)
            if connection:
                cursor = connection.cursor()
                print("Подключение к БД установлено")
            else:
                print("Нет подключения к БД")
        except Exception as e:
            print(f"Ошибка подключения к БД: {e}")

        for filename in os.listdir(contract_folder):
            file_path = os.path.join(contract_folder, filename)

            # Пропускаем папки
            if os.path.isdir(file_path):
                continue

            # Получаем информацию о файле
            file_stat = os.stat(file_path)

            # Парсим имя файла: {id}_{type}_{version}.pdf
            parts = filename.replace('.pdf', '').split('_')
            doc_type = parts[1] if len(parts) > 1 else '0'
            file_version = parts[2] if len(parts) > 2 else ''

            # Типы документов
            doc_types = {
                '1': 'Договор',
                '2': 'Лист согласования',
                '3': 'Дополнительные соглашения',
                '4': 'Расчет арендной платы',
                '5': 'Соглашение о расторжении',
                '6': 'Платежки',
                '7': 'Акт/накладная'
            }

            # Проверка публикации
            published = ''
            published_date = ''

            if cursor and contract_num and doc_type and file_version:
                try:
                    cursor.execute("""
                        SELECT date_publ FROM dog_file_p 
                        WHERE id_file = ? AND type_file = ? AND num_file = ?
                    """, contract_num, doc_type, file_version)
                    publ_row = cursor.fetchone()
                    if publ_row and publ_row[0]:
                        published = '1'
                        published_date = publ_row[0]
                        print(f"  📌 Файл {filename} - опубликован {published_date}")
                except Exception as e:
                    print(f"  ❌ Ошибка проверки публикации для {filename}: {e}")

            files.append({
                'filename': filename,
                'doc_type': doc_types.get(doc_type, 'Неизвестный тип'),
                'doc_type_code': doc_type,
                'size_kb': round(file_stat.st_size / 1024, 1),
                'created': datetime.fromtimestamp(file_stat.st_ctime).strftime('%d.%m.%Y'),
                'modified': datetime.fromtimestamp(file_stat.st_mtime).strftime('%d.%m.%Y'),
                'published': published,
                'published_date': published_date,
                'full_path': file_path
            })

        if cursor:
            cursor.close()
        if connection:
            connection.close()

        # Сортируем по дате создания (новые сверху)
        files.sort(key=lambda x: x['created'], reverse=True)
        print(f"Найдено файлов: {len(files)}")
        return files

    except Exception as e:
        print(f'Error getting contract files: {e}')
        import traceback
        traceback.print_exc()
        return []

# получение списка подразделений для поиска по договору
def get_podr_list(request):
    try:
        connection = get_user_connection(request)
        if not connection:
            return []

        cursor = connection.cursor()
        cursor.execute("""
            SELECT idpodr as id, namepodr as name 
            FROM spotd 
            ORDER BY namepodr
        """)
        result = []
        for row in cursor.fetchall():
            result.append({'id': row[0], 'name': row[1]})

        cursor.close()
        connection.close()
        return result
    except Exception as e:
        print(f'Error getting podr list: {e}')
        return []


#ЗАПРОСЫ ДЛЯ ВТОРОГО МОДУЛЯ ПРОГРАММЫ - ПРОСМОТР ДОГОВОРОВ
#для главной страницы всех договоров
def get_dogs_ch(request):
    try:
        connection = get_user_connection_ch(request)
        if not connection:
            return []

        user = request.session.get("user")
        user_id = user.get("id_user_ch") if user else None

        if not user_id:
            return []

        cursor = connection.cursor()

        cursor.execute("SELECT n1, n2 FROM to_ident WHERE id_user = ?", (user_id,))
        user_row = cursor.fetchone()

        if not user_row:
            return []

        user_n1, user_n2 = user_row[0], user_row[1]

        sql = """
            SELECT top 200 
                to_ch_dog_tab.id_dog,
                to_ch_dog_tab.id_klient,
                to_ch_klient.FIO,
                to_ch_addr_object.addr,
                to_ch_dog_tab.num_dog_txt,
                to_ch_type_dog.name_type,
                to_ch_dog_tab.d_dog,
                to_ch_status.name_st
            FROM to_ch_dog_tab
            INNER JOIN to_ch_type_dog ON to_ch_dog_tab.type_dog = to_ch_type_dog.id_type
            INNER JOIN to_ch_status ON to_ch_dog_tab.status = to_ch_status.id_status
            INNER JOIN to_ch_klient ON to_ch_dog_tab.id_klient = to_ch_klient.id_klient
            INNER JOIN to_slu ON to_ch_klient.idr = to_slu.id
            inner join to_ch_addr_object on to_ch_klient.id_object = to_ch_addr_object.id_obj 
            WHERE to_ch_dog_tab.d_dog <= GETDATE()
        """
        params = []

        if user_n1 != 0:
            sql += " AND to_slu.n1new = ?"
            params.append(user_n1)
        if user_n2 != 0:
            sql += " AND to_slu.n11new = ?"
            params.append(user_n2)

        sql += " ORDER BY to_ch_dog_tab.d_dog DESC"

        cursor.execute(sql, params)

        result = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

        cursor.close()
        connection.close()
        return result
    except Exception as e:
        print(f'Error in get_dogs_ch: {e}')
        return []

#ЛИЧНЫЕ ДАННЫЕ В ОКНЕ КЛИЕНТА
def get_dog_ch(request, id_dog: int):
    try:
        connection = get_user_connection_ch(request)
        if not connection: return []

        cursor = connection.cursor()
        cursor.execute("""
            select to_ch_dog_tab.id_dog, 
			to_ch_klient.id_object as объект,
			RGK.ls_negr AS РГК,
			ELS.els AS ЕЛС,
            to_ch_type_dog.name_type as типдог, 
            to_ch_dog_tab.d_dog as датадог, 
            to_ch_status.name_st,
            to_ch_klient.FIO as фио, 
            to_ch_klient.telefon as телефон,
            to_ch_klient.email as почта, 
            to_ch_klient.id_klient as айди,
            to_ch_addr_object.addr as адрес,
            to_ch_addr_object.addr_home as адресклиента,
            to_ch_dog_tab.id_klient, 
            to_ch_klient.m_vdgo as месобс,
            to_ch_klient.postob as индекс,
            to_ch_dog_tab.num_dog_txt as номердог
            from to_ch_dog_tab
            inner join to_ch_type_dog on to_ch_dog_tab.type_dog = to_ch_type_dog.id_type
            inner join to_ch_status on to_ch_dog_tab.status = to_ch_status.id_status
            inner join to_ch_klient on to_ch_dog_tab.id_klient = to_ch_klient.id_klient 
            inner join to_ch_addr_object on to_ch_klient.id_object = to_ch_addr_object.id_obj 
			left join (select MAX(ls_negr) as ls_negr, id_object from vdg_object_negr where valid = 1 group by id_object) RGK on to_ch_klient.id_object = RGK.id_object
            left join (select els, id_klient from to_ch_kl_els where no_use = 0) ELS on to_ch_klient.id_klient = ELS.id_klient 
			where to_ch_dog_tab.id_dog = ?
            order by d_dog desc
        """, id_dog)
        columns = [column[0] for column in cursor.description]
        row = cursor.fetchone()
        cursor.close()
        connection.close()
        if row:  return dict(zip(columns, row))
        else:    return None
    except Exception as e:
        print(f'Error in get_dog_ch: {e}')
        return None

#ДОГОВОРЫ КЛИЕНТА
def dogs_for_klient(request, id_klient: int):
    try:
        connection = get_user_connection_ch(request)
        if not connection: return []
        cursor = connection.cursor()
        cursor.execute("""
            select to_ch_dog_tab.id_dog , 
            to_ch_dog_tab.num_dog_txt, 
            to_ch_dog_tab.d_dog, 
            to_ch_type_dog.name_type, 
            to_ch_status.name_st, 
            to_ch_dog_tab.saldo_now
            from to_ch_dog_tab
            inner join to_ch_type_dog on to_ch_dog_tab.type_dog = to_ch_type_dog.id_type 
            inner join to_ch_status on to_ch_dog_tab.status = to_ch_status.id_status
            where to_ch_dog_tab.id_klient = ?
        """, id_klient)
        result = []
        columns = [column[0] for column in cursor.description]
        rows = cursor.fetchall()
        for row in rows:
            row_dict = dict(zip(columns, row))
            result.append(row_dict)
        cursor.close()
        connection.close()
        return result
    except Exception as e:
        print(f'Error in dogs_for_klient:{e}')
        return []


#таблица для получания начислений и оплат для ТО+АДО
def get_tabl_for_TOADO(request, id_dog: int):
    try:
        connection = get_user_connection_ch(request)
        if not connection:
            return []

        cursor = connection.cursor()

        cursor.execute("""
            with base as (
                select 
                    to_ch_dog_tab2.id_dog as id_dog,
                    year(to_ch_dog_tab2.dat_n) as god,
                    isnull(nach.nach400, 0) as nach400,
                    isnull(nach.nach1431, 0) as nach1431,
                    isnull(nach.nach400, 0) + isnull(nach.nach1431, 0) as summanach,
                    opl.s as s,
                    opl.dn as dn,
                    row_number() over (partition by year(to_ch_dog_tab2.dat_n) order by opl.dn) as rn
                from to_ch_dog_tab2
                left join (
                    select 
                        id_dog, 
                        god,
                        sum(case when kod_wrk = 411 then s_nds else 0 end) as nach400,
                        sum(case when kod_wrk = 1431 then s_nds else 0 end) as nach1431
                    from to_ch_tabl_nach
                    group by id_dog, god
                ) nach on to_ch_dog_tab2.id_dog = nach.id_dog and year(to_ch_dog_tab2.dat_n) = nach.god
                left join (
                    select id_dog, dn, s
                    from to_ch_work
                ) opl on to_ch_dog_tab2.id_dog = opl.id_dog and year(to_ch_dog_tab2.dat_n) = year(opl.dn)
                where to_ch_dog_tab2.id_dog = ?
            )
            
            select 
                cast(id_dog as varchar) as id_dog,
                cast(god as varchar) as god, 
                cast(case when rn = 1 then nach400 else null end as varchar) as nach400,
                cast(case when rn = 1 then nach1431 else null end as varchar) as nach1431,
                cast(case when rn = 1 then summanach else null end as varchar) as summanach,
                cast(s as varchar) as s,
                convert(varchar, dn, 104) as dn,
                0 as sort_order,
                case when god = '' then 0 else god end as god_sort
            from base
            
            union all
            
            --ИТОГОВАЯ СТРОКА (суммируем только строки с rn = 1)
            select 
                'ИТОГО:',
                '',
                cast(sum(case when rn = 1 then nach400 else 0 end) as varchar),
                cast(sum(case when rn = 1 then nach1431 else 0 end) as varchar),
                cast(sum(case when rn = 1 then summanach else 0 end) as varchar),
                cast(sum(s) as varchar),
                cast(sum(case when rn = 1 then summanach else 0 end) - sum(s) as varchar) as saldo,
                1 as sort_order,
                0 as god_sort
            from base
            
            order by sort_order, god_sort
        """, (id_dog))

        columns = [column[0] for column in cursor.description]
        result = []
        for row in cursor.fetchall():
            result.append(dict(zip(columns, row)))

        cursor.close()
        connection.close()
        return result

    except Exception as e:
        print(f'Error in get_tabl_for_TOADO: {e}')
        return []


#ЗАПРОС НА ВЫВОД ТАБЛИЦЫ ВДГО 100%/ФАКТ/(СТАР.)
def get_tabl_for_VDGO(request, id_dog: int):
    try:
        connection = get_user_connection_ch(request)
        if not connection:
            return []

        cursor = connection.cursor()

        cursor.execute("""
            with base as (
                select 
                    to_ch_dog_tab2.id_dog, 
                    convert(varchar, dat_n, 104) + '-' + convert(varchar, dat_k, 104) as period, 
                    isnull(nach.nach500, 0) as nach500, 
                    opl.s as opl,
                    convert(varchar, dn, 104) as dn,
                    row_number() over (partition by year(to_ch_dog_tab2.dat_n) order by opl.dn) as rn
                from to_ch_dog_tab2
                left join (
                    select 
                        id_dog, 
                        god, 
                        sum(case when kod_wrk = 522 then s_nds else 0 end) as nach500
                    from to_ch_tabl_nach
                    group by id_dog, god
                ) nach on to_ch_dog_tab2.id_dog = nach.id_dog and year(to_ch_dog_tab2.dat_n) = nach.god
                left join (
                    select id_dog, dn, s
                    from to_ch_work
                ) opl on to_ch_dog_tab2.id_dog = opl.id_dog and year(to_ch_dog_tab2.dat_n) = year(opl.dn)
                where to_ch_dog_tab2.id_dog = ?
            )
            
            select 
                cast(id_dog as varchar) as id_dog,
                period,
                cast(case when rn = 1 then nach500 else null end as varchar) as nach500,
                cast(opl as varchar) as opl, 
                dn,
                rn
            from base
            
            union all
            
            -- ИТОГОВАЯ СТРОКА
            select 
                'ИТОГО:',
                '',
                cast(sum(case when rn = 1 then nach500 else 0 end) as varchar),
                cast(sum(opl) as varchar),
                cast(sum(case when rn = 1 then nach500 else 0 end) - sum(opl) as varchar),
                ''
            from base
        """, (id_dog))

        columns = [column[0] for column in cursor.description]
        result = []
        for row in cursor.fetchall():
            result.append(dict(zip(columns, row)))

        cursor.close()
        connection.close()
        return result

    except Exception as e:
        print(f'Error in get_tabl_for_VDGO: {e}')
        return []

#ЗАПРОС НА ВЫВОД ТАБЛИЦЫ ЧАСТНЫЙ СЕКТОР
def get_tabl_for_CHSEK(request, id_dog: int):
    try:
        connection = get_user_connection_ch(request)
        if not connection:
            return []

        cursor = connection.cursor()

        cursor.execute("""
            with base as(
                select 
                    to_ch_dog_tab2.id_dog as id_dog, 
                    CONVERT(varchar, to_ch_dog_tab2.dat_n, 104) + '-' + CONVERT(varchar, to_ch_dog_tab2.dat_k, 104) as period,
                    nach.nach400 as nach400,
                    nach.nach1431 as nach1431,
                    nach.nach500 as nach500, 
                    nach.nach400 + nach.nach500 + nach.nach1431 as summanach,
                    opl.s as opl,
                    convert(varchar, opl.dn, 104) as dn,
                    row_number() over (partition by year(to_ch_dog_tab2.dat_n) order by opl.dn) as rn
                from to_ch_dog_tab2 
                left join (
                    select 
                        id_dog, 
                        god, 
                        sum(case when kod_wrk in (411,444) then s_nds else 0 end) as nach400,
                        sum(case when kod_wrk = 1431 then s_nds else 0 end) as nach1431,
                        sum(case when kod_wrk in (521) then s_nds else 0 end) as nach500
                    from to_ch_tabl_nach
                    group by id_dog, god
                ) nach on to_ch_dog_tab2.id_dog = nach.id_dog and YEAR(to_ch_dog_tab2.dat_n) = nach.god
                left join (
                    select id_dog, dn, s from to_ch_work) opl on to_ch_dog_tab2.id_dog = opl.id_dog and year(to_ch_dog_tab2.dat_n) = year(opl.dn)
                where to_ch_dog_tab2.id_dog = ?)
            
            select id_dog, 
            period,
            cast(case when rn = 1 then nach400 else 0 end as varchar) as nach400,
            cast(case when rn = 1 then nach1431 else 0 end  as varchar) as nach1431,
            cast(case when rn = 1 then nach500 else 0 end as varchar) as nach500, 
            cast(case when rn = 1 then summanach else 0 end as varchar) as summanach,
            cast(opl as varchar) as opl,
            dn
            from base 
            
            union all 
            
            select 
            'ИТОГО:',
            '',
            cast(SUM(case when rn = 1 then nach400 else 0 end) as varchar), 
            cast(SUM(case when rn = 1 then nach1431 else 0 end) as varchar), 
            cast(SUM(case when rn = 1 then nach500 else 0 end) as varchar),
            cast(SUM(case when rn = 1 then summanach else 0 end) as varchar), 
            cast(SUM(opl) as varchar),
            cast((sum(case when rn = 1 then summanach else 0 end) - sum(opl)) as varchar) as saldo
            from base
        """, (id_dog))

        columns = [column[0] for column in cursor.description]
        result = []
        for row in cursor.fetchall():
            result.append(dict(zip(columns, row)))

        cursor.close()
        connection.close()
        return result

    except Exception as e:
        print(f'Error in get_tabl_for_VDGO: {e}')
        return []



#ВЫВОД РЕЗУЛЬТАТОВ ПОСЛЕ ПОИСКА
def search_dog_ch(request, idklient: str = "", iddog: str = "", numdog: str = "", fio: str = "", town: str = "", street: str = "",
                  house: str = "", flat: str = "", els: str = ""):
    try:
        connection = get_user_connection_ch(request)
        if not connection:
            return []

        cursor = connection.cursor()
        sql = """
            select top(200) to_ch_dog_tab.id_dog, 
            to_ch_klient.id_klient,
            to_ch_klient.FIO,
            to_ch_addr_object.addr,
            to_ch_type_dog.name_type, 
            to_ch_dog_tab.num_dog_txt, 
            to_ch_dog_tab.d_dog, 
            to_ch_status.name_st
            from to_ch_dog_tab
            inner join to_ch_type_dog on to_ch_dog_tab.type_dog = to_ch_type_dog.id_type
            inner join to_ch_status on to_ch_dog_tab.status = to_ch_status.id_status
            inner join to_ch_klient on to_ch_dog_tab.id_klient = to_ch_klient.id_klient
            inner join to_ch_addr_object on to_ch_klient.id_object = to_ch_addr_object.id_obj 
            left join to_ch_kl_els on to_ch_klient.id_klient = to_ch_kl_els.id_klient
            where 1=1 and d_dog <= GETDATE()
        """
        params = []

        if idklient:
            sql += " AND to_ch_klient.id_klient = ?"
            params.append(idklient)
        if iddog:
            sql += " AND to_ch_dog_tab.id_dog = ?"
            params.append(iddog)
        if numdog:
            sql += " AND to_ch_dog_tab.num_dog_txt LIKE ?"
            params.append(f'%{numdog}%')
        if fio:
            fio = fio.strip()
            sql += " AND LOWER(to_ch_klient.FIO) LIKE ?"
            params.append(f'%{fio.lower()}%')
        if town:
            town = town.strip()
            sql += " AND LOWER(to_ch_addr_object.addr) LIKE ?"
            params.append(f'%{town.lower()}%')
        if street:
            street = street.strip()
            sql += " AND LOWER(to_ch_addr_object.addr) LIKE ?"
            params.append(f'%{street.lower()}%')
        if house:
            house = house.strip()
            sql += " AND to_ch_addr_object.addr LIKE ?"
            params.append(f'%{house.lower()}%')
        if flat:
            flat = flat.strip()
            sql += " AND to_ch_addr_object.addr LIKE ?"
            params.append(f'%{flat.lower()}%')
        if els:
            sql += " AND to_ch_kl_els.els LIKE ?"
            params.append(f'%{els}%')


        cursor.execute(sql, params)

        columns = [column[0] for column in cursor.description]
        result = []
        for row in cursor.fetchall():
            result.append(dict(zip(columns, row)))

        cursor.close()
        connection.close()
        return result

    except Exception as e:
        print(f'Error in search_dog_ch: {e}')
        return []



#ПОДРЯДЧИК
def get_podryadchik(request, id_klient: int):
    try:
        connection = get_user_connection_ch(request)
        if not connection:
            return ''

        cursor = connection.cursor()
        cursor.execute("""
          select name_org
          from vdg_podryad
          inner join vdg_home_podr on vdg_podryad.id_p = vdg_home_podr.id_podr
          inner join to_ch_klient on vdg_home_podr.id_home = to_ch_klient.id_home
          where id_klient = ? and vdg_home_podr.god = YEAR(GETDATE()) and valid = 1 AND active = 1
        """, (id_klient,))

        row = cursor.fetchone()
        cursor.close()
        connection.close()

        return row[0] if row and row[0] else 'Нет'

    except Exception as e:
        print(f'Error in get_podryadchik: {e}')
        return 'Ошибка'

#АКТУАЛЬНОЕ ОБОРУДОВНАИЕ
def get_actual_equipment(request, id_klient: str, actual_only: int = 1):
    try:
        connection = get_user_connection_ch(request)
        if not connection:
            return []

        cursor = connection.cursor()

        sql = """
            SELECT name_ob, 
                name_izg,
                name_model, 
                kol_oborud, 
                dol_ob, 
                du, 
                do, 
                id_kl,
                to_ch_ob.id_ob
            FROM to_ch_story 
            INNER JOIN to_ch_klient ON to_ch_story.id_obj = to_ch_klient.id_object
            INNER JOIN to_ch_ob ON to_ch_story.id_ob = to_ch_ob.id_ob 
            LEFT JOIN vdg_izg ON to_ch_story.id_izg = vdg_izg.id_izg
            LEFT JOIN vdg_model ON to_ch_story.id_model = vdg_model.id_model
            WHERE to_ch_klient.id_klient = ?
                AND name_ob NOT LIKE '(МОП)%'
        """
        params = [id_klient]

        if actual_only == 1:
            from datetime import datetime
            current_year = datetime.now().year
            sql += " AND (YEAR(du) <= ? AND YEAR(do) >= ?)"
            params.append(current_year)
            params.append(current_year)

        sql += " order by du"

        cursor.execute(sql, params)

        columns = [column[0] for column in cursor.description]
        rows = cursor.fetchall()
        result = []
        for row in rows:
            row_dict = dict(zip(columns, row))
            if row_dict.get('du'):
                row_dict['du'] = row_dict['du'].strftime('%Y-%m-%d')
            if row_dict.get('do'):
                row_dict['do'] = row_dict['do'].strftime('%Y-%m-%d')
            result.append(row_dict)

        cursor.close()
        connection.close()
        return result

    except Exception as e:
        print(f'Error in get_actual_equipment: {e}')
        return []

#ищет есть ли юзер в to_ident
def get_user_id_ch(username: str):
    try:
        connection_string_ch = f'DRIVER={driver};SERVER={server};DATABASE=to_ch_dog;Trusted_Connection=yes'
        conn = pyodbc.connect(connection_string_ch)
        cursor = conn.cursor()
        cursor.execute("SELECT id_user FROM to_ident WHERE im = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None
    except Exception as e:
        print(f'Error in get_user_id_ch: {e}')
        return None

#ДАТА ОБСЛУЖИВАНИЯ ВДГО ПО ДОГОВОРУ
def obj_for_dog(request, id_dog: int):
    try:
        connection = get_user_connection_ch(request)
        if not connection:
            return []

        cursor = connection.cursor()
        cursor.execute("""
            select distinct 
                to_ch_klient.id_klient,
                to_ch_klient.FIO,
                to_ch_klient.id_object,
                to_ch_dog_tab.id_dog,
                vdg_obj_work.date_action
            from vdg_obj_work
            inner join to_ch_klient on vdg_obj_work.id_object = to_ch_klient.id_object
            inner join to_ch_dog_tab on to_ch_klient.id_klient = to_ch_dog_tab.id_klient
            where to_ch_dog_tab.id_dog = ?
                and vdg_obj_work.type_action = 10
                and exists (
                    select 1
                    from to_ch_tabl_nach
                    where to_ch_tabl_nach.id_dog = to_ch_dog_tab.id_dog
                )
        """, (id_dog))

        result = []
        columns = [column[0] for column in cursor.description]
        rows = cursor.fetchall()
        for row in rows:
            row_dict = dict(zip(columns, row))
            result.append(row_dict)

        cursor.close()
        connection.close()
        return result
    except Exception as e:
        print(f'Error in obj_for_dog: {e}')
        return []






