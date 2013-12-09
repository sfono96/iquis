from flask import *
from pgdb import *
from functools import wraps

##################### app #####################

app = Flask(__name__)
app.jinja_env.add_extension('jinja2.ext.loopcontrols') # add counter looping
app.secret_key = '5RD{Hd1CRSwCoqct4Y497&4Ar12t5V'

# login decorator
def login_required(test):
	@wraps(test)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return test(*args, **kwargs)
		else:
			flash('You need to login first dude.')
			return redirect(url_for('log'))
	return wrap

##################### routes #####################

# logout session
@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash('You were logged out')
	return redirect(url_for('log'))

# login
@app.route('/log',methods=['GET','POST'])
def log():
	error = None
	if request.method == 'POST':
		if request.form['uid'] != 'admin' or request.form['pwd'] != 'ponytracks':
			error = 'Invalid Credentials. Please try again.'
			flash(error)
			return redirect(url_for('log'))
		else:
			session['logged_in'] = True
			return redirect(url_for('grade'))
	return render_template('log.html',error=error)

# filter quizzes by grade level
@app.route('/')
@login_required
@app.route('/grade',methods=['GET','POST'])
def grade(chartID = 'chart_ID', chart_type = 'bar', chart_height = 500, f_grade = '2 - Second Grade', f_proficiency = 'All'):
	if request.method == 'POST':
		f_grade = request.form.getlist("rb")[0]
		f_proficiency = request.form.getlist("rb2")[0]
	chart = {"renderTo": chartID, "type": chart_type, "height": chart_height}
	series = [{'name':'Average Assessment Score','data':quiz(f_grade,f_proficiency)[1]}] # quiz method from pgdb module
	title_text = 'Math Assessment Tracking - %s' % str(f_grade[4:])
	title = {"text": title_text} 
	xAxis = {"categories":quiz(f_grade,f_proficiency)[0]}
	yAxis = {"min":0,"max":6,"title": {"text": 'Average Score'}}
	#plotOptions = {"series":{"dataLabels":{"enabled":"true","format":'{y} pct',"style":{"fontWeight":'bold',"fontSize":'15px'}}}}
	plotOptions = {"series":{"colorByPoint":"true"}}
	#tooltip = {"valueSuffix":' pct',"valueDecimals":1}
	tooltip = {"valueDecimals":2}
	return render_template('grade.html', chartID=chartID, chart=chart, series=series, title=title, xAxis=xAxis, yAxis=yAxis, plotOptions=plotOptions, tooltip=tooltip,grades=grades, \
	proficiency_list=proficiency_groups, f_grade=f_grade,f_proficiency=f_proficiency)

# by teacher with grade and crt group filters
@app.route('/teachers',methods=['POST','GET'])
@login_required
def teachers(chartID = 'chart_ID', chart_type = 'column', chart_height = 500, f_grade='2 - Second Grade', f_proficiency='All'):	
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
	yAxis = {"min":0,"max":6,"title": {"text": 'Average Score'}}
	plotOptions = {"series":{"colorByPoint":"true","dataLabels":{"enabled":"true","format":'{point.y:.2f}',"valueDecimals":2,"inside":"true","color":"white","style":{"fontWeight":'bold',"fontSize":'20px'}}}}
	#plotOptions = {"series":{"colorByPoint":"true","dataLabels":{"enabled":"true","valueDecimals":2,"inside":"true","color":"white","style":{"fontWeight":'bold',"fontSize":'20px'}}}}
	#tooltip = {"valueSuffix":' pct',"valueDecimals":1}
	tooltip = {"valueDecimals":2}
	return render_template('teacher.html', chartID=chartID, chart=chart, series=series, title=title, xAxis=xAxis, yAxis=yAxis, plotOptions=plotOptions, tooltip=tooltip,grades=grades, \
	proficiency_list=proficiency_groups, quizzes = relevant_quiz(f_grade), f_grade=f_grade, f_proficiency=f_proficiency,f_quiz=f_quiz)

# by students with grade, teacher, and crt group filters
@app.route('/students',methods=['POST','GET'])
@login_required
def students(f_grade = '2 - Second Grade', f_teacher = 'Monteath, Chelcie', f_proficiency='All'):	
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
# @app.route('/attempts',methods=['POST','GET'])
# @login_required
# def retakes(f_grade = '0 - Kindergarten', f_teacher = 'Mr. Sternberg', f_proficiency='All'):	
# 	f_quiz = relevant_quiz(f_grade)[0]
# 	if request.method == 'POST':
# 		f_grade = request.form.getlist("r1")[0]
# 		f_teacher = request.form.getlist("r2")[0]
# 		f_proficiency = request.form.getlist("r3")[0]
# 		f_quiz = request.form.getlist("r4")[0]
# 		if f_teacher not in relevant_teachers(f_grade):
# 			f_teacher = relevant_teachers(f_grade)[0]
# 		if f_quiz not in relevant_quiz(f_grade):
# 			f_quiz = relevant_quiz(f_grade)[0]
# 	students = student_attempts(f_grade,f_teacher,f_proficiency,f_quiz)
# 	return render_template('retakes.html', quizzes=relevant_quiz(f_grade),students=students, grades=grades,teachers=relevant_teachers(f_grade), \
# 	proficiency_list=proficiency_groups, f_grade=f_grade, f_teacher=f_teacher, f_proficiency=f_proficiency,f_quiz=f_quiz,acnt=3)


##################### run #####################

if __name__ == "__main__":
	#app.run(debug = True, host='0.0.0.0', port=8080, passthrough_errors=True)
	app.run(debug = True)

