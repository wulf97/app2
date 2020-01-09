from flask import Flask
from flask import request
from flask import render_template
from flask import redirect
from flask import session
from flask import url_for

import psycopg2
from psycopg2.extras import DictCursor

from dbconfig import dbconfig
from user import Student
from forms import *

app = Flask(__name__)
app.secret_key = 'key'

# **********************************************************
# Главная страница
@app.route('/', methods = ['GET', 'POST'])
@app.route('/index')
def index():
	rec = []
	form = []

	if not session.get('acc_type'):
		return redirect(url_for('login'))

	conn = psycopg2.connect(dbname = dbconfig['dbname'],
							user = dbconfig['user'],
							password = dbconfig['password'],
							host = dbconfig['host'])
	cursor = conn.cursor()

	if request.args.get('act', '') == 'my_schedule':
		if session['acc_type'] == 1:
			sql = '''select "group_number" from "student" where "user_id" = '{}' '''.format(session['id'])
			cursor.execute(sql)
			group_number  = cursor.fetchone()[0]
			print(group_number)

			sql = '''select ttt1."day_of_the_week", ttt1."serial_number", ttt1."subject_type", ttt1."audience_number", ttt1."name" "sub_name", ttt2."name", ttt2."surname", ttt2."patronymic"  from'''
			sql += '''(select * from'''
			sql += '''(select * from'''
			sql += '''"lesson" t1 inner join "group_lesson" t2 '''
			sql += '''on t1."id" = t2."lesson_id"'''
			sql += '''where "group_number" = '{}') '''.format(group_number)
			sql += '''tt1 inner join "subject_in_the_curriculum" tt2 '''
			sql += '''on tt1."subject_id" = tt2."id") '''
			sql += '''ttt1 inner join "user" ttt2 '''
			sql += '''on ttt1."teacher_id" = ttt2."id" '''
			sql += '''order by "day_of_the_week", "serial_number" asc'''
			cursor.execute(sql)
			rec = cursor.fetchall()
			print(rec)
		elif session['acc_type'] == 2:
			sql = '''select ttt1."day_of_the_week", ttt1."serial_number", ttt1."subject_type", ttt1."audience_number", ttt1."name" "sub_name", ttt2."name", ttt2."surname", ttt2."patronymic"  from'''
			sql += '''(select * from'''
			sql += '''(select * from'''
			sql += '''"lesson" t1 inner join "group_lesson" t2 '''
			sql += '''on t1."id" = t2."lesson_id")'''
			sql += '''tt1 inner join "subject_in_the_curriculum" tt2 '''
			sql += '''on tt1."subject_id" = tt2."id") '''
			sql += '''ttt1 inner join "user" ttt2 '''
			sql += '''on ttt1."teacher_id" = ttt2."id" '''
			sql += '''where ttt1."teacher_id" = '{}' '''.format(session['id'])
			sql += '''order by "day_of_the_week", "serial_number" asc'''
			cursor.execute(sql)
			rec = cursor.fetchall()

	elif request.args.get('act', '') == 'group_schedule':
		form = GetGroupSchedule(request.form)
		sql = '''select "number" from "group"'''
		cursor.execute(sql)
		rec = cursor.fetchall()
	elif request.args.get('act', '') == 'teacher_schedule':
		form = GetTeacherSchedule(request.form)
		sql = '''select "user_id" from "teacher"'''
		cursor.execute(sql)
		rec = cursor.fetchall()

	if rec:
		choices = []
		if len(rec) > 0:
			for i in rec:
				choices += [(str(i[0]), str(i[0]))]
		else:
			choices = [(0, None)]

		if hasattr(form, 'group_number'):
			form.group_number.choices = choices;
		if hasattr(form, 'teacher_id'):
			form.teacher_id.choices = choices;

	# rec = []
	if request.args.get('group_number', '') != '':
		sql = '''select ttt1."day_of_the_week", ttt1."serial_number", ttt1."subject_type", ttt1."audience_number", ttt1."name" "sub_name", ttt2."name", ttt2."surname", ttt2."patronymic"  from'''
		sql += '''(select * from'''
		sql += '''(select * from'''
		sql += '''"lesson" t1 inner join "group_lesson" t2 '''
		sql += '''on t1."id" = t2."lesson_id"'''
		sql += '''where "group_number" = '{}') '''.format(request.args.get('group_number', ''))
		sql += '''tt1 inner join "subject_in_the_curriculum" tt2 '''
		sql += '''on tt1."subject_id" = tt2."id") '''
		sql += '''ttt1 inner join "user" ttt2 '''
		sql += '''on ttt1."teacher_id" = ttt2."id" '''
		sql += '''order by "day_of_the_week", "serial_number" asc'''
		cursor.execute(sql)
		rec = cursor.fetchall()
	elif request.args.get('teacher_id', '') != '':
		sql = '''select ttt1."day_of_the_week", ttt1."serial_number", ttt1."subject_type", ttt1."audience_number", ttt1."name" "sub_name", ttt2."name", ttt2."surname", ttt2."patronymic"  from'''
		sql += '''(select * from'''
		sql += '''(select * from'''
		sql += '''"lesson" t1 inner join "group_lesson" t2 '''
		sql += '''on t1."id" = t2."lesson_id")'''
		sql += '''tt1 inner join "subject_in_the_curriculum" tt2 '''
		sql += '''on tt1."subject_id" = tt2."id") '''
		sql += '''ttt1 inner join "user" ttt2 '''
		sql += '''on ttt1."teacher_id" = ttt2."id" '''
		sql += '''where ttt1."teacher_id" = '{}' '''.format(request.args.get('teacher_id', ''))
		sql += '''order by "day_of_the_week", "serial_number" asc'''
		cursor.execute(sql)
		rec = cursor.fetchall()

	cursor.close()
	conn.close()
	return render_template('index.html', rec = rec, form = form)

