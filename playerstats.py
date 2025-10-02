class PlayerStats:

    def __init__(self, ID, FIRST_NAME:str, LAST_NAME:str, POSITION, GP, GOALS, ASSISTS, POINTS, PPP, GWG, SHG, PIM, SOG, PLUSMINUS):
        self.ID = ID
        self.FIRST_NAME = FIRST_NAME.replace("'", " ")
        self.LAST_NAME = LAST_NAME.replace("'", " ")
        self.POSITION = POSITION
        self.GP = GP  # Games Played
        self.GOALS = GOALS
        self.ASSISTS = ASSISTS
        self.POINTS = POINTS
        self.PPP = PPP  # Power Play Points
        self.GWG = GWG  # Game Winning Goals
        self.SHG = SHG  # Short-Handed Goals
        self.PIM = PIM  # Penalty Minutes
        self.SOG = SOG  # Shots on Goal
        self.PLUSMINUS = PLUSMINUS  # Plus/Minus Rating