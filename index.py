from flask import Flask, render_template,redirect
app = Flask(__name__)
from nhlApi import NHLAPI 
statSeason = '20242025' #which season to get stats from
rosterSeason = '20252026' #which season to get roster from - one year ahead, to get current season 
defensemanWeightBump = 2.5 #variable to control if d should get a bump in value, set to 0 if not required
nhl = NHLAPI(statSeason,rosterSeason) #To get new stats, you have to refresh after changing stat/roster seasons

@app.route('/')
def main():

    #just shows currently loaded players - NO API CALLS HERE
    outputData = nhl.GenerateTopFantasyRatingList(200,defensemanWeightBump) 

    if type(outputData) is list:
        return render_template('index.html',data=outputData)
    else:
        return render_template('index.html',data=[])

@app.route('/refresh')
def refresh():

    #refreshes data/calls api
    nhl.GetTeamData()

    return redirect('/')

app.run(debug=True)



