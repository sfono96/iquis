#from flask import Flask, render_template, request
from flask import *
from data import mylist
from math import trunc
#from decimal import *

##################### lists and methods #####################

# get unique lists for filtering on
students = sorted(set([row['name'] for row in mylist]))
teachers = sorted(set([row['teacher'] for row in mylist]))
grades = sorted(set([row['grade'] for row in mylist]))
crt_groups = sorted(set([row['CRT Score Group'] for row in mylist]))
assessments = sorted(set([row['standard'] for row in mylist]))
proficiency_groups = sorted(set([row['proficiency'] for row in mylist]))
proficiency_groups.append('All')
#weeks = sorted(set([row['week'] for row in mylist]))

# average formula takes a list of numbers and returns the average
def average(list):
	if len(list) == 0:
		return 0
	else:
		return float(sum(list))/float(len(list))

def round_me(number):
	 #return Decimal(number).quantize(Decimal('0.01'))
	 return (trunc(round(float(number)*1000))+.0)/1000

# pulls back list of teachers based on grade level
def relevant_teachers(grade):
	return sorted(set([row['teacher'] for row in mylist if row['grade'] == grade]))

# split out the checkbox values
def split_out_grade(list):
	crt_group_list = [i[2:] for i in list if i[0] == 'c']
	grade_list = [i[2:] for i in list if i[0] == 'g']
	return crt_group_list, grade_list

def relevant_quiz(grade):
	list = sorted(set([q['standard'] for q in mylist if q['grade'] == grade]))
	return list

# display series = quiz score by grade by proficiency
def quiz(grade,proficiency_list):
	mydict = {}
	for row in mylist:
		if row['grade'] == grade:
			if proficiency_list == 'All' or row['proficiency'] == proficiency_list:
				if row['standard'] not in mydict:
					mydict[row['standard']] = []
				mydict[row['standard']].append(float(row['score']))
	
	data = []
	for i in mydict:
		[key, val] = [i, round_me(average(mydict[i]))]
		data.append([key, val])
	
	data = [round_me(d[1]*100) for d in sorted(data)]

	data_series = {}
	data_series['name'] = 'Average Quiz Score'
	data_series['data'] = data

	return data_series

def teacher(grade,proficiency_list,quiz):
	mydict = {}
	for row in mylist:
		if row['grade'] == grade and row['standard'] == quiz: 
			if row['proficiency'] == proficiency_list or proficiency_list == 'All':
				if row['teacher'] not in mydict:
					mydict[row['teacher']] = []
				mydict[row['teacher']].append(float(row['score']))
	
	data = []
	for i in mydict:
		[key, val] = [i, round_me(average(mydict[i]))]
		data.append([key, val])
	
	data = [round_me(d[1]*100) for d in sorted(data)]

	data_series = {}
	data_series['name'] = 'Average Quiz Score'
	data_series['data'] = data

	return data_series

# method to filter students by grade by teacher by crt group levels and return relevant assessments
def students_list(grade,teacher,proficiency_list):
	student_dict = {}
	quizzes = relevant_quiz(grade)
	for row in mylist:
		if row['grade'] == grade and row['teacher'] == teacher: 
			if row['proficiency'] == proficiency_list or proficiency_list == 'All': # if it is the target grade and teacher
				if row['name'] not in student_dict:
					student_dict[row['name']] = []
				for q in quizzes:
					if row['standard'] == q:
						student_dict[row['name']].append(round_me(row['score'])*100)
	
	data_series = []
	for k in student_dict:
		r = []
		r.append(k)
		for i in student_dict[k]:
			r.append(i)
		data_series.append(r)
	
	data_series = sorted(data_series)		
	
	return data_series

##################### app #####################

app = Flask(__name__)
app.jinja_env.add_extension('jinja2.ext.loopcontrols') # add counter looping

##################### routes #####################

# login stuff
@app.route('/log',methods=['GET','POST'])
def log():
	error = None
	if request.method == 'POST':
		if request.form['username'] != 'admin' or request.form['password'] != 'admin':
			error = 'Invalid Credentials. Please try again.'
		else:
			session['logged_in'] = True
			return redirect(url_for('/'))
	return render_template('log.html',error=error)

# logout session
@app.route('/logout')
def logout():
	session.pop('logged_in', None)


