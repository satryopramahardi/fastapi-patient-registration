# fastapi-patient-registration
Fastapi implementation with sqlaclhemy and mariadb for a system backend. Imported jinja for later frontend development. ~There is some issues with default value for patient registration where patients birth date will set today's date as a default value.~ Fixed.

After running, go to http://localhost:8080/docs/ for testing purpose

| Route | Description | Response|
| ----------- | ----------- | ----------- |
| /login | For patient login. Login id created through registration process | Returns access token |
| /register | Create a patient profile, used for login | Returns user input |
| /patients/view | Show all patients from database. Used for debugging purpose | Returns all patient data |
| /patients/profile/ | Show current user information | Returns information about patient currently login |
| /patients/profile/update | Updates currently login patient password and/or birthday | Returns updated information |
