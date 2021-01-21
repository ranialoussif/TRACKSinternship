import psycopg2
from flask import Flask, render_template, request, redirect, session, jsonify

app = Flask(__name__)
app.secret_key = 'random secret key'
con = psycopg2.connect(database="tracks", user="postgres", password="admin", host='localhost')


@app.route('/')
def homepage():
    return redirect("/login")


@app.route('/login', methods=['POST', 'GET'])
def loginpage():
    message = ''
    if 'username' in session:
        return redirect("/analytics")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if checkCredentials(username, password):
            session['username'] = username
            return redirect("/analytics")
        message = "Please verify your credentials (username is website_developer)"
    return render_template("loginpage.html", message=message)


@app.route("/analytics")
def analyticspage():
    if 'username' not in session:
        return redirect("/login")
    cur = con.cursor()
    filters = ["type_of_calculations", "type_of_goods", "start_city", "end_city"]
    filter = request.args.get("filter")
    req = ""
    if filter is not None and filter in filters:
        if filter == "all" or filter == "empty":
            req = "SELECT * FROM homework.shipments"
        else:
            req = "SELECT * FROM homework.shipments order by {} ".format(filter)
    else:
        req = "SELECT * FROM homework.shipments"
    cur.execute(req)
    shipments = cur.fetchall()
    return render_template("analyticspage.html", shipments=shipments)


@app.route("/analytics/carrier/<id>")
def analyticssinglepage(id):
    if 'username' not in session:
        return redirect("/login")
    cur = con.cursor()
    cur.execute("SELECT * FROM homework.shipments where id={}".format(id))
    item = cur.fetchone()
    return render_template("carrier.html", carrier=item)


def checkCredentials(username, password):
    if username != "website_developer":
        return False
    return True


@app.route("/logout")
def logout():
    if 'username' in session:
        session.pop('username', None)
        return redirect("/login")
    return redirect("/login")


@app.route("/analytics/date", methods=["POST"])
def getBydate():
    start_date = request.form["start_date"]
    end_date = request.form["end_date"]
    cur = con.cursor()
    req = "SELECT * FROM homework.shipments"
    if len(start_date) > 0:
        req += " WHERE start_time >= timestamp '{}'".format(start_date)
    if len(end_date) > 0 and len(start_date) > 0:
        req += " AND end_time <= timestamp '{}'".format(end_date)
    if len(start_date) == 0 and len(end_date) > 0:
        req += " WHERE end_time <= timestamp '{}'".format(end_date)
    cur.execute(req)
    shipments = cur.fetchall()

    return jsonify(shipments)


if __name__ == '__main__':
    app.run(debug=True)
