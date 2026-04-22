import pyodbc
import winrm
import os
from datetime import datetime
import platform

CONTRACTS_BASE_PATH = os.environ.get('CONTRACTS_PATH', '/mnt/oblgaz/system/contracts_archive')
pyodbc.pooling = True

# подключение к бд
driver = '{ODBC Driver 17 for SQL Server}'
server = 'gazprosql'
database = 'tmp_dog'
connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection=yes'


# создает подключение к серверу от имени пользователя
def get_user_connection(request):
    user = request.session.get("user")
    if not user:
        return None

    conn_str = (
        f'DRIVER={driver};'
        f'SERVER={server};'
        f'DATABASE={database};'
        f'UID={user["login"]};'
        f'Trusted_Connection=yes;'
    )
    return pyodbc.connect(conn_str)


# функция вывода таблицы почастично ( первые 4000 клиентов. вторые 4000 клиентов и тд)
def get_clients_page(request, page: int = 1, page_size: int = 4000):
    try:
        connection = get_user_connection(request)
        if not connection:
            return []

        user = request.session.get("user")
        if not user:
            return []

        id_user = user.get("id_user")  # ← берём id_user

        cursor = connection.cursor()
        offset = (page - 1) * page_size

        cursor.execute(f"""
            SELECT 
                dog.id as 'ID договора', 
                dbo.dog_fGetNum(dog.id) as 'Номер договора',
                dog.n4 as '№ контрагента',
                dog.dd as 'Дата договора',
                klint.name as 'Контрагент', 
                dog.predmet as 'Предмет договора'
            FROM dog 
            LEFT JOIN klint ON dog.klient = klint.id
            LEFT JOIN dog_ident ON dog.kodpodr = dog_ident.otd 
                                OR dog_ident.opt <= 6 
                                OR dog.n2 = dog_ident.viddog
            WHERE dog.dohod = 3 AND dog_ident.id_user = ?
            ORDER BY dog.id
            OFFSET ? ROWS
            FETCH NEXT ? ROWS ONLY
        """, id_user, offset, page_size)

        columns = [column[0] for column in cursor.description]  # получение названия заголовков
        result = []  # создание списка

        for row in cursor.fetchall():  # fetchall - берет все строки. fetchone - получение первой строки
            row_dict = dict(zip(columns, row))  # zip(columns, row) получает сначала строку с заголовками, потом строку с его значением и соединяет их, а dict преобразует каждую такую строку в словарь типа  {'ID договора': 8001, '№ контрагента': '123', 'Дата начала': '2023-01-01', ...},
            result.append(row_dict)  # заносит результат в список

        cursor.close()
        connection.close()  # закрывается соединение
        return result  # возвращается результат

    except Exception as e:  # вывод ошибки и пустого списка в случае краха
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
        otd = user.get("otd")
        search_podr = otd if otd else 0
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
def get_total_count(request):
    try:
        connection = get_user_connection(request)
        if not connection:
            return 0

        user = request.session.get("user")
        if not user:
            return 0

        id_user = user.get("id_user")

        cursor = connection.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM dog 
            LEFT JOIN dog_ident ON dog.kodpodr = dog_ident.otd 
                                OR dog_ident.opt <= 6 
                                OR dog.n2 = dog_ident.viddog
            WHERE dog.dohod = 3 AND dog_ident.id_user = ?
        """, id_user)
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
        user = request.session.get("user")
        user_otd = user.get("otd")
        cursor.execute("SELECT kodpodr FROM dog WHERE id = ?", contract_id)
        row = cursor.fetchone()

        # если user_otd = 0 - разрешаем обновлять любые договоры
        # if not row or (user_otd != 0 and row[0] != user_otd):
        #   return False

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


# функция поиска 1 или несколько договоров после нажатия кнопки найти на диалоговом окне
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
            return []

        user = request.session.get("user")
        if not user:
            return []
        otd = user.get("otd")
        cursor = connection.cursor()

        if search_archive:
            sql = """
                SELECT 
                    dog.id as 'ID договора',
                    dbo.dog_fGetNum(dog.id) as 'Номер договора',
                    dog.n4 as '№ контрагента',
                    dog.dd as 'Дата договора',
                    klint.name as 'Контрагент', 
                    dog.predmet as 'Предмет договора',
                    dog.summa as 'Сумма договора'
                FROM dog
                LEFT JOIN klint ON dog.klient = klint.id
                LEFT JOIN dog_okz ON dog.id = dog_okz.id_dog
                WHERE 1=1

                UNION ALL

                SELECT 
                    dog.id as 'ID договора',
                    dbo.dog_fGetNum(dog.id) as 'Номер договора',
                    dog.n4 as '№ контрагента',
                    dog.dd as 'Дата договора',
                    klint.name as 'Контрагент', 
                    dog.predmet as 'Предмет договора',
                    dog.summa as 'Сумма договора'
                FROM dogarh dog
                LEFT JOIN klint ON dog.klient = klint.id
                LEFT JOIN dog_okz ON dog.id = dog_okz.id_dog
                WHERE 1=1
            """
        else:
            # щем только в основных договорах
            sql = """
                SELECT 
                    dog.id as 'ID договора',
                    dbo.dog_fGetNum(dog.id) as 'Номер договора',
                    dog.n4 as '№ контрагента',
                    dog.dd as 'Дата договора',
                    klint.name as 'Контрагент', 
                    dog.predmet as 'Предмет договора',
                    dog.summa as 'Сумма договора'
                FROM dog
                LEFT JOIN klint ON dog.klient = klint.id
                LEFT JOIN dog_okz ON dog.id = dog_okz.id_dog
                WHERE 1=1
            """

        params = []
        # подразделение (фильтр по отделу пользователя)
        if podr:
            search_podr = int(podr)
        elif otd:
            search_podr = otd
        else:
            search_podr = 0

        sql += " AND (dog.kodpodr = ? OR ? = 0)"
        params.append(search_podr)
        params.append(search_podr)

        # номер договора
        if numberdog:
            sql += " AND dbo.dog_fGetNum(dog.id) = ?"
            params.append(numberdog)

        # номер контрагента
        if numberkontr:
            sql += " AND dog.n4 LIKE ?"
            params.append(f'%{numberkontr}%')

        # дата с
        if date_from:
            sql += " AND dog.dd >= ?"
            params.append(date_from)

        # дата по
        if date_to:
            sql += " AND dog.dd <= ?"
            params.append(date_to)

        # сумма от
        if sum_from:
            sql += " AND dog.summa >= ?"
            params.append(float(sum_from))

        # сумма до
        if sum_to:
            sql += " AND dog.summa <= ?"
            params.append(float(sum_to))

        # предмет договора
        if pr_dog:
            sql += " AND dog.predmet LIKE ?"
            params.append(f'%{pr_dog}%')

        # нижегородоблгаз Сервис
        if gazsrv:
            sql += " AND dog.gazsrv = 1"

        # только подлежащие публикации (только если НЕ ищем в архиве)
        if publ and not search_archive:
            sql += " AND dog_okz.publ = 0 AND dog.eis = 1"

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
        print(f'Search error: {e}')
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


# проверка логина и пароля, выполнение команды на удаленном компе и возвращения true/false в результате, показывая подключилось или нет
def verify_windows_login(host, username, password):
    try:
        # создаем сессию с подключением через winrm с логином и паролем и протоколом ntlm (используется для проверки подлинности пользователей для доступа к ресурсам на windows компе)
        session = winrm.Session(
            f'http://{host}:5985/wsman',  # стандартный HTTP порт (5985) для управравления удаленным виндовс компом
            auth=(username, password),
            transport='ntlm'  # протокол
        )
        # пробуем выполнить команду 'hostname' для проверки - команда получения имени компьютера
        result = session.run_cmd('hostname')

        # если команда выполнилась без ошибок (код 0), значит аутентификация пройдена
        if result.status_code == 0:
            print(f"Успешный вход для {username}")
            return True
        else:
            print(f"Ошибка выполнения команды для {username}: {result.std_err.decode('cp866', errors='ignore')}")
            return False

    except winrm.exceptions.InvalidCredentialsError:
        print(f"Неверный логин или пароль для {username}")
        return False
    except Exception as e:
        # ловим любые другие ошибки
        print(f"Ошибка подключения для {username}: {e}")
        return False


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
        print(f"=== get_contract_files для договора {contract_num} ===")

        base_path = CONTRACTS_BASE_PATH
        contract_folder = os.path.join(base_path, str(contract_num))

        print(f"Ищем папку: {contract_folder}")

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
                print("✅ Подключение к БД установлено")
            else:
                print("❌ Нет подключения к БД")
        except Exception as e:
            print(f"❌ Ошибка подключения к БД: {e}")

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