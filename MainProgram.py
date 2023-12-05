import sqlite3  # Module for working with SQLite databases
import random  # Module for generating random numbers
import tkinter as tk  # Module for creating GUI applications
from tkinter import ttk
import downton
from tabulate import tabulate  # Module for creating tables from data
import threading
from PIL import ImageTk, Image
from tkinter import *
import time

window = tk.Tk()
window.attributes("-fullscreen", True)
window.title("Football Match Predictor")
window.configure(bg="gray20")


def CalcThreatRating(t1, t2):
    teams = [t1, t2]
    teamids = ["t1", "t2"]
    teamratings = []
    for x in range(0, 2):
        teamid = teamids[x]
        defrating = []
        midrating = []
        attrating = []
        connection = sqlite3.connect("TeamsDatabase.db")
        cursor = connection.cursor()
        positionsandratings = cursor.execute(
            "SELECT position, rating, form FROM players WHERE abbreviation = ? AND injury = ?",
            (teams[x], '0')).fetchall()
        for set in positionsandratings:
            if set[0] == "(G)" or set[0] == "(RB)" or set[0] == "(LB)" or set[0] == "(CB)":
                defrating.append(int(set[1]) + int(set[2]))
            elif set[0] == "(CM)" or set[0] == "(CAM)" or set[0] == "(CDM)":
                midrating.append(int(set[1]) + int(set[2]))
            elif set[0] == "(ST)" or set[0] == "(RW)" or set[0] == "(LW)":
                attrating.append(int(set[1]) + int(set[2]))
        ovrRating = round(((sum(defrating) / len(defrating) if defrating else 0) + (
            sum(midrating) / len(midrating) if midrating else 0) + (
                               sum(attrating) / len(attrating) if attrating else 0)) / 3)
        homeadvantage = random.randint(2, 6)
        if teamid == "t1":
            ovrRating += homeadvantage
        teamratings.append(ovrRating)
        connection.close()
    return teamratings[0], teamratings[1]


def ChooseGoalScorer(teamplayernames, positiontouse, aspositiontouse):
    potentialscorers = []
    potentialassisters = []
    indexes = []
    teamplayernames = downton.MergeSort().sort(teamplayernames, 5)
    for player in teamplayernames:
        if aspositiontouse in player:
            potentialassisters.append(player)
        if positiontouse in player:
            potentialscorers.append(player)
    howmany = 30
    initialindex = 0
    if len(potentialscorers) > 1:
        for x in range(len(potentialscorers)):
            for y in range(howmany):
                indexes.append(initialindex)
            howmany = round(howmany / 3)
            initialindex += 1
        random.shuffle(indexes)
        index = random.choice(indexes)
        goalscorer = potentialscorers[index]
    else:
        goalscorer = potentialscorers[0]
    if len(potentialassisters) > 1:
        assister = random.choice(potentialassisters)
        while assister == goalscorer:
            assister = random.choice(potentialassisters)
    elif len(potentialassisters) == 1:
        assister = potentialassisters[0]
        while assister == goalscorer:
            assister = random.choice(teamplayernames)
    else:
        assister = random.choice(teamplayernames)
        while assister == goalscorer:
            assister = random.choice(teamplayernames)
    return goalscorer, assister


def AssignGoalsAndAssistsToPlayers(t1, t2, t1score, t2score, score, fixtureresult):
    positionsforscorers = ["(ST)"] * 60 + ["(CAM)", "(LW)", "(RW)"] * 20 + ["(CM)", "(CDM)"] * 10 + ["(LB)",
                                                                                                     "(RB)"] * 5 + [
                              "(CB)"] * 2
    positionsforassisters = ["(ST)"] * 20 + ["(CAM)", "(LW)", "(RW)"] * 40 + ["(CM)", "(CDM)"] * 30 + ["(LB)",
                                                                                                       "(RB)"] * 20 + [
                                "(CB)"] * 10 + ["(G)"] * 10
    positiontouse = ""
    aspositiontouse = ""
    connection = sqlite3.connect('TeamsDatabase.db')
    cursor = connection.cursor()
    if fixtureresult == "draw":
        for y in range(score):
            team1playernames = cursor.execute("SELECT * FROM players WHERE abbreviation = ? AND injury = ?",
                                              (t1, '0')).fetchall()
            x = 0
            while x == 0:
                random.shuffle(positionsforscorers)
                random.shuffle(positionsforassisters)
                positiontouse = random.choice(positionsforscorers)
                aspositiontouse = random.choice(positionsforassisters)
                for player in team1playernames:
                    if positiontouse in player:
                        x += 1
            goalscorer, assister = ChooseGoalScorer(team1playernames, positiontouse, aspositiontouse)
            appendgoals = int(goalscorer[6]) + 1
            appendassists = int(assister[7]) + 1
            appendgsform = int(goalscorer[9]) + 1
            appendasform = int(assister[9]) + 1
            cursor.execute(
                "UPDATE players SET goalcount = ?, form = ? WHERE name = ? AND abbreviation = ? AND position = ?",
                (appendgoals, appendgsform, goalscorer[2], goalscorer[1], positiontouse))
            cursor.execute(
                "UPDATE players SET assistcount = ?, form = ? WHERE name = ? AND abbreviation = ? AND position = ?",
                (appendassists, appendasform, assister[2], assister[1], aspositiontouse))
        for x in range(score):
            team2playernames = cursor.execute("SELECT * FROM players WHERE abbreviation = ? AND injury = ?",
                                              (t2, '0')).fetchall()
            x = 0
            while x == 0:
                positiontouse = random.choice(positionsforscorers)
                aspositiontouse = random.choice(positionsforassisters)
                for player in team2playernames:
                    if positiontouse in player:
                        x += 1
            goalscorer, assister = ChooseGoalScorer(team2playernames, positiontouse, aspositiontouse)
            appendgoals = int(goalscorer[6]) + 1
            appendassists = int(assister[7]) + 1
            appendgsform = int(goalscorer[9]) + 1
            appendasform = int(assister[9]) + 1
            cursor.execute(
                "UPDATE players SET goalcount = ?, form = ? WHERE name = ? AND abbreviation = ? AND position = ?",
                (appendgoals, appendgsform, goalscorer[2], goalscorer[1], positiontouse))
            cursor.execute(
                "UPDATE players SET assistcount = ?, form = ? WHERE name = ? AND abbreviation = ? AND position = ?",
                (appendassists, appendasform, assister[2], assister[1], aspositiontouse))
    elif fixtureresult == "nondraw":
        for x in range(t1score):
            team1playernames = cursor.execute("SELECT * FROM players WHERE abbreviation = ? AND injury = ?",
                                              (t1, '0')).fetchall()
            x = 0
            while x == 0:
                positiontouse = random.choice(positionsforscorers)
                aspositiontouse = random.choice(positionsforassisters)
                for player in team1playernames:
                    if positiontouse in player:
                        x += 1
            goalscorer, assister = ChooseGoalScorer(team1playernames, positiontouse, aspositiontouse)
            appendgoals = int(goalscorer[6]) + 1
            appendassists = int(assister[7]) + 1
            appendgsform = int(goalscorer[9]) + 1
            appendasform = int(assister[9]) + 1
            cursor.execute(
                "UPDATE players SET goalcount = ?, form = ? WHERE name = ? AND abbreviation = ? AND position = ?",
                (appendgoals, appendgsform, goalscorer[2], goalscorer[1], positiontouse))
            cursor.execute(
                "UPDATE players SET assistcount = ?, form = ? WHERE name = ? AND abbreviation = ? AND position = ?",
                (appendassists, appendasform, assister[2], assister[1], aspositiontouse))
        for x in range(t2score):
            team2playernames = cursor.execute("SELECT * FROM players WHERE abbreviation = ? AND injury = ?",
                                              (t2, '0')).fetchall()
            x = 0
            while x == 0:
                positiontouse = random.choice(positionsforscorers)
                aspositiontouse = random.choice(positionsforassisters)
                for player in team2playernames:
                    if positiontouse in player:
                        x += 1
            goalscorer, assister = ChooseGoalScorer(team2playernames, positiontouse, aspositiontouse)
            appendgoals = int(goalscorer[6]) + 1
            appendassists = int(assister[7]) + 1
            appendgsform = int(goalscorer[9]) + 1
            appendasform = int(assister[9]) + 1
            cursor.execute(
                "UPDATE players SET goalcount = ?, form = ? WHERE name = ? AND abbreviation = ? AND position = ?",
                (appendgoals, appendgsform, goalscorer[2], goalscorer[1], positiontouse))
            cursor.execute(
                "UPDATE players SET assistcount = ?, form = ? WHERE name = ? AND abbreviation = ? AND position = ?",
                (appendassists, appendasform, assister[2], assister[1], aspositiontouse))
    connection.commit()
    connection.close()