# **********************************************************
# Вход в систему
@app.route('/login', methods = ['POST', 'GET'])
def login():
	form = LoginForm(request.form)
	if request.method == 'POST' and form.validate():
			login = request.form.get('login', '')
			password = request.form.get('password', '')

			if login != 'admin' and password != 'admin':
				conn = psycopg2.connect(dbname = dbconfig['dbname'],
										user = dbconfig['user'],
										password = dbconfig['password'],
										host = dbconfig['host'])
				cursor = conn.cursor()
				sql = '''select * from "user" where "login" = '{}' and password = '{}' '''.format(login, password)
				cursor.execute(sql)
				rec = cursor.fetchone()

				if rec:
					session['id'] = rec[0]
					session['login'] = rec[1]
					session['name'] = rec[3]
					session['surname'] = rec[4]
					session['patronymic'] = rec[5]
					session['acc_type'] = rec[6];

				cursor.close()
				conn.close()
			else:
				session['acc_type'] = 3;

	if session.get('acc_type'):
		return redirect(url_for('index'))
	else:
		return render_template('login.html', form = form)

# **********************************************************
# Регистрация в системе
@app.route('/registration', methods = ['POST', 'GET'])
def registration():
	#**********************
	# Записываем в базу данные пользователя
	conn = psycopg2.connect(dbname = dbconfig['dbname'],
							user = dbconfig['user'],
							password = dbconfig['password'],
							host = dbconfig['host'])
	cursor = conn.cursor()

	if request.args.get('acc_type', '') == 'student':
		acc_type = 1
		form = RegistrationStudentForm(request.form)
	elif request.args.get('acc_type', '') == 'teacher':
		acc_type = 2
		form = RegistrationTeacherForm(request.form)

	print(form.errors)

	#**********************
	# Задание полей выбора
	if acc_type == 1:
		sql = '''select "number" from "group"'''
		cursor.execute(sql)
		rec = cursor.fetchall()

		if rec:
			choices = []
			if len(rec) > 0:
				for i in rec:
					choices += [(str(i[0]), str(i[0]))]
			else:
				choices = [(0, None)]
			if hasattr(form, 'group_number'):
				form.group_number.choices = choices;

	elif acc_type ==2:
		sql = '''select "number" from "department"'''
		cursor.execute(sql)
		rec = cursor.fetchall()

		if rec:
			choices = []
			if len(rec) > 0:
				for i in rec:
					choices += [(str(i[0]), str(i[0]))]
			else:
				choices = [(0, None)]
			if hasattr(form, 'department_number'):
				form.department_number.choices = choices;

	#**********************
	if request.method == 'POST' and form.validate():
		# Если кнопка 'Отправить' нажата
		login = request.form.get('login', '')
		password = request.form.get('password', '')
		name = request.form.get('name', '')
		surname = request.form.get('surname', '')
		patronymic = request.form.get('patronymic', '')

		# Проверяем правильность пароля
		if password != request.form.get('confirm_password', ''):
			print('Check password')
			return render_template('registration.html', form = form, acc_type = acc_type)

		sql = '''insert into "user"("login", "password", "name", "surname", "patronymic", "user_type")'''
		sql += '''values('{}', '{}', '{}', '{}', '{}', '{}') returning "id"'''.format(login, password, name, surname, patronymic, acc_type)
		cursor.execute(sql)
		id = cursor.fetchone()[0];


		if acc_type == 1:
			# Регистрация студента
			group_number = request.form.get('group_number', '')

			# Запишем в базу данные о студенте
			sql = '''insert into "student"("user_id", "group_number") values('{}', '{}')'''.format(id, group_number)
			cursor.execute(sql)

		elif acc_type == 2:
			print('teach')
			# Регистрация преподавателя
			science_degree = request.form.get('science_degree', '')
			number_of_publications = request.form.get('number_of_publications', '')
			department_number = request.form.get('department_number', '')

			# Запишем в базу данные о преподавателе
			sql = '''insert into "teacher"("user_id", "science_degree", "number_of_publications", "number_of_department")'''
			sql += '''values('{}', '{}', '{}', '{}')'''.format(id, science_degree, number_of_publications, department_number)
			cursor.execute(sql)

		# Закрытие соединения с базой
		conn.commit()
		cursor.close()
		conn.close()

		return redirect(url_for('index'))

	# Закрытие соединения с базой
	cursor.close()
	conn.close()

	return render_template('registration.html', form = form, acc_type = acc_type)

