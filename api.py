from flask import Flask, render_template, url_for, request, flash, session, redirect
from flask_classy import FlaskView, route
import csv, json, string, random

QUESTIONS_LOCATION = 'questions.csv'

QUESTION_LENGTH = 3
QUESTION_INDEX = 0
ANSWER_INDEX = 1
CATEGORY_INDEX = 2

app = Flask(__name__)

questions = []

class ApiView(FlaskView):
    route_base = "/api/"

    def index(self):
        return str(questions), 200

    @route("/<int:id>")
    def get(self, id):
        if (int(id) >= len(questions)):
            return '', 404
        return str(questions[id]), 200


    @route("/category/<category>")
    def get(self, category):
        return str(getQuestionsForCategory(category))

    @route("/post/", methods=['POST'])
    def post(self):
        question_info = json.loads(request.data)

        question = question_info["question"]
        answer = question_info["answer"]
        category = question_info["category"]

        questions.append([question, answer, category.lower()])
        with open(QUESTIONS_LOCATION, 'a') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
            writer.writerow([question, answer, category])
        return "success", 200


    def categories(self):
        return str(getCategories())


class WebAppView(FlaskView):
    route_base = "/"
    def index(self):
        return render_template('home.html')

    def create(self):
        return render_template('create.html', javascriptPath=url_for('static', filename='js/create.js'))

    def subjects(self):
        categoriesFormatted = [[]]
        row = 0
        column = 0
        for category in getCategories():
            categoriesFormatted[row].append(category)
            column += 1
            if (column >= 3):
                column = 0
                categoriesFormatted.append([])
                row += 1

        return render_template('subjects.html', categories=categoriesFormatted)

    def subject(self, category):
        questions = getQuestionsForCategory(category)
        question = random.choice(questions)
        return render_template('answer.html', subject=category, question=question[QUESTION_INDEX], answer=question[ANSWER_INDEX], javascriptPath=url_for('static', filename='js/answerPage.js'))

class LoginView(FlaskView):
    def index(self):
        return render_template('login.html')

    def post(self):
        # data = json.loads(request.data)

        users = []
        with open('users.csv') as usersFile:
            users = list(csv.reader(usersFile, delimiter=",", quotechar='"'))

        username = request.form["username"]
        password_candidate = request.form["password"]

        login_sucess = False
        for user in users:
            if user[0] == username:
                if password_candidate == user[1]:
                    login_sucess = True
                    session['logged_in'] = True
                    session['username'] = username

                    flash('You are now logged in', 'success')
                    return redirect(url_for('WebAppView:index'))

        if not login_sucess:
            error = "Incorrect login"
            return render_template('login.html', error=error)
        return render_template('login.html')


class LogoutView(FlaskView):
    def index(self):
        session.clear()
        flash('You are now logged out', 'success')
        return redirect(url_for('WebAppView:index'))


def getCategories():
    categories = []
    for question in questions:
        if len(question) == QUESTION_LENGTH:
            catagory = question[CATEGORY_INDEX].lower()
            if not catagory.lower() in (name.lower() for name in categories):
                categories.append(string.capwords(catagory))
    return categories

def getQuestionsForCategory(category):
    output = [];
    for question in questions:
        if len(question) == QUESTION_LENGTH:
            if question[CATEGORY_INDEX].lower() == category.lower():
                output.append(question)
    return output

ApiView.register(app)
WebAppView.register(app)
LoginView.register(app)
LogoutView.register(app)

if __name__ == '__main__':
    app.secret_key = 'secret1234'

    with open(QUESTIONS_LOCATION, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        questions = list(reader)

    app.run(debug=True, port=80)
