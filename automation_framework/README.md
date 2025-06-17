In this home assigment I focused on following OOP principles and used the Page Object Model design pattern for the UI part.
I created a pages folder where each page handles its own elements and actions that inherit from BasePage for reusability and structure.
To keep the project clean and organized, I added to the utilities folder helper and creator classes, each handling a specific functionality.
All data files are locate in a data folder, and sensitive values like the API key and PATH are stored securely in a .env file.
Finally, I included a reports folder for the final HTML report, and the SQLite database file sits at the root of the project.

# The files that added:

- ./utilities/base_page.py
- ./utilities/data_helper.py
- ./utilities/json_helper.py
- ./utilities/logger_helper.py
- ./utilities/report_creator.py
####
- ./pages/pages_object.py
- ./pages/whaether_main_page.py
- ./pages/whaether_city_page.py

####
**Tests include:**
- ./tests/conftest.py --> combine all the modules
- ./tests/test_end_to_end.py --> End-To-End flow
- ./tests/test_db.py -- > DB Connection 
- ./tests/test_openweather_api.py --> API response
- ./tests/test_openweather_web.py --> Web scraping

###
- data --> json files
- reports --> html report
- data --> SQLite DB for the table
###

**Note:** 
I would add .env file to store sensative data such as API key and path.


# Setup instruction

1. Clone the project from github to vscode / extract the folder from the zip file and open in IDE 
2. Make sure your under '\automation_framework' folder
3. Run pip install -r requirements.txt
4. Run pip freeze > requirements.txt

# Run Tests

1. To run all the tests togther run --> python -m pytest -s .\tests\
2. To run each file test:
    -  python -m pytest -s .\tests\test_db.py
    -  python -m pytest -s .\tests\test_openweather_api.py
    -  python -m pytest -s .\tests\test_openweather_web.py 
    -  python -m pytest -s .\tests\test_end_to_end.py  

# View Report

1. In Visual Studio marketplace install HTML Preview
2. Double click on the html file under report
3. Press inside the file with the mouse to fucos the file
4. Press ctrl+shift+V (Windows) or cmd+k v (Mac)
