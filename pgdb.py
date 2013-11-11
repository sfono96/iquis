import psycopg2, os, urlparse
from math import trunc


############ DB CONNECTION ############ 

production = False # set this to true if pushing changes to production server (heroku) else keep false on development box

if production == False:

	# development server (local box)
	host = 'localhost'
	dbname = 'inquis'
	user = 'postgres'
	password = 'password'
	conn_string = 'host=%s dbname=%s user=%s password=%s' %(host,dbname,user,password)
	conn = psycopg2.connect(conn_string)

else:

	#production server (heroku)
	urlparse.uses_netloc.append("postgres")
	url = urlparse.urlparse(os.environ["DATABASE_URL"])

	conn = psycopg2.connect(
	    database=url.path[1:],
	    user=url.username,
	    password=url.password,
	    host=url.hostname,
	    port=url.port
	)

# cursor object
cursor = conn.cursor()

############ DEFAULT LISTS ############

# PROFICIENCY GROUPS
cursor.execute('select distinct PRIOR_YEAR_PROFICIENCY from data;')
proficiency_groups = [r[0] for r in cursor.fetchall()]
proficiency_groups.append('All')

# GRADE LEVELS
cursor.execute('select distinct GRADE from data order by 1;')
grades = [r[0] for r in cursor.fetchall()]

# ATTEMPTS
cursor.execute('select distinct attempt from data order by 1;')
attempts = [r[0] for r in cursor.fetchall()]

############ HELPER METHODS ############

def round_me(number):
	 #return Decimal(number).quantize(Decimal('0.01'))
	 return (trunc(round(number,3)*1000)+.0)/10

def relevant_quiz(grade):
	sql = 'SELECT DISTINCT ASSESSMENT FROM DATA WHERE GRADE = \'%s\' ORDER BY 1;' % grade
	cursor.execute(sql)
	return [r[0] for r in cursor.fetchall()]

def relevant_teachers(grade):
	sql = 'SELECT DISTINCT TEACHER FROM DATA WHERE GRADE = \'%s\' ORDER BY 1;' % grade
	cursor.execute(sql)
	rs = [r[0] for r in cursor.fetchall()]
	rs.append('All') # Allow for all teachers within the grade
	return rs	

############ MAIN METHODS ############

def quiz(grade,proficiency):
	if proficiency == 'All':
		sql = 'SELECT ASSESSMENT, AVG(SCORE) FROM DATA WHERE GRADE = \'%s\' AND ATTEMPT = 1 GROUP BY ASSESSMENT ORDER BY 1;' % grade
	else:
		sql = 'SELECT ASSESSMENT, AVG(SCORE) FROM DATA WHERE GRADE = \'%s\' AND ATTEMPT = 1 AND PRIOR_YEAR_PROFICIENCY = \'%s\' GROUP BY ASSESSMENT ORDER BY 1;' % (grade,proficiency)
	cursor.execute(sql)
	rs = cursor.fetchall()
	assessments = [r[0] for r in rs]
	scores = [round_me(r[1]) for r in rs]
	return assessments, scores


def teacher(grade,proficiency,quiz):
	if proficiency == 'All':
		sql = 'SELECT TEACHER, AVG(SCORE) FROM DATA WHERE GRADE = \'%s\' AND ASSESSMENT = \'%s\'  AND ATTEMPT = 1 GROUP BY TEACHER ORDER BY 1;' % (grade,quiz)
	else:
		sql = 'SELECT TEACHER, AVG(SCORE) FROM DATA WHERE GRADE = \'%s\' AND ASSESSMENT = \'%s\' AND ATTEMPT = 1 AND PRIOR_YEAR_PROFICIENCY = \'%s\' GROUP BY TEACHER ORDER BY 1;' % (grade,quiz,proficiency)
	cursor.execute(sql)
	rs = cursor.fetchall()
	teachers = [r[0] for r in rs]
	scores = [round_me(r[1]) for r in rs]
	return teachers, scores	


def students_list(grade,teacher,proficiency):
	if proficiency == 'All':
		if teacher == 'All':
			sql = 'SELECT STUDENT, ASSESSMENT, SCORE FROM DATA WHERE GRADE = \'%s\' AND ATTEMPT = 1 ORDER BY 1,2;' % grade
		else:
			sql = 'SELECT STUDENT, ASSESSMENT, SCORE FROM DATA WHERE TEACHER = \'%s\' AND ATTEMPT = 1 ORDER BY 1,2;' % teacher
	else:
		if teacher == 'All':
			sql = 'SELECT STUDENT, ASSESSMENT, SCORE FROM DATA WHERE GRADE = \'%s\' AND ATTEMPT = 1 AND PRIOR_YEAR_PROFICIENCY = \'%s\' ORDER BY 1,2;' % (grade,proficiency)
		else:
			sql = 'SELECT STUDENT, ASSESSMENT, SCORE FROM DATA WHERE TEACHER = \'%s\' AND ATTEMPT = 1 AND PRIOR_YEAR_PROFICIENCY = \'%s\' ORDER BY 1,2;' % (teacher,proficiency)
	cursor.execute(sql)
	rs = cursor.fetchall()
	data_series = []
	sdict = {}
	for r in rs:
		if r[0] not in sdict:
			sdict[r[0]] = []
		sdict[r[0]].append(r[2])
	for k in sdict:
		list = []
		list.append(k)
		for v in sdict[k]:
			list.append(round_me(v))
		data_series.append(list)

	data_series = sorted(data_series)
	return data_series

def student_attempts(grade,teacher,proficiency,quiz):
	# SQL depending on selections
	if proficiency == 'All':
		if teacher == 'All':
			sql = 'SELECT STUDENT, ATTEMPT, SCORE FROM DATA WHERE GRADE = \'%s\' AND ASSESSMENT = \'%s\' ORDER BY 1,2;' %(grade, quiz)
		else:
			sql = 'SELECT STUDENT, ATTEMPT, SCORE FROM DATA WHERE TEACHER = \'%s\' AND ASSESSMENT = \'%s\' ORDER BY 1,2;' %(teacher, quiz)
	else:
		if teacher == 'All':
			sql = 'SELECT STUDENT, ATTEMPT, SCORE FROM DATA WHERE GRADE = \'%s\' AND ASSESSMENT = \'%s\' AND PRIOR_YEAR_PROFICIENCY = \'%s\' ORDER BY 1,2;' % (grade,quiz,proficiency)
		else:
			sql = 'SELECT STUDENT, ATTEMPT, SCORE FROM DATA WHERE TEACHER = \'%s\' AND ASSESSMENT = \'%s\' AND PRIOR_YEAR_PROFICIENCY = \'%s\' ORDER BY 1,2;' % (teacher,quiz,proficiency)
	cursor.execute(sql)
	rs = cursor.fetchall()
	
	# get list of scores (val) for each student (key)
	sdict = {}
	for r in rs:
		if r[0] not in sdict:
			sdict[r[0]] = []
		sdict[r[0]].append(r[2])
	
	# now combine in key, val into 1 row and toss into data series list for returning
	data_series = []
	for k in sdict:
		list = []
		list.append(k)
		for v in sdict[k]:
			if v is not None:
				list.append(round_me(v))
			else:
				list.append(None)
		data_series.append(list)

	data_series = sorted(data_series)
	return data_series

# st = student_attempts('0 - Kindergarten','Mr. Boler','All','K.CC.A.1')
# for s in st:
# 	print s