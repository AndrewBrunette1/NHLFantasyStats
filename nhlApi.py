#https://gitlab.com/dword4/nhlapi/-/blob/master/new-api.md
import requests
from sqlitefunctions import SQLiteFunctions
from playerstats import PlayerStats

class NHLAPI:

    def __init__(self,statSeason,rosterSeason):

        self.nhldb = SQLiteFunctions()

        self.nhl_team_abbreviations = [
                            "ANA",  # Anaheim Ducks
                            "BOS",  # Boston Bruins
                            "BUF",  # Buffalo Sabres
                            "CGY",  # Calgary Flames
                            "CAR",  # Carolina Hurricanes
                            "CHI",  # Chicago Blackhawks
                            "COL",  # Colorado Avalanche
                            "CBJ",  # Columbus Blue Jackets
                            "DAL",  # Dallas Stars
                            "DET",  # Detroit Red Wings
                            "EDM",  # Edmonton Oilers
                            "FLA",  # Florida Panthers
                            "LAK",  # Los Angeles Kings
                            "MIN",  # Minnesota Wild
                            "MTL",  # Montreal Canadiens
                            "NSH",  # Nashville Predators
                            "NJD",  # New Jersey Devils
                            "NYI",  # New York Islanders
                            "NYR",  # New York Rangers
                            "OTT",  # Ottawa Senators
                            "PHI",  # Philadelphia Flyers
                            "PIT",  # Pittsburgh Penguins
                            "SJS",  # San Jose Sharks
                            "SEA",  # Seattle Kraken
                            "STL",  # St. Louis Blues
                            "TBL",  # Tampa Bay Lightning
                            "TOR",  # Toronto Maple Leafs
                            "UTA",  # Utah Hockey Club
                            "VAN",  # Vancouver Canucks
                            "VGK",  # Vegas Golden Knights
                            "WSH",  # Washington Capitals
                            "WPG"   # Winnipeg Jets
                        ]

        self.rosterEndPoint = 'https://api-web.nhle.com/v1/roster'
        self.playerEndPoint = 'https://api.nhle.com/stats/rest/en/skater/summary'
    
        self.statSeasonId = statSeason #'20242025'
        self.rosterSeasonId = rosterSeason #'20252026'
        self.playerList = []




    def GetTeamData(self):

        #go through each team
        for team in self.nhl_team_abbreviations:
            
            #get teams roster
            rosterResponse = requests.get(f'{self.rosterEndPoint}/{team}/{self.rosterSeasonId}')

            if rosterResponse.status_code >= 200 and rosterResponse.status_code <= 299:

                rosterData = rosterResponse.json()

                #go through each player on the team
                for positionName,positionPlayers in rosterData.items():

                    for player in positionPlayers:
                        
                        params = {
                            "cayenneExp": f"playerId={player['id']} and seasonId={self.statSeasonId} and gameTypeId=2",
                            "limit": 1,
                            "start": 0,
                            "isAggregate": "false",
                            "isGame": "false"
                        }

                        #get each players details/stats
                        playerResponse = requests.get(self.playerEndPoint, params=params)

                        if playerResponse.status_code >= 200 and playerResponse.status_code <= 299:
                            
                            #check to ensure player has stats from the season in question
                            if len(playerResponse.json()['data']) > 0:

                                PlayerData = playerResponse.json()['data'][0]
                                
                                #add all details to a player stats class obj
                                self.playerList.append(PlayerStats(ID=player['id'],
                                                                FIRST_NAME=player['firstName']['default'],
                                                                LAST_NAME=player['lastName']['default'],
                                                                POSITION=PlayerData['positionCode'],
                                                                GP=PlayerData['gamesPlayed'],
                                                                GOALS=PlayerData['goals'],
                                                                ASSISTS=PlayerData['assists'],
                                                                POINTS=PlayerData['points'],
                                                                PPP=PlayerData['ppPoints'],
                                                                GWG=PlayerData['gameWinningGoals'],
                                                                SHG=PlayerData['shGoals'],
                                                                PIM=PlayerData['penaltyMinutes'], 
                                                                SOG=PlayerData['shots'],
                                                                PLUSMINUS=PlayerData['plusMinus']))
                            

                        else:
                            print(f"Bad response {playerResponse.status_code} for player {player['firstName']['default']} {player['lastName']['default']}. ")
                            return

            else:
                print(f"Bad response {rosterResponse.status_code} for team {team}.")
                return

        if len(self.playerList) > 20:
            
            #clear old entries in the DB
            output = self.nhldb.ClearDB()

            #add new data into db
            output = self.nhldb.AddPlayers(self.playerList)


    def GenerateTopFantasyRatingList(self,topMatches:int,defWeightBump:int):
        
        sqlQuery = f'''WITH BASE_SCORES AS (
                            SELECT FIRST_NAME,
                                    LAST_NAME,
                                    POSITION,
                                    GP,
                                    GOALS,
                                    ASSISTS,
                                    POINTS,
                                    SOG,
                                    PIM,
                                    PLUSMINUS,
                                    PPP,
                                    SHG,
                                    GWG,
                                    (
                                        ((GOALS - (SELECT AVG(GOALS) FROM main.skaters)) / 
                                        (SELECT SQRT(AVG((GOALS - (SELECT AVG(GOALS) FROM main.skaters)) * 
                                                                (GOALS - (SELECT AVG(GOALS) FROM main.skaters)))) FROM main.skaters)) +

                                        ((ASSISTS - (SELECT AVG(ASSISTS) FROM main.skaters)) / 
                                        (SELECT SQRT(AVG((ASSISTS - (SELECT AVG(ASSISTS) FROM main.skaters)) * 
                                                                (ASSISTS - (SELECT AVG(ASSISTS) FROM main.skaters)))) FROM main.skaters)) +

                                        ((PLUSMINUS - (SELECT AVG(PLUSMINUS) FROM main.skaters)) / 
                                        (SELECT SQRT(AVG((PLUSMINUS - (SELECT AVG(PLUSMINUS) FROM main.skaters)) * 
                                                                    (PLUSMINUS - (SELECT AVG(PLUSMINUS) FROM main.skaters)))) FROM main.skaters)) +

                                        ((PIM - (SELECT AVG(PIM) FROM main.skaters)) / 
                                        (SELECT SQRT(AVG((PIM - (SELECT AVG(PIM) FROM main.skaters)) * 
                                                                (PIM - (SELECT AVG(PIM) FROM main.skaters)))) FROM main.skaters)) +

                                        ((PPP - (SELECT AVG(PPP) FROM main.skaters)) / 
                                        (SELECT SQRT(AVG((PPP - (SELECT AVG(PPP) FROM main.skaters)) * 
                                                                (PPP - (SELECT AVG(PPP) FROM main.skaters)))) FROM main.skaters)) +

                                        ((SHG - (SELECT AVG(SHG) FROM main.skaters)) / 
                                        (SELECT SQRT(AVG((SHG - (SELECT AVG(SHG) FROM main.skaters)) * 
                                                                (SHG - (SELECT AVG(SHG) FROM main.skaters)))) FROM main.skaters)) +

                                        ((GWG - (SELECT AVG(GWG) FROM main.skaters)) / 
                                        (SELECT SQRT(AVG((GWG - (SELECT AVG(GWG) FROM main.skaters)) * 
                                                                (GWG - (SELECT AVG(GWG) FROM main.skaters)))) FROM main.skaters)) +

                                        ((SOG - (SELECT AVG(SOG) FROM main.skaters)) / 
                                        (SELECT SQRT(AVG((SOG - (SELECT AVG(SOG) FROM main.skaters)) * 
                                                                (SOG - (SELECT AVG(SOG) FROM main.skaters)))) FROM main.skaters))

                                    ) AS PLAYER_SCORE
                                    FROM main.skaters
                                    ORDER BY PLAYER_SCORE DESC)
                                    SELECT
                                    ROW_NUMBER() OVER (ORDER BY 
                                        CASE WHEN POSITION = 'D' THEN PLAYER_SCORE + {defWeightBump} ELSE PLAYER_SCORE END DESC
                                    ) AS RN,
                                    FIRST_NAME,
                                    LAST_NAME,
                                    POSITION,
                                    GP,
                                    GOALS,
                                    ASSISTS,
                                    POINTS,
                                    SOG,
                                    PIM,
                                    PLUSMINUS,
                                    PPP,
                                    SHG,
                                    GWG,
                                    CASE 
                                        WHEN POSITION = 'D' THEN ROUND(PLAYER_SCORE + {defWeightBump},2)
                                        ELSE ROUND(PLAYER_SCORE,2)
                                    END AS MOD_PLAYER_SCORE
                                FROM BASE_SCORES
                                ORDER BY MOD_PLAYER_SCORE DESC
                                LIMIT {topMatches};'''
        
        return self.nhldb.Query(sqlQuery)