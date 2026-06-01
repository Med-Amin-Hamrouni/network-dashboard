from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
import subprocess

app = Flask(__name__)

# DATABASE CONFIG
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///network.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# DATABASE TABLE
class History(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    host = db.Column(db.String(100))

    status = db.Column(db.String(50))


@app.route('/')
def home():

    host = request.args.get("host")

    status = "Waiting for test..."
    color = "white"

    if host:

        result = subprocess.run(
            ["ping", "-n", "1", host],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:

            status = "ONLINE ✅"
            color = "lightgreen"

        else:

            status = "OFFLINE ❌"
            color = "red"

        # SAVE TO DATABASE
        new_test = History(
            host=host,
            status=status
        )

        db.session.add(new_test)
        db.session.commit()

    # GET HISTORY
    history = History.query.all()

    return render_template(
        "index.html",
        status=status,
        color=color,
        history=history
    )


# CLEAR HISTORY
@app.route('/clear')
def clear():

    History.query.delete()

    db.session.commit()

    return """
    <h1>History Cleared 😄</h1>

    <a href='/'>
        Go Back
    </a>
    """


if __name__ == '__main__':

    with app.app_context():
        db.create_all()

    app.run(debug=True)