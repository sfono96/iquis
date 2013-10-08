from flask import *
from pgdb import *

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
def grade(chartID = 'chart_ID', chart_type = 'bar', chart_height = 500, f_grade = '0 - Kindergarten', f_proficiency = 'All'):
	if request.method == 'POST':
		f_grade = request.form.getlist("rb")[0]
		f_proficiency = request.form.getlist("rb2")[0]
	chart = {"renderTo": chartID, "type": chart_type, "height": chart_height}
	series = [{'name':'Average Assessment Score','data':quiz(f_grade,f_proficiency)[1]}] # quiz method from pgdb module
	title_text = 'Math Assessment Tracking - %s' % str(f_grade[4:])
	title = {"text": title_text} 
	xAxis = {"categories":quiz(f_grade,f_proficiency)[0]}
	yAxis = {"min":20,"max":50,"title": {"text": 'Score %'}}
	#plotOptions = {"series":{"dataLabels":{"enabled":"true","format":'{y} pct',"style":{"fontWeight":'bold',"fontSize":'15px'}}}}
	plotOptions = {"series":{"colorByPoint":"true"}}
	tooltip = {"valueSuffix":' pct',"valueDecimals":1}
	return render_template('grade.html', chartID=chartID, chart=chart, series=series, title=title, xAxis=xAxis, yAxis=yAxis, plotOptions=plotOptions, tooltip=tooltip,grades=grades, \
	proficiency_list=proficiency_groups, f_grade=f_grade,f_proficiency=f_proficiency)

# by teacher with grade and crt group filters
@app.route('/teachers',methods=['POST','GET'])
def teachers(chartID = 'chart_ID', chart_type = 'column', chart_height = 500, f_grade='0 - Kindergarten', f_proficiency='All'):	
	f_quiz = relevant_quiz(f_grade)[0]
	if request.method == 'POST':
		f_proficiency = request.form.getlist("r3")[0]
		f_grade = request.form.getlist("r1")[0]
		f_quiz = request.form.getlist("r2")[0]
		if f_quiz not in relevant_quiz(f_grade):
			f_quiz = relevant_quiz(f_grade)[0]
	chart = {"renderTo": chartID, "type": chart_type, "height": chart_height}
	series = [{'name':'Average Quiz Scores','data':teacher(f_grade,f_proficiency,f_quiz)[1]}] 
	title_text = 'Math Assessment Tracking - %s Teachers' % str(f_grade[4:])
	title = {"text": title_text} 
	xAxis = {"categories": teacher(f_grade,f_proficiency,f_quiz)[0],"labels":{"style":{"font-size":"16px","fontWeight":'bold'}}}
	yAxis = {"min":0,"max":50,"title": {"text": 'Score %'}}
	plotOptions = {"series":{"colorByPoint":"true","dataLabels":{"enabled":"true","format":'{y} pct',"valueDecimals":1,"inside":"true","color":"white","style":{"fontWeight":'bold',"fontSize":'20px'}}}}
	tooltip = {"valueSuffix":' pct',"valueDecimals":1}
	return render_template('teacher.html', chartID=chartID, chart=chart, series=series, title=title, xAxis=xAxis, yAxis=yAxis, plotOptions=plotOptions, tooltip=tooltip,grades=grades, \
	proficiency_list=proficiency_groups, quizzes = relevant_quiz(f_grade), f_grade=f_grade, f_proficiency=f_proficiency,f_quiz=f_quiz)

# by students with grade, teacher, and crt group filters
@app.route('/students',methods=['POST','GET'])
def students(f_grade = '0 - Kindergarten', f_teacher = 'Mr. Sternberg', f_proficiency='All'):	
	if request.method == 'POST':
		f_grade = request.form.getlist("r1")[0]
		f_proficiency = request.form.getlist("r3")[0]
		f_teacher = request.form.getlist("r2")[0]
		if f_teacher not in relevant_teachers(f_grade):
			f_teacher = relevant_teachers(f_grade)[0]
	students = students_list(f_grade,f_teacher,f_proficiency)
	return render_template('student.html', quizzes=relevant_quiz(f_grade),students=students, grades=grades,teachers=relevant_teachers(f_grade), \
	proficiency_list=proficiency_groups, f_grade=f_grade, f_teacher=f_teacher, f_proficiency=f_proficiency,qcnt=len(relevant_quiz(f_grade)))

# by students with grade, teacher, and crt group filters
@app.route('/attempts',methods=['POST','GET'])
def retakes(f_grade = '0 - Kindergarten', f_teacher = 'Mr. Sternberg', f_proficiency='All'):	
	f_quiz = relevant_quiz(f_grade)[0]
	if request.method == 'POST':
		f_grade = request.form.getlist("r1")[0]
		f_teacher = request.form.getlist("r2")[0]
		f_proficiency = request.form.getlist("r3")[0]
		f_quiz = request.form.getlist("r4")[0]
		if f_teacher not in relevant_teachers(f_grade):
			f_teacher = relevant_teachers(f_grade)[0]
		if f_quiz not in relevant_quiz(f_grade):
			f_quiz = relevant_quiz(f_grade)[0]
	students = student_attempts(f_grade,f_teacher,f_proficiency,f_quiz)
	return render_template('retakes.html', quizzes=relevant_quiz(f_grade),students=students, grades=grades,teachers=relevant_teachers(f_grade), \
	proficiency_list=proficiency_groups, f_grade=f_grade, f_teacher=f_teacher, f_proficiency=f_proficiency,f_quiz=f_quiz,acnt=3)


##################### run #####################

if __name__ == "__main__":
	#app.run(debug = True, host='0.0.0.0', port=8080, passthrough_errors=True)
	app.run(debug = True)

