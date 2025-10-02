import sqlite3
from playerstats import PlayerStats

class SQLiteFunctions:

    def __init__(self):
        pass


    def Update(self,sqlQuery:str):

        try: 

            connection = sqlite3.connect("static/nhlStats.db")
            cursor = connection.cursor()

            output = cursor.execute(sqlQuery)
            connection.commit()

            return f"{output.rowcount} rows affected."

        except Exception as e:
            
            return e
        
        finally:
            connection.close()

    def Query(self,sqlQuery:str):

        try: 

            connection = sqlite3.connect("static/nhlStats.db")
            cursor = connection.cursor()

            cursor.execute(sqlQuery)
            rows = cursor.fetchall()

            return rows

        except Exception as e:

            return e
        
        finally:
            connection.close()
    
    def AddPlayers(self,players:list):

        sqlQueryHeader = '''INSERT INTO "main"."skaters" ("ID", "FIRST_NAME", "LAST_NAME", "POSITION", "GP", "GOALS", "ASSISTS", "POINTS","PPP", "GWG", "SHG", "PIM", "SOG", "PLUSMINUS" ) VALUES'''
        
        sqlQueryBody = []

        for player in players:
            sqlQueryBody.append(f"({player.ID}, '{player.FIRST_NAME}', '{player.LAST_NAME}', '{player.POSITION}', {player.GP}, {player.GOALS}, {player.ASSISTS}, {player.POINTS}, {player.PPP}, {player.GWG}, {player.SHG}, {player.PIM}, {player.SOG}, {player.PLUSMINUS})")

        fullQuery = f"{sqlQueryHeader} {','.join(sqlQueryBody)}"

        return self.Update(fullQuery)
    

    def ClearDB(self):

        output = self.Update('DELETE FROM "main"."skaters"')

        return output


