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

#print assessments

# average formula takes a list of numbers and returns the average
def average(list):
	if len(list) == 0:
		return 0
	else:
		return float(sum(list))/float(len(list))

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
	return render_template('grade.html', chartID=chartID, chart=chart, series=series, title=title, xAxis=xAxis, yAxis=yAxis,crt_groups=crt_groups)

# by crt group with grade slicer
@app.route('/crt_group/<grade>')
def crtGroup(chartID = 'chart_ID', chart_type = 'line', chart_height = 500, grade = 'all'):	
	chart = {"renderTo": chartID, "type": chart_type, "height": chart_height,}
	series = crt_by_grade(grade)[0] 
	title_text = 'Weekly Assessment Tracking - By CRT Group - Grades: %s' % str(grade)
	title = {"text": title_text} 
	xAxis = {"categories": crt_by_grade(grade)[1], "title":{"text":'Assessment'}}
	yAxis = {"title": {"text": 'Score %'}}
	return render_template('crt_group.html', chartID=chartID, chart=chart, series=series, title=title, xAxis=xAxis, yAxis=yAxis,grades=grades)


##################### run #####################

if __name__ == "__main__":
	#app.run(debug = True, host='0.0.0.0', port=8080, passthrough_errors=True)
	app.run(debug = True)