# filter quizzes by grade level
@app.route('/')
@app.route('/grade',methods=['GET','POST'])
def grade(chartID = 'chart_ID', chart_type = 'bar', chart_height = 500, f_grade = '0 - Kindergarten', f_proficiency_list = 'All'):
	if request.method == 'POST':
		f_grade = request.form.getlist("rb")[0]
		f_proficiency_list = request.form.getlist("rb2")[0]
	chart = {"renderTo": chartID, "type": chart_type, "height": chart_height}
	series = [quiz(f_grade,f_proficiency_list)] #quiz(grade,proficiency_list)
	title_text = 'Math Assessment Tracking - %srs' % str(f_grade[4:])
	title = {"text": title_text} 
	xAxis = {"categories":relevant_quiz(f_grade)}
	yAxis = {"min":20,"max":50,"title": {"text": 'Score %'}}
	#plotOptions = {"series":{"dataLabels":{"enabled":"true","format":'{y} pct',"style":{"fontWeight":'bold',"fontSize":'15px'}}}}
	plotOptions = {"series":{"colorByPoint":"true"}}
	tooltip = {"valueSuffix":' pct'}
	return render_template('grade.html', chartID=chartID, chart=chart, series=series, title=title, xAxis=xAxis, yAxis=yAxis, plotOptions=plotOptions, tooltip=tooltip,grades=grades, \
	proficiency_list=proficiency_groups, f_grade=f_grade,f_proficiency_list=f_proficiency_list)

# by teacher with grade and crt group filters
@app.route('/teachers',methods=['POST','GET'])
def teachers(chartID = 'chart_ID', chart_type = 'column', chart_height = 500, f_grade='0 - Kindergarten', f_proficiency_list='All'):	
	f_quiz = relevant_quiz(f_grade)[0]
	if request.method == 'POST':
		f_proficiency_list = request.form.getlist("r3")[0]
		f_grade = request.form.getlist("r1")[0]
		f_quiz = request.form.getlist("r2")[0]
		if f_quiz not in relevant_quiz(f_grade):
			f_quiz = relevant_quiz(f_grade)[0]
	chart = {"renderTo": chartID, "type": chart_type, "height": chart_height}
	series = [teacher(f_grade,f_proficiency_list,f_quiz)] 
	title_text = 'Math Assessment Tracking - %s Teachers' % str(f_grade[4:])
	title = {"text": title_text} 
	xAxis = {"categories": relevant_teachers(f_grade)}
	yAxis = {"min":0,"max":50,"title": {"text": 'Score %'}}
	plotOptions = {"series":{"colorByPoint":"true","dataLabels":{"enabled":"true","format":'{y} pct',"inside":"true","color":"white","style":{"fontWeight":'bold',"fontSize":'20px'}}}}
	tooltip = {"valueSuffix":" pct"}
	return render_template('teacher.html', chartID=chartID, chart=chart, series=series, title=title, xAxis=xAxis, yAxis=yAxis, plotOptions=plotOptions, tooltip=tooltip,grades=grades, \
	proficiency_list=proficiency_groups, quizzes = relevant_quiz(f_grade), f_grade=f_grade, f_proficiency_list=f_proficiency_list,f_quiz=f_quiz)

# by students with grade, teacher, and crt group filters
@app.route('/students',methods=['POST','GET'])
def students(f_grade = '0 - Kindergarten', f_teacher = 'Mr. Sternberg', f_proficiency_list='All'):	
	if request.method == 'POST':
		f_grade = request.form.getlist("r1")[0]
		f_proficiency_list = request.form.getlist("r3")[0]
		f_teacher = request.form.getlist("r2")[0]
		if f_teacher not in relevant_teachers(f_grade):
			f_teacher = relevant_teachers(f_grade)[0]
	students = students_list(f_grade,f_teacher,f_proficiency_list)
	return render_template('student.html', quizzes=relevant_quiz(f_grade),students=students, grades=grades,teachers=relevant_teachers(f_grade), \
	proficiency_list=proficiency_groups, f_grade=f_grade, f_teacher=f_teacher, f_proficiency_list=f_proficiency_list,qcnt=len(relevant_quiz(f_grade)))

##################### run #####################

if __name__ == "__main__":
	#app.run(debug = True, host='0.0.0.0', port=8080, passthrough_errors=True)
	app.run(debug = True)