def DecideTheWinnerOfTheFixture(t1, t2, t1prcntg, t2prcntg):
    global score, t1score, t2score, fixtureresult
    connection = sqlite3.connect("TeamsDatabase.db")
    cursor = connection.cursor()
    possiblescores = [1] * 250 + [2] * 200 + [3] * 150 + [4] * 100 + [5] * 20 + [6, 7, 8, 9]
    drawscores = [0] * 200 + [1] * 125 + [2] * 75 + [3] * 50 + [4] * 5
    draw = random.randint(1, 8)
    result = f"{t1} vs {t2} => "
    if draw == 5 or t1prcntg == t2prcntg:
        fixtureresult = "draw"
        score = random.choice(drawscores)
        team_points[t1][1] += 1
        team_points[t1][3] += 1
        team_points[t2][1] += 1
        team_points[t2][3] += 1
        team_points[t1][4] += score
        team_points[t1][5] += score
        team_points[t2][4] += score
        team_points[t2][5] += score
        result += f"{score} - {score}"
        AssignGoalsAndAssistsToPlayers(t1, t2, t1score, t2score, score, fixtureresult)
        if score == 0:
            t1keepers = []
            t2keepers = []
            gett1gks = cursor.execute(
                "SELECT name, goalcount, rating FROM players WHERE abbreviation = ? AND position = ? AND injury = ?",
                (t1, "(G)", 0))
            for player in gett1gks:
                t1keepers.append(player)
            t1gks = downton.MergeSort().sort(t1keepers, 2)
            t1newcs = int(t1gks[0][1]) + 1
            cursor.execute("UPDATE players SET goalcount = ? WHERE abbreviation = ? AND name = ? AND position = ?",
                           (t1newcs, t1, t1gks[0][0], "(G)"))
            gett2gks = cursor.execute(
                "SELECT name, goalcount, rating FROM players WHERE abbreviation = ? AND position = ? AND injury = ?",
                (t2, "(G)", 0))
            for player in gett2gks:
                t2keepers.append(player)
            t2gks = downton.MergeSort().sort(t2keepers, 2)
            t2newcs = int(t2gks[0][1]) + 1
            cursor.execute("UPDATE players SET goalcount = ? WHERE abbreviation = ? AND name = ? AND position = ?",
                           (t2newcs, t2, t2gks[0][0], "(G)"))
            connection.commit()
        return result
    elif t1prcntg > t2prcntg:
        fixtureresult = "nondraw"
        t1score = random.choice(possiblescores)
        t2score = random.choice([score for score in drawscores if score <= t1score])
        team_points[t1][0] += 1
        team_points[t1][3] += 3
        team_points[t2][2] += 1
        team_points[t1][4] += t1score
        team_points[t1][5] += t2score
        team_points[t2][4] += t2score
        team_points[t2][5] += t1score
        team_points[t1][6] = team_points[t1][4] - team_points[t1][5]
        team_points[t2][6] = team_points[t2][4] - team_points[t2][5]
        result += f"{t1score} - {t2score}"
        AssignGoalsAndAssistsToPlayers(t1, t2, t1score, t2score, score, fixtureresult)
        t1forms = cursor.execute("SELECT name, form FROM players WHERE abbreviation = ?", (t1,))
        for player in t1forms:
            newform = int(player[1]) + 1
            cursor.execute("UPDATE players SET form = ? WHERE abbreviation = ? AND name = ?", (newform, t1, player[0]))
        t2forms = cursor.execute("SELECT name, form FROM players WHERE abbreviation = ?", (t2,))
        for player in t2forms:
            newform = int(player[1]) - 1
            cursor.execute("UPDATE players SET form = ? WHERE abbreviation = ? AND name = ?", (newform, t2, player[0]))
        connection.commit()
        if t2score == 0:
            keepers = []
            gett1gks = cursor.execute(
                "SELECT name, goalcount, rating FROM players WHERE abbreviation = ? AND position = ? AND injury = ?",
                (t1, "(G)", 0))
            for player in gett1gks:
                keepers.append(player)
            t1gks = downton.MergeSort().sort(keepers, 2)
            t1newcs = int(t1gks[0][1]) + 1
            cursor.execute("UPDATE players SET goalcount = ? WHERE abbreviation = ? AND name = ? AND position = ?",
                           (t1newcs, t1, t1gks[0][0], "(G)"))
            connection.commit()
        elif t1score == 0:
            keepers = []
            gett2gks = cursor.execute(
                "SELECT name, goalcount, rating FROM players WHERE abbreviation = ? AND position = ? AND injury = ?",
                (t2, "(G)", 0))
            for player in gett2gks:
                keepers.append(player)
            t2gks = downton.MergeSort().sort(keepers, 2)
            t2newcs = int(t2gks[0][1]) + 1
            cursor.execute("UPDATE players SET goalcount = ? WHERE abbreviation = ? AND name = ? AND position = ?",
                           (t2newcs, t2, t2gks[0][0], "(G)"))
            connection.commit()
        return result
    elif t1prcntg < t2prcntg:
        fixtureresult = "nondraw"
        t2score = random.choice(possiblescores)
        t1score = random.choice([score for score in drawscores if score <= t2score])
        team_points[t2][0] += 1
        team_points[t2][3] += 3
        team_points[t1][2] += 1
        team_points[t1][4] += t1score
        team_points[t1][5] += t2score
        team_points[t2][4] += t2score
        team_points[t2][5] += t1score
        team_points[t1][6] = team_points[t1][4] - team_points[t1][5]
        team_points[t2][6] = team_points[t2][4] - team_points[t2][5]
        result += f"{t1score} - {t2score}"
        AssignGoalsAndAssistsToPlayers(t1, t2, t1score, t2score, score, fixtureresult)
        t1forms = cursor.execute("SELECT name, form FROM players WHERE abbreviation = ?", (t1,))
        for player in t1forms:
            newform = int(player[1]) - 1
            cursor.execute("UPDATE players SET form = ? WHERE abbreviation = ? AND name = ?", (newform, t1, player[0]))
        t2forms = cursor.execute("SELECT name, form FROM players WHERE abbreviation = ?", (t2,))
        for player in t2forms:
            newform = int(player[1]) + 1
            cursor.execute("UPDATE players SET form = ? WHERE abbreviation = ? AND name = ?", (newform, t2, player[0]))
        connection.commit()
        if t2score == 0:
            keepers = []
            gett1gks = cursor.execute(
                "SELECT name, goalcount, rating FROM players WHERE abbreviation = ? AND position = ? AND injury = ?",
                (t1, "(G)", 0))
            for player in gett1gks:
                keepers.append(player)
            t1gks = downton.MergeSort().sort(keepers, 2)
            t1newcs = int(t1gks[0][1]) + 1
            cursor.execute("UPDATE players SET goalcount = ? WHERE abbreviation = ? AND name = ? AND position = ?",
                           (t1newcs, t1, t1gks[0][0], "(G)"))
            connection.commit()
        elif t1score == 0:
            keepers = []
            gett2gks = cursor.execute(
                "SELECT name, goalcount, rating FROM players WHERE abbreviation = ? AND position = ? AND injury = ?",
                (t2, "(G)", 0))
            for player in gett2gks:
                keepers.append(player)
            t2gks = downton.MergeSort().sort(keepers, 2)
            t2newcs = int(t2gks[0][1]) + 1
            cursor.execute("UPDATE players SET goalcount = ? WHERE abbreviation = ? AND name = ? AND position = ?",
                           (t2newcs, t2, t2gks[0][0], "(G)"))
            connection.commit()
        return result


def CalculateTeamsChanceToWin(game):
    t1 = game[:3]  # Extract the team 1 abbreviation
    t2 = game[-3:]  # Extract the team 2 abbreviation
    t1tr, t2tr = CalcThreatRating(t1, t2)
    prcntg = 100 / (t1tr + t2tr)  # Calculate the percentage factor
    t1prcntg = t1tr * prcntg  # Calculate team 1's win percentage
    t2prcntg = 100 - t1prcntg  # Calculate team 2's win percentage (assuming a draw is not possible)
    result = DecideTheWinnerOfTheFixture(t1, t2, t1prcntg, t2prcntg)
    return result


def ProcessNextMatchday():
    global matchday
    connection = sqlite3.connect('TeamsDatabase.db')
    cursor = connection.cursor()
    testTab['state'] = tk.NORMAL
    resultTab['state'] = tk.NORMAL
    cleansheetTab['state'] = tk.NORMAL
    testTab.delete("1.0", tk.END)
    cleansheetTab.delete("1.0", tk.END)
    matchday_filename = f"matchdays/matchday{matchday}.txt"  # Generate the filename for the current matchday
    with open(matchday_filename, "r") as m:
        games = str(m.readlines()).replace("[", "").replace("]", "").replace("'", "").split(",")
    resultTab.delete("1.0", tk.END)  # Clear the resultText widget
    if len(str(matchday)) == 1:
        matchdayno = "0" + str(matchday)
    else:
        matchdayno = str(matchday)
    resultTab.insert(tk.END, f"==== Matchday {matchdayno} ===\n")  # Display the current matchday
    for game in games:  # Process each game
        result = CalculateTeamsChanceToWin(game)  # Calculate the result of the game
        resultTab.insert(tk.END, result + "\n")  # Display the result
    testTab.insert(tk.END, "===== League Top Goalscorers ======\n")
    allplayersforgctallies = []
    gctallies = cursor.execute(
        "SELECT goalcount, assistcount, abbreviation, position, name FROM players").fetchall()
    for player in gctallies:
        if player[3] != "(G)":
            allplayersforgctallies.append(player)
    gctallies = downton.MergeSort().sort(allplayersforgctallies, 0)
    for x in range(1, 6):
        playertallies = str(gctallies[x])
        x = str(x)
        playertallies = playertallies.replace("(", "").replace(")", "").replace("'", "")
        if len(x) == 1:
            x = " " + x
        testTab.insert(tk.END, "" + x + ". " + playertallies + "\n")
    testTab.insert(tk.END, "===================================")
    cleansheetTab.insert(tk.END, "==== Top GKeepers ====\n")
    cstalliesarr = []
    cstallies = cursor.execute("SELECT goalcount, abbreviation, name FROM players WHERE position = ?",
                               ("(G)",)).fetchall()
    for player in cstallies:
        cstalliesarr.append(player)
    cstallies = downton.MergeSort().sort(cstalliesarr, 0)
    for x in range(1, 6):
        playertallies = str(cstallies[x])
        x = str(x)
        playertallies = playertallies.replace("(", "").replace(")", "").replace("'", "")
        if len(x) == 1:
            x = " " + x
        cleansheetTab.insert(tk.END, "" + x + ". " + playertallies + "\n")
    cleansheetTab.insert(tk.END, "======================")
    CheckForInjuries()
    DisplayTable()
    testTab['state'] = tk.DISABLED
    resultTab['state'] = tk.DISABLED
    cleansheetTab['state'] = tk.DISABLED
    matchday += 1  # Increment the matchday counter
    if matchday == 39:
        DisplayTable2()
        repeatButton['state'] = tk.NORMAL
        nextMatchdayButton['state'] = tk.DISABLED
        skipButton['state'] = tk.DISABLED
        transferButton['state'] = tk.DISABLED
        injuriesButton['state'] = tk.DISABLED
        chancesButton['state'] = tk.DISABLED
        editPlayerButton['state'] = tk.DISABLED


def DisplayTable():
    leagueTable['state'] = tk.NORMAL
    sortedTable = sorted(team_points.items(), key=lambda x: (x[1][3], x[1][6], x[1][4]), reverse=True)
    Table = [[team, points[0], points[1], points[2], points[4], points[5], points[6], points[3]] for team, points in
             sortedTable]
    headers = ["POS", "TEAM", "W", "D", "L", "GF", "GA", "GD", "PTS"]
    Table = [[i + 1] + row for i, row in enumerate(Table)]
    leagueTable.delete("1.0", tk.END)
    leagueTable.insert(tk.END, tabulate(Table, headers=headers, tablefmt="csv"))
    leagueTable['state'] = tk.DISABLED

def DisplayTable2():
    leagueTable['state'] = tk.NORMAL
    sortedTable = sorted(team_points.items(), key=lambda x: (x[1][3], x[1][6], x[1][4]), reverse=True)
    Table = [[team, points[0], points[1], points[2], points[4], points[5], points[6], points[3]] for team, points in
             sortedTable]
    for x in range(len(sortedTable)):
        with open('filetest.txt', "a") as filetest:
            filetest.write(str(Table[x][0]))
            x+=1
            filetest.write("\n")
            if x == 20:
                filetest.write("\n")
    headers = ["POS", "TEAM", "W", "D", "L", "GF", "GA", "GD", "PTS"]
    Table = [[i + 1] + row for i, row in enumerate(Table)]
    leagueTable.delete("1.0", tk.END)
    leagueTable.insert(tk.END, tabulate(Table, headers=headers, tablefmt="csv"))
    leagueTable['state'] = tk.DISABLED


def SkipRemainingMatchdays():
    global matchday
    while matchday < 39:
        ProcessNextMatchday()
    repeatButton['state'] = tk.NORMAL
    skipButton['state'] = tk.DISABLED
    nextMatchdayButton['state'] = tk.DISABLED

def CloseProgram():
    RevertChanges()
    window.destroy()


def RevertChanges():
    connection = sqlite3.connect("MasterDatabase.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM players")
    result = cursor.fetchall()
    playerdata = []
    for row in result:
        playerdata.append(row)
    connection.commit()
    connection.close()
    connection = sqlite3.connect("TeamsDatabase.db")
    cursor = connection.cursor()
    cursor.execute("DROP TABLE players")
    connection.commit()
    sqlCommand = """
    CREATE TABLE players
    (idnumber INTEGER,
    abbreviation TEXT,
    name TEXT,
    number INTEGER,
    position INTEGER,
    rating INTEGER,
    goalcount INTEGER,
    assistcount INTEGER,
    injury INTEGER,
    form INTEGER,
    primary key (idnumber)
    )"""
    cursor.execute(sqlCommand)
    connection.commit()
    for playertoadd in playerdata:
        cursor.execute('INSERT INTO players VALUES(?,?,?,?,?,?,?,?,?,?)', playertoadd)
    connection.commit()
    connection.close()


