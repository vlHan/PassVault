# PassVault CHANGELOG
All notable change to this project will be documented here.

## [Unreleased]

## [V1.0] - 2021-12-29
This is the initial version.

## [V1.1] - 2021-12-30
### Added
- master password table (`masterpassword`) in the database SQlite.
- a logo (`demo/logo.png`) and moved `passvault.png` to `demo` folder 

### Changed
- The json file as a database to a table in the SQlite database.
- key system to a ID system (change/delete informations)

### Removed
- json master password system.
- key system

## [V1.2] - 2022-01-23
### Added
- Exceptions (KeyboardInterrupt) and exit config
- Colors library (_rich_)
- See only one information (`stored_passwords()`)
    - It shows just the platofrm and the ID
- Checkmark and x mark

### Changed
- Manager class in `__main__.py` to `modules/main.py`
- Remove _colorama_ as the color library to _rich_
- to look up the password, need to know the ID using the function `stored_password()`

### Removed
- Old show informations function (`see_all()`)

## [V1.3] - 2022-01-25
### Added
- Code optimization using new functions 
- New password generator function

### Changed
- instance of menu and database class in `modules/main.py`

### Removed
- unused functions

## [V1.4] - 2022-01-29
### Added
- New functions in the database file to avoid sqlite3 functions repetitions.
- The name of the sqlite database is the name of your machine
    - Be sure not to change the name or something, otherwise the program will create another file and you'll lose the database

### Changed
- Connection to the database file, now verify if the user is running in or out of the PassVault diretory

### Removed
- `vault.db` in `.gitignore`
- Remove coding utf-8 (do not need)
