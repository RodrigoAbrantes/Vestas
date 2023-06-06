'''Module to manage the sqlite3 database'''
import sqlite3
from flask import Flask, flash, request, render_template, g, redirect, url_for


app = Flask(__name__)
app.secret_key = 'vestas_project'


def get_db():
    '''Returns a cursor connected to the tower service database'''
    database = getattr(g, '_database', None)
    if database is None:
        database = g._database = sqlite3.connect('tower_service.db')
        cursor = database.cursor()
    return cursor


@app.route("/")
def index_page():
    '''Renders index page'''
    return render_template("index.html")


@app.route("/", methods=["post"])
def retrieve_tower():
    '''Checks for valid Id value and redirects to tower's page'''
    tower_id = int(request.form["towerId"])
    if tower_id < 1:
        flash("Invalid id provided!")
        return redirect("/")
    return redirect(f"/tower/{tower_id}")


@app.route('/tower/<int:tower_id>')
def tower(tower_id):
    '''Checks if exists tower with provided Id and renders tower page'''
    db_cursor = get_db()
    db_cursor.execute(f"SELECT * FROM shell where \
                      shell.shell_tower_id = {tower_id}\
                          ORDER BY shell.position")
    
    data = db_cursor.fetchall()

    if len(data) < 1:
        flash("No tower found for that id")
        return redirect("/")

    num_shells = len(data)
    height = 0
    for shell in data:
        height += shell[2]
    return render_template("view.html", tower_data=data,
                           tower_size=num_shells, tower_height=height,
                           tower_id=tower_id)


@app.route("/add")
def add_page():
    '''Renders static html page for adding towers'''
    return render_template("add.html")


@app.route("/add", methods=["post"])
def add_tower():
    '''Parses tower section input string, validates the data provided\
    and insert the data into the database'''
    form_info = request.form["shellInfo"]

    if len(form_info) < 1:
        flash("No values inserted!")
        return redirect("/add")

    tower_shells = []
    for index, shell in enumerate(form_info.split(";")):
        shell_properties = shell.split(",")
        # checks if correct number of input values were provided
        if len(shell_properties) == 6:
            tower_shells.append(list(map(float, shell_properties)))
        elif len(shell) == 0:
            break
        else:
            flash(f"Invalid number of parameters in shell nº{index+1}")
            return redirect("/add")

    tower_shells.sort(key=lambda x: x[0])

    # checks if positions are valid, which implies that 1st shell has position
    # 1 and last shell position len(tower) after sorting
    if tower_shells[0][0] != 1 or tower_shells[-1][0] != len(tower_shells):
        flash("Invalid positions given to shells!")
        return redirect("/add")

    if validate_tower(tower_shells):

        database = g._database = sqlite3.connect('tower_service.db')

        db_cursor = database.cursor()

        tower_bottom_diameter = tower_shells[0][2]
        tower_top_diameter = tower_shells[-1][3]

        db_cursor.execute(f"""INSERT INTO tower\
            (tower_id,bottom_diameter,top_diameter,number_of_shells) \
            VALUES(null,{tower_bottom_diameter},{tower_top_diameter},\
                {len(tower_shells)})""")

        shell_tower_id = db_cursor.lastrowid

        for shell in tower_shells:

            db_cursor.execute(
                f"""INSERT INTO shell VALUES (null,{shell[0]},\
                {shell[1]},{shell[2]},{shell[3]},{shell[4]},{shell[5]}\
                ,{shell_tower_id})""")

        database.commit()

        flash(f"Tower added succesfully with id {shell_tower_id}")
        return redirect("/")

    flash('Failed to add tower due to wrong shell values')
    return redirect("/add")


def validate_numeric_values_of_shell(shell_properties):
    '''To validate if the shell properties are valid'''
    height = shell_properties[1]
    bottom_diameter = shell_properties[2]
    top_diameter = shell_properties[3]
    thickness = shell_properties[4]
    steel_density = shell_properties[5]
    
    if height <= 0:
        flash('Invalid shell height!')
        return False
    if bottom_diameter <= 0:
        flash('Invalid bottom diameter!')
        return False
    if top_diameter <= 0:
        flash('Invalid top diameter!')
        return False
    if thickness <= 0:
        flash('Invalid top diameter!')
        return False
    if steel_density <= 0:
        flash('Invalid top diameter!')
        return False
    return True


def validate_tower(tower_shells):
    '''To validate if the shell properties are consistent with\
        the adjacent shells'''

    tower_shells_list = []
    previous_top_diameter = -1

    for index, shell_properties in enumerate(tower_shells):

        bottom_diameter = shell_properties[2]
        top_diameter = shell_properties[3]

        if index > 0:
            if bottom_diameter != previous_top_diameter:
                flash(f'Shell nº{shell_properties[0]} bottom diameter\
                    is not the same as \
                        shell nº{int(shell_properties[0])-1} top diameter!')
                return False

        if validate_numeric_values_of_shell(shell_properties):
            tower_shells_list.append(shell_properties)
            previous_top_diameter = top_diameter
        else:
            return False

    return True


@app.route("/delete")
def delete_page():
    '''Renders static html page for deleting towers'''
    return render_template("delete.html")


@app.route("/delete", methods=["post"])
def delete_tower():
    '''Validates Id provided, and deletes tower with received Id'''
    tower_id = int(request.form["towerId"])

    if tower_id < 1:
        flash("Invalid Id provided!")
        return redirect("/delete")

    database = g._database = sqlite3.connect('tower_service.db')

    db_cursor = database.cursor()

    db_cursor.execute(
        f"""DELETE FROM shell where \
                    shell.shell_tower_id = {tower_id}""")

    db_cursor.execute(
        f"""DELETE FROM tower where tower.tower_id = {tower_id}""")

    database.commit()

    if db_cursor.rowcount > 0:
        flash("Tower deleted succesfully!")
        return redirect("/")

    flash("Tower Id not found!")
    return redirect("/delete")


@app.route("/update")
def update_page():
    '''Renders the static page for updating towers'''
    return render_template("update.html")


@app.route("/update", methods=["post"])
def update_tower():
    '''Verifies if tower and shell exist, and perform the update to the\
        chosen section of the tower'''
    new_value_to_update = int(request.form["propertyValue"])
    tower_property = request.form["property"]

    if new_value_to_update <= 0:
        flash(f"Invalid {tower_property} value!")
        return redirect("/update")

    tower_id = int(request.form["towerId"])

    if tower_id < 1:
        flash("Invalid Id!")
        return redirect("/update")

    shell_position = request.form["shellId"]

    conn = sqlite3.connect('tower_service.db')

    db_cursor = conn.cursor()

    db_cursor.execute(
        f"""SELECT * FROM tower \
            where
            tower.tower_id = {tower_id}""")

    if db_cursor.fetchone():

        db_cursor.execute(f"""UPDATE shell SET \
            {tower_property} = {new_value_to_update} \
            where
            shell.position = {shell_position}\
                AND \
                    shell.shell_tower_id = {tower_id}""")

        if db_cursor.rowcount < 1:
            flash(f"Update didn't go through, tower doesn't have shell\
                in position {shell_position}!")
            return redirect("/update")

        conn.commit()
        flash("Update Successful!")
        return redirect(url_for('tower', tower_id=tower_id))

    flash(f"No tower with Id {tower_id}")
    return redirect("/update")


@app.route("/searchDimensions")
def search_dimensions_page():
    '''Renders the static page for searching towers by diameter'''
    return render_template("searchDimensions.html")


@app.route("/searchDimensions", methods=["post"])
def search_tower():
    '''Searches for towers that match the provided requirements'''
    bottom_diameter_min = request.form['bottomDiameterMin']
    top_diameter_min = request.form['topDiameterMin']
    bottom_diameter_max = request.form['bottomDiameterMax']
    top_diameter_max = request.form['topDiameterMax']

    conn = sqlite3.connect('tower_service.db')

    db_cursor = conn.cursor()

    db_cursor.execute(f"""SELECT * FROM tower where\
        tower.bottom_diameter BETWEEN {bottom_diameter_min} \
            AND {bottom_diameter_max}\
            AND tower.top_diameter BETWEEN {top_diameter_min} AND\
                {top_diameter_max}
            """)

    towers = db_cursor.fetchall()

    print(towers)

    if len(towers) < 1:
        flash("No towers found for that specifications")
        return redirect("searchDimensions")

    flash(f"Found {len(towers)} towers!")
    return render_template("searchDimensions.html", towers=towers)


@app.teardown_appcontext
def close_connection(exception):
    '''Closes database connection after requests'''
    if exception:
        exit()
    database = getattr(g, '_database', None)
    if database is not None:
        database.close()


if __name__ == '__main__':
    app.run()