def RepeatProcess():
    global matchday, team_points
    repeatButton['state'] = tk.DISABLED
    nextMatchdayButton['state'] = tk.NORMAL
    skipButton['state'] = tk.NORMAL
    cleansheetTab['state'] = tk.NORMAL
    testTab['state'] = tk.NORMAL
    resultTab['state'] = tk.NORMAL
    editPlayerButton['state'] = tk.NORMAL
    transferButton['state'] = tk.NORMAL
    injuriesButton['state'] = tk.NORMAL
    chancesButton['state'] = tk.NORMAL
    connection = sqlite3.connect('TeamsDatabase.db')
    cursor = connection.cursor()
    RevertChanges()
    nextMatchdayButton.configure(text="Next Matchday")
    teamdata = []  # Temporary list to store team data
    allteamsdata = []  # List to store all teams' data
    matchday = 1  # Reset the matchday counter
    team_points = {}  # Reset the team points dictionary
    leagueTable.delete("1.0", tk.END)  # Clear the resultText widget
    cursor.execute("SELECT * FROM plteams")  # Execute SQL query to fetch team data
    for row in cursor.fetchall():
        teamdata.append(row[2])  # Append team abbreviation
        teamdata.append(row[3])  # Append team name
        teamdata.append(row[4])  # Append team stadium
        teamdata.append(row[5])  # Append team rating
        allteamsdata.append(teamdata)  # Append team data to the allteamsdata list
        teamdata = []  # Reset the teamdata list
    connection.commit()
    connection.close()
    for team in allteamsdata:
        team_points[team[0]] = [0, 0, 0, 0, 0, 0, 0]
    leagueTable.delete("1.0", tk.END)
    testTab.delete("1.0", tk.END)
    resultTab.delete("1.0", tk.END)
    injuryTab.delete("1.0", tk.END)
    cleansheetTab.delete("1.0", tk.END)
    transferTab.delete("1.0", tk.END)
    injuryTab.insert(tk.END, "Injured Players:\n")
    transferTab.insert(tk.END, "Transferred Players:\n")
    testTab.insert(tk.END, "===== League Top Goalscorers ======\n\n\n\n\n\n===================================")
    cleansheetTab.insert(tk.END, "==== Top GKeepers ====\n\n\n\n\n\n======================")
    resultTab.insert(tk.END, "==== Matchday 00 ===")
    DisplayTable()
    cleansheetTab['state'] = tk.DISABLED
    testTab['state'] = tk.DISABLED
    resultTab['state'] = tk.DISABLED
    repeatButton['state'] = tk.DISABLED


def ProduceChancesTable():
    teamnames = [['MCI', 0, 0], ['BOU', 0, 0], ['MUN', 0, 0], ['ARS', 0, 0], ['TOT', 0, 0], ['CHE', 0, 0],
                 ['NEW', 0, 0], ['AVL', 0, 0],
                 ['EVE', 0, 0],
                 ['NFO', 0, 0], ['FUL', 0, 0], ['BRE', 0, 0], ['BRI', 0, 0], ['WHU', 0, 0], ['WOL', 0, 0],
                 ['LIV', 0, 0], ['LEI', 0, 0],
                 ['SOU', 0, 0],
                 ['CRY', 0, 0], ['LEE', 0, 0]]
    tableplaces = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    chancestableraw = []
    with open('filetest.txt', 'r') as f:
        x = f.readlines()
        num = 0
        for item in x:
            if item == '\n':
                num = 0
            else:
                tableplaces[num].append(item)
                num += 1

    def GiveNumTimesInEachPos(posnum):
        teamdata = [['MCI', 0, 0], ['BOU', 0, 0], ['MUN', 0, 0], ['ARS', 0, 0], ['TOT', 0, 0], ['CHE', 0, 0],
                    ['NEW', 0, 0], ['AVL', 0, 0],
                    ['EVE', 0, 0],
                    ['NFO', 0, 0], ['FUL', 0, 0], ['BRE', 0, 0], ['BRI', 0, 0], ['WHU', 0, 0], ['WOL', 0, 0],
                    ['LIV', 0, 0], ['LEI', 0, 0],
                    ['SOU', 0, 0],
                    ['CRY', 0, 0], ['LEE', 0, 0]]
        pos = []
        for x in range(len(tableplaces[posnum])):
            for team in teamdata:
                if (team[0] + "\n") == tableplaces[posnum][x]:
                    team[1] += 1
        for team in teamdata:
            pos.append(team)
        pos = downton.OppositeMergeSort().sort(pos, 0)
        chancestableraw.append(pos)
        return chancestableraw

    for x in range(len(tableplaces)):
        tabledata = GiveNumTimesInEachPos(x)

    def FindNumOfSims():
        numofsims = 0
        for set in chancestableraw:
            for item in set:
                if 'MUN' in item:
                    numofsims += item[1]
        return numofsims

    numofsims = FindNumOfSims()

    for item in tabledata:
        for team in item:
            team[2] = str(round((team[1] / numofsims) * 100))

    headers = ["Team", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17",
               "18", "19", "20"]
    finaltabledata = []
    teamnames = downton.OppositeMergeSort().sort(teamnames, 0)
    for team in teamnames:
        teamchances = []
        teamchances.append(team[0])
        for set in tabledata:
            for item in set:
                if team[0] in item:
                    teamchances.append(float(item[2]))
        finaltabledata.append(teamchances)
    return (tabulate(finaltabledata, headers=headers, tablefmt="csv"))


def TransferThePlayer():
    transferTab['state'] = tk.NORMAL
    playername = str(nameEntry.get())
    playercurrentteam = str(teamEntry.get().upper())
    playernewteam = str(teamtoEntry.get().upper())
    connection = sqlite3.connect("TeamsDatabase.db")
    cursor = connection.cursor()
    cursor.execute("UPDATE players SET abbreviation = ? WHERE name = ? AND abbreviation = ?",
                   (playernewteam, playername, playercurrentteam))
    connection.commit()
    connection.close()
    transferred = playername, "from", playercurrentteam, "to", playernewteam
    transferred = (str(transferred) + "\n").replace("(", "").replace(",", "").replace(")", "").replace("'", "").replace(
        "'", "")
    transferredplayers.append(transferred)
    transferTab.delete("1.0", tk.END)
    transferTab.insert(tk.END, "Transferred Players:\n")
    for x in range(len(transferredplayers)):
        player = transferredplayers[x]
        transferTab.insert(tk.END, player)
    transferTab['state'] = tk.DISABLED


def CloseTransferPlayerWindow():
    transferFrame.destroy()


def TransferPlayerWindow(): #open transfer player window
    global nameEntry, teamEntry, teamtoEntry, transferFrame
    transferFrame = tk.Text(window, height=24, width=34, bg="dark slate blue", borderwidth=2)
    transferFrame.place(x=400, y=200)
    transferTitle = tk.Text(transferFrame, font=("Consolas", 16, "bold", "underline"), height=1, width=20,
                            bg="dark slate blue", fg="Ghost White", borderwidth=0)
    transferTitle.place(x=0, y=0)
    transferTitle.insert(tk.END, "Transfer A Player")
    nameEntry = tk.Entry(transferFrame, font=("Consolas", 22), width=10,
                         bg="grey20", fg="Ghost White", borderwidth=2)
    nameEntry.place(x=50, y=75)
    teamEntry = tk.Entry(transferFrame, font=("Consolas", 22), width=10,
                         bg="grey20", fg="Ghost White", borderwidth=2)
    teamEntry.place(x=50, y=175)
    teamtoEntry = tk.Entry(transferFrame, font=("Consolas", 22), width=10,
                           bg="grey20", fg="Ghost White", borderwidth=2)
    teamtoEntry.place(x=50, y=275)
    nameText = tk.Text(transferFrame, font=("Consolas", 11), width=20, height=1, bg="grey20", fg="Ghost White",
                       borderwidth=2)
    nameText.place(x=50, y=50)
    teamText = tk.Text(transferFrame, font=("Consolas", 11), width=20, height=1, bg="grey20", fg="Ghost White",
                       borderwidth=2)
    teamText.place(x=50, y=150)
    teamtoText = tk.Text(transferFrame, font=("Consolas", 11), width=20, height=1, bg="grey20", fg="Ghost White",
                         borderwidth=2)
    teamtoText.place(x=50, y=250)
    nameText.insert(tk.END, "Enter Player's Name:")
    teamText.insert(tk.END, "Enter Player's Team:")
    teamtoText.insert(tk.END, "Player's New Team:")
    closeTransferWindowButton = tk.Button(transferFrame, height=1, width=2, text="X", command=CloseTransferPlayerWindow,
                                          font=("Consolas", 15, "bold"), bg="grey20", fg="Ghost White")
    closeTransferWindowButton.place(x=244, y=0)
    submitTransferButton = tk.Button(transferFrame, height=1, width=6, text="SUBMIT", command=TransferThePlayer,
                                     font=("Consolas", 12, "bold"), bg="grey20", fg="Ghost White")
    submitTransferButton.place(x=100, y=330)


def CheckForInjuries(): #check array for injured players to present them
    connection = sqlite3.connect("TeamsDatabase.db")
    cursor = connection.cursor()
    injuryTab['state'] = tk.NORMAL
    injuredplayersinfo = []
    injuredplayers = []
    cursor.execute("SELECT * FROM players")
    for row in cursor.fetchall():
        if row[8] == 1:
            injuredplayersinfo.append(row)
    injuryTab.delete("1.0", tk.END)
    injuryTab.insert(tk.END, "Injured Players:\n")
    for x in range(len(injuredplayersinfo)):
        playertuple = injuredplayersinfo[x][2], "is injured.", "[" + injuredplayersinfo[x][1] + "]"
        playerstr = (str(playertuple) + "\n").replace("(", "").replace(",", "").replace(")", "").replace("'",
                                                                                                         "").replace(
            "'", "")
        injuredplayers.append(playerstr)
    for player in injuredplayers:
        injuryTab.insert(tk.END, player)
    injuryTab['state'] = tk.DISABLED


def InjureThePlayer(): #injure the selected player
    playername = str(injureNameEntry.get().title())
    playercurrentteam = str(injureTeamEntry.get().upper())
    connection = sqlite3.connect("TeamsDatabase.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM players")
    x = 0
    for row in cursor.fetchall():
        if playername in row and playercurrentteam in row:
            x = 1
            if row[8] == 1:
                cursor.execute("UPDATE players SET injury = ? WHERE name = ? AND abbreviation = ?",
                               ('0', playername, playercurrentteam))
                connection.commit()
                statement = "This player is now uninjured"
                informofinjuryText.delete("1.0", tk.END)
                informofinjuryText.insert(tk.END, statement)
            else:
                cursor.execute("UPDATE players SET injury = ? WHERE name = ? AND abbreviation = ?",
                               ('1', playername, playercurrentteam))
                connection.commit()
                statement = "This player is now injured"
                informofinjuryText.delete("1.0", tk.END)
                informofinjuryText.insert(tk.END, statement)
        if x == 0:
            informofinjuryText.delete("1.0", tk.END)
            statement = ("This player does not exist.")
            informofinjuryText.insert(tk.END, statement)
    CheckForInjuries()


def CloseInjurePlayerWindow(): #program to close the injury window
    injureplayerFrame.destroy()


