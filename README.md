# <center>ThePlaylist (***backend***)</center>

> ## <h2 style="color:green">**Description**</h2>

***ThePLaylist*** is a social network that allows to its users to create, store and share his owns playlists with other users. The tracks on this playlists can be uploaded from the user's device and downloaded by any user.

> ## <h2 style="color:green">**Main Features**</h2>

### <h2 style="color:#5595b5">Advanced authentication and authorization</h2>

 - JWT with httpOnly cookies for maximum security against XSS
 - Tokens with configurable expiration and automatic renewal
 - Granular authorization (users only access/modify their own resources)
 - Session validation using an especific endpoint

### <h2 style="color:#5595b5">Complete Music Content Management</h2>

 - Intelligent upload with validation of real MIME types (not just extensions)
 - Duplicate detection using SHA-256 hash of the content
 - Adaptive streaming (memory vs. streaming based on file size)
 - Comprehensive metadata: likes, plays, dislikes, loves with individual tracking

### <h2 style="color:#5595b5">Resilient Architecture</h2>

 - Circuit breaker pattern for operations with external services
 - Configurable timeouts per operation
 - Transactional error handling with automatic rollback
 - Generic repository pattern for consistent CRUD operations

### <h2 style="color:#5595b5">Optimized Data Management</h2>

 - Asynchronous database with SQLAlchemy 2.0+ and asyncpg
 - Context-configurable lazy/eager loading relationships
 - Efficient pagination with environment-configurable limits
 - Pydantic models with compile-time validation

### <h2 style="color:#5595b5">Automated tests with pytest</h2>

 - Unit and integration tests
 - Logging to file for tests failed


> ## <h2 style="color:green">**Technical Architecture**</h2>

### Project Structure

```text
    app/
    |-- api/
    |       |-- __init__.py
    |       |-- v1/
    |           |-- __init__.py
    |           |-- user.py
    |           |-- track.py
    |           |-- playlist.py
    |-- database/
    |           |-- __init__.py
    |           |-- session.py
    |-- migrations/
    |-- models/
    |           |-- __init__.py
    |           |-- playlist.py
    |           |-- track.py
    |           |-- user.py
    |-- repositories/
    |           |-- __init__.py
    |           |-- playlist.py
    |           |-- repository.py
    |           |-- track.py
    |           |-- user.py
    |-- schemas/
    |           |-- __init__.py
    |           |-- access_token.py
    |           |-- playlist.py
    |           |-- track_upload.py
    |           |-- track.py
    |           |-- user.py
    |-- services/
    |           |-- external/
    |                       |-- __init__.py
    |                       |-- circuit_breaker.py
    |                       |-- upload_download.py
    |           |-- __init__.py
    |           |-- auth.py
    |           |-- playlist.py
    |           |-- service.py
    |           |-- track.py
    |           |-- user.py
    |-- settings/
    |           |-- __init__.py
    |           |-- settings.py
    |-- tests/
    |           |-- integration
    |           |-- tests_assets
    |           |-- unit/
    |                   |-- repositories/
    |                   |-- services/
    |-- tools/
    |           |-- __init__.py
    |-- .env
    |-- alembic.ini
    |-- main.py
```

> ## <h2 style="color:green">**Implemented Design Patterns**</h2>

 - `1`: ***Repository Pattern*** - Data Access Abstraction
 - `2`: ***Dependency Injection*** - Native FastAPI Injection
 - `3`: ***Circuit Breaker*** - Resilience Against External Failures
 - `4`: ***Service Layer*** - Clear Separation of Responsibilities
 - `5`: ***Singleton*** - Single Global Configuration

