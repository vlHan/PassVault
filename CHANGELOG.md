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
- Colors
- See only one information (`stored_passwords()`)
    - It shows just the platofrm and the ID
- Checkmark and x mark

### Changed
- Manager class in `__main__.py` to `modules/main.py`
- to look up the password, need to know the ID using the function `stored_password()`

### Removed
- Old show informations function (`see_all()`)
