import psycopg2


class DBConnect:

    def __init__(self):
        DB_URL = '#'
        try:
            self.conn = psycopg2.connect(DB_URL, sslmode='require')
            self.conn.autocommit = True
            self.cursor = self.conn.cursor()
        except:
            print('Failed')

##WARSTATS

    def addentry(self, name, wins, losses):
        winrate = '0%' if wins+losses == 0 else '{}%'.format(int(100/(wins+losses)*wins))
        self.cursor.execute("INSERT INTO warrers(name, s_wins, s_losses, winrate) VALUES('" + '{}'.format(name.capitalize()) + "','" + '{}'.format(wins) + "','" + '{}'.format(losses) + "','" + '{}'.format(winrate) + "')")

    def rementry(self, name):
        self.cursor.execute("DELETE FROM warrers WHERE name = '{}'".format(name.capitalize()))

    def getall(self):
        self.cursor.execute("SELECT * FROM warrers ORDER BY s_wins DESC")
        init = self.cursor.fetchall()
        names = [i[0] for i in init]
        wins = [i[1] for i in init]
        losses = [i[2] for i in init]
        winrate = [i[3] for i in init]
        return(names, wins, losses, winrate)

    def nameget(self):
        self.cursor.execute("SELECT name FROM warrers ORDER BY s_wins DESC")
        tnames = self.cursor.fetchall()
        return([n[0] for n in tnames])

    def getstat(self, name):
        self.cursor.execute("SELECT s_wins, s_losses, winrate FROM warrers WHERE name = '{}'".format(name.capitalize()))
        stats = self.cursor.fetchall()
        wins, losses, ratio = stats[0]
        return(wins, losses, ratio)

    def calcrate(self, name):
        self.cursor.execute("SELECT s_wins, s_losses FROM warrers WHERE name = '{}'".format(name.capitalize()))
        w, l = self.cursor.fetchall()[0]
        winrate = '0%' if int(w+l) == 0 else '{}%'.format(int((100/(w+l)*w)))          
        self.cursor.execute("UPDATE warrers SET winrate = '{}' WHERE name = '{}'".format(winrate, name.capitalize()))

    def addw(self, name):
        self.cursor.execute("SELECT s_wins FROM warrers WHERE name = '{}'".format(name.capitalize()))
        w = self.cursor.fetchall()[0][0]
        self.cursor.execute("UPDATE warrers SET s_wins = {} WHERE name = '{}'".format(w+1, name.capitalize()))
        self.calcrate(name.capitalize())

    def addl(self, name):
        self.cursor.execute("SELECT s_losses FROM warrers WHERE name = '{}'".format(name.capitalize()))
        l = self.cursor.fetchall()[0][0]
        self.cursor.execute("UPDATE warrers SET s_losses = {} WHERE name = '{}'".format(l+1, name.capitalize()))
        self.calcrate(name.capitalize())

    def setx(self, name, wins, losses):
        self.cursor.execute("UPDATE warrers SET s_wins = {}, s_losses = {} WHERE name = '{}'".format(wins, losses, name.capitalize()))
        self.calcrate(name.capitalize())

    def reset(self, name):
        self.setx(name, 0, 0)


##TOURNAMENT

    def gethof(self):
        self.cursor.execute("SELECT ttype, winner, row_number() OVER () FROM hof ORDER BY id ASC")
        ttypes = []
        winners = []
        editions = []
        for n in self.cursor.fetchall():
            ttypes.append(n[0])
            winners.append(n[1])
            editions.append(n[2])
        return(ttypes, winners, editions)
    
    def addhof(self, ttype, name):
        self.cursor.execute("INSERT INTO hof(ttype, winner) VALUES('{}', '{}')".format(ttype, name))

    def remhof(self, name):
        self.cursor.execute("DELETE FROM hof WHERE id = '{}'".format(name))

    def getcount(self):
        self.cursor.execute("SELECT row_number() OVER () FROM hof")
        t = self.cursor.fetchall()
        e = t[len(t)-1][0]
        return(e+1)