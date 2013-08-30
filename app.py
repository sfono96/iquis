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



##################### run #####################

if __name__ == "__main__":
	#app.run(debug = True, host='0.0.0.0', port=8080, passthrough_errors=True)
	app.run(debug = True)

