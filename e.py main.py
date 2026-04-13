[1mdiff --git a/.gitignore b/.gitignore[m
[1mnew file mode 100644[m
[1mindex 0000000..93a7dfe[m
[1m--- /dev/null[m
[1m+++ b/.gitignore[m
[36m@@ -0,0 +1,15 @@[m
[32m+[m[32m__pycache__/[m
[32m+[m[32m*.pyc[m
[32m+[m[32m*.pyo[m
[32m+[m[32m*.pyd[m
[32m+[m[32m.venv/[m
[32m+[m[32mvenv/[m
[32m+[m[32menv/[m
[32m+[m[32m.Python[m
[32m+[m[32m*.so[m
[32m+[m[32m*.egg[m
[32m+[m[32m*.egg-info/[m
[32m+[m[32mdist/[m
[32m+[m[32mbuild/[m
[32m+[m[32m.vscode/[m
[32m+[m[32m.idea/[m
[1mdiff --git a/database.py b/database.py[m
[1mindex 8eee70b..9dc9f2e 100644[m
[1m--- a/database.py[m
[1m+++ b/database.py[m
[36m@@ -27,7 +27,15 @@[m [mdef get_clients_page(request, page: int = 1, page_size: int = 4000):[m
     try:[m
         connection = get_user_connection(request)[m
         if not connection:[m
[32m+[m[32m            print("Нет соединения с БД")[m
             return [][m
[32m+[m
[32m+[m[32m        user = request.session.get("user")[m
[32m+[m[32m        if not user:[m
[32m+[m[32m            print("Нет пользователя в сессии")[m
[32m+[m[32m            return [][m
[32m+[m[32m        otd = user.get("otd")[m
[32m+[m
         cursor = connection.cursor()  # курсор для выполнения sql запросов[m
 [m
         # Рассчитываем offset (колво строк которые будем пропускать)[m
[36m@@ -43,10 +51,11 @@[m [mdef get_clients_page(request, page: int = 1, page_size: int = 4000):[m
                 dog.predmet as 'Предмет договора'[m
             FROM dog [m
             left join klint on dog.klient = klint.id[m
[32m+[m[32m            WHERE dog.kodpodr = ?[m
             ORDER BY dog.id[m
[31m-            OFFSET {offset} ROWS[m
[31m-            FETCH NEXT {page_size} ROWS ONLY[m
[31m-        """)[m
[32m+[m[32m            OFFSET ? ROWS[m
[32m+[m[32m            FETCH NEXT ? ROWS ONLY[m
[32m+[m[32m        """, otd, offset, page_size)[m
 [m
         columns = [column[0] for column in cursor.description]  # получение названия заголовков[m
         result = []  # создание списка[m
[36m@@ -71,6 +80,11 @@[m [mdef get_contract_id(request, contract_id: int):[m
         connection = get_user_connection(request)[m
         if not connection:[m
             return [][m
[32m+[m
[32m+[m[32m        user = request.session.get("user")[m
[32m+[m[32m        if not user:[m
[32m+[m[32m            return [][m
[32m+[m[32m        otd = user.get("otd")[m
         cursor = connection.cursor()[m
         cursor.execute("""[m
             select [m
[36m@@ -122,8 +136,8 @@[m [mdef get_contract_id(request, contract_id: int):[m
             left join klint on dog.klient = klint.id[m
             left join dog_okz on dog.id = dog_okz.id_dog[m
             inner join dog_status on dog.statusD  = dog_status.id_status[m
[31m-            where dog.id = ?[m
[31m-        """, contract_id)[m
[32m+[m[32m            WHERE dog.id = ? AND dog.kodpodr = ?[m
[32m+[m[32m        """, contract_id, otd)[m
 [m
         columns = [column[0] for column in cursor.description][m
         row = cursor.fetchone()  # получение строки[m
[36m@@ -146,9 +160,15 @@[m [mdef get_total_count(request):[m
         connection = get_user_connection(request)[m
         if not connection:[m
             return [][m
[32m+[m
[32m+[m[32m        user = request.session.get("user")  # получаем пользователя[m
[32m+[m[32m        if not user:[m
[32m+[m[32m            return 0[m
[32m+[m[32m        otd = user.get("otd")[m
[32m+[m
         cursor = connection.cursor()[m
 [m
[31m-        cursor.execute("SELECT COUNT(*) FROM dog")  # подсчет количества строк в таблице[m
[32m+[m[32m        cursor.execute("SELECT COUNT(*) FROM dog WHERE kodpodr = ?", otd)  # подсчет количества строк в таблице[m
         count = cursor.fetchone()[0]  # выводит первой строк - цифры количества строк[m
 [m
         cursor.close()[m
[36m@@ -170,6 +190,13 @@[m [mdef update_par(request, contract_id: int, konk: int, prol: int, beznds: int, opl[m
             return [][m
         cursor = connection.cursor()[m
 [m
[32m+[m[32m        user = request.session.get("user")[m
[32m+[m[32m        user_otd = user.get("otd")[m
[32m+[m[32m        cursor.execute("SELECT kodpodr FROM dog WHERE id = ?", contract_id)[m
[32m+[m[32m        row = cursor.fetchone()[m
[32m+[m[32m        if not row or row[0] != user_otd:[m
[32m+[m[32m            return False  # договор чужой — не обновляем[m
[32m+[m
         cursor.execute("""[m
             UPDATE dog [m
             SET konk = ?,[m
[36m@@ -222,6 +249,11 @@[m [mdef search_dog(request, numberdog: str = "", numberkontr: str = ""):[m
         connection = get_user_connection(request)[m
         if not connection:[m
             return [][m
[32m+[m
[32m+[m[32m        user = request.session.get("user")[m
[32m+[m[32m        if not user:[m
[32m+[m[32m            return [][m
[32m+[m[32m        otd = user.get("otd")[m
         cursor = connection.cursor()[m
 [m
         if numberdog and numberkontr:[m
[36m@@ -237,8 +269,9 @@[m [mdef search_dog(request, numberdog: str = "", numberkontr: str = ""):[m
                 LEFT JOIN klint ON dog.klient = klint.id[m
                 WHERE dbo.dog_fGetNum(dog.id) = ? [m
                   AND dog.n4 LIKE ?[m
[32m+[m[32m                  AND dog.kodpodr = ?[m
                 ORDER BY dog.id[m
[31m-            """, numberdog, f'%{numberkontr}%')[m
[32m+[m[32m            """, numberdog, f'%{numberkontr}%', otd)[m
 [m
         elif numberdog:[m
             cursor.execute("""[m
[36m@@ -252,8 +285,9 @@[m [mdef search_dog(request, numberdog: str = "", numberkontr: str = ""):[m
                 FROM dog[m
                 LEFT JOIN klint ON dog.klient = klint.id[m
                 WHERE dbo.dog_fGetNum(dog.id) = ?[m
[32m+[m[32m                AND dog.kodpodr = ?[m
                 ORDER BY dog.id[m
[31m-            """, numberdog)[m
[32m+[m[32m            """, numberdog, otd)[m
 [m
         elif numberkontr:[m
             cursor.execute("""[m
[36m@@ -267,8 +301,9 @@[m [mdef search_dog(request, numberdog: str = "", numberkontr: str = ""):[m
                 FROM dog[m
                 LEFT JOIN klint ON dog.klient = klint.id[m
                 WHERE n4 like ?[m
[32m+[m[32m                AND dog.kodpodr = ?[m
                 ORDER BY dog.id[m
[31m-            """, f'%{numberkontr}%')[m
[32m+[m[32m            """, f'%{numberkontr}%', otd)[m
 [m
         else:[m
             # Ничего не указано[m
[36m@@ -323,8 +358,8 @@[m [mdef verify_windows_login(host, username, password):[m
         session = winrm.Session([m
             f'http://{host}:5985/wsman', #стандартный HTTP порт (5985) для управравления удаленным виндовс компом[m
             auth=(username, password),[m
[31m-            transport='ntlm'   #протокол[m
[31m-        )[m
[32m+[m[32m            transport='ntlm'  #протокол[m
[32m+[m[32m       )[m
         #пробуем выполнить команду 'hostname' для проверки - команда получения имени компьютера[m
         result = session.run_cmd('hostname')[m
 [m
[36m@@ -344,14 +379,56 @@[m [mdef verify_windows_login(host, username, password):[m
         print(f"Ошибка подключения для {username}: {e}")[m
         return False[m
 [m
[32m+[m
 #функция получения отдела зашедшего пользователя для того чтобы вывести только те договора которые относятся к его отделу[m
 def get_us