> ## <h2 style="color:green">**Key Design Decisions**</h2>

 - **<h3 style="color:blue">Cookies vs. Headers for JWT</h3>**
    > <p style="color:#6060a0">Decision:</p>
        
        Use httpOnly cookies with secure and SameSite flags
    
    > <p style="color:#6060a0">Justification:</p>

        Greater protection against XSS, CORS compatibility, automatic renewal in browsers
 - **<h3 style="color:blue">Content Hash Validation</h3>**
    > <p style="color:#6060a0">Decision:</p>

        SHA-256 of binary content vs. name/metadata
    
    > <p style="color:#6060a0">Justification:</p>
    
        Prevents true duplicates, optimizes storage, independent of the name

 - **<h3 style="color:blue">Circuit Breaker for Backblaze B2</h3>**
    > <p style="color:#6060a0">Decision:</p>

        Implement a resilience pattern for cloud operations
    
    > <p style="color:#6060a0">Justification:</p>

        Prevents cascading failures, provides elegant fallback, health metrics

 - **<h3 style="color:blue">Strict Layer Separation</h3>**
    > <p style="color:#6060a0">Decision:</p>

        Routers → Services → Repositories → Models
    
    > <p style="color:#6060a0">Justification:</p>

        Testability, maintainability, clear separation of responsibilities

> ## <h2 style="color:green">**Project configuration**</h2>

 - `1`: Create a file named <b style="color:#5595a5">.env</b> with the content **(** an account on **BackBlazeb2** is required, and you must have postgresql already installed **)**:

```ini
# Settings for the app
DB_ENGINE=postgresql
DB_USER=your_username
DB_HOST=your_host
DB_PASSWORD=your_password
DB_PORT=your_port
DB_NAME=your_database
API_GLOBAL_PREFIX=/api/v1
VERSION=1.0.0
SECRET_KEY=MySecretKey
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRES_MINUTES=5 # your decision
ALEMBIC_CONFIG_FILE=alembic.ini
SQLALCHEMY_POOL_SIZE=85 # your decision
SQLALCHEMY_MAX_OVERFLOW=10 # your decision
SQLALCHEMY_POOL_TIMEOUT=60 # your decision
MAX_TRACK_SIZE=100 # in megabytes, your decision
STREAMING_THRESHOLD=10 # in megabytes, your decision
MAX_LIMIT_ALLOWED=100 # your decision
MIN_USERNAME_LENGTH=8 # your decision
MAX_USERNAME_LENGTH=50 # your decision
MIN_USER_PASSWORD_LENGTH=8 # your decision
MAX_USER_PASSWORD_LENGTH=50 # your decision
MIN_PLAYLIST_NAME_LENGTH=4 # your decision
MAX_PLAYLIST_NAME_LENGTH=50 # your decision
MAX_PLAYLIST_DESCRIPTION_LENGTH=100 # your decision
PRODUCTION=false # depends on the environment
ALLOWED_ORIGINS=["http://your_allowed_host:your_allowed_port"]
ALLOWED_CREDENTIALS=true
ALLOWED_METHODS=["*"] # must be changed in production
ALLOWED_HEADERS=["*"] # must be changed in production
SAME_SITE_HEADER=lax # your decision
DOMAIN=your_host
BACKBLAZEB2_BUCKET_NAME=your_bucket_name
BACKBLAZEB2_AWS_ACCESS_KEY_ID=your_key_id
BACKBLAZEB2_AWS_SECRET_ACCESS_KEY=your_own_secret_key
BACKBLAZEB2_BUCKET_ID=your_bucket_id
BACKBLAZEB2_URL_LIFETIME=600 # your decision
CHUNK_SIZE=1 # in megabytes,# your decision
JSON_CONFIG_FILE=rate_limiter_rules.json
ALLOWED_TRACKS_MIME_TYPES=["audio/mpeg","audio/wav","audio/flac","audio/ogg","audio/x-m4a"]
UPLOAD_TIMEOUT=600 # your decision
URL_DOWNLOAD_TIMEOUT=120 # your decision
RENAME_TIMEOUT=120 # your decision
DELETE_TRACK_TIMEOUT=120 # your decision
```

 - `2`: Create a file named <b style="color:#5595a5">alembic.ini</b> with this content:

```ini
# A generic, single database configuration.

[alembic]
# path to migration scripts.
# this is typically a path given in POSIX (e.g. forward slashes)
# format, relative to the token %(here)s which refers to the location of this
# ini file
script_location = %(here)s/migrations

# template used to generate migration file names; The default value is %%(rev)s_%%(slug)s
# Uncomment the line below if you want the files to be prepended with date and time
# see https://alembic.sqlalchemy.org/en/latest/tutorial.html#editing-the-ini-file
# for all available tokens
# file_template = %%(year)d_%%(month).2d_%%(day).2d_%%(hour).2d%%(minute).2d-%%(rev)s_%%(slug)s

# sys.path path, will be prepended to sys.path if present.
# defaults to the current working directory.  for multiple paths, the path separator
# is defined by "path_separator" below.
prepend_sys_path = .

# timezone to use when rendering the date within the migration file
# as well as the filename.
# If specified, requires the tzdata library which can be installed by adding
# `alembic[tz]` to the pip requirements.
# string value is passed to ZoneInfo()
# leave blank for localtime
# timezone =

# max length of characters to apply to the "slug" field
# truncate_slug_length = 40

# set to 'true' to run the environment during
# the 'revision' command, regardless of autogenerate
# revision_environment = false

# set to 'true' to allow .pyc and .pyo files without
# a source .py file to be detected as revisions in the
# versions/ directory
# sourceless = false

# version location specification; This defaults
# to <script_location>/versions.  When using multiple version
# directories, initial revisions must be specified with --version-path.
# The path separator used here should be the separator specified by "path_separator"
# below.
# version_locations = %(here)s/bar:%(here)s/bat:%(here)s/alembic/versions

# path_separator; This indicates what character is used to split lists of file
# paths, including version_locations and prepend_sys_path within configparser
# files such as alembic.ini.
# The default rendered in new alembic.ini files is "os", which uses os.pathsep
# to provide os-dependent path splitting.
#
# Note that in order to support legacy alembic.ini files, this default does NOT
# take place if path_separator is not present in alembic.ini.  If this
# option is omitted entirely, fallback logic is as follows:
#
# 1. Parsing of the version_locations option falls back to using the legacy
#    "version_path_separator" key, which if absent then falls back to the legacy
#    behavior of splitting on spaces and/or commas.
# 2. Parsing of the prepend_sys_path option falls back to the legacy
#    behavior of splitting on spaces, commas, or colons.
#
# Valid values for path_separator are:
#
# path_separator = :
# path_separator = ;
# path_separator = space
# path_separator = newline
#
# Use os.pathsep. Default configuration used for new projects.
path_separator = os


# set to 'true' to search source files recursively
# in each "version_locations" directory
# new in Alembic version 1.10
# recursive_version_locations = false

# the output encoding used when revision files
# are written from script.py.mako
# output_encoding = utf-8

# database URL.  This is consumed by the user-maintained env.py script only.
# other means of configuring database URLs may be customized within the env.py
# file.
sqlalchemy.url = postgresql+asyncpg://postgres:your_password@your_host:your_port/your_database


[post_write_hooks]
# post_write_hooks defines scripts or Python functions that are run
# on newly generated revision scripts.  See the documentation for further
# detail and examples

# format using "black" - use the console_scripts runner, against the "black" entrypoint
# hooks = black
# black.type = console_scripts
# black.entrypoint = black
# black.options = -l 79 REVISION_SCRIPT_FILENAME

# lint with attempts to fix using "ruff" - use the module runner, against the "ruff" module
# hooks = ruff
# ruff.type = module
# ruff.module = ruff
# ruff.options = check --fix REVISION_SCRIPT_FILENAME

# Alternatively, use the exec runner to execute a binary found on your PATH
# hooks = ruff
# ruff.type = exec
# ruff.executable = ruff
# ruff.options = check --fix REVISION_SCRIPT_FILENAME

# Logging configuration.  This is also consumed by the user-maintained
# env.py script only.
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARNING
handlers = console
qualname =

[logger_sqlalchemy]
level = WARNING
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

> ## <h2 style="color:green">**Running the API**</h2>

 - `1`: Run this command

```bash
pip install -r requirements.txt
```
 
 - `2`: Run this commands:

```bash
alembic revision --autogenerate -m "first migration"
```

```bash
alembic upgrade head
```

 - `3`: Run the command

```bash
fastapi run # fastapi dev
```