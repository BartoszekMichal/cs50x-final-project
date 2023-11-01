# BUDGETING APP

#### Description:

"""THIS WORK SHALL NOT BE USED, REPRODUCED OR DISTRIBUTED BY ANY OTHER THIRD PARTY EXCEPT HARVARD UNIVERSITY AND THE AUTHOR"""
"""THIS PROJECT REQUIRES "lib50" AND "cs50" PACKAGES INSTALLED."""

This app has been created simply for budgeting needs of households, however it can be simply altered for other uses.

helpers.py include login_required function which is a decorator, a function which calls itself in order to "decorate" certain functions in app.py which requires user to be logged in to call a certain function.

The very first page of the app is entry.html, where you can register your account and log in.

If you don't have an account yet, click register button. It will render register.html template when reached via GET method. You should fill "username", "password" and "confirm password" fields. If user already exists in database or passwords do not match, a proper error will occur. However, if you submit all the fields correctly with a unique "username" a hash password will be gerenated based on your input and your profile will be added to database. Then you will be redirected to the login.html.

After reaching login.html the app forgets any user id, when login.html reached via GET method, the app renders login.html. When reached via POST, by submitting form, the app firstly check if both "username" and "password" fields have been submitted. Then the username is queried in SQL database. If the user exists in the database and the password is correct the app will remember the user by assigning it to session["user_id"]. Then redirect to the homepage layout.html.

After loggin in, you're being redirected to layout.html, which is the homepage of the app.
You will see a navbar with few options. You will also see the current balance of the user.

The "Home" link will redirect you to homepage, updating user's balance.

"Add Income" link renders add_income.html where you can choose your source of income and an amount. After clicking "Add Income" button with chosen source and typed amount, the data will be inserted into SQL "income" table via POST method. User's balance will be updated and you will be redirected into the same page in order to add another income.

"Add Expenses" link renders add_expenses.html where you can choose your expense and an amount. After clicking "Add Expense" button with chosen expense and typed amount the app will verify if the user has enough cash to add an expense, if positive the data will be inserted into SQL "expenses" table via POST method. User's balance will be updated and you will be redirected into the same page in order to add another expense.

List of sources as well as list of expenses have been imported from ielist.py.

"Income Chart" renders income_chart.html with a bar chart with source of income on the x_axis and the amount on the y_axis based on the data selected from SQL "income" table displaying all the income the user has ever submitted. Duplicated sources of income will be summed up.

"Expense Chart" renders expense_chart.html with a bar chart with expenses on the x_axis and the amount on the y_axis based on the data selected from SQL "expenses" table displaying all the expenses the user has ever submitted. Duplicated sources of expenses will be summed up.

Both charts have been created using chart.js framework and Flask.

"Change Password" link should be used by correct "old" current password and two times new password. If all the requirements will not be fulfilled, the webpage will give error.

If user will submit all the fields by reaching route via POST, change_password function will extract the old password from users database and check all conditions. If all are met
generate_password_hash function will create a new hash key and it will be replaced in users database. Then user will be redirected to homepage with changed password.

The "Log Out" link will forget any user_id from the session and will redirect to entry.html.

THE END