# **********************************************************
# Выход из профиля
@app.route('/logout')
def logout():
	# Удаление сессий
	session.pop('id', None)
	session.pop('login', None)
	session.pop('name', None)
	session.pop('surname', None)
	session.pop('patronymic', None)
	session.pop('acc_type', None)
	return redirect(url_for('login'))

# **********************************************************
# Панель администратора
@app.route('/control_panel', methods = ['GET', 'POST'])
def control_panel():
	rec = []
	rec2 = []
	rec3 = []
	rec4 = []
	rec, form = update_control_panel_content();

	# Открытие соединения с БД
	conn = psycopg2.connect(dbname = dbconfig['dbname'],
							user = dbconfig['user'],
							password = dbconfig['password'],
							host = dbconfig['host'])
	cursor = conn.cursor()
	# Получение списка номеров специальностей
	if request.args.get('act', '') == 'semester_curriculum' or request.args.get('act', '') == 'group':
		sql = '''select "number" from "speciality"'''
		cursor.execute(sql)
		rec = cursor.fetchall()
	elif request.args.get('act', '') == 'subject_in_the_curriculum':
		sql = '''select "id" from "semester_curriculum"'''
		cursor.execute(sql)
		rec = cursor.fetchall()
	elif request.args.get('act', '') == 'lesson':
		sql = '''select "number" from "audience"'''
		cursor.execute(sql)
		rec = cursor.fetchall()

		sql = '''select "id" from "subject_in_the_curriculum"'''
		cursor.execute(sql)
		rec2 = cursor.fetchall()

		sql = '''select "number" from "group"'''
		cursor.execute(sql)
		rec3 = cursor.fetchall()

		sql = '''select "user_id" from "teacher"'''
		cursor.execute(sql)
		rec4 = cursor.fetchall()

	if rec:
		choices = []
		if len(rec) > 0:
			for i in rec:
				choices += [(str(i[0]), str(i[0]))]
	else:
		choices = [(0, None)]

	if rec2:
		choices2 = []
		if len(rec2) > 0:
			for i in rec2:
				choices2 += [(str(i[0]), str(i[0]))]
	else:
		choices2 = [(0, None)]

	if rec3:
		choices3 = []
		if len(rec3) > 0:
			for i in rec3:
				choices3 += [(str(i[0]), str(i[0]))]
	else:
		choices3 = [(0, None)]

	if rec4:
		choices4 = []
		if len(rec4) > 0:
			for i in rec4:
				choices4 += [(str(i[0]), str(i[0]))]
	else:
		choices4 = [(0, None)]

	# Установка choices
	if hasattr(form, 'speciality_number'):
		form.speciality_number.choices = choices
	if hasattr(form, 'semester_id'):
		form.semester_id.choices = choices
	if hasattr(form, 'audience_number'):
		form.audience_number.choices = choices
	if hasattr(form, 'subject_id'):
		form.subject_id.choices = choices2
	if hasattr(form, 'group_number'):
		form.group_number.choices = choices3
	if hasattr(form, 'teacher_id'):
		form.teacher_id.choices = choices4

	# Добавление новых элементов в БД
	if request.method == 'POST' and form.validate():
		if request.args.get('act', '') == 'department':
			department_number = request.form.get('department_number', '')
			sql = '''insert into "department"("number") values('{}')'''.format(department_number)
			cursor.execute(sql)
			conn.commit()
		elif request.args.get('act', '') == 'speciality':
			speciality_number = request.form.get('speciality_number', '')
			speciality_name = request.form.get('speciality_name', '')
			sql = '''insert into "speciality"("number", "name") values('{}', '{}')'''.format(speciality_number, speciality_name)
			cursor.execute(sql)
			conn.commit()
		elif request.args.get('act', '') == 'semester_curriculum':
			id = request.form.get('id', '')
			semester_number = request.form.get('semester_number', '')
			speciality_number = request.form.get('speciality_number', '')
			print(semester_number)
			print(speciality_number)
			sql = '''insert into "semester_curriculum"("semester_number", "speciality_number") values('{}', '{}')'''.format(semester_number, speciality_number)
			cursor.execute(sql)
			conn.commit()
		elif request.args.get('act', '') == 'subject_in_the_curriculum':
			subject_name = request.form.get('subject_name', '')
			number_of_lection = request.form.get('number_of_lection', '')
			number_of_labs = request.form.get('number_of_labs', '')
			kr = request.form.get('kr', '')
			if kr == '': kr = 'n'
			semester_id = request.form.get('semester_id', '')
			sql = '''insert into "subject_in_the_curriculum"("name", "number_of_lection", "number_of_labs", "kr", "semester_curriculum_id") values('{}', '{}', '{}', '{}', '{}')'''.format(subject_name, number_of_lection, number_of_labs, kr, semester_id)
			cursor.execute(sql)
			conn.commit()
		elif request.args.get('act', '') == 'lesson':
			group_number = request.form.get('group_number', '')
			day_of_the_week = request.form.get('day_of_the_week', '')
			serial_number = request.form.get('serial_number', '')
			subject_type = request.form.get('subject_type', '')
			audience_number = request.form.get('audience_number', '')
			subject_id = request.form.get('subject_id', '')
			teacher_id = request.form.get('teacher_id', '')
			sql = '''insert into "lesson"("day_of_the_week", "serial_number", "subject_type", "audience_number", "subject_id", "teacher_id") values('{}', '{}', '{}', '{}', '{}', '{}') returning "id"'''.format(day_of_the_week, serial_number, subject_type, audience_number, subject_id, teacher_id)
			cursor.execute(sql)
			lesson_id = cursor.fetchone()[0]
			sql = '''insert into "group_lesson"("group_number", "lesson_id")'''
			sql += '''values('{}', '{}')'''.format(group_number, lesson_id)
			cursor.execute(sql)
			conn.commit()
		elif request.args.get('act', '') == 'group':
			group_number = request.form.get('group_number', '')
			current_sem = request.form.get('current_sem', '')
			speciality_number = request.form.get('speciality_number', '')
			sql = '''insert into "group"("number", "current_sem", "speciality_number") values('{}', '{}', '{}')'''.format(group_number, current_sem, speciality_number)
			cursor.execute(sql)
			conn.commit()
		elif request.args.get('act', '') == 'audience':
			audience_number = request.form.get('audience_number', '')
			sql = '''insert into "audience"("number") values('{}')'''.format(audience_number)
			cursor.execute(sql)
			conn.commit()
		# Выполнение записи в БД
		# cursor.execute(sql)
		# conn.commit()

	# Закрытие соединения с БД
	cursor.close()
	conn.close()

	# Удаление строк из БД
	if request.args.get('del', ''):
		conn = psycopg2.connect(dbname = dbconfig['dbname'],
								user = dbconfig['user'],
								password = dbconfig['password'],
								host = dbconfig['host'])
		cursor = conn.cursor()
		if request.args.get('act', '') == 'department':
			sql = '''delete from "department" where "number" = {}'''.format(request.args.get('del', ''))
		elif request.args.get('act', '') == 'speciality':
			sql = '''delete from "speciality" where "number" = {}'''.format(request.args.get('del', ''))
		elif request.args.get('act', '') == 'semester_curriculum':
			sql = '''delete from "semester_curriculum" where "id" = {}'''.format(request.args.get('del', ''))
		elif request.args.get('act', '') == 'subject_in_the_curriculum':
			sql = '''delete from "subject_in_the_curriculum" where "id" = {}'''.format(request.args.get('del', ''))
		elif request.args.get('act', '') == 'lesson':
			sql = '''delete from "group_lesson" where "lesson_id" = '{}';'''.format(request.args.get('del', ''))
			sql += '''delete from "lesson" where "id" = {}'''.format(request.args.get('del', ''))
		elif request.args.get('act', '') == 'group':
			sql = '''delete from "group" where "number" = {}'''.format(request.args.get('del', ''))
		elif request.args.get('act', '') == 'audience':
			sql = '''delete from "audience" where "number" = {}'''.format(request.args.get('del', ''))


		cursor.execute(sql)
		# Закрытие соединения с БД
		conn.commit()
		cursor.close()
		conn.close()
		if request.args.get('act', '') == 'lesson':
			return redirect(url_for('control_panel', act = request.args.get('act'), group = request.args.get('group') ))
		else:
			return redirect(url_for('control_panel', act = request.args.get('act')))

	#*********************
	# conn = psycopg2.connect(dbname = dbconfig['dbname'],
	# 						user = dbconfig['user'],
	# 						password = dbconfig['password'],
	# 						host = dbconfig['host'])
	# cursor = conn.cursor()

	rec, buf = update_control_panel_content();

	return render_template('control_panel.html', form = form, rec = rec)

# **********************************************************
def update_control_panel_content():
	sql = ''
	conn = psycopg2.connect(dbname = dbconfig['dbname'],
							user = dbconfig['user'],
							password = dbconfig['password'],
							host = dbconfig['host'])
	cursor = conn.cursor()

	if request.args.get('act', '') == 'department':
		form = AddDepartment(request.form)
		sql = '''select * from "department"'''
	elif request.args.get('act', '') == 'speciality':
		form = AddSpeciality(request.form)
		sql = '''select * from "speciality"'''
	elif request.args.get('act', '') == 'semester_curriculum':
		form = AddSemesterCurriculum(request.form)
		sql = '''select * from "semester_curriculum"'''
	elif request.args.get('act', '') == 'subject_in_the_curriculum':
		form = AddSubjectInTheCurriculum(request.form)
		sql = '''select * from "subject_in_the_curriculum"'''
	elif request.args.get('act', '') == 'lesson':
		form = AddLesson(request.form)
		# sql = '''select * from "lesson"'''
		if request.args.get('group', ''):
			sql = '''select * from'''
			sql += '''"lesson" t1 inner join "group_lesson" t2 '''
			sql += '''on t1."id" = t2."lesson_id"'''
			sql += '''where "group_number" = '{}' '''.format(request.args.get('group', ''))
	elif request.args.get('act', '') == 'group':
		form = AddGroup(request.form)
		sql = '''select * from "group"'''
	elif request.args.get('act', '') == 'audience':
		form = AddAudience(request.form)
		sql = '''select * from "audience"'''

	if sql != '':
		cursor.execute(sql)
		return cursor.fetchall(), form

	return [], form

