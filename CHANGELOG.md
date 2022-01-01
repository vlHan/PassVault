# PassVault CHANGELOG

All notable change to this project will be documented here.

## [Unreleased]

## [V1.0] - 2021-12-29
### Added
- db folder in `.gitgnore`
- install of dependencies in `run.py`
- variables which is intended to be private

### Changed
- python code format (pep8)

### Removed
- Imports from database.py 
- email verification in begin_informations method
- sqlite parameter (close database)

## [V1.1] - 2021-12-30
### Added
- master password table (`masterpassword`)
- a logo (`.github/logo.png`) and moved `passvault.png` to `.github` folder 

### Changed
- The json file as a file database to a table in SQlite.
- key system to a ID sytem. 

### Removed
- json file imports, and function to stored the master password.
- key system 
