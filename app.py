from flask import Flask, render_template, request
from data import mylist
from decimal import *

##################### lists and methods #####################

# get unique lists for filtering on
students = sorted(set([row['name'] for row in mylist]))
teachers = sorted(set([row['teacher'] for row in mylist]))
grades = sorted(set([row['grade'] for row in mylist]))
crt_groups = sorted(set([row['CRT Score Group'] for row in mylist]))
assessments = sorted(set([row['standard'] for row in mylist]))
weeks = sorted(set([row['week'] for row in mylist]))

# average formula takes a list of numbers and returns the average
def average(list):
	if len(list) == 0:
		return 0
	else:
		return float(sum(list))/float(len(list))

def round_me(number):
	 return Decimal(number).quantize(Decimal('.01'),rounding=ROUND_HALF_UP)

# pulls back list of teachers based on grade level
def relevant_teachers(grade):
	return sorted(set([row['teacher'] for row in mylist if row['grade'] == grade]))

# split out the checkbox values
def split_out_grade(list):
	crt_group_list = [i[2:] for i in list if i[0] == 'c']
	grade_list = [i[2:] for i in list if i[0] == 'g']
	return crt_group_list, grade_list

# method to filter on CRT level and show all grades
def grade_by_crt(grade_list, crt_list):
	# grade is the series filter crt is a data filter
	mydict = {}
	for row in mylist:
		if row['grade'] in grade_list and row['CRT Score Group'] in crt_list:
			if row['grade'] not in mydict:
				mydict[row['grade']] = {}
			if row['week'] not in mydict[row['grade']]:
				mydict[row['grade']][row['week']] = []
			mydict[row['grade']][row['week']].append(float(row['score']))
	
	data_series = []
	for i in mydict:
		for j in mydict[i]:
			mydict[i][j] = average(mydict[i][j])
		grade_dict = {}
		grade_dict['name'] = i
		grade_dict['data'] = [(j, mydict[i][j]) for j in mydict[i]] # throw tuples into list so i can sort by assessment then ditch assessments and keep only score
		grade_dict['data'] = sorted(grade_dict['data'])
		grade_dict['data'] = [l[1] for l in grade_dict['data']]
		data_series.append(grade_dict)

	data_series = sorted(data_series, key=lambda k: k['name']) 
	return data_series

def crt_by_grade(crt_list,grade_list):
	# crt is the series filter grade is a data filter
	mydict = {}
	for row in mylist:
		if row['grade'] in grade_list and row['CRT Score Group'] in crt_list:
			if row['CRT Score Group'] not in mydict:
				mydict[row['CRT Score Group']] = {}
			if row['standard'] not in mydict[row['CRT Score Group']]:
				mydict[row['CRT Score Group']][row['standard']] = []
			mydict[row['CRT Score Group']][row['standard']].append(round_me(row['score']))
	
	data_series = []
	for i in mydict:
		for j in mydict[i]:
			mydict[i][j] = average(mydict[i][j])
		crt_dict = {}
		crt_dict['name'] = i
		crt_dict['data'] = [(j, mydict[i][j]) for j in mydict[i]] # throw tuples into list so i can sort by assessment then ditch assessments and keep only score
		crt_dict['data'] = sorted(crt_dict['data'])
		crt_dict['data'] = [l[1] for l in crt_dict['data']]
		data_series.append(crt_dict)

	data_series = sorted(data_series, key=lambda k: k['name']) 				

	# relevant assessments
	if grade == 'all':
		relevant_assessments = assessments	
	else:
		relevant_assessments = sorted(set([row['standard'] for row in mylist if row['grade'] in grade_list]))
	
	return data_series, relevant_assessments

# method to filter teachers by grade by crt group levels and return relevant assessments
def teachers_by_grade_crt(grade_list,crt_list):
	mydict = {}
	for row in mylist:
		if row['CRT Score Group'] in crt_list and row['grade'] in grade_list :
			if row['teacher'] not in mydict:
				mydict[row['teacher']] = {}
			if row['standard'] not in mydict[row['teacher']]:
				mydict[row['teacher']][row['standard']] = []
			mydict[row['teacher']][row['standard']].append(round_me(row['score']))

	data_series = []
	for i in mydict:
		for j in mydict[i]:
			mydict[i][j] = average(mydict[i][j])
		teacher_dict = {}
		teacher_dict['name'] = i
		teacher_dict['data'] = [(j, mydict[i][j]) for j in mydict[i]] # throw tuples into list so i can sort by assessment then ditch assessments and keep only score
		teacher_dict['data'] = sorted(teacher_dict['data'])
		teacher_dict['data'] = [l[1] for l in teacher_dict['data']]
		data_series.append(teacher_dict)

	data_series = sorted(data_series)		
	
	# relevant assessments
	relevant_assessments = sorted(set([row['standard'] for row in mylist if row['grade'] in grade_list]))

	return data_series, relevant_assessments

# method to filter students by grade by teacher by crt group levels and return relevant assessments
def students_by_grade_teacher_crt(grade,teacher,crt_group):
	mydict = {}
	for row in mylist:
		if crt_group == 'all' or row['CRT Score Group'] == crt_group:
			if row['grade'] == grade and row['teacher'] == teacher: # if it is the target grade and teacher
				if row['name'] not in mydict:
					mydict[row['name']] = {}
					mydict[row['name']]['name'] = row['name']
					mydict[row['name']]['data'] = []
					#mydict[row['name']]['crt'] = row['CRT Score Group']
				mydict[row['name']]['data'].append(float(row['score']))
	data_series = sorted([mydict[k] for k in mydict],key=lambda k: k['name'])		
	
	# relevant assessments
	if grade == 'all':
		relevant_assessments = assessments	
	else:
		relevant_assessments = sorted(set([row['standard'] for row in mylist if row['grade'] == grade]))

	return data_series, relevant_assessments

##################### app #####################

app = Flask(__name__)

##################### routes #####################

# by grade with crt group slicers
@app.route('/')
@app.route('/grade', methods=['POST','GET'])
def grade(chartID = 'chart_ID', chart_type = 'line', chart_height = 500, f_crt_groups=crt_groups, f_grades=grades):	
	if request.method == 'POST':
		f_crt_groups = split_out_grade(request.form.getlist("ck"))[0]
		f_grades = split_out_grade(request.form.getlist("ck"))[1]
	chart = {"renderTo": chartID, "type": chart_type, "height": chart_height}
	series = grade_by_crt(f_grades,f_crt_groups)
	title_text = 'Weekly Assessment Tracking - By Grade'
	title = {"text": title_text} 
	xAxis = {"categories": weeks, "title":{"text":'Week'}}
	yAxis = {"title": {"text": 'Score %'}}
	return render_template('grade.html', chartID=chartID, chart=chart, series=series, title=title, xAxis=xAxis, yAxis=yAxis, crt_groups=crt_groups,grades=grades, f_crt_groups=f_crt_groups, f_grades=f_grades)

# by crt group with grade slicer
@app.route('/crt_group', methods=['POST','GET'])
def crtGroup(chartID = 'chart_ID', chart_type = 'line', chart_height = 500 ,f_grades='0 - Kindergarten',f_crt_groups=crt_groups):	
	if request.method == 'POST':
		f_crt_groups = split_out_grade(request.form.getlist("ck"))[0]
		f_grades = split_out_grade(request.form.getlist("ck"))[1]
	chart = {"renderTo": chartID, "type": chart_type, "height": chart_height}
	series = crt_by_grade(f_crt_groups,f_grades)[0]
	title_text = 'Weekly Assessment Tracking - By CRT Group'
	title = {"text": title_text} 
	xAxis = {"categories": crt_by_grade(f_crt_groups,f_grades)[1], "title":{"text":'Assessment'}}
	yAxis = {"title": {"text": 'Score %'}}
	return render_template('crt_group.html', chartID=chartID, chart=chart, series=series, title=title, xAxis=xAxis, yAxis=yAxis,grades=grades, crt_groups=crt_groups,f_grades=f_grades,f_crt_groups=f_crt_groups)

# by teacher with grade and crt group filters
@app.route('/teachers',methods=['POST','GET'])
def teachers(chartID = 'chart_ID', chart_type = 'line', chart_height = 500, f_grades=['0 - Kindergarten'], f_crt_groups=crt_groups):	
	if request.method == 'POST':
		f_crt_groups = split_out_grade(request.form.getlist("ck"))[0]
		f_grades = split_out_grade(request.form.getlist("ck"))[1]
	chart = {"renderTo": chartID, "type": chart_type, "height": chart_height,}
	series = teachers_by_grade_crt(f_grades,f_crt_groups)[0] 
	title_text = 'Weekly Assessment Tracking - By Teacher'
	title = {"text": title_text} 
	xAxis = {"categories": teachers_by_grade_crt(f_grades,f_crt_groups)[1], "title":{"text":'Assessment'}}
	yAxis = {"title": {"text": 'Score %'}}
	return render_template('teacher.html', chartID=chartID, chart=chart, series=series, title=title, xAxis=xAxis, yAxis=yAxis, grades=grades, crt_groups=crt_groups, f_grades=f_grades, f_crt_groups=f_crt_groups)


# by students with grade, teacher, and crt group filters
@app.route('/students',methods=['POST','GET'])
def students(chartID = 'chart_ID', chart_type = 'line', chart_height = 500, f_grades = ['0 - Kindergarten'], f_teacher = ['Mr. Sternberg'], f_crt_groups=crt_groups):	
	#if request.method == 'POST':

	chart = {"renderTo": chartID, "type": chart_type, "height": chart_height,}
	series = students_by_grade_teacher_crt(grade,teacher,crt_group)[0]
	title_text = 'Weekly Assessment Tracking - By Students - %s - %s' % (str(grade[4:]),str(teacher))
	title = {"text": title_text} 
	xAxis = {"categories": students_by_grade_teacher_crt(grade,teacher,crt_group)[1], "title":{"text":'Assessment'}}
	yAxis = {"title": {"text": 'Score %'}}
	return render_template('student.html', chartID=chartID, chart=chart, series=series, title=title, xAxis=xAxis, yAxis=yAxis,grades=grades,teachers=relevant_teachers(grade), crt_groups=crt_groups, grade=grade, teacher=teacher, crt_group=crt_group)

##################### run #####################

if __name__ == "__main__":
	#app.run(debug = True, host='0.0.0.0', port=8080, passthrough_errors=True)
	app.run(debug = True)

