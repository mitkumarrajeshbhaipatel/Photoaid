



### For database views 
brew install sqlite3

sqlite3 test.db 

### Detailed Setup ######################################################

### Project Setup Instructions ##########################################

Welcome!

Follow these simple steps to set up, run, and manage the project locally:

1. Create Virtual Environment

        python3.11 -m venv myenv
        This command will create a virtual environment named myenv.

2. Activate Virtual Environment

        source myenv/bin/activate
        After activation, your terminal will show (myenv) at the start of the line.

3. Install Project Dependencies

        pip install -r requirements.txt
        This will install all required Python packages listed in the requirements.txt file.

        python3.11 createTables.py
        this will create tables in database(only needs to do first time)

4. Run the FastAPI Server

        uvicorn app.main:app --reload
        After running this command:

Open http://127.0.0.1:8000/docs to access the Swagger UI API documentation.

Open http://127.0.0.1:8000/redoc to access the ReDoc API documentation.


### For Testing the APIs ###############################################
Follow these simple steps to test and run the project automatically:

1. Clean the database if needed.

    Photoaid % rm test.db
    python3.11 createTables.py

2. Set up a Virtual Environment:

    python3.11 -m venv myenv
    This command will create a virtual environment named myenv.

3. Activate the Virtual Environment:

    source myenv/bin/activate
    After activation, your terminal prompt will show (myenv) at the start.

4. Install project dependencies:

    pip install -r requirements.txt

5. Run the FastAPI Server:

    uvicorn app.main:app --reload
    The server will start at http://127.0.0.1:8000

6. Run All Tests:

    pytest
    This command will automatically discover and run all test cases under app/tests/ and show the results.

Summary of Commands:

python3.11 -m venv myenv

source myenv/bin/activate

pip install -r requirements.txt

uvicorn app.main:app --reload

pytest


### Database Management (SQLite) ##################################
If you want to view or interact with the SQLite database (test.db):

Install SQLite3 (if not installed)

        brew install sqlite3
        (You only need to install it once.)

Open and Use the Database

        sqlite3 test.db
        Inside the SQLite shell, you can run:


To list all tables:

        sql

        .tables
        To view the schema of a table (for example, users):

        sql
        .schema users
        To see all data in a table:

        sql
        SELECT * FROM users;
To exit:

        sql
        .exit
        Quick Example (Full Setup)


### Quick start ##################################

python3.11 -m venv myenv

source myenv/bin/activate

pip install -r requirements.txt

uvicorn app.main:app --reload


In another terminal window:

brew install sqlite3

sqlite3 test.db


### Notes #######################################

Always activate your virtual environment before running any Python commands.

Make sure you are inside the project directory (where app/ and test.db exist).

Press CTRL+C to stop the server at any time.

✅ Setup complete! You can now develop, test, and explore your FastAPI application.

================================================