# **********************************************************
# Редактирование личного профиля
@app.route('/profile', methods = ['GET', 'POST'])
def profile():
	conn = psycopg2.connect(dbname = dbconfig['dbname'],
							user = dbconfig['user'],
							password = dbconfig['password'],
							host = dbconfig['host'])
	cursor = conn.cursor()

	if session['acc_type'] == 1:
		form = profileStudentForm(request.form)
		acc_type = 1
	elif session['acc_type'] == 2:
		form = profileTeacherForm(request.form)
		acc_type = 2

	sql = '''select * from "user" where "id" = {}'''.format(session['id'])
	cursor.execute(sql)
	rec = cursor.fetchone()
	form.login.process_data(rec[1])
	form.name.process_data(rec[3])
	form.surname.process_data(rec[4])
	form.patronymic.process_data(rec[5])

	if acc_type == 1:
		# Получить список всех групп
		sql = '''select "number" from "group"'''
		cursor.execute(sql)
		rec = cursor.fetchall()

		if rec:
		    choices = []
		    if len(rec) > 0:
		        for i in rec:
		            choices += [(str(i[0]), str(i[0]))]
		else:
		    choices = [(0, None)]

		# Получить номер группы студента
		sql = '''select "group_number" from "student" where "user_id" = {}'''.format(session['id'])
		cursor.execute(sql)
		rec = cursor.fetchone()

		form.group_number.choices = choices
		if rec:
			form.group_number.process_data(rec[0])
	elif acc_type == 2:
		# Получить список всех кафедр
		sql = '''select "number" from "department"'''
		cursor.execute(sql)
		rec = cursor.fetchall()

		if rec:
		    choices = []
		    if len(rec) > 0:
		        for i in rec:
		            choices += [(str(i[0]), str(i[0]))]
		else:
		    choices = [(0, None)]

		# Получить информацию о преподавателе
		sql = '''select * from "teacher" where "user_id" = {}'''.format(session['id'])
		cursor.execute(sql)
		rec = cursor.fetchone()

		if rec:
			form.science_degree.process_data(rec[1])
			form.number_of_publications.process_data(rec[2])
			form.department_number.process_data(rec[3])

		form.department_number.choices = choices

	# Если нажата кнопка 'Сохранить'
	if request.method == 'POST' and form.validate():
		login = request.form.get('login', '')
		name = request.form.get('name', '')
		surname = request.form.get('surname', '')
		patronymic = request.form.get('patronymic', '')

		sql = '''update "user"'''
		sql += '''set "login" = '{}', "name" = '{}' , "surname" = '{}', "patronymic" = '{}' '''.format(login, name, surname, patronymic)
		sql += '''where "id" = '{}' '''.format(session['id'])
		cursor.execute(sql)
		conn.commit()

		if acc_type == 1:
			group_number = request.form.get('group_number', '')

			sql = '''update "student"'''
			sql += '''set "group_number" = '{}' '''.format(group_number)
			sql += '''where "user_id" = '{}' '''.format(session['id'])
		elif acc_type == 2:
			science_degree = request.form.get('science_degree', '')
			number_of_publications = request.form.get('number_of_publications', '')
			department_number = request.form.get('department_number', '')

			sql = '''update "teacher"'''
			sql += '''set "science_degree" = '{}', "number_of_publications" = '{}', "number_of_department" = '{}' '''.format(science_degree, number_of_publications, department_number)
			sql += '''where "user_id" = '{}' '''.format(session['id'])

		cursor.execute(sql)
		conn.commit()

		cursor.close()
		conn.close()
		return redirect(url_for('profile'))

	# Закрытие соединения с базой
	cursor.close()
	conn.close()

	return render_template('profile.html', form = form)
