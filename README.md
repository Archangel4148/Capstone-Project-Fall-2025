# Nudgy
This is Nudgy, an application meant to help you stay on track and get your work done on time. It consists of application tracking, a calendar to schedule your work, a To-Do list, and a timer. The name "Nudgy" comes from the ability for the app to "Nudge" you when you need to do work, or when it notices you are slacking off!

## Installation
See [Building](README.md#building).

Nudgy uses a PostgreSQL database.  

To keep database credentials **out of the repository**, we use a local `.env` file that is never committed. See `src/api/config.example.env` for a template. To connect to the database, make a copy of the template, naming it `.env`, and filling in your PostgreSQL details.

## Building
### Linux
#### Dependencies
* [Coreutils](https://www.gnu.org/software/coreutils)
* [Make](https://www.gnu.org/software/make)
* [PyQt5](https://www.riverbankcomputing.com/static/Docs/PyQt5)
* [Python 3](https://www.python.org)
* [rsync](https://rsync.samba.org)
* [Tar](https://www.gnu.org/software/tar)

#### Compiling
1. Run `make compile`. Builds will appear in the `bin` directory.

### Windows
#### Dependencies
* [Make](https://www.gnu.org/software/make)
* [PyQt5](https://www.riverbankcomputing.com/static/Docs/PyQt5)
* [Python 3](https://www.python.org)

#### Compiling
1. Run `make.exe compile`. Builds will appear in the `bin` directory.

## Roadmap
[Jira - Capstone 1 Project](https://cs4090group30.atlassian.net/jira/software/projects/KAN/boards/1)

## Authors and acknowledgment
* Ryan Brazill
* Sarah Stamper
* Simon Edmunds
