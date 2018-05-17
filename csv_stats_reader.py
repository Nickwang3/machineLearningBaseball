import pandas as pd 
import numpy as np
from mlbScraper import getPlayersStats, getPlayerIDS, getBirthYear
from salaryScraper import getSalaryData
import io
import csv
import random
from playerAndContract import Player, Contract
import pandas.io.common


#creating panda data frames for player id search and salary data search
salary_data = pd.read_csv('salary_data/salary_data.csv')

player_IDS = pd.read_csv('playerIDS/IDS.csv', encoding='ANSI')


#creates a list of all players with mlb contracts to be used for machine learning sample data POSSIBLY CHANGE SEARCH METHOD TO USE THIS DICTIONARY FASTER
def getActivePlayerList():

	dict_of_active_players = {}

	list_of_active_players = []
	list_of_player_teams = []

	#creating list of players as keys
	for playerName in salary_data.Name.values:

		list_of_active_players.append(playerName)

	#creating list of player's teams 
	for team in salary_data.Team.values:

		list_of_player_teams.append(team)

	count = 0
	for player in list_of_active_players:

		dict_of_active_players[player] = list_of_player_teams[count]
		count+=1

	return dict_of_active_players

#grabs a random active player. can be used as sample data for machine learning
def getRandomPlayer():

	dicts = getActivePlayerList()

	getRandomPlayer.player, getRandomPlayer.team = random.choice(list(dicts.items()))



#below are the get methods for retrieving data from the data bases
#these will be called to retrive data in the easiest way possible

#gets the id of a specific player
def getPlayerID(playerName, teamAbbrev):

	df = []
	#check if player entered is in data base. Must check multiple name sources because sometimes there is variance
	if playerName in player_IDS.espn_name.values and teamAbbrev in player_IDS.mlb_team.values:

		df = player_IDS[player_IDS.espn_name==playerName]

	elif playerName in player_IDS.mlb_name.values and teamAbbrev in player_IDS.mlb_team.values:

		df = player_IDS[player_IDS.mlb_name==playerName]

	elif playerName in player_IDS.cbs_name.values and teamAbbrev in player_IDS.mlb_team.values:

		df = player_IDS[player_IDS.cbs_name==playerName]
	else:
		print("player not found (Possibly changed teams recently)")
		return -1

	#checking if there are players with the same name
	if len(df.index) > 1:
		for row in df.itertuples(index=True, name='Pandas'):

			if str(getattr(row, "mlb_team"))==teamAbbrev:
				return str(int(getattr(row, "espn_id")))
	else:
		for row in df.itertuples(index=True, name='Pandas'):

			return str(int(getattr(row, "espn_id")))




def get_USA_name(playerName):
	pass

#finds the players current team (STRING)
def getPlayerTeam(playerName):

	#check if player entered is in data base
	if playerName in salary_data.Name.values:

		indx = salary_data[salary_data['Name']==playerName].index.item()
		team = salary_data.at[indx, 'Team']
		team = str(team.strip())

	else:

		print()
		print("Player not found")
		return

	return team

#finds the players position
def getPlayerPos(playerName):

	#check if player entered is in data base
	if playerName in salary_data.Name.values:

		indx = salary_data[salary_data['Name']==playerName].index.item()
		position = salary_data.at[indx, 'POS']
		position = str(position.strip())

	else:

		print()
		print("Player not found")
		return

	return position

#return true if pitcher
def isPitcher(playerName):

	pos = getPlayerPos(playerName)

	if pos == 'RP' or pos == 'SP':
		return True 
	return False

#finds a players current salary value for current year in (INTEGER)
def getCurrentYearSalary(playerName):

	#check if player entered is in data base
	if playerName in salary_data.Name.values:

		indx = salary_data[salary_data['Name']==playerName].index.item()
		salary = salary_data.at[indx, 'Salary']
		salary = int(salary[2:].replace(",", ""))

	else:

		print()
		print("Player not found")
		return

	return salary

def getAverageAnnualSalary(playerName):

	#check if player entered is in data base
	if playerName in salary_data.Name.values:

		indx = salary_data[salary_data['Name']==playerName].index.item()
		salary = salary_data.at[indx, 'Avg Annual']
		salary = int(salary[1:].replace(",", ""))

	else:

		print()
		print("Player not found")
		return

	return salary

#finds the contracts total value
def getTotalContractValue(playerName):

	#check if player entered is in data base
	if playerName in salary_data.Name.values:

		indx = salary_data[salary_data['Name']==playerName].index.item()
		salary = salary_data.at[indx, 'Total Value']
		salary = int(salary[1:].replace(",", ""))

	else:

		print()
		print("Player not found")
		return

	return salary

#finds num of years contract is active for (INTEGER)
def getContractLength(playerName):

	#check if player entered is in data base
	if playerName in salary_data.Name.values:

		indx = salary_data[salary_data['Name']==playerName].index.item()
		years = salary_data.at[indx, 'Years']
		indx_paren = years.index("(")
		years = int(years[:indx_paren].strip())

	else:

		print()
		print("Player not found")
		return 

	return years

#gets year span that contract is active in (STRING)
def getContractYears(playerName):
	
	#check if player entered is in data base
	if playerName in salary_data.Name.values:

		indx = salary_data[salary_data['Name']==playerName].index.item()
		years = salary_data.at[indx, 'Years']
		indx_paren = years.index("(")
		indx_close = years.index(")")
		years = years[indx_paren+1:indx_close].strip()

	else:

		print()
		print("Player not found")
		return 

	return years

#gets the year of signing (INTEGER)
def getContractSignYear(playerName):

	#check if player entered is in data base
	if playerName in salary_data.Name.values:

		indx = salary_data[salary_data['Name']==playerName].index.item()
		years = salary_data.at[indx, 'Years']
		indx_paren = years.index("(")
		indx_dash = years.find("-")
		year_signed = int(years[indx_paren+1:indx_dash])


	else:

		print()
		print("Player not found")
		return 

	return year_signed


# gets the players standard stats  (DATAFRAME)
def getStats(playerName, teamAbbrev):

	espn_id = getPlayerID(playerName, teamAbbrev)
	getPlayersStats(espn_id, playerName)

	player_file_name = playerName.replace(" ", "-")

	#looks for player stats file in folder
	try:
		player_stats = pd.read_csv('baseballStatsPlayers/' + player_file_name + ".csv")
	except (FileNotFoundError, TypeError, pandas.io.common.EmptyDataError):
		# print("That player does not exist or has no stats prior to signing")
		return -1

	return player_stats


# gets the players stats from the years prior to the signing of the newest contract (DATAFRAME)
def getStatsBeforeSigning(playerName, teamAbbrev):

	espn_id = getPlayerID(playerName, teamAbbrev)

	getPlayersStats(espn_id, playerName)

	player_file_name = playerName.replace(" ", "-")


	#looks for player stats file in folder
	try:
		player_stats = pd.read_csv('baseballStatsPlayers/' + player_file_name + ".csv")
	except (FileNotFoundError, TypeError, pandas.io.common.EmptyDataError):
		# print("That player does not exist or has no stats prior to signing")
		return -1



	year_signed = getContractSignYear(playerName)

	try:
		player_stats = player_stats[(player_stats[['SEASON']] < year_signed).all(axis=1)]
	except KeyError:
		player_stats = player_stats[(player_stats[['YEAR']] < year_signed).all(axis=1)]
	#checks if player has stats before being signed
	# try:
	# 	indx = player_stats[player_stats['YEAR'].astype(int)==year_signed].index.item()
	# except KeyError:
	# 	indx = player_stats[player_stats['SEASON'].astype(int)==year_signed].index.item()
	# except ValueError:
	# 	print("This player has no stats from previous years")
	# 	return

	if isPitcher(playerName):
		age = year_signed - getBirthYear('http://www.espn.com/mlb/player/stats/_/id/' + getPlayerID(playerName, teamAbbrev) + "/" + playerName)
	else:
		age = year_signed - getBirthYear('http://www.espn.com/mlb/player/stats/_/id/' + getPlayerID(playerName, teamAbbrev) + "/" + playerName)

	# if isPitcher(playerName):
	# 	adjusted_stats = player_stats.ix[~(player_stats['SEASON'] > year_signed)]
	# else:
	# 	adjusted_stats = player_stats.ix[~(player_stats['YEAR'] > year_signed)]

	return player_stats, age


#will only be used inside playerObjectFunction
def createContractObject(playerName):

	length = getContractLength(playerName)
	years = getContractYears(playerName)
	total_value = getTotalContractValue(playerName)
	current_salary = getCurrentYearSalary(playerName)
	avg_value = getAverageAnnualSalary(playerName)
	sign_year = getContractSignYear(playerName)


	contract = Contract(length, years, total_value, current_salary, avg_value, sign_year)

	return contract


#creates an mlb player object 
def createPlayerObject():

	getRandomPlayer()
	name = getRandomPlayer.player
	team = getRandomPlayer.team

	print(name)																						#This line is used for testing when there are errors. It will tell me which player is breaking

	stats = getStats(name, team)

	try:
		stats_before_signing, age_at_signing = getStatsBeforeSigning(name, team)
	except TypeError:
		return -1           #player has no previous stats return null for error

	position = getPlayerPos(name)

	#calls the contract method to create contract object for player
	contract = createContractObject(name)


	player = name+team
	#creating the player object
	player = Player(name, team, stats, stats_before_signing, position, contract, age_at_signing)

	return player



#creates a random player object with attributes
def main():

	getPlayerIDS()
	getSalaryData()
	getActivePlayerList()

	#below is user input program (commented out) vs an automated random selection of a player


	# player1 = createPlayerObject()
	# try:
	# 	print(player1.name)
	# 	print(player1.stats_before_signing)
	# 	print(player1.contract.length)
	# 	print(player1.contract.total_value)
	# 	print(player1.age_at_signing)
	# 	print(player1.contract.sign_year)
	# except:
	# 	return -1


	# print(getStatsBeforeSigning("Jordan Hicks", "STL"))
	# print(getStatsBeforeSigning("Mike Trout", "LAA"))
	# print(getStatsBeforeSigning("Nathan Karns", "KC"))

	# print(getStatsBeforeSigning("Tim Lincecum", "TEX"))
	# print(getStats("Billy Hamilton", "CIN"))
	# print(getPlayerID("Billy Hamilton", "CIN"))
	# print(getStatsBeforeSigning("Billy Hamilton", "CIN"))

	# print(getStatsBeforeSigning("Eric Hosmer", "SD"))
	# print(getStatsBeforeSigning("Brad Keller","KC"))
