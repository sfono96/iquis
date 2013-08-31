from flask import Flask, render_template
from data import mylist

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

# pulls back list of teachers based on grade level
def relevant_teachers(grade):
	return sorted(set([row['teacher'] for row in mylist if row['grade'] == grade]))

# method to filter on CRT level and show all grades
def grade_by_crt(crt):
	data_series = []
	for grade in grades:
		data = []
		for week in weeks:
			if crt == 'all':
				scores = [float(row['score']) for row in mylist if row['grade'] == grade if row['week'] == week]
			else:	
				scores = [float(row['score']) for row in mylist if row['grade'] == grade if row['week'] == week if row['CRT Score Group'] == crt]
			data.append(average(scores))
		dict = {}
		dict['name'] = grade
		dict['data'] = data
		data_series.append(dict)
	return data_series

# method to filter CRT Groups By Grade Level and return relevant assessments
def crt_by_grade(grade):
	# data series
	data_series = []
	for crt in crt_groups: # each crt group is a series
		data = [] # this will be one average score per relevant assessment for the respective crt group
		for a in assessments:
			if grade == 'all':
				scores = [float(row['score']) for row in mylist if row['CRT Score Group'] == crt if row['standard'] == a]
				data.append(average(scores))
			else:
				scores = [float(row['score']) for row in mylist if row['CRT Score Group'] == crt if row['standard'] == a if row['grade'] == grade]
				if sum(scores) > 0:
					data.append(average(scores))
		dict = {}
		dict['name'] = crt
		dict['data'] = data
		data_series.append(dict)

	# # new improved code (not quite done yet)
	# mydict = {}
	# for row in mylist:
	# 	if grade == 'all' or row['grade'] == grade:
	# 		if row['CRT Score Group'] not in mydict:
	# 			mydict[row['CRT Score Group']] = {}
	# 		if row['standard'] not in mydict[row['CRT Score Group']]:
	# 			mydict[row['CRT Score Group']][row['standard']] = []
	# 		mydict[row['CRT Score Group']][row['standard']].append(float(row['score']))
	# 	for i in mydict:
	# 		for j in mydict[i]:
	# 			mydict[i][j] = average(mydict[i][j])
				

	# relevant assessments
	if grade == 'all':
		relevant_assessments = assessments	
	else:
		relevant_assessments = sorted(set([row['standard'] for row in mylist if row['grade'] == grade]))
	
	return data_series, relevant_assessments

# method to filter teachers by grade by crt group levels and return relevant assessments
def teachers_by_grade_crt(grade,crt_group):
	mydict = {}
	for row in mylist:
		if crt_group == 'all' or row['CRT Score Group'] == crt_group:
			if row['grade'] == grade: # if it is the target grade
				if row['teacher'] not in mydict:
					mydict[row['teacher']] = {}
				if row['standard'] not in mydict[row['teacher']]:
					mydict[row['teacher']][row['standard']] = []
				mydict[row['teacher']][row['standard']].append(float(row['score']))

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
	if grade == 'all':
		relevant_assessments = assessments	
	else:
		relevant_assessments = sorted(set([row['standard'] for row in mylist if row['grade'] == grade]))

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

# by grade with crt group slicer
@app.route('/')
@app.route('/grade/<crt_group>')
def grade(chartID = 'chart_ID', chart_type = 'line', chart_height = 500, crt_group = 'all'):	
	chart = {"renderTo": chartID, "type": chart_type, "height": chart_height,}
	series = grade_by_crt(crt_group) 
	title_text = 'Weekly Assessment Tracking - By Grade - CRT Group: %s' % str(crt_group)
	title = {"text": title_text} 
	xAxis = {"categories": weeks, "title":{"text":'Week'}}
	yAxis = {"title": {"text": 'Score %'}}
	print crt_group
	return render_template('grade.html', chartID=chartID, chart=chart, series=series, title=title, xAxis=xAxis, yAxis=yAxis, crt_groups=crt_groups, crt_group=crt_group)

# by crt group with grade slicer
@app.route('/crt_group/<grade>')
def crtGroup(chartID = 'chart_ID', chart_type = 'line', chart_height = 500, grade = '0 - Kindergarten'):	
	chart = {"renderTo": chartID, "type": chart_type, "height": chart_height,}
	series = crt_by_grade(grade)[0] 
	title_text = 'Weekly Assessment Tracking - By CRT Group - %s' % str(grade[4:])
	title = {"text": title_text} 
	xAxis = {"categories": crt_by_grade(grade)[1], "title":{"text":'Assessment'}}
	yAxis = {"title": {"text": 'Score %'}}
	return render_template('crt_group.html', chartID=chartID, chart=chart, series=series, title=title, xAxis=xAxis, yAxis=yAxis,grades=grades, grade=grade)

# by teacher with grade and crt group filters
@app.route('/teachers/<grade>/<crt_group>')
def teachers(chartID = 'chart_ID', chart_type = 'line', chart_height = 500, grade = '0 - Kindergarten', crt_group = 'all'):	
	chart = {"renderTo": chartID, "type": chart_type, "height": chart_height,}
	series = teachers_by_grade_crt(grade,crt_group)[0] 
	title_text = 'Weekly Assessment Tracking - By Teacher - %s -%s' % (str(grade[4:]),str(crt_group))
	title = {"text": title_text} 
	xAxis = {"categories": teachers_by_grade_crt(grade,crt_group)[1], "title":{"text":'Assessment'}}
	yAxis = {"title": {"text": 'Score %'}}
	return render_template('teacher.html', chartID=chartID, chart=chart, series=series, title=title, xAxis=xAxis, yAxis=yAxis, grades=grades, crt_groups=crt_groups, grade=grade, crt_group=crt_group)

# by students with grade, teacher, and crt group filters
@app.route('/students/<grade>/<teacher>/<crt_group>')
def students(chartID = 'chart_ID', chart_type = 'line', chart_height = 500, grade = '0 - Kindergarten', teacher = 'Mr. Sternberg', crt_group = 'all'):	
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

