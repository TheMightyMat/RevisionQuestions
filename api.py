from flask import Flask, render_template, url_for, request, flash, session, redirect
from flask_classy import FlaskView, route
from functools import wraps
import csv, json, string, random, hashlib, shutil
import logging

QUESTIONS_LOCATION = 'questions.csv'

QUESTION_LENGTH = 5

fieldnames = ["primary_key", "question", "answer", "category", "user"]

app = Flask(__name__)
app.secret_key = 'secret1234'

questions = []

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You must be logged in to do that, please log in', 'danger')
            return redirect(url_for('LoginView:index'))
    return wrap

class ApiView(FlaskView):
    route_base = "/api/"

    def index(self):
        return str(questions), 200

    @route("/<int:id>")
    def get(self, id):
        question = getQuestionById(id)
        if not question == None:
            return str(question), 200
        else:
            return "Question not found", 404


    @route("/category/<category>")
    def get(self, category):
        return str(getQuestionsByColumn(category, "category"))

    @route("/post/", methods=['POST'])
    def post(self):
        question_info = json.loads(request.data.decode('utf-8'))

        primary_key = getNextKeyValue()
        question = question_info["question"]
        answer = question_info["answer"]
        category = question_info["category"]
        user = question_info["user"]

        questions.append({"primary_key": primary_key, "question": question, "answer": answer, "category": category.lower(), "user": user})
        with open(QUESTIONS_LOCATION, 'a', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
            writer.writerow({"primary_key": primary_key, "question": question, "answer": answer, "category": category, "user": user})
        return "success", 200


    @route("/put/<int:id>", methods=['PUT'])
    def put(self, id):
        question_info = json.loads(request.data.decode('utf-8'))

        question = question_info["question"]
        answer = question_info["answer"]
        category = question_info["category"]

        with open(QUESTIONS_LOCATION, 'r') as csvFile, open("temp.csv", 'w') as output:
            reader = csv.DictReader(csvFile, fieldnames=fieldnames, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
            writer = csv.DictWriter(output, fieldnames=fieldnames, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

            for row in reader:
                if id == int(row["primary_key"]):
                    row['question'] = question
                    row['answer'] = answer
                    row['category'] = category

                writer.writerow({'primary_key': row['primary_key'], 'question': row['question'], 'answer': row['answer'], 'category': row['category'], 'user': row['user']})

        shutil.move("temp.csv", QUESTIONS_LOCATION)
        return "success", 200

    def categories(self):
        return str(getCategories())


class WebAppView(FlaskView):
    route_base = "/"

    def index(self):
        return render_template('home.html')

    @route('/create/')
    @login_required
    def create(self):
        return render_template('create.html', categories=getCategories(), javascriptPath=url_for('static', filename='js/create.js'))

    @route('/edit/<int:questionId>')
    @login_required
    def edit(self, questionId):
        question = getQuestionById(questionId)
        return render_template('edit.html', categories=getCategories(), questionId=questionId, question=question["question"], answer=question["answer"], category=question["category"], user=question["user"], javascriptPath=url_for('static', filename='js/edit.js'))

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
        categoryQuestions = getQuestionsByColumn(category, "category")
        return render_template('questionList.html', questionsTitle=category, questionsList=categoryQuestions)


    def random(self, category):
        categoryQuestions = getQuestionsByColumn(category, "category")
        questionId = random.choice(categoryQuestions)["primary_key"]
        return redirect(url_for("WebAppView:question", id=int(questionId)))


    @route('/question/<int:id>')
    def question(self, id):
        question=getQuestionById(id)
        answer = question["answer"].split("\n")
        return render_template('question.html', questionId=int(question["primary_key"]), subject=string.capwords(question["category"]), question=question["question"], answerLines=answer, answer=question["answer"], user=question["user"], javascriptPath=url_for('static', filename='js/answerPage.js'))

    def user(self, user):
        userQuestions = getQuestionsByColumn(user, "user")
        return render_template('questionList.html', questionsTitle=user, questionsList=userQuestions)


class SignUpView(FlaskView):
    def index(self):
        return render_template('signup.html')

    def post(self):
        username=request.form["username"]
        password=request.form["password"]

        password_hash = hashlib.sha512(password.encode('utf-8')).hexdigest()

        existingUsers = []
        with open('users.csv') as usersFile:
            existingUsers = list(csv.reader(usersFile, delimiter=",", quotechar='"'))

        if username in [name[0] for name in existingUsers if name != []]:
            error = 'Username already taken'
            return render_template('signup.html', error=error)

        with open('users.csv', 'a') as usersFile:
            writer = csv.writer(usersFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
            writer.writerow([username, password_hash])

        flash('Account created, you can now log in!', 'success')
        return redirect(url_for('WebAppView:index'))

class LoginView(FlaskView):
    def index(self):
        return render_template('login.html')

    def post(self):
        users = []
        with open('users.csv') as usersFile:
            users = list(csv.reader(usersFile, delimiter=",", quotechar='"'))

        username = request.form["username"]
        password_candidate = request.form["password"]

        password_candidate_hash = hashlib.sha512(password_candidate.encode('utf-8')).hexdigest()

        login_sucess = False
        for user in users:
            if user[0] == username:
                if password_candidate_hash == user[1]:
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
    questions = []
    with open(QUESTIONS_LOCATION, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=fieldnames, delimiter=',', quotechar='"')
        for row in reader:
            questions.append(row)

    categories = []
    for question in questions:
        if len(question) == QUESTION_LENGTH:
            category = question["category"].lower()
            if not category.lower() in (name.lower() for name in categories):
                categories.append(string.capwords(category))
    return categories


def getQuestionsByColumn(value, columnName):
    questions = []
    with open(QUESTIONS_LOCATION, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=fieldnames, delimiter=',', quotechar='"')
        for row in reader:
            questions.append(row)

    output = []
    for question in questions:
        if len(question) == QUESTION_LENGTH:
            if question[columnName].lower() == value.lower():
                output.append(question)
    return output

def getNextKeyValue():
    highest = 0
    with open(QUESTIONS_LOCATION, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=fieldnames, delimiter=',', quotechar='"')
        for row in reader:
            if (int(row["primary_key"]) > highest):
                highest = int(row["primary_key"])
    return highest + 1

def getQuestionById(id):
    questions = []
    with open(QUESTIONS_LOCATION, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=fieldnames, delimiter=',', quotechar='"')
        for row in reader:
            questions.append(row)

    for question in questions:
        if (len(question) == QUESTION_LENGTH):
            if int(question["primary_key"]) == id:
                return question
    return None

ApiView.register(app)
WebAppView.register(app)
LoginView.register(app)
LogoutView.register(app)
SignUpView.register(app)

if __name__ == '__main__':
    with open(QUESTIONS_LOCATION, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=fieldnames, delimiter=',', quotechar='"')
        for row in reader:
            questions.append(row)

    app.run(debug=True, port=80)
