from flask import *
from flask import Flask
from flask import render_template, request, redirect, session, url_for
import sqlite3
import string
import csv
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from operator import itemgetter
from functools import wraps
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dns import resolver



# Global Definitions
count = 0
applicant_login = False
company_login = False
useremail = ""
userid = 0

app = Flask(__name__, template_folder='templates')

# secret key
app.secret_key = b'0p]*:;_zd}=@hu'


# verify login for secure web pages
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return render_template('login.html', msg="You will need to login first!")
        return f(*args, **kwargs)

    return decorated_function


# home page
@app.route('/', methods=["GET", "POST"])
def home():
    # search for job
    if request.method == "POST":
        if request.form["jobtitle"] != "" and request.form["locselect"] != "":
            jobtitle = request.form['jobtitle']
            location = request.form['locselect']
            jobs = searchjob(location, jobtitle)
            con = sqlite3.connect("user_data.db")
            c = con.cursor()
            c.execute("Select count(*) from applicant_info;")
            result = c.fetchone()
            data_can = result[0]
            c.execute("Select count(*) from company_info;")
            result = c.fetchone()
            data_com = result[0]
            with open('Profile_data.csv', 'r', encoding='utf-8') as file1:
                csv_can = csv.reader(file1)
                csv_can = list(csv_can)
                file1.close()
            with open('Job_roles.csv', 'r', encoding='utf-8') as file1:
                csv_com = csv.reader(file1)
                csv_com = list(csv_com)
                file1.close()
            return render_template('index.html', jobs=jobs, len=len(jobs), data_can_count=data_can,
                                   data_com_count=data_com,
                                   linkedin_count=len(csv_can), indeed_count=len(csv_com))
    # website statistics
    jobs = searchjob("", "")
    con = sqlite3.connect("user_data.db")
    c = con.cursor()
    c.execute("Select count(*) from applicant_info;")
    result = c.fetchone()
    data_can = result[0]
    c.execute("Select count(*) from company_info;")
    result = c.fetchone()
    data_com = result[0]
    with open('Profile_data.csv', 'r', encoding='utf-8') as file1:
        csv_can = csv.reader(file1)
        csv_can = list(csv_can)
        file1.close()
    with open('Job_roles.csv', 'r', encoding='utf-8') as file1:
        csv_com = csv.reader(file1)
        csv_com = list(csv_com)
        file1.close()
    return render_template('index.html', jobs=jobs, len="Top", data_can_count=data_can, data_com_count=data_com,
                           linkedin_count=len(csv_can), indeed_count=len(csv_com))


# contact page
@app.route('/contact')
def contact():
    return render_template('contact.html')


# about page
@app.route('/about')
def about():
    return render_template('about.html')


# login page
@app.route('/login', methods=["GET", "POST"])
def login():
    if (request.method == "POST"):
        global useremail
        global userid
        global company_login
        global applicant_login
        email = request.form["username"]
        password = request.form["pass"]
        con = sqlite3.connect("user_data.db")
        c = con.cursor()
        c.execute(
            "SELECT * FROM company_info WHERE username=? and password=?", (email, password))
        recruiter = c.fetchall()
        c.execute(
            "SELECT * FROM applicant_info WHERE username=? and password=?", (email, password))
        applicant = c.fetchall()
        for i in recruiter:
            if (email == i[11] and password == i[12]):
                useremail = email
                userid = i[0]
                company_login = True
                session['username'] = email
                session['role'] = 'company'
                can = candidatelist()
                can = sorted(can, key=lambda d: d['URL'][:2])
                pass_dict = {'companyname': i[1], 'jobtitle': i[2], 'location': i[3], 'jobtype': i[4],
                             'description': i[5].replace('`', '\n'), 'website': i[6], 'email': i[7], 'salary': i[10],
                             'facebook': i[8], 'twitter': i[9]}
                return render_template('candidatelisting.html', len=len(can), candidates=can, profile=pass_dict)
        for j in applicant:
            if (email == j[8] and password == j[9]):
                useremail = email
                userid = j[0]
                applicant_login = True
                session['username'] = email
                session['role'] = 'applicant'
                jobs = joblistings()
                jobs = sorted(jobs, key=lambda d: d['URL'][:2])
                pass_dict = {'Name': j[1], 'email': j[2], 'location': j[3], 'education': j[4], 'skills': j[5],
                             'contact': j[6], 'linkedin': j[7], 'tagline': j[10]}
                return render_template('job-listings.html', len=len(jobs), candidates=jobs, profile=pass_dict)
        con.close()
        return render_template('login.html', msg="Invalid username or password! Try again....")
    return render_template('login.html')


