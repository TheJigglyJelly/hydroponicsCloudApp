# - Import flask, os, and pyodbc (sql connection) - #
from flask import Flask, render_template_string
import os
import pymysql

# - Pass __name__ - # 
app = Flask(__name__)

# - Database connection deets - #
dbServ = os.environ.get('DB_SERVER')
dbDatabase = os.environ.get('DB_DATABASE')
dbUsername = os.environ.get('DB_USERNAME')
dbPass = os.environ.get('DB_PASSWORD')

# - HTML for output of SQL data - #
HTMLTemp = """
<!DOCTYPE html>
<html>
    <head><title>Hydroponics System</title></head>
    <body>
        <h1>Hydroponics System Tell-er What to Do-er</h1>
        <p>Current PH: {{phLevel}}</p>
        <p>Current EC: {{ecLevel}}</p>
        <p>Water Temp: {{tempLevel}}</p>
        <h3>{{hydroRec}}</h3>
        <p>Last Checked: {{lastCheck}}</p>
    </body>
</html>
"""

# - Attempt database connection - #
def getDatabase():
    connection = None
    try:
        # - pyodbc connection string to connect to database - #
        connection = pymysql.connect(
            host     = dbServ,
            user     = dbUsername,
            password = dbPass,
            database = dbDatabase,
            port     = 3306
        )
        cursor = connection.cursor()
        cursor.execute("SELECT ph, ec, temp, timeStamp FROM sensor_data ORDER BY timeStamp DESC LIMIT 1")
        row = cursor.fetchone()

        # - Insert database values into row - #
        if row:
            return {
                'ph': row[0],
                'ec': row[1],
                'temp': row[2],
                'timestamp': row[3]
            }
        return None
    # - Close connection for next use - #
    finally:
        if 'connection' in locals() and connection:
            connection.close()

# - Get reccomendation based on database readings - #
def getRec(ph, ec, temp):
    if ph < 5.5:
        return "pH too low, add pH Grow solution"
    elif ph > 6.5:
        return "pH too high, add pH Down solution"
    elif ec < 1.0:
        return "EC too low, add EC solution"
    elif ec > 1.5:
        return "EC too high, add more water to dilute"
    else: 
        return "Levels are good"

# - Define web app route - #
@app.route('/')
def index():
    data = getDatabase()
    if data:
        # - Insert values into HTML template set previousely - #
        hydroRec = getRec(data['ph'], data['ec'], data['temp'])
        return render_template_string(HTMLTemp,
                          phLevel = data['ph'],
                          ecLevel = data['ec'],
                          tempLevel = data['temp'],
                          hydroRec = hydroRec,
                          lastCheck = data['timestamp'])

# - Allow app to be available across server it is deployed on - #
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000))
