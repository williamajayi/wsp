# wsp
This app allows students to register and take the created test questions by their teacher, following on from the registration and login process.
Once a student has taken the test, that student gets taken to a results page notifying them whether they have passed or failed the test.
The teacher can also view the students that have attempted the test as well as their test scores and percentage grades in a single location.

#Requirements:
python version 3.7
Flask version 1.0.2
Jinja2 version 2.10
requests version 2.21.0


#Usage: commands
Virtualenv venv --python=python3.7 (Create the virtual environment)
. venv/bin/activate (Activate the virtual environment on a UNIX like system)
pip install -r requirements.txt (Install the dependencies)
python create_table.py (Create database and table to store user and admin information)
python main.py  (Launch the application)

#Documentation:
This application was built with Python and Flask micro-framework for rapid application development. It has several endpoints which are as follows in the order :

'/':
Serves as an index page that welcomes the student immediately after a successful log in.

'/test':  
This takes care of loading the questions from a file and displaying to the student, accepting whatever option the student chooses in each of the questions and checking if its the correct one then incrementing the score as the test progresses. When the question in the bank reaches the end, it redirects to the results page and displays the score and the grade.

'/results':
This handles displaying the score and grades for the test takers

'/admin/view':
This area is available only to the admin users supposedly, the teachers and it takes care of displaying the questions in the bank with checkboxes to allow teachers select the questions with different difficulties they want to post as the test questions from the question bank. A post questions button is located at the top of the page.

'/admin/students':
This area is also available only to the admin users and it handles displaying the registered students in a table format with columns including their personal details, if the registered students have taken the test or not, as well as their scores and grades. It also computes the percentage passed or failed out of the students registered and taken the test.

'/admin/post':
This area is available only to the admin users for posting questions to the question bank.

'/logout':
This handles the logout process for logged in students.

'/login':
This handles the login process for students.

'/register':
This handles the registration process for the students.

'/admin':
This handles the admin index page after successful login for the admin users (teachers).

'/admin/login':
This takes care of the login process for the admin users.

'/admin/register':
This handles the registration process for the admin users.