# post a job
@app.route('/post', methods=["GET", "POST"])
def post():
    if (request.method == "POST"):
        if (request.form["companyemail"] != "" and request.form["jobtitle"] != "" and request.form[
            "joblocation"] != "" and request.form["jobtype"] != "" and request.form["companyname"] != "" and
                request.form["companywebsite"] != "" and request.form["description"] != "" and request.form[
                    "email"] != "" and request.form['passw'] != "" and request.form["retype"] != ""):
            paj_email = request.form["companyemail"]
            jobtitle = request.form["jobtitle"]
            joblocation = request.form["joblocation"]
            jobtype = request.form["jobtype"]
            companyname = request.form["companyname"]
            companywebsite = request.form["companywebsite"]
            if request.form["companywebsitefb"] != "":
                companywebsitefb = request.form["companywebsitefb"]
            else:
                companywebsitefb = " "
            if request.form["companywebsitetw"] != "":
                companywebsitetw = request.form["companywebsitetw"]
            else:
                companywebsitetw = " "
            if request.form["salary"] != "":
                salary = request.form["salary"]
            else:
                salary = " "
            desc = request.form["description"]
            desc = desc.replace('\n', '`')
            email = request.form["email"]
            password = request.form["passw"]
            con = sqlite3.connect("user_data.db")
            c = con.cursor()
            c.execute(
                "Select count(*) from company_info where companyname=? and jobtitle=? and joblocation=? and username=?",
                (companyname, jobtitle, joblocation, email))
            duplic = c.fetchone()
            if duplic[0] == 0:
                if is_email_exists(paj_email):
                    query1 = "INSERT INTO company_info(companyname,jobtitle,joblocation,jobtype,description,companywebsite,email,companywebsitefb,companywebsitetw,salary,username,password) VALUES (?,?,?,?,?,?,?,?,?,?,?,?);"
                    c.execute(query1, (
                    companyname, jobtitle, joblocation, jobtype, desc, companywebsite, paj_email, companywebsitefb,
                    companywebsitetw, salary, email, password))
                    con.commit()
                    con.close()
                    write_dict = {'Job Title': jobtitle, 'Company': companyname, 'Location': joblocation, 'Salary': salary,
                                  'Description': desc, 'URL': "database"}
                    head = ['Job Title', 'Company', 'Location', 'Salary', 'Description', 'URL']
                    with open('Job_roles.csv', 'a', newline='', encoding='utf-8') as file1:
                        writor = csv.DictWriter(file1, head)
                        writor.writerow(write_dict)
                        file1.close()
                    body_mail = "Welcome " + companyname + '''\nThank you for joining us. We gladly welcome you to Job Net community. Get recommendations right at your click!\n\n
                                        Keep updated on aspiring candidates for your location. Know who is interested in joining your job. We are here to connect you to your next best employee!\n\n                                                  Job Net '''
                    send_email(paj_email, "Welcome to Job Net!", body_mail)
                    return render_template('login.html')
                else:
                    con.close()
                    flash("The email is not recognized!\nPlease provide a valid email adddress.....")
            else:
                con.close()
                flash("Job Profile with the mentioned details already exist!\nTry changing some of the fields.....")
        elif (request.form["companyemail"] == "" or request.form["jobtitle"] == "" or request.form[
            "joblocation"] == "" or request.form["jobtype"] == "" or request.form["companyname"] == "" or request.form[
                  "companywebsite"] == "" or request.form["description"] == "" or request.form["email"] == ""):
            flash("Please fill all the required fields!")
        elif (request.form['passw'] != request.form["retype"]):
            flash("Password and retyped password don't match!")

    return render_template('post-job.html')


def candidatelist():
    global useremail
    global userid
    vectorizer = TfidfVectorizer()
    stop_words = set(stopwords.words('english'))
    con = sqlite3.connect("user_data.db")
    c = con.cursor()
    c.execute("Select * from company_info where username=? and companyid=?", (useremail, userid))
    result = c.fetchone()
    c.execute("")
    con.close()
    loc1 = result[3]
    skill1 = result[5]
    recommend2 = []
    loc_similar_rows = []
    default_recommend = []
    recommend = []
    temp_dict = {}
    with open('Profile_data.csv', 'r', encoding='utf-8') as file1:
        data = csv.DictReader(file1,
                              fieldnames=['Name', 'Job Title', 'Company', 'College', 'Location', 'Skills', 'URL'])
        for one_row in data:
            if one_row['Name'] == 'Name':
                continue
            temp_dict = one_row
            locat2 = one_row['Location']
            loc1 = loc1.lower()
            loca2 = locat2.lower()
            loc1 = loc1.translate(str.maketrans(" ", " ", string.punctuation))
            loc2 = loca2.translate(str.maketrans(" ", " ", string.punctuation))
            lo1 = word_tokenize(loc1)
            lo2 = word_tokenize(loc2)
            loc1_nostop = [w for w in lo1 if not w.lower() in stop_words]
            loc2_nostop = [w for w in lo2 if not w.lower() in stop_words]
            corpus_location = [' '.join(loc1_nostop), ' '.join(loc2_nostop)]
            matrix_location = vectorizer.fit_transform(corpus_location)
            cosine_sim_loc = cosine_similarity(matrix_location, matrix_location)
            loc_similarity = cosine_sim_loc[0][1]
            skill2 = one_row['Skills']
            skill2.replace('`', ' ')
            skill1 = skill1.lower()
            skill2 = skill2.lower()
            location2 = locat2.lower()
            skill1 = skill1.translate(str.maketrans(" ", " ", string.punctuation))
            skill2 = skill2.translate(str.maketrans(" ", " ", string.punctuation))
            skill_1 = word_tokenize(skill1)
            skill_2 = word_tokenize(skill2)
            Doc1_nostop = [w for w in skill_1 if not w.lower() in stop_words]
            Doc2_nostop = [w for w in skill_2 if not w.lower() in stop_words]
            corpus_skills = [' '.join(Doc1_nostop), ' '.join(Doc2_nostop)]
            matrix_skill = vectorizer.fit_transform(corpus_skills)
            cosine_sim_skill = cosine_similarity(matrix_skill, matrix_skill)
            if one_row['URL'] == 'database':
                con = sqlite3.connect("user_data.db")
                c = con.cursor()
                c.execute("Select applicantid,tagline from applicant_info where name=? and email=?",
                          (one_row['Name'], one_row['Company']))
                result = c.fetchone()
                temp_dict.update({'applicantid': result[0]})
                temp_dict.update({'tagline': result[1]})
                con.close()
            temp_dict.update({'Location_similarity': cosine_sim_loc[0][1]})
            temp_dict.update({'Skill_similarity': cosine_sim_skill[0][1]})
            if cosine_sim_loc[0][1] > 0.3 or cosine_sim_skill[0][1] >= 0.3:
                if cosine_sim_skill[0][1] >= 0.01:
                    recommend.append(one_row)
            elif cosine_sim_loc[0][1] >= 0:
                loc_similar_rows.append(one_row)
            else:
                default_recommend.append(one_row)
        if recommend != []:
            jobs = sorted(recommend, key=itemgetter('Skill_similarity'), reverse=True)
        elif loc_similar_rows != []:
            jobs = sorted(loc_similar_rows, key=itemgetter('Skill_similarity'), reverse=True)
        elif default_recommend != []:
            jobs = sorted(default_recommend, key=itemgetter('Skill_similarity'), reverse=True)
        # else:
        #     jobs = sorted(recommend2, key=itemgetter('Skill_similarity'), reverse=True)

        file1.close()
    return (jobs)


# logic for home page job search
def searchjob(loc1, skill1):
    if loc1 != "" and skill1 != "":
        vectorizer = TfidfVectorizer()
        stop_words = set(stopwords.words('english'))
        recommend2 = []
        loc_similar_rows = []
        default_recommend = []
        recommend = []
        temp_dict = {}
        with open('Job_roles.csv', 'r', encoding='utf-8') as file1:
            data = csv.DictReader(file1,
                                  fieldnames=['Job Title', 'Company', 'Location', 'Salary', 'Description', 'URL'])
            for one_row in data:
                # Location similarity
                if one_row['Job Title'] == 'Job Title':
                    continue
                temp_dict = one_row
                locat2 = one_row['Location']
                loc1 = loc1.lower()
                loca2 = locat2.lower()
                loc1 = loc1.translate(str.maketrans(" ", " ", string.punctuation))
                loc2 = loca2.translate(str.maketrans(" ", " ", string.punctuation))
                lo1 = word_tokenize(loc1)
                lo2 = word_tokenize(loc2)
                loc1_nostop = [w for w in lo1 if not w.lower() in stop_words]
                loc2_nostop = [w for w in lo2 if not w.lower() in stop_words]
                corpus_location = [' '.join(loc1_nostop), ' '.join(loc2_nostop)]
                matrix_location = vectorizer.fit_transform(corpus_location)
                cosine_sim_loc = cosine_similarity(matrix_location, matrix_location)
                loc_similarity = cosine_sim_loc[0][1]

                # Skill similarity
                skill2 = one_row['Job Title']
                skill1 = skill1.lower()
                skill2 = skill2.lower()
                location2 = locat2.lower()
                skill1 = skill1.translate(str.maketrans(" ", " ", string.punctuation))
                skill2 = skill2.translate(str.maketrans(" ", " ", string.punctuation))
                skill_1 = word_tokenize(skill1)
                skill_2 = word_tokenize(skill2)
                Doc1_nostop = [w for w in skill_1 if not w.lower() in stop_words]
                Doc2_nostop = [w for w in skill_2 if not w.lower() in stop_words]
                corpus_skills = [' '.join(Doc1_nostop), ' '.join(Doc2_nostop)]
                matrix_skill = vectorizer.fit_transform(corpus_skills)
                cosine_sim_skill = cosine_similarity(matrix_skill, matrix_skill)
                temp_dict.update({'Location_similarity': cosine_sim_loc[0][1]})
                temp_dict.update({'Skill_similarity': cosine_sim_skill[0][1]})
                if cosine_sim_loc[0][1] > 0.3:
                    if cosine_sim_skill[0][1] >= 0.01:
                        recommend.append(one_row)
                    elif cosine_sim_loc[0][1] >= 0:
                        loc_similar_rows.append(one_row)
                    else:
                        default_recommend.append(one_row)
                else:
                    recommend2.append(one_row)
            if recommend != []:
                jobs = sorted(recommend, key=itemgetter('Skill_similarity'), reverse=True)
            elif loc_similar_rows != []:
                jobs = sorted(loc_similar_rows, key=itemgetter('Skill_similarity'), reverse=True)
            elif default_recommend != []:
                jobs = sorted(default_recommend, key=itemgetter('Skill_similarity'), reverse=True)
            else:
                jobs = sorted(recommend2, key=itemgetter('Skill_similarity'), reverse=True)
            file1.close()
        return (jobs)
    else:
        recommend = []
        jobs = []
        with open('Job_roles.csv', 'r', encoding='utf-8') as file1:
            data = csv.DictReader(file1,
                                  fieldnames=['Job Title', 'Company', 'Location', 'Salary', 'Description', 'URL'])
            for one_row in data:
                if one_row['Job Title'] == 'Job Title':
                    continue
                recommend.append(one_row)
            file1.close()
        for l in range(0, 9):
            jobs.append(recommend[l])
        return (jobs)


# protected web page job listing
def joblistings():
    global useremail
    global userid
    vectorizer = TfidfVectorizer()
    stop_words = set(stopwords.words('english'))
    con = sqlite3.connect("user_data.db")
    c = con.cursor()
    c.execute("Select * from applicant_info where username=? and applicantid=?", (useremail, userid))
    result = c.fetchone()
    con.close()
    loc1 = result[3]
    skill1 = result[5]
    recommend2 = []
    loc_similar_rows = []
    default_recommend = []
    recommend = []
    temp_dict = {}
    with open('Job_roles.csv', 'r', encoding='utf-8') as file1:
        data = csv.DictReader(file1, fieldnames=['Job Title', 'Company', 'Location', 'Salary', 'Description', 'URL'])
        for one_row in data:
            # Location similarity
            if one_row['Job Title'] == 'Job Title':
                continue
            temp_dict = one_row
            locat2 = one_row['Location']
            loc1 = loc1.lower()
            loca2 = locat2.lower()
            loc1 = loc1.translate(str.maketrans(" ", " ", string.punctuation))
            loc2 = loca2.translate(str.maketrans(" ", " ", string.punctuation))
            lo1 = word_tokenize(loc1)
            lo2 = word_tokenize(loc2)
            loc1_nostop = [w for w in lo1 if not w.lower() in stop_words]
            loc2_nostop = [w for w in lo2 if not w.lower() in stop_words]
            corpus_location = [' '.join(loc1_nostop), ' '.join(loc2_nostop)]
            matrix_location = vectorizer.fit_transform(corpus_location)
            cosine_sim_loc = cosine_similarity(matrix_location, matrix_location)
            loc_similarity = cosine_sim_loc[0][1]

            # Skill similarity
            skill2 = one_row['Description']
            skill2.replace('`', ' ')
            skill1 = skill1.lower()
            skill2 = skill2.lower()
            location2 = locat2.lower()
            skill1 = skill1.translate(str.maketrans(" ", " ", string.punctuation))
            skill2 = skill2.translate(str.maketrans(" ", " ", string.punctuation))
            skill_1 = word_tokenize(skill1)
            skill_2 = word_tokenize(skill2)
            Doc1_nostop = [w for w in skill_1 if not w.lower() in stop_words]
            Doc2_nostop = [w for w in skill_2 if not w.lower() in stop_words]
            corpus_skills = [' '.join(Doc1_nostop), ' '.join(Doc2_nostop)]
            matrix_skill = vectorizer.fit_transform(corpus_skills)
            cosine_sim_skill = cosine_similarity(matrix_skill, matrix_skill)
            if one_row['URL'] == 'database':
                con = sqlite3.connect("user_data.db")
                c = con.cursor()
                c.execute("Select companyid,companywebsite,email from company_info where companyname=? and jobtitle=?",
                          (one_row['Company'], one_row['Job Title']))
                result = c.fetchone()
                websit = result[1]
                maile = result[2]
                temp_dict.update({'companyid': result[0]})
                temp_dict.update({'website': websit})
                temp_dict.update({'email': maile})
                con.close()
            temp_dict.update({'Location_similarity': cosine_sim_loc[0][1]})
            temp_dict.update({'Skill_similarity': cosine_sim_skill[0][1]})
            if cosine_sim_loc[0][1] > 0.3 or cosine_sim_skill[0][1] >= 0.3:
                if cosine_sim_skill[0][1] >= 0.01:
                    recommend.append(one_row)
            elif cosine_sim_loc[0][1] >= 0:
                loc_similar_rows.append(one_row)
            else:
                default_recommend.append(one_row)
        if recommend != []:
            jobs = sorted(recommend, key=itemgetter('Skill_similarity'), reverse=True)
        elif loc_similar_rows != []:
            jobs = sorted(loc_similar_rows, key=itemgetter('Skill_similarity'), reverse=True)
        elif default_recommend != []:
            jobs = sorted(default_recommend, key=itemgetter('Skill_similarity'), reverse=True)
        # else:
        #     jobs = sorted(recommend2, key=itemgetter('Skill_similarity'), reverse=True)
        file1.close()
    return (jobs)


# create profile page
@app.route('/createprofile', methods=["GET", "POST"])
def createprofile():
    if (request.method == "POST"):
        if (request.form["name"] != "" and request.form["profileemail"] != "" and request.form["location"] != "" and
                request.form["education"] != "" and request.form["skills"] != "" and request.form["contact"] != "" and
                request.form["email"] != "" and request.form['passw'] != "" and request.form["retype"] != ""):
            can_name = request.form["name"]

            can_mail = request.form["profileemail"]
            location = request.form["location"]
            edu = request.form["education"]
            skills = request.form["skills"]
            can_contact = request.form["contact"]
            if request.form["linkedin"] != "":
                can_linkedin = request.form["linkedin"]
            else:
                can_linkedin = " "
            if request.form["subtitle"] != "":
                can_tag = request.form["subtitle"]
            else:
                can_tag = " "
            email = request.form["email"]
            password = request.form["passw"]
            con = sqlite3.connect("user_data.db")
            c = con.cursor()
            c.execute("Select count(*) from applicant_info where name=? and email=? and username=?",
                      (can_name, can_mail, email))
            duplic = c.fetchone()
            if duplic[0] == 0:
                if is_email_exists(can_mail):
                    query = "INSERT INTO applicant_info(name,email,location,education,skills,contact,linkedin,username,password,tagline) VALUES (?,?,?,?,?,?,?,?,?,?)"
                    c.execute(query, (
                    can_name, can_mail, location, edu, skills.replace('\n','`'), can_contact, can_linkedin, email, password, can_tag))
                    con.commit()
                    con.close()
                    write_dict = {'Name': can_name, 'Job Title': can_contact, 'Company': can_mail, 'College': edu,
                                  'Location': location,
                                  'Skills': skills, 'URL': "database"}
                    head = ['Name', 'Job Title', 'Company', 'College', 'Location', 'Skills', 'URL']
                    with open('Profile_data.csv', 'a', newline='', encoding='utf-8') as file1:
                        writor = csv.DictWriter(file1, head)
                        writor.writerow(write_dict)
                    body_mail="Welcome "+can_name+'''\nThank you for joining us. We gladly welcome you to Job Net community. Get recommendations right at your click!\n\n
                    Keep updated on the latest job postings for your location. Know which recruiter checked out your profile. We are here to connect you to your dream job!\n\n                                                  Job Net '''
                    send_email(can_mail,"Welcome to Job Net!",body_mail)
                    return render_template('login.html')
                else:
                    con.close()
                    flash("The email is not recognized!\nPlease provide a valid email adddress.....")
            else:
                con.close()
                flash("Applicant with the mentioned details already exist!\nTry changing some of the fields.....")
        elif (request.form["name"] == "" or request.form["profileemail"] == "" or request.form[
            "location"] == "" or request.form["education"] == "" or request.form["skills"] == "" or request.form[
                  "contact"] == "" or request.form["email"] == "" or request.form["passw"] == ""):
            flash("Please fill all the required fields!")
        elif (request.form['passw'] != request.form["retype"]):
            flash("Password and retyped password don't match!")
    return render_template('create-profile.html')


# view a single job or candidate in recommended list
@app.route('/<int:passedid>', methods=["Get", "post"])
@login_required
def viewprofile(passedid):
    global company_login, userid, useremail

    def check_role():
        if 'role' not in session:
            return None
        elif session['role'] == 'company':
            return 'company'
        else:
            return 'applicant'

    role = check_role()
    if role is None:
        return render_template('login.html',
                               msg="You are not authorized to visit the page! Please log in to continue...")
    elif role == 'company':
        con = sqlite3.connect("user_data.db")
        c = con.cursor()
        c.execute("Select * from applicant_info where applicantid=?", (passedid,))
        result = c.fetchone()
        if result == None:
            flash("The Profile you are trying to access, does not exist anymore!")
            return render_template("index.html")
        pass_dict = {'Name': result[1], 'email': result[2], 'location': result[3], 'education': result[4],
                     'skills': result[5], 'contact': result[6], 'linkedin': result[7], 'tagline': result[10]}
        body_email="Hello "+result[1]+" !\nA recruiter viewed your profile! Find out who is interested in hiring your skills!\nVisit- https://localhost:5004/"+str(userid)+" \n\n                                               Job Net"
        send_email(result[2],"Recruiter viewed your profile!",body_email)
        con.close()
        return render_template('profile-single.html', candi=pass_dict)
    else:
        con = sqlite3.connect("user_data.db")
        c = con.cursor()
        c.execute("Select * from company_info where companyid=?", (passedid,))
        result = c.fetchone()
        pass_dict = {'companyname': result[1], 'jobtitle': result[2], 'location': result[3], 'jobtype': result[4],
                     'description': result[5].replace('`', '\n'), 'website': result[6], 'email': result[7],
                     'salary': result[10], 'facebook': result[8], 'twitter': result[9]}
        con.close()
        return render_template('job-single.html', jobd=pass_dict)


# update a user profile
@app.route('/updateprofile', methods=['POST', 'GET'])
@login_required
def update():
    user = session['username']

    def chec_role():
        if 'role' not in session:
            return None
        elif session['role'] == 'company':
            return 'company'
        else:
            return 'applicant'

    role = chec_role()
    if role is None:
        return render_template('login.html',
                               msg="You are not authorized to visit the page! Please log in to continue...")
    elif role == 'company':
        # recruiter updated the profile
        if (request.method == "POST"):
            paj_email = request.form["companyemail"]
            jobtitle = request.form["jobtitle"]
            joblocation = request.form["joblocation"]
            # jobregion= request.form["jobregion"]
            jobtype = request.form["jobtype"]
            # editor1 = request.form["editor1"]
            companyname = request.form["companyname"]
            companywebsite = request.form["companywebsite"]
            if request.form["companywebsitefb"] != "":
                companywebsitefb = request.form["companywebsitefb"]
            else:
                companywebsitefb = " "
            if request.form["companywebsitetw"] != "":
                companywebsitetw = request.form["companywebsitetw"]
            else:
                companywebsitetw = " "
            if request.form["salary"] != "":
                salary = request.form["salary"]
            else:
                salary = " "
            desc = request.form["description"]
            desc = desc.replace('\n', '`')
            if is_email_exists(paj_email):
                conn = sqlite3.connect('user_data.db')
                c = conn.cursor()
                c.execute("Select * from company_info where username=?", (user,))
                result_list = c.fetchone()
                c.execute(
                    "UPDATE company_info SET companyname=?, jobtitle=?,joblocation=?,jobtype=?, description=?, companywebsite=?, email=?, companywebsitefb=?, companywebsitetw=?, salary=? WHERE username=?",
                    (companyname, jobtitle, joblocation, jobtype, desc.replace('\n', '`'), companywebsite, paj_email,
                     companywebsitefb, companywebsitetw, salary, user))
                conn.commit()
                new_values = {'Job Title': result_list[2], 'Company': result_list[1], 'Location': joblocation,
                              'Salary': salary, 'Description': desc, 'URL': 'database'}
                print(new_values)
                with open('Job_roles.csv', mode='r', encoding='utf-8') as file:
                    csv_reader = csv.DictReader(file)
                    rows = []
                    for row in csv_reader:
                        rows.append(row)
                    file.close()
                for index, row in enumerate(rows):
                    if row['Job Title'] == result_list[2] and row['Company'] == result_list[1]:
                        rows[index].update(new_values)

                with open('Job_roles.csv', mode='w', newline='', encoding='utf-8') as file:
                    head = ['Job Title', 'Company', 'Location', 'Salary', 'Description', 'URL']
                    csv_writer = csv.DictWriter(file, fieldnames=head)
                    csv_writer.writeheader()
                    for row in rows:
                        csv_writer.writerow(row)
                    file.close()
                conn.close()
                return render_template('login.html', msg="Profile updated successfully! Please login again...")
            else:
                return render_template('login.html', msg="Profile update failed! Updated email was not found...")
        # display the previous filled form of recruiter
        else:
            con = sqlite3.connect("user_data.db")
            c = con.cursor()
            c.execute("Select * from company_info where username=?", (user,))
            result = c.fetchone()
            pass_dict = {'companyname': result[1], 'jobtitle': result[2], 'location': result[3], 'jobtype': result[4],
                         'description': result[5].replace('`', '\n'), 'website': result[6], 'email': result[7],
                         'salary': result[10], 'facebook': result[8], 'twitter': result[9]}
            con.close()
            return render_template('update.html', role=role, profile=pass_dict)

    elif role == 'applicant':
        # applicant updated the profile
        if (request.method == "POST"):
            can_name = request.form["name"]
            can_mail = request.form["profileemail"]
            location = request.form["location"]
            edu = request.form["education"]
            skills = request.form["skills"]
            can_contact = request.form["contact"]
            if request.form["linkedin"] != "":
                can_linkedin = request.form["linkedin"]
            else:
                can_linkedin = " "
            if request.form["subtitle"] != "":
                can_tag = request.form["subtitle"]
            else:
                can_tag = " "
            if is_email_exists(can_mail):
                conn = sqlite3.connect('user_data.db')
                c = conn.cursor()
                c.execute("Select * from applicant_info where username=?", (user,))
                result_list = c.fetchone()
                c.execute(
                    "UPDATE applicant_info SET name=?, email=?, location=?, education=?, skills=?, contact=?, linkedin=?, tagline=? WHERE username=?",
                    (can_name, can_mail, location, edu, skills, can_contact, can_linkedin, can_tag, user))
                conn.commit()
                new_values = {'Name': result_list[1], 'Job Title': can_contact, 'Company': can_mail, 'College': edu,
                              'Location': location,
                              'Skills': skills, 'URL': 'database'}
                with open('Profile_data.csv', mode='r', encoding='utf-8') as file:
                    csv_reader = csv.DictReader(file)
                    rows = []
                    for row in csv_reader:
                        rows.append(row)
                    file.close()
                for index, row in enumerate(rows):
                    if row['Name'] == result_list[1] and row['Company'] == result_list[2] and row['College'] == result_list[
                        4]:
                        rows[index].update(new_values)

                with open('Profile_data.csv', mode='w', newline='', encoding='utf-8') as file:
                    head = ['Name', 'Job Title', 'Company', 'College', 'Location', 'Skills', 'URL']
                    csv_writer = csv.DictWriter(file, fieldnames=head)
                    csv_writer.writeheader()
                    for row in rows:
                        csv_writer.writerow(row)
                    file.close()

                conn.close()
                return render_template('login.html', msg="Profile updated successfully! Please login again...")
            else:
                return render_template('login.html', msg="Profile update failed! Updated email was not found...")
        # display previously filled form of applicant
        else:
            con = sqlite3.connect("user_data.db")
            c = con.cursor()
            c.execute("Select * from applicant_info where username=?", (str(user),))
            result = c.fetchone()
            pass_dict = {'name': result[1], 'email': result[2], 'location': result[3], 'education': result[4],
                         'skills': result[5], 'contact': result[6], 'linkedin': result[7], 'tagline': result[10]}
            con.close()
            return render_template('update.html', role=role, profile=pass_dict)


# logout and clear session
@app.route('/logout')
def logout():
    global applicant_login, userid, useremail, company_login
    applicant_login = False
    company_login = False
    useremail = ""
    userid = 0
    session.clear()
    return render_template('login.html')


# delete a account
@app.route('/dropaccount', methods=['POST'])
@login_required
def dropaccount():
    user = session['username']

    def check_role():
        if 'role' not in session:
            return None
        elif session['role'] == 'company':
            return 'company'
        else:
            return 'applicant'

    role = check_role()
    if request.method == "POST" and role == 'company':
        passw = request.form['del_password']
        conn = sqlite3.connect('user_data.db')
        c = conn.cursor()
        c.execute("Select * from company_info where username=?", (user,))
        result_list = c.fetchone()
        if passw == result_list[12]:
            c.execute("UPDATE company_info SET password='' WHERE username=?", (user,))
            conn.commit()
            with open('Job_roles.csv', mode='r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                rows = []
                for row in csv_reader:
                    rows.append(row)
                file.close()
            for index, row in enumerate(rows):
                if row['Job Title'] == result_list[2] and row['Company'] == result_list[1]:
                    del rows[index]

            with open('Job_roles.csv', mode='w', newline='', encoding='utf-8') as file:
                head = ['Job Title', 'Company', 'Location', 'Salary', 'Description', 'URL']
                csv_writer = csv.DictWriter(file, fieldnames=head)
                csv_writer.writeheader()
                for row in rows:
                    csv_writer.writerow(row)
                file.close()
            conn.close()
            return render_template('login.html', msg="Profile deleted successfully!")

    elif request.method == "POST" and role == 'applicant':
        passw = request.form['del_password2']
        conn = sqlite3.connect('user_data.db')
        c = conn.cursor()
        c.execute("Select * from applicant_info where username=?", (user,))
        result_list = c.fetchone()
        if passw == result_list[9]:
            c.execute("UPDATE applicant_info SET password='' WHERE username=?", (user,))
            conn.commit()
            with open('Profile_data.csv', mode='r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                rows = []
                for row in csv_reader:
                    rows.append(row)
                file.close()
            for index, row in enumerate(rows):
                if row['Name'] == result_list[1] and row['Company'] == result_list[2] and row['College'] == result_list[
                    4]:
                    del rows[index]

            with open('Profile_data.csv', mode='w', newline='', encoding='utf-8') as file:
                head = ['Name', 'Job Title', 'Company', 'College', 'Location', 'Skills', 'URL']
                csv_writer = csv.DictWriter(file, fieldnames=head)
                csv_writer.writeheader()
                for row in rows:
                    csv_writer.writerow(row)
                file.close()

            conn.close()
            return render_template('login.html', msg="Profile Deleted Successfully!")


def send_email(recipient_email, subject, message):
    sender_email="jobnetrecommendations@gmail.com"
    sender_password="zbze ipzn zwqb ivyz"
    email_message = MIMEMultipart()
    email_message['From'] = sender_email
    email_message['To'] = recipient_email
    email_message['Subject'] = subject
    email_message.attach(MIMEText(message, 'plain'))
    smtp_session = smtplib.SMTP('smtp.gmail.com', 587)
    smtp_session.starttls()
    smtp_session.login(sender_email, sender_password)
    smtp_session.send_message(email_message)
    smtp_session.quit()



def is_email_exists(email):
    domain = email.split('@')[1]
    try:
        mx_records = resolver.query(domain, 'MX')
        if mx_records:
            # MX records exist
            return True
        else:
            # No MX records found
            return False
    except resolver.NXDOMAIN:
        # Domain does not exist
        return False
    except resolver.NoAnswer:
        # No DNS response
        return False

if __name__ == '__main__':
    app.run(debug=True, port=5004)
