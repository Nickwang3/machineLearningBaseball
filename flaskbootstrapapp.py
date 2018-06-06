from flask import Flask, render_template, request, redirect, flash
from flask_bootstrap import Bootstrap 
import pandas as pd 
from pandas import DataFrame
from flask_nav import Nav
from flask_nav.elements import Navbar, View
from wtforms import Form, StringField
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
from forms import SearchNameForm
import locale
import dataset
from dataManipulation import convert_stats_to_dataframe




db = dataset.connect('postgresql://baseball_project:baseball_project@localhost:5432/player_database')

table = db['players']


app = Flask(__name__)
Bootstrap(app)
app.secret_key = 'development key'


@app.route('/')
def index():
	return render_template("index.html")


@app.route('/about')
def about():
	return render_template("about.html")

@app.route('/prediction-models')
def models():

	rankings_0 = pd.DataFrame(columns=("Rank","Name","Salary Predicted"))
	result = db.query('SELECT * FROM players ORDER BY weighted_war_salary_prediction DESC NULLS LAST LIMIT 20')

	count = 0
	for row in result:
		rankings_0.loc[count] = [count + 1, row['name'], '{0:,d}'.format(row['weighted_war_salary_prediction'])]
		count+=1	

	#average war
	rankings_1 = pd.DataFrame(columns=("Rank","Name","Salary Predicted"))
	result = db.query('SELECT * FROM players ORDER BY average_war_salary_prediction DESC NULLS LAST LIMIT 20')

	count = 0
	for row in result:
		rankings_1.loc[count] = [count + 1, row['name'], '{0:,d}'.format(row['average_war_salary_prediction'])]
		count+=1

	#peak war
	rankings_2 = pd.DataFrame(columns=("Rank","Name","Salary Predicted"))
	result = db.query('SELECT * FROM players ORDER BY peak_war_salary_prediction DESC NULLS LAST LIMIT 20')

	count = 0
	for row in result:
		rankings_2.loc[count] = [count + 1, row['name'], '{0:,d}'.format(row['peak_war_salary_prediction'])]
		count+=1

	#triple crown
	rankings_3 = pd.DataFrame(columns=("Rank","Name","Salary Predicted"))
	result = db.query('SELECT * FROM players ORDER BY triple_crown_salary_prediction DESC NULLS LAST LIMIT 20')

	count = 0
	for row in result:
		rankings_3.loc[count] = [count + 1, row['name'], (row['triple_crown_salary_prediction'])]
		count+=1

	return render_template("prediction_models.html",rankings_0=rankings_0, rankings_1=rankings_1, rankings_2=rankings_2, rankings_3=rankings_3)



#searches for players
@app.route('/players', methods=['GET', 'POST'])
def players():
	form = SearchNameForm()

	try:
		if form.validate_on_submit():
			name = form.player_name.data
			team = form.team.data 
			name = name.split()
			first = name[0]
			last = name[1]
			return redirect('/players/' + team + "/" + first + "-" + last)
	except AttributeError:
		# flash("That player does not exist")
		return redirect('/players')

	return render_template("players.html", form=form)



#specific player page where all kinds of stats and predictions can be found
@app.route("/players/<team>/<first>-<last>")
def return_player(first, last, team):
	name = first + " " + last
	
	players = table.find(name=name)


	length = 0
	for player in players:
		length+=1

	if length > 1:

		player = table.find_one(name=name, team=team)

	else:

		player = table.find_one(name=name)

	stats = convert_stats_to_dataframe(player['stats'])

	stats = stats.drop(columns=['Unnamed: 0'])

	weighted_war_salary = player['weighted_war_salary_prediction']
	average_war_salary = player['average_war_salary_prediction']
	peak_war_salary = player['peak_war_salary_prediction']


	if player['position'] != 'P':
		trip_salary = player['triple_crown_salary_prediction']
	else:
		trip_salary = None

	return render_template("playerpage.html", player=player, stats=stats, title=player['name'], weighted_war_salary=weighted_war_salary, average_war_salary=average_war_salary, peak_war_salary=peak_war_salary, trip_salary=trip_salary)


if __name__ == '__main__':
	app.run(debug=True)