def InjurePlayerWindow(): #program for the injury window
    global injureNameEntry, injureTeamEntry, injureplayerFrame, informofinjuryText
    injureplayerFrame = tk.Text(window, height=24, width=34, bg="dark slate blue", borderwidth=2)
    injureplayerFrame.place(x=400, y=200)
    createplayerTitle = tk.Text(injureplayerFrame, font=("Consolas", 16, "bold", "underline"), height=1, width=20,
                                bg="dark slate blue", fg="Ghost White", borderwidth=0)
    createplayerTitle.place(x=0, y=0)
    createplayerTitle.insert(tk.END, "Injure A Player")
    injureNameEntry = tk.Entry(injureplayerFrame, font=("Consolas", 22), width=10,
                               bg="grey20", fg="Ghost White", borderwidth=2)
    injureNameEntry.place(x=50, y=75)
    injureTeamEntry = tk.Entry(injureplayerFrame, font=("Consolas", 22), width=10,
                               bg="grey20", fg="Ghost White", borderwidth=2)
    injureTeamEntry.place(x=50, y=175)
    nameText = tk.Text(injureplayerFrame, font=("Consolas", 11), width=20, height=1, bg="grey20", fg="Ghost White",
                       borderwidth=2)
    nameText.place(x=50, y=50)
    teamText = tk.Text(injureplayerFrame, font=("Consolas", 11), width=20, height=1, bg="grey20", fg="Ghost White",
                       borderwidth=2)
    teamText.place(x=50, y=150)
    nameText.insert(tk.END, "Enter Player's Name:")
    teamText.insert(tk.END, "Enter Player's Team:")
    closeInjurePlayerWindowButton = tk.Button(injureplayerFrame, height=1, width=2, text="X",
                                              command=CloseInjurePlayerWindow,
                                              font=("Consolas", 15, "bold"), bg="grey20", fg="Ghost White")
    closeInjurePlayerWindowButton.place(x=244, y=0)
    informofinjuryText = tk.Text(injureplayerFrame, font=("Consolas", 11), width=18, height=2, bg="grey20",
                                 fg="Ghost White", borderwidth=2)
    informofinjuryText.place(x=55, y=250)
    InjureThePlayerButton = tk.Button(injureplayerFrame, height=1, width=6, text="SUBMIT", command=InjureThePlayer,
                                      font=("Consolas", 12, "bold"), bg="grey20", fg="Ghost White")
    InjureThePlayerButton.place(x=100, y=330)


def CloseEditPlayerWindow(): #Close the player-editing window
    editFrame.destroy()


def EditThePlayer(): #Run the program that edits the player's rating
    playername = str(editNameEntry.get())
    playercurrentteam = str(editTeamEntry.get().upper())
    playernewrating = str(editRatingEntry.get())
    connection = sqlite3.connect("TeamsDatabase.db")
    cursor = connection.cursor()
    cursor.execute("UPDATE players SET rating = ? WHERE name = ? AND abbreviation = ?",
                   (playernewrating, playername, playercurrentteam))
    connection.commit()
    connection.close()
    CloseEditPlayerWindow()


def EditPlayerWindow(): #Open the window after the edit button is pressed
    global editNameEntry, editTeamEntry, editRatingEntry, editFrame
    editFrame = tk.Text(window, height=24, width=34, bg="dark slate blue", borderwidth=2)
    editFrame.place(x=400, y=200)
    transferTitle = tk.Text(editFrame, font=("Consolas", 16, "bold", "underline"), height=1, width=20,
                            bg="dark slate blue", fg="Ghost White", borderwidth=0)
    transferTitle.place(x=0, y=0)
    transferTitle.insert(tk.END, "Edit Player Ratings")
    editNameEntry = tk.Entry(editFrame, font=("Consolas", 22), width=10,
                         bg="grey20", fg="Ghost White", borderwidth=2)
    editNameEntry.place(x=50, y=75)
    editTeamEntry = tk.Entry(editFrame, font=("Consolas", 22), width=10,
                         bg="grey20", fg="Ghost White", borderwidth=2)
    editTeamEntry.place(x=50, y=175)
    editRatingEntry = tk.Entry(editFrame, font=("Consolas", 22), width=10,
                           bg="grey20", fg="Ghost White", borderwidth=2)
    editRatingEntry.place(x=50, y=275)
    nameText = tk.Text(editFrame, font=("Consolas", 11), width=20, height=1, bg="grey20", fg="Ghost White",
                       borderwidth=2)
    nameText.place(x=50, y=50)
    teamText = tk.Text(editFrame, font=("Consolas", 11), width=20, height=1, bg="grey20", fg="Ghost White",
                       borderwidth=2)
    teamText.place(x=50, y=150)
    ratingText = tk.Text(editFrame, font=("Consolas", 11), width=20, height=1, bg="grey20", fg="Ghost White",
                         borderwidth=2)
    ratingText.place(x=50, y=250)
    nameText.insert(tk.END, "Enter Player's Name:")
    teamText.insert(tk.END, "Enter Player's Team:")
    ratingText.insert(tk.END, "Enter Player's New Rating:")
    closeEditWindowButton = tk.Button(editFrame, height=1, width=2, text="X", command=CloseEditPlayerWindow,
                                          font=("Consolas", 15, "bold"), bg="grey20", fg="Ghost White")
    closeEditWindowButton.place(x=244, y=0)
    submitEditButton = tk.Button(editFrame, height=1, width=6, text="SUBMIT", command=EditThePlayer,
                                     font=("Consolas", 12, "bold"), bg="grey20", fg="Ghost White")
    submitEditButton.place(x=100, y=330)


def CloseChancesTableWindow(): #program to close the injury window
    chancestableFrame.destroy()

def ChancesTableWindow(): #program for the injury window
    global chancestableFrame, chancestableText, closechancestableWindowButton
    chancestableFrame = tk.Text(window, height=60, width=180, bg="dark slate blue", borderwidth=2)
    chancestableFrame.place(x=0, y=0)
    createplayerTitle = tk.Text(chancestableFrame, font=("Consolas", 40, "bold", "underline"), height=1, width=30,
                                bg="dark slate blue", fg="Ghost White", borderwidth=0)
    createplayerTitle.place(x=0, y=0)
    createplayerTitle.insert(tk.END, "Position Chances Table")
    closechancestableWindowButton = tk.Button(chancestableFrame, height=2, width=4, text="X",
                                              command=CloseChancesTableWindow,
                                              font=("Consolas", 15, "bold"), bg="grey20", fg="Ghost White")
    closechancestableWindowButton.place(x=1220, y=0)
    chancestableText = tk.Text(chancestableFrame, font=("Consolas", 12), width=120, height=22, bg="grey20", fg="Ghost White",
                       borderwidth=2)
    chancestableText.place(x=20, y=100)
    chancestableText['state'] = tk.NORMAL
    chancestableText.insert(tk.END, ProduceChancesTable())
    chancestableText['state'] = tk.DISABLED


def GUI():
    global leagueTable, simulationFrame, testTab, transferTab, injuryTab, nextMatchdayButton, repeatButton, skipButton, cleansheetTab, repeatTab, resultTab, transferButton, editPlayerButton, injuriesButton, chancesButton
    Title = tk.Text(window, font=("Consolas", 44, "bold", "underline"), height=1, width=35,
                    bg="dark slate blue", fg="Ghost White", borderwidth=2)
    Title.place(x=60, y=2)
    Title.insert(tk.END, " English Premier League Simulation")
    Title['state'] = tk.DISABLED
    simulationFrame = tk.Frame(window, height=740, width=1400, bg="gray20", borderwidth=2)
    simulationFrame.place(x=0, y=80)
    textFrame = tk.Frame(simulationFrame, height=725, width=990, bg="dark slate blue", borderwidth=2)
    textFrame.place(x=10, y=20)
    buttonFrame = tk.Frame(simulationFrame, height=725, width=263, bg="dark slate blue", borderwidth=2)
    buttonFrame.place(x=1000, y=20)
    nextMatchdayButton = tk.Button(buttonFrame, height=2, width=16, text="Next Fixture", command=ProcessNextMatchday,
                                   font=("Consolas", 18, "bold"), bg="gray20", fg="Ghost White")
    nextMatchdayButton.place(x=20, y=25)
    skipButton = tk.Button(buttonFrame, height=2, width=16, text="Skip Fixtures", command=SkipRemainingMatchdays,
                           font=("Consolas", 18, "bold"), bg="gray20", fg="Ghost White")
    skipButton.place(x=20, y=125)
    repeatButton = tk.Button(buttonFrame, height=2, width=16, text="Reset Season", state=tk.DISABLED,
                             command=RepeatProcess, font=("Consolas", 18, "bold"), bg="gray20", fg="Ghost White")
    repeatButton.place(x=20, y=225)
    chancesButton = tk.Button(buttonFrame, height=2, width=16, text="Generate Chances", command=ChancesTableWindow,
                           font=("Consolas", 18, "bold"), bg="gray20", fg="Ghost White")
    chancesButton.place(x=20, y=325)
    transferButton = tk.Button(buttonFrame, height=2, width=16, text="Transfer Player", command=TransferPlayerWindow,
                               font=("Consolas", 18, "bold"), bg="gray20", fg="Ghost White")
    transferButton.place(x=20, y=425)
    editPlayerButton = tk.Button(buttonFrame, height=2, width=16, text="Edit A Player", command=EditPlayerWindow,
                                 font=("Consolas", 18, "bold"), bg="gray20", fg="Ghost White")
    editPlayerButton.place(x=20, y=525)
    injuriesButton = tk.Button(buttonFrame, height=2, width=16, text="Injure A Player", command=InjurePlayerWindow,
                               font=("Consolas", 18, "bold"), bg="gray20", fg="Ghost White")
    injuriesButton.place(x=20, y=625)
    closeButton = tk.Button(window, height=1, width=3, text=" X ", command=CloseProgram, font=("Consolas", 18, "bold"),
                            bg="dark slate blue", fg="Ghost White")
    closeButton.place(x=1231, y=0)
    resultTab = tk.Text(textFrame, height=11, width=20, font=("Consolas", 17, "bold"), borderwidth=2,
                        bg="gray20", fg="Ghost White")
    resultTab.place(x=20, y=20)
    resultTab.insert(tk.END, "==== Matchday 00 ===")
    leagueTable = tk.Text(textFrame, height=22, width=55, font=("Consolas", 14, "bold"), borderwidth=2,
                          bg="gray20", fg="Ghost White")
    leagueTable.place(x=400, y=20)
    DisplayTable()
    testTab = tk.Text(textFrame, height=7, width=35, font=("Consolas", 14, "bold"), borderwidth=2,
                      bg="gray20", fg="Ghost White")
    testTab.place(x=20, y=350)
    testTab.insert(tk.END, "===== League Top Goalscorers ======\n\n\n\n\n\n===================================")
    transferTab = tk.Text(textFrame, height=7, width=32, font=("Consolas", 14, "bold"), borderwidth=2,
                          bg="gray20", fg="Ghost White")
    transferTab.place(x=270, y=530)
    transferTab.insert(tk.END, "Transferred Players:\n")
    injuryTab = tk.Text(textFrame, height=7, width=34, font=("Consolas", 14, "bold"), borderwidth=2,
                        bg="gray20", fg="Ghost White")
    injuryTab.place(x=610, y=530)
    injuryTab.insert(tk.END, "Injured Players:\n")
    cleansheetTab = tk.Text(textFrame, height=7, width=22, font=("Consolas", 14, "bold"), borderwidth=2,
                            bg="gray20", fg="Ghost White")
    cleansheetTab.place(x=20, y=530)
    cleansheetTab.insert(tk.END, "==== Top GKeepers ====\n\n\n\n\n\n======================")
    window.mainloop()


teamdata = []
allteamsdata = []
allplayersdata = []
playerdata = []
transferredplayers = []
matchday = 1
score = ""
fixtureresult = ""
t1score = 0
t2score = 0
team_points = {}
connection = sqlite3.connect("TeamsDatabase.db")
cursor = connection.cursor()
RevertChanges()
with open('filetest.txt', 'w') as f:
    f.write("")
cursor.execute("SELECT * FROM plteams")
for row in cursor.fetchall():
    teamdata.append(row[2])
    teamdata.append(row[3])
    teamdata.append(row[4])
    teamdata.append(row[5])
    allteamsdata.append(teamdata)
    teamdata = []
for team in allteamsdata:
    team_points[team[0]] = [0, 0, 0, 0, 0, 0, 0]
connection.commit()
connection.close()
GUI()

import sqlite3  # Module for working with SQLite databases
import random  # Module for generating random numbers
import tkinter as tk  # Module for creating GUI applications
from tkinter import ttk
import downton
from tabulate import tabulate  # Module for creating tables from data
import threading
from PIL import ImageTk, Image
from tkinter import *
import time

window = tk.Tk()
window.attributes("-fullscreen", True)
window.title("Football Match Predictor")
window.configure(bg="gray20")


def CalcThreatRating(t1, t2):
    teams = [t1, t2]
    teamids = ["t1", "t2"]
    teamratings = []
    for x in range(0, 2):
        teamid = teamids[x]
        defrating = []
        midrating = []
        attrating = []
        connection = sqlite3.connect("TeamsDatabase.db")
        cursor = connection.cursor()
        positionsandratings = cursor.execute(
            "SELECT position, rating, form FROM players WHERE abbreviation = ? AND injury = ?",
            (teams[x], '0')).fetchall()
        for set in positionsandratings:
            if set[0] == "(G)" or set[0] == "(RB)" or set[0] == "(LB)" or set[0] == "(CB)":
                defrating.append(int(set[1]) + int(set[2]))
            elif set[0] == "(CM)" or set[0] == "(CAM)" or set[0] == "(CDM)":
                midrating.append(int(set[1]) + int(set[2]))
            elif set[0] == "(ST)" or set[0] == "(RW)" or set[0] == "(LW)":
                attrating.append(int(set[1]) + int(set[2]))
        ovrRating = round(((sum(defrating) / len(defrating) if defrating else 0) + (
            sum(midrating) / len(midrating) if midrating else 0) + (
                               sum(attrating) / len(attrating) if attrating else 0)) / 3)
        homeadvantage = random.randint(2, 6)
        if teamid == "t1":
            ovrRating += homeadvantage
        teamratings.append(ovrRating)
        connection.close()
    return teamratings[0], teamratings[1]


def ChooseGoalScorer(teamplayernames, positiontouse, aspositiontouse):
    potentialscorers = []
    potentialassisters = []
    indexes = []
    teamplayernames = downton.MergeSort().sort(teamplayernames, 5)
    for player in teamplayernames:
        if aspositiontouse in player:
            potentialassisters.append(player)
        if positiontouse in player:
            potentialscorers.append(player)
    howmany = 30
    initialindex = 0
    if len(potentialscorers) > 1:
        for x in range(len(potentialscorers)):
            for y in range(howmany):
                indexes.append(initialindex)
            howmany = round(howmany / 3)
            initialindex += 1
        random.shuffle(indexes)
        index = random.choice(indexes)
        goalscorer = potentialscorers[index]
    else:
        goalscorer = potentialscorers[0]
    if len(potentialassisters) > 1:
        assister = random.choice(potentialassisters)
        while assister == goalscorer:
            assister = random.choice(potentialassisters)
    elif len(potentialassisters) == 1:
        assister = potentialassisters[0]
        while assister == goalscorer:
            assister = random.choice(teamplayernames)
    else:
        assister = random.choice(teamplayernames)
        while assister == goalscorer:
            assister = random.choice(teamplayernames)
    return goalscorer, assister


def AssignGoalsAndAssistsToPlayers(t1, t2, t1score, t2score, score, fixtureresult):
    positionsforscorers = ["(ST)"] * 60 + ["(CAM)", "(LW)", "(RW)"] * 20 + ["(CM)", "(CDM)"] * 10 + ["(LB)",
                                                                                                     "(RB)"] * 5 + [
                              "(CB)"] * 2
    positionsforassisters = ["(ST)"] * 20 + ["(CAM)", "(LW)", "(RW)"] * 40 + ["(CM)", "(CDM)"] * 30 + ["(LB)",
                                                                                                       "(RB)"] * 20 + [
                                "(CB)"] * 10 + ["(G)"] * 10
    positiontouse = ""
    aspositiontouse = ""
    connection = sqlite3.connect('TeamsDatabase.db')
    cursor = connection.cursor()
    if fixtureresult == "draw":
        for y in range(score):
            team1playernames = cursor.execute("SELECT * FROM players WHERE abbreviation = ? AND injury = ?",
                                              (t1, '0')).fetchall()
            x = 0
            while x == 0:
                random.shuffle(positionsforscorers)
                random.shuffle(positionsforassisters)
                positiontouse = random.choice(positionsforscorers)
                aspositiontouse = random.choice(positionsforassisters)
                for player in team1playernames:
                    if positiontouse in player:
                        x += 1
            goalscorer, assister = ChooseGoalScorer(team1playernames, positiontouse, aspositiontouse)
            appendgoals = int(goalscorer[6]) + 1
            appendassists = int(assister[7]) + 1
            appendgsform = int(goalscorer[9]) + 1
            appendasform = int(assister[9]) + 1
            cursor.execute(
                "UPDATE players SET goalcount = ?, form = ? WHERE name = ? AND abbreviation = ? AND position = ?",
                (appendgoals, appendgsform, goalscorer[2], goalscorer[1], positiontouse))
            cursor.execute(
                "UPDATE players SET assistcount = ?, form = ? WHERE name = ? AND abbreviation = ? AND position = ?",
                (appendassists, appendasform, assister[2], assister[1], aspositiontouse))
        for x in range(score):
            team2playernames = cursor.execute("SELECT * FROM players WHERE abbreviation = ? AND injury = ?",
                                              (t2, '0')).fetchall()
            x = 0
            while x == 0:
                positiontouse = random.choice(positionsforscorers)
                aspositiontouse = random.choice(positionsforassisters)
                for player in team2playernames:
                    if positiontouse in player:
                        x += 1
            goalscorer, assister = ChooseGoalScorer(team2playernames, positiontouse, aspositiontouse)
            appendgoals = int(goalscorer[6]) + 1
            appendassists = int(assister[7]) + 1
            appendgsform = int(goalscorer[9]) + 1
            appendasform = int(assister[9]) + 1
            cursor.execute(
                "UPDATE players SET goalcount = ?, form = ? WHERE name = ? AND abbreviation = ? AND position = ?",
                (appendgoals, appendgsform, goalscorer[2], goalscorer[1], positiontouse))
            cursor.execute(
                "UPDATE players SET assistcount = ?, form = ? WHERE name = ? AND abbreviation = ? AND position = ?",
                (appendassists, appendasform, assister[2], assister[1], aspositiontouse))
    elif fixtureresult == "nondraw":
        for x in range(t1score):
            team1playernames = cursor.execute("SELECT * FROM players WHERE abbreviation = ? AND injury = ?",
                                              (t1, '0')).fetchall()
            x = 0
            while x == 0:
                positiontouse = random.choice(positionsforscorers)
                aspositiontouse = random.choice(positionsforassisters)
                for player in team1playernames:
                    if positiontouse in player:
                        x += 1
            goalscorer, assister = ChooseGoalScorer(team1playernames, positiontouse, aspositiontouse)
            appendgoals = int(goalscorer[6]) + 1
            appendassists = int(assister[7]) + 1
            appendgsform = int(goalscorer[9]) + 1
            appendasform = int(assister[9]) + 1
            cursor.execute(
                "UPDATE players SET goalcount = ?, form = ? WHERE name = ? AND abbreviation = ? AND position = ?",
                (appendgoals, appendgsform, goalscorer[2], goalscorer[1], positiontouse))
            cursor.execute(
                "UPDATE players SET assistcount = ?, form = ? WHERE name = ? AND abbreviation = ? AND position = ?",
                (appendassists, appendasform, assister[2], assister[1], aspositiontouse))
        for x in range(t2score):
            team2playernames = cursor.execute("SELECT * FROM players WHERE abbreviation = ? AND injury = ?",
                                              (t2, '0')).fetchall()
            x = 0
            while x == 0:
                positiontouse = random.choice(positionsforscorers)
                aspositiontouse = random.choice(positionsforassisters)
                for player in team2playernames:
                    if positiontouse in player:
                        x += 1
            goalscorer, assister = ChooseGoalScorer(team2playernames, positiontouse, aspositiontouse)
            appendgoals = int(goalscorer[6]) + 1
            appendassists = int(assister[7]) + 1
            appendgsform = int(goalscorer[9]) + 1
            appendasform = int(assister[9]) + 1
            cursor.execute(
                "UPDATE players SET goalcount = ?, form = ? WHERE name = ? AND abbreviation = ? AND position = ?",
                (appendgoals, appendgsform, goalscorer[2], goalscorer[1], positiontouse))
            cursor.execute(
                "UPDATE players SET assistcount = ?, form = ? WHERE name = ? AND abbreviation = ? AND position = ?",
                (appendassists, appendasform, assister[2], assister[1], aspositiontouse))
    connection.commit()
    connection.close()


def DecideTheWinnerOfTheFixture(t1, t2, t1prcntg, t2prcntg):
    global score, t1score, t2score, fixtureresult
    connection = sqlite3.connect("TeamsDatabase.db")
    cursor = connection.cursor()
    possiblescores = [1] * 250 + [2] * 200 + [3] * 150 + [4] * 100 + [5] * 20 + [6, 7, 8, 9]
    drawscores = [0] * 200 + [1] * 125 + [2] * 75 + [3] * 50 + [4] * 5
    draw = random.randint(1, 8)
    result = f"{t1} vs {t2} => "
    if draw == 5 or t1prcntg == t2prcntg:
        fixtureresult = "draw"
        score = random.choice(drawscores)
        team_points[t1][1] += 1
        team_points[t1][3] += 1
        team_points[t2][1] += 1
        team_points[t2][3] += 1
        team_points[t1][4] += score
        team_points[t1][5] += score
        team_points[t2][4] += score
        team_points[t2][5] += score
        result += f"{score} - {score}"
        AssignGoalsAndAssistsToPlayers(t1, t2, t1score, t2score, score, fixtureresult)
        if score == 0:
            t1keepers = []
            t2keepers = []
            gett1gks = cursor.execute(
                "SELECT name, goalcount, rating FROM players WHERE abbreviation = ? AND position = ? AND injury = ?",
                (t1, "(G)", 0))
            for player in gett1gks:
                t1keepers.append(player)
            t1gks = downton.MergeSort().sort(t1keepers, 2)
            t1newcs = int(t1gks[0][1]) + 1
            cursor.execute("UPDATE players SET goalcount = ? WHERE abbreviation = ? AND name = ? AND position = ?",
                           (t1newcs, t1, t1gks[0][0], "(G)"))
            gett2gks = cursor.execute(
                "SELECT name, goalcount, rating FROM players WHERE abbreviation = ? AND position = ? AND injury = ?",
                (t2, "(G)", 0))
            for player in gett2gks:
                t2keepers.append(player)
            t2gks = downton.MergeSort().sort(t2keepers, 2)
            t2newcs = int(t2gks[0][1]) + 1
            cursor.execute("UPDATE players SET goalcount = ? WHERE abbreviation = ? AND name = ? AND position = ?",
                           (t2newcs, t2, t2gks[0][0], "(G)"))
            connection.commit()
        return result
    elif t1prcntg > t2prcntg:
        fixtureresult = "nondraw"
        t1score = random.choice(possiblescores)
        t2score = random.choice([score for score in drawscores if score <= t1score])
        team_points[t1][0] += 1
        team_points[t1][3] += 3
        team_points[t2][2] += 1
        team_points[t1][4] += t1score
        team_points[t1][5] += t2score
        team_points[t2][4] += t2score
        team_points[t2][5] += t1score
        team_points[t1][6] = team_points[t1][4] - team_points[t1][5]
        team_points[t2][6] = team_points[t2][4] - team_points[t2][5]
        result += f"{t1score} - {t2score}"
        AssignGoalsAndAssistsToPlayers(t1, t2, t1score, t2score, score, fixtureresult)
        t1forms = cursor.execute("SELECT name, form FROM players WHERE abbreviation = ?", (t1,))
        for player in t1forms:
            newform = int(player[1]) + 1
            cursor.execute("UPDATE players SET form = ? WHERE abbreviation = ? AND name = ?", (newform, t1, player[0]))
        t2forms = cursor.execute("SELECT name, form FROM players WHERE abbreviation = ?", (t2,))
        for player in t2forms:
            newform = int(player[1]) - 1
            cursor.execute("UPDATE players SET form = ? WHERE abbreviation = ? AND name = ?", (newform, t2, player[0]))
        connection.commit()
        if t2score == 0:
            keepers = []
            gett1gks = cursor.execute(
                "SELECT name, goalcount, rating FROM players WHERE abbreviation = ? AND position = ? AND injury = ?",
                (t1, "(G)", 0))
            for player in gett1gks:
                keepers.append(player)
            t1gks = downton.MergeSort().sort(keepers, 2)
            t1newcs = int(t1gks[0][1]) + 1
            cursor.execute("UPDATE players SET goalcount = ? WHERE abbreviation = ? AND name = ? AND position = ?",
                           (t1newcs, t1, t1gks[0][0], "(G)"))
            connection.commit()
        elif t1score == 0:
            keepers = []
            gett2gks = cursor.execute(
                "SELECT name, goalcount, rating FROM players WHERE abbreviation = ? AND position = ? AND injury = ?",
                (t2, "(G)", 0))
            for player in gett2gks:
                keepers.append(player)
            t2gks = downton.MergeSort().sort(keepers, 2)
            t2newcs = int(t2gks[0][1]) + 1
            cursor.execute("UPDATE players SET goalcount = ? WHERE abbreviation = ? AND name = ? AND position = ?",
                           (t2newcs, t2, t2gks[0][0], "(G)"))
            connection.commit()
        return result
    elif t1prcntg < t2prcntg:
        fixtureresult = "nondraw"
        t2score = random.choice(possiblescores)
        t1score = random.choice([score for score in drawscores if score <= t2score])
        team_points[t2][0] += 1
        team_points[t2][3] += 3
        team_points[t1][2] += 1
        team_points[t1][4] += t1score
        team_points[t1][5] += t2score
        team_points[t2][4] += t2score
        team_points[t2][5] += t1score
        team_points[t1][6] = team_points[t1][4] - team_points[t1][5]
        team_points[t2][6] = team_points[t2][4] - team_points[t2][5]
        result += f"{t1score} - {t2score}"
        AssignGoalsAndAssistsToPlayers(t1, t2, t1score, t2score, score, fixtureresult)
        t1forms = cursor.execute("SELECT name, form FROM players WHERE abbreviation = ?", (t1,))
        for player in t1forms:
            newform = int(player[1]) - 1
            cursor.execute("UPDATE players SET form = ? WHERE abbreviation = ? AND name = ?", (newform, t1, player[0]))
        t2forms = cursor.execute("SELECT name, form FROM players WHERE abbreviation = ?", (t2,))
        for player in t2forms:
            newform = int(player[1]) + 1
            cursor.execute("UPDATE players SET form = ? WHERE abbreviation = ? AND name = ?", (newform, t2, player[0]))
        connection.commit()
        if t2score == 0:
            keepers = []
            gett1gks = cursor.execute(
                "SELECT name, goalcount, rating FROM players WHERE abbreviation = ? AND position = ? AND injury = ?",
                (t1, "(G)", 0))
            for player in gett1gks:
                keepers.append(player)
            t1gks = downton.MergeSort().sort(keepers, 2)
            t1newcs = int(t1gks[0][1]) + 1
            cursor.execute("UPDATE players SET goalcount = ? WHERE abbreviation = ? AND name = ? AND position = ?",
                           (t1newcs, t1, t1gks[0][0], "(G)"))
            connection.commit()
        elif t1score == 0:
            keepers = []
            gett2gks = cursor.execute(
                "SELECT name, goalcount, rating FROM players WHERE abbreviation = ? AND position = ? AND injury = ?",
                (t2, "(G)", 0))
            for player in gett2gks:
                keepers.append(player)
            t2gks = downton.MergeSort().sort(keepers, 2)
            t2newcs = int(t2gks[0][1]) + 1
            cursor.execute("UPDATE players SET goalcount = ? WHERE abbreviation = ? AND name = ? AND position = ?",
                           (t2newcs, t2, t2gks[0][0], "(G)"))
            connection.commit()
        return result


def CalculateTeamsChanceToWin(game):
    t1 = game[:3]  # Extract the team 1 abbreviation
    t2 = game[-3:]  # Extract the team 2 abbreviation
    t1tr, t2tr = CalcThreatRating(t1, t2)
    prcntg = 100 / (t1tr + t2tr)  # Calculate the percentage factor
    t1prcntg = t1tr * prcntg  # Calculate team 1's win percentage
    t2prcntg = 100 - t1prcntg  # Calculate team 2's win percentage (assuming a draw is not possible)
    result = DecideTheWinnerOfTheFixture(t1, t2, t1prcntg, t2prcntg)
    return result




def ProcessNextMatchday():
    global matchday
    connection = sqlite3.connect('TeamsDatabase.db')
    cursor = connection.cursor()
    testTab['state'] = tk.NORMAL
    resultTab['state'] = tk.NORMAL
    cleansheetTab['state'] = tk.NORMAL
    testTab.delete("1.0", tk.END)
    cleansheetTab.delete("1.0", tk.END)
    matchday_filename = f"matchdays/matchday{matchday}.txt"  # Generate the filename for the current matchday
    with open(matchday_filename, "r") as m:
        games = str(m.readlines()).replace("[", "").replace("]", "").replace("'", "").split(",")
    resultTab.delete("1.0", tk.END)  # Clear the resultText widget
    if len(str(matchday)) == 1:
        matchdayno = "0" + str(matchday)
    else:
        matchdayno = str(matchday)
    resultTab.insert(tk.END, f"==== Matchday {matchdayno} ===\n")  # Display the current matchday
    for game in games:  # Process each game
        result = CalculateTeamsChanceToWin(game)  # Calculate the result of the game
        resultTab.insert(tk.END, result + "\n")  # Display the result
    testTab.insert(tk.END, "===== League Top Goalscorers ======\n")
    allplayersforgctallies = []
    gctallies = cursor.execute(
        "SELECT goalcount, assistcount, abbreviation, position, name FROM players").fetchall()
    for player in gctallies:
        if player[3] != "(G)":
            allplayersforgctallies.append(player)
    gctallies = downton.MergeSort().sort(allplayersforgctallies, 0)
    for x in range(1, 6):
        playertallies = str(gctallies[x])
        x = str(x)
        playertallies = playertallies.replace("(", "").replace(")", "").replace("'", "")
        if len(x) == 1:
            x = " " + x
        testTab.insert(tk.END, "" + x + ". " + playertallies + "\n")
    testTab.insert(tk.END, "===================================")
    cleansheetTab.insert(tk.END, "==== Top GKeepers ====\n")
    cstalliesarr = []
    cstallies = cursor.execute("SELECT goalcount, abbreviation, name FROM players WHERE position = ?",
                               ("(G)",)).fetchall()
    for player in cstallies:
        cstalliesarr.append(player)
    cstallies = downton.MergeSort().sort(cstalliesarr, 0)
    for x in range(1, 6):
        playertallies = str(cstallies[x])
        x = str(x)
        playertallies = playertallies.replace("(", "").replace(")", "").replace("'", "")
        if len(x) == 1:
            x = " " + x
        cleansheetTab.insert(tk.END, "" + x + ". " + playertallies + "\n")
    cleansheetTab.insert(tk.END, "======================")
    CheckForInjuries()
    DisplayTable()
    testTab['state'] = tk.DISABLED
    resultTab['state'] = tk.DISABLED
    cleansheetTab['state'] = tk.DISABLED
    matchday += 1  # Increment the matchday counter
    if matchday == 39:
        DisplayTable2()
        repeatButton['state'] = tk.NORMAL
        nextMatchdayButton['state'] = tk.DISABLED
        skipButton['state'] = tk.DISABLED
        transferButton['state'] = tk.DISABLED
        injuriesButton['state'] = tk.DISABLED
        chancesButton['state'] = tk.DISABLED
        editPlayerButton['state'] = tk.DISABLED


def DisplayTable():
    leagueTable['state'] = tk.NORMAL
    sortedTable = sorted(team_points.items(), key=lambda x: (x[1][3], x[1][6], x[1][4]), reverse=True)
    Table = [[team, points[0], points[1], points[2], points[4], points[5], points[6], points[3]] for team, points in
             sortedTable]
    headers = ["POS", "TEAM", "W", "D", "L", "GF", "GA", "GD", "PTS"]
    Table = [[i + 1] + row for i, row in enumerate(Table)]
    leagueTable.delete("1.0", tk.END)
    leagueTable.insert(tk.END, tabulate(Table, headers=headers, tablefmt="csv"))
    leagueTable['state'] = tk.DISABLED

def DisplayTable2():
    leagueTable['state'] = tk.NORMAL
    sortedTable = sorted(team_points.items(), key=lambda x: (x[1][3], x[1][6], x[1][4]), reverse=True)
    Table = [[team, points[0], points[1], points[2], points[4], points[5], points[6], points[3]] for team, points in
             sortedTable]
    for x in range(len(sortedTable)):
        with open('filetest.txt', "a") as filetest:
            filetest.write(str(Table[x][0]))
            x+=1
            filetest.write("\n")
            if x == 20:
                filetest.write("\n")
    headers = ["POS", "TEAM", "W", "D", "L", "GF", "GA", "GD", "PTS"]
    Table = [[i + 1] + row for i, row in enumerate(Table)]
    leagueTable.delete("1.0", tk.END)
    leagueTable.insert(tk.END, tabulate(Table, headers=headers, tablefmt="csv"))
    leagueTable['state'] = tk.DISABLED


def SkipRemainingMatchdays():
    global matchday
    while matchday < 39:
        ProcessNextMatchday()
    repeatButton['state'] = tk.NORMAL
    skipButton['state'] = tk.DISABLED
    nextMatchdayButton['state'] = tk.DISABLED

def CloseProgram():
    RevertChanges()
    window.destroy()


def RevertChanges():
    connection = sqlite3.connect("MasterDatabase.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM players")
    result = cursor.fetchall()
    playerdata = []
    for row in result:
        playerdata.append(row)
    connection.commit()
    connection.close()
    connection = sqlite3.connect("TeamsDatabase.db")
    cursor = connection.cursor()
    cursor.execute("DROP TABLE players")
    connection.commit()
    sqlCommand = """
    CREATE TABLE players
    (idnumber INTEGER,
    abbreviation TEXT,
    name TEXT,
    number INTEGER,
    position INTEGER,
    rating INTEGER,
    goalcount INTEGER,
    assistcount INTEGER,
    injury INTEGER,
    form INTEGER,
    primary key (idnumber)
    )"""
    cursor.execute(sqlCommand)
    connection.commit()
    for playertoadd in playerdata:
        cursor.execute('INSERT INTO players VALUES(?,?,?,?,?,?,?,?,?,?)', playertoadd)
    connection.commit()
    connection.close()


def RepeatProcess():
    global matchday, team_points
    repeatButton['state'] = tk.DISABLED
    nextMatchdayButton['state'] = tk.NORMAL
    skipButton['state'] = tk.NORMAL
    cleansheetTab['state'] = tk.NORMAL
    testTab['state'] = tk.NORMAL
    resultTab['state'] = tk.NORMAL
    editPlayerButton['state'] = tk.NORMAL
    transferButton['state'] = tk.NORMAL
    injuriesButton['state'] = tk.NORMAL
    chancesButton['state'] = tk.NORMAL
    connection = sqlite3.connect('TeamsDatabase.db')
    cursor = connection.cursor()
    RevertChanges()
    nextMatchdayButton.configure(text="Next Matchday")
    teamdata = []  # Temporary list to store team data
    allteamsdata = []  # List to store all teams' data
    matchday = 1  # Reset the matchday counter
    team_points = {}  # Reset the team points dictionary
    leagueTable.delete("1.0", tk.END)  # Clear the resultText widget
    cursor.execute("SELECT * FROM plteams")  # Execute SQL query to fetch team data
    for row in cursor.fetchall():
        teamdata.append(row[2])  # Append team abbreviation
        teamdata.append(row[3])  # Append team name
        teamdata.append(row[4])  # Append team stadium
        teamdata.append(row[5])  # Append team rating
        allteamsdata.append(teamdata)  # Append team data to the allteamsdata list
        teamdata = []  # Reset the teamdata list
    connection.commit()
    connection.close()
    for team in allteamsdata:
        team_points[team[0]] = [0, 0, 0, 0, 0, 0, 0]
    leagueTable.delete("1.0", tk.END)
    testTab.delete("1.0", tk.END)
    resultTab.delete("1.0", tk.END)
    injuryTab.delete("1.0", tk.END)
    cleansheetTab.delete("1.0", tk.END)
    transferTab.delete("1.0", tk.END)
    injuryTab.insert(tk.END, "Injured Players:\n")
    transferTab.insert(tk.END, "Transferred Players:\n")
    testTab.insert(tk.END, "===== League Top Goalscorers ======\n\n\n\n\n\n===================================")
    cleansheetTab.insert(tk.END, "==== Top GKeepers ====\n\n\n\n\n\n======================")
    resultTab.insert(tk.END, "==== Matchday 00 ===")
    DisplayTable()
    cleansheetTab['state'] = tk.DISABLED
    testTab['state'] = tk.DISABLED
    resultTab['state'] = tk.DISABLED
    repeatButton['state'] = tk.DISABLED


def ProduceChancesTable():
    teamnames = [['MCI', 0, 0], ['BOU', 0, 0], ['MUN', 0, 0], ['ARS', 0, 0], ['TOT', 0, 0], ['CHE', 0, 0],
                 ['NEW', 0, 0], ['AVL', 0, 0],
                 ['EVE', 0, 0],
                 ['NFO', 0, 0], ['FUL', 0, 0], ['BRE', 0, 0], ['BRI', 0, 0], ['WHU', 0, 0], ['WOL', 0, 0],
                 ['LIV', 0, 0], ['LEI', 0, 0],
                 ['SOU', 0, 0],
                 ['CRY', 0, 0], ['LEE', 0, 0]]
    tableplaces = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    chancestableraw = []
    with open('filetest.txt', 'r') as f:
        x = f.readlines()
        num = 0
        for item in x:
            if item == '\n':
                num = 0
            else:
                tableplaces[num].append(item)
                num += 1

    def GiveNumTimesInEachPos(posnum):
        teamdata = [['MCI', 0, 0], ['BOU', 0, 0], ['MUN', 0, 0], ['ARS', 0, 0], ['TOT', 0, 0], ['CHE', 0, 0],
                    ['NEW', 0, 0], ['AVL', 0, 0],
                    ['EVE', 0, 0],
                    ['NFO', 0, 0], ['FUL', 0, 0], ['BRE', 0, 0], ['BRI', 0, 0], ['WHU', 0, 0], ['WOL', 0, 0],
                    ['LIV', 0, 0], ['LEI', 0, 0],
                    ['SOU', 0, 0],
                    ['CRY', 0, 0], ['LEE', 0, 0]]
        pos = []
        for x in range(len(tableplaces[posnum])):
            for team in teamdata:
                if (team[0] + "\n") == tableplaces[posnum][x]:
                    team[1] += 1
        for team in teamdata:
            pos.append(team)
        pos = downton.OppositeMergeSort().sort(pos, 0)
        chancestableraw.append(pos)
        return chancestableraw

    for x in range(len(tableplaces)):
        tabledata = GiveNumTimesInEachPos(x)

    def FindNumOfSims():
        numofsims = 0
        for set in chancestableraw:
            for item in set:
                if 'MUN' in item:
                    numofsims += item[1]
        return numofsims

    numofsims = FindNumOfSims()

    for item in tabledata:
        for team in item:
            team[2] = str(round((team[1] / numofsims) * 100))

    headers = ["Team", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17",
               "18", "19", "20"]
    finaltabledata = []
    teamnames = downton.OppositeMergeSort().sort(teamnames, 0)
    for team in teamnames:
        teamchances = []
        teamchances.append(team[0])
        for set in tabledata:
            for item in set:
                if team[0] in item:
                    teamchances.append(float(item[2]))
        finaltabledata.append(teamchances)
    return (tabulate(finaltabledata, headers=headers, tablefmt="csv"))


def TransferThePlayer():
    transferTab['state'] = tk.NORMAL
    playername = str(nameEntry.get())
    playercurrentteam = str(teamEntry.get().upper())
    playernewteam = str(teamtoEntry.get().upper())
    connection = sqlite3.connect("TeamsDatabase.db")
    cursor = connection.cursor()
    cursor.execute("UPDATE players SET abbreviation = ? WHERE name = ? AND abbreviation = ?",
                   (playernewteam, playername, playercurrentteam))
    connection.commit()
    connection.close()
    transferred = playername, "from", playercurrentteam, "to", playernewteam
    transferred = (str(transferred) + "\n").replace("(", "").replace(",", "").replace(")", "").replace("'", "").replace(
        "'", "")
    transferredplayers.append(transferred)
    transferTab.delete("1.0", tk.END)
    transferTab.insert(tk.END, "Transferred Players:\n")
    for x in range(len(transferredplayers)):
        player = transferredplayers[x]
        transferTab.insert(tk.END, player)
    transferTab['state'] = tk.DISABLED


def CloseTransferPlayerWindow():
    transferFrame.destroy()


def TransferPlayerWindow(): #open transfer player window
    global nameEntry, teamEntry, teamtoEntry, transferFrame
    transferFrame = tk.Text(window, height=24, width=34, bg="dark slate blue", borderwidth=2)
    transferFrame.place(x=400, y=200)
    transferTitle = tk.Text(transferFrame, font=("Consolas", 16, "bold", "underline"), height=1, width=20,
                            bg="dark slate blue", fg="Ghost White", borderwidth=0)
    transferTitle.place(x=0, y=0)
    transferTitle.insert(tk.END, "Transfer A Player")
    nameEntry = tk.Entry(transferFrame, font=("Consolas", 22), width=10,
                         bg="grey20", fg="Ghost White", borderwidth=2)
    nameEntry.place(x=50, y=75)
    teamEntry = tk.Entry(transferFrame, font=("Consolas", 22), width=10,
                         bg="grey20", fg="Ghost White", borderwidth=2)
    teamEntry.place(x=50, y=175)
    teamtoEntry = tk.Entry(transferFrame, font=("Consolas", 22), width=10,
                           bg="grey20", fg="Ghost White", borderwidth=2)
    teamtoEntry.place(x=50, y=275)
    nameText = tk.Text(transferFrame, font=("Consolas", 11), width=20, height=1, bg="grey20", fg="Ghost White",
                       borderwidth=2)
    nameText.place(x=50, y=50)
    teamText = tk.Text(transferFrame, font=("Consolas", 11), width=20, height=1, bg="grey20", fg="Ghost White",
                       borderwidth=2)
    teamText.place(x=50, y=150)
    teamtoText = tk.Text(transferFrame, font=("Consolas", 11), width=20, height=1, bg="grey20", fg="Ghost White",
                         borderwidth=2)
    teamtoText.place(x=50, y=250)
    nameText.insert(tk.END, "Enter Player's Name:")
    teamText.insert(tk.END, "Enter Player's Team:")
    teamtoText.insert(tk.END, "Player's New Team:")
    closeTransferWindowButton = tk.Button(transferFrame, height=1, width=2, text="X", command=CloseTransferPlayerWindow,
                                          font=("Consolas", 15, "bold"), bg="grey20", fg="Ghost White")
    closeTransferWindowButton.place(x=244, y=0)
    submitTransferButton = tk.Button(transferFrame, height=1, width=6, text="SUBMIT", command=TransferThePlayer,
                                     font=("Consolas", 12, "bold"), bg="grey20", fg="Ghost White")
    submitTransferButton.place(x=100, y=330)


def CheckForInjuries(): #check array for injured players to present them
    connection = sqlite3.connect("TeamsDatabase.db")
    cursor = connection.cursor()
    injuryTab['state'] = tk.NORMAL
    injuredplayersinfo = []
    injuredplayers = []
    cursor.execute("SELECT * FROM players")
    for row in cursor.fetchall():
        if row[8] == 1:
            injuredplayersinfo.append(row)
    injuryTab.delete("1.0", tk.END)
    injuryTab.insert(tk.END, "Injured Players:\n")
    for x in range(len(injuredplayersinfo)):
        playertuple = injuredplayersinfo[x][2], "is injured.", "[" + injuredplayersinfo[x][1] + "]"
        playerstr = (str(playertuple) + "\n").replace("(", "").replace(",", "").replace(")", "").replace("'",
                                                                                                         "").replace(
            "'", "")
        injuredplayers.append(playerstr)
    for player in injuredplayers:
        injuryTab.insert(tk.END, player)
    injuryTab['state'] = tk.DISABLED


def InjureThePlayer(): #injure the selected player
    playername = str(injureNameEntry.get().title())
    playercurrentteam = str(injureTeamEntry.get().upper())
    connection = sqlite3.connect("TeamsDatabase.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM players")
    x = 0
    for row in cursor.fetchall():
        if playername in row and playercurrentteam in row:
            x = 1
            if row[8] == 1:
                cursor.execute("UPDATE players SET injury = ? WHERE name = ? AND abbreviation = ?",
                               ('0', playername, playercurrentteam))
                connection.commit()
                statement = "This player is now uninjured"
                informofinjuryText.delete("1.0", tk.END)
                informofinjuryText.insert(tk.END, statement)
            else:
                cursor.execute("UPDATE players SET injury = ? WHERE name = ? AND abbreviation = ?",
                               ('1', playername, playercurrentteam))
                connection.commit()
                statement = "This player is now injured"
                informofinjuryText.delete("1.0", tk.END)
                informofinjuryText.insert(tk.END, statement)
        if x == 0:
            informofinjuryText.delete("1.0", tk.END)
            statement = ("This player does not exist.")
            informofinjuryText.insert(tk.END, statement)
    CheckForInjuries()


def CloseInjurePlayerWindow(): #program to close the injury window
    injureplayerFrame.destroy()


def InjurePlayerWindow(): #program for the injury window
    global injureNameEntry, injureTeamEntry, injureplayerFrame, informofinjuryText
    injureplayerFrame = tk.Text(window, height=24, width=34, bg="dark slate blue", borderwidth=2)
    injureplayerFrame.place(x=400, y=200)
    createplayerTitle = tk.Text(injureplayerFrame, font=("Consolas", 16, "bold", "underline"), height=1, width=20,
                                bg="dark slate blue", fg="Ghost White", borderwidth=0)
    createplayerTitle.place(x=0, y=0)
    createplayerTitle.insert(tk.END, "Injure A Player")
    injureNameEntry = tk.Entry(injureplayerFrame, font=("Consolas", 22), width=10,
                               bg="grey20", fg="Ghost White", borderwidth=2)
    injureNameEntry.place(x=50, y=75)
    injureTeamEntry = tk.Entry(injureplayerFrame, font=("Consolas", 22), width=10,
                               bg="grey20", fg="Ghost White", borderwidth=2)
    injureTeamEntry.place(x=50, y=175)
    nameText = tk.Text(injureplayerFrame, font=("Consolas", 11), width=20, height=1, bg="grey20", fg="Ghost White",
                       borderwidth=2)
    nameText.place(x=50, y=50)
    teamText = tk.Text(injureplayerFrame, font=("Consolas", 11), width=20, height=1, bg="grey20", fg="Ghost White",
                       borderwidth=2)
    teamText.place(x=50, y=150)
    nameText.insert(tk.END, "Enter Player's Name:")
    teamText.insert(tk.END, "Enter Player's Team:")
    closeInjurePlayerWindowButton = tk.Button(injureplayerFrame, height=1, width=2, text="X",
                                              command=CloseInjurePlayerWindow,
                                              font=("Consolas", 15, "bold"), bg="grey20", fg="Ghost White")
    closeInjurePlayerWindowButton.place(x=244, y=0)
    informofinjuryText = tk.Text(injureplayerFrame, font=("Consolas", 11), width=18, height=2, bg="grey20",
                                 fg="Ghost White", borderwidth=2)
    informofinjuryText.place(x=55, y=250)
    InjureThePlayerButton = tk.Button(injureplayerFrame, height=1, width=6, text="SUBMIT", command=InjureThePlayer,
                                      font=("Consolas", 12, "bold"), bg="grey20", fg="Ghost White")
    InjureThePlayerButton.place(x=100, y=330)


def CloseEditPlayerWindow(): #Close the player-editing window
    editFrame.destroy()


def EditThePlayer(): #Run the program that edits the player's rating
    playername = str(editNameEntry.get())
    playercurrentteam = str(editTeamEntry.get().upper())
    playernewrating = str(editRatingEntry.get())
    connection = sqlite3.connect("TeamsDatabase.db")
    cursor = connection.cursor()
    cursor.execute("UPDATE players SET rating = ? WHERE name = ? AND abbreviation = ?",
                   (playernewrating, playername, playercurrentteam))
    connection.commit()
    connection.close()
    CloseEditPlayerWindow()


def EditPlayerWindow(): #Open the window after the edit button is pressed
    global editNameEntry, editTeamEntry, editRatingEntry, editFrame
    editFrame = tk.Text(window, height=24, width=34, bg="dark slate blue", borderwidth=2)
    editFrame.place(x=400, y=200)
    transferTitle = tk.Text(editFrame, font=("Consolas", 16, "bold", "underline"), height=1, width=20,
                            bg="dark slate blue", fg="Ghost White", borderwidth=0)
    transferTitle.place(x=0, y=0)
    transferTitle.insert(tk.END, "Edit Player Ratings")
    editNameEntry = tk.Entry(editFrame, font=("Consolas", 22), width=10,
                         bg="grey20", fg="Ghost White", borderwidth=2)
    editNameEntry.place(x=50, y=75)
    editTeamEntry = tk.Entry(editFrame, font=("Consolas", 22), width=10,
                         bg="grey20", fg="Ghost White", borderwidth=2)
    editTeamEntry.place(x=50, y=175)
    editRatingEntry = tk.Entry(editFrame, font=("Consolas", 22), width=10,
                           bg="grey20", fg="Ghost White", borderwidth=2)
    editRatingEntry.place(x=50, y=275)
    nameText = tk.Text(editFrame, font=("Consolas", 11), width=20, height=1, bg="grey20", fg="Ghost White",
                       borderwidth=2)
    nameText.place(x=50, y=50)
    teamText = tk.Text(editFrame, font=("Consolas", 11), width=20, height=1, bg="grey20", fg="Ghost White",
                       borderwidth=2)
    teamText.place(x=50, y=150)
    ratingText = tk.Text(editFrame, font=("Consolas", 11), width=20, height=1, bg="grey20", fg="Ghost White",
                         borderwidth=2)
    ratingText.place(x=50, y=250)
    nameText.insert(tk.END, "Enter Player's Name:")
    teamText.insert(tk.END, "Enter Player's Team:")
    ratingText.insert(tk.END, "Enter Player's New Rating:")
    closeEditWindowButton = tk.Button(editFrame, height=1, width=2, text="X", command=CloseEditPlayerWindow,
                                          font=("Consolas", 15, "bold"), bg="grey20", fg="Ghost White")
    closeEditWindowButton.place(x=244, y=0)
    submitEditButton = tk.Button(editFrame, height=1, width=6, text="SUBMIT", command=EditThePlayer,
                                     font=("Consolas", 12, "bold"), bg="grey20", fg="Ghost White")
    submitEditButton.place(x=100, y=330)


def CloseChancesTableWindow(): #program to close the injury window
    chancestableFrame.destroy()

def ChancesTableWindow(): #program for the injury window
    global chancestableFrame, chancestableText, closechancestableWindowButton
    chancestableFrame = tk.Text(window, height=60, width=180, bg="dark slate blue", borderwidth=2)
    chancestableFrame.place(x=0, y=0)
    createplayerTitle = tk.Text(chancestableFrame, font=("Consolas", 40, "bold", "underline"), height=1, width=30,
                                bg="dark slate blue", fg="Ghost White", borderwidth=0)
    createplayerTitle.place(x=0, y=0)
    createplayerTitle.insert(tk.END, "Position Chances Table")
    closechancestableWindowButton = tk.Button(chancestableFrame, height=2, width=4, text="X",
                                              command=CloseChancesTableWindow,
                                              font=("Consolas", 15, "bold"), bg="grey20", fg="Ghost White")
    closechancestableWindowButton.place(x=1220, y=0)
    chancestableText = tk.Text(chancestableFrame, font=("Consolas", 12), width=120, height=22, bg="grey20", fg="Ghost White",
                       borderwidth=2)
    chancestableText.place(x=20, y=100)
    chancestableText['state'] = tk.NORMAL
    chancestableText.insert(tk.END, ProduceChancesTable())
    chancestableText['state'] = tk.DISABLED


def GUI():
    global leagueTable, simulationFrame, testTab, transferTab, injuryTab, nextMatchdayButton, repeatButton, skipButton, cleansheetTab, repeatTab, resultTab, transferButton, editPlayerButton, injuriesButton, chancesButton
    Title = tk.Text(window, font=("Consolas", 44, "bold", "underline"), height=1, width=35,
                    bg="dark slate blue", fg="Ghost White", borderwidth=2)
    Title.place(x=60, y=2)
    Title.insert(tk.END, " English Premier League Simulation")
    Title['state'] = tk.DISABLED
    simulationFrame = tk.Frame(window, height=740, width=1400, bg="gray20", borderwidth=2)
    simulationFrame.place(x=0, y=80)
    textFrame = tk.Frame(simulationFrame, height=725, width=990, bg="dark slate blue", borderwidth=2)
    textFrame.place(x=10, y=20)
    buttonFrame = tk.Frame(simulationFrame, height=725, width=263, bg="dark slate blue", borderwidth=2)
    buttonFrame.place(x=1000, y=20)
    nextMatchdayButton = tk.Button(buttonFrame, height=2, width=16, text="Next Fixture", command=ProcessNextMatchday,
                                   font=("Consolas", 18, "bold"), bg="gray20", fg="Ghost White")
    nextMatchdayButton.place(x=20, y=25)
    skipButton = tk.Button(buttonFrame, height=2, width=16, text="Skip Fixtures", command=SkipRemainingMatchdays,
                           font=("Consolas", 18, "bold"), bg="gray20", fg="Ghost White")
    skipButton.place(x=20, y=125)
    repeatButton = tk.Button(buttonFrame, height=2, width=16, text="Reset Season", state=tk.DISABLED,
                             command=RepeatProcess, font=("Consolas", 18, "bold"), bg="gray20", fg="Ghost White")
    repeatButton.place(x=20, y=225)
    chancesButton = tk.Button(buttonFrame, height=2, width=16, text="Generate Chances", command=ChancesTableWindow,
                           font=("Consolas", 18, "bold"), bg="gray20", fg="Ghost White")
    chancesButton.place(x=20, y=325)
    transferButton = tk.Button(buttonFrame, height=2, width=16, text="Transfer Player", command=TransferPlayerWindow,
                               font=("Consolas", 18, "bold"), bg="gray20", fg="Ghost White")
    transferButton.place(x=20, y=425)
    editPlayerButton = tk.Button(buttonFrame, height=2, width=16, text="Edit A Player", command=EditPlayerWindow,
                                 font=("Consolas", 18, "bold"), bg="gray20", fg="Ghost White")
    editPlayerButton.place(x=20, y=525)
    injuriesButton = tk.Button(buttonFrame, height=2, width=16, text="Injure A Player", command=InjurePlayerWindow,
                               font=("Consolas", 18, "bold"), bg="gray20", fg="Ghost White")
    injuriesButton.place(x=20, y=625)
    closeButton = tk.Button(window, height=1, width=3, text=" X ", command=CloseProgram, font=("Consolas", 18, "bold"),
                            bg="dark slate blue", fg="Ghost White")
    closeButton.place(x=1231, y=0)
    resultTab = tk.Text(textFrame, height=11, width=20, font=("Consolas", 17, "bold"), borderwidth=2,
                        bg="gray20", fg="Ghost White")
    resultTab.place(x=20, y=20)
    resultTab.insert(tk.END, "==== Matchday 00 ===")
    leagueTable = tk.Text(textFrame, height=22, width=55, font=("Consolas", 14, "bold"), borderwidth=2,
                          bg="gray20", fg="Ghost White")
    leagueTable.place(x=400, y=20)
    DisplayTable()
    testTab = tk.Text(textFrame, height=7, width=35, font=("Consolas", 14, "bold"), borderwidth=2,
                      bg="gray20", fg="Ghost White")
    testTab.place(x=20, y=350)
    testTab.insert(tk.END, "===== League Top Goalscorers ======\n\n\n\n\n\n===================================")
    transferTab = tk.Text(textFrame, height=7, width=32, font=("Consolas", 14, "bold"), borderwidth=2,
                          bg="gray20", fg="Ghost White")
    transferTab.place(x=270, y=530)
    transferTab.insert(tk.END, "Transferred Players:\n")
    injuryTab = tk.Text(textFrame, height=7, width=34, font=("Consolas", 14, "bold"), borderwidth=2,
                        bg="gray20", fg="Ghost White")
    injuryTab.place(x=610, y=530)
    injuryTab.insert(tk.END, "Injured Players:\n")
    cleansheetTab = tk.Text(textFrame, height=7, width=22, font=("Consolas", 14, "bold"), borderwidth=2,
                            bg="gray20", fg="Ghost White")
    cleansheetTab.place(x=20, y=530)
    cleansheetTab.insert(tk.END, "==== Top GKeepers ====\n\n\n\n\n\n======================")
    window.mainloop()


teamdata = []
allteamsdata = []
allplayersdata = []
playerdata = []
transferredplayers = []
matchday = 1
score = ""
fixtureresult = ""
t1score = 0
t2score = 0
team_points = {}
connection = sqlite3.connect("TeamsDatabase.db")
cursor = connection.cursor()
RevertChanges()
with open('filetest.txt', 'w') as f:
    f.write("")
cursor.execute("SELECT * FROM plteams")
for row in cursor.fetchall():
    teamdata.append(row[2])
    teamdata.append(row[3])
    teamdata.append(row[4])
    teamdata.append(row[5])
    allteamsdata.append(teamdata)
    teamdata = []
for team in allteamsdata:
    team_points[team[0]] = [0, 0, 0, 0, 0, 0, 0]
connection.commit()
connection.close()
GUI()