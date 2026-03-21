# Setting FastAPI Environment

## Step1:
Create your project folder manually or used cmd

```
mkdir my_fastapi_project
```

## Step2:
Open CMD/Terminal inside the folder or cd into the folder

```
cd my_fastapi_project
```

## Step3:
Create virtual environment

```
python -m venv .venv 
```

## Step4: 

Activate enviroment

### For windows

```
.venv\Scripts\activate
```

### macOS/Linux:

```
source .venv/bin/activate
```

## Step5: 

Install FastAPI and Uvicorn

```
pip install fastapi uvicorn
```

## Step6:

Create folders in this structure

```
my_fastapi_project/
│
├── app/
│   ├── __init__.py
│   └── routes/
│   |   └── __init__.py
|   ├── models/
│   |   └── __init__.py
|   ├── schema/
│       └── __init__.py
├── main.py
├── requirements.txt
└── README.md
```


Add folders and structures accordingly as you move

## Step7: 

 Stage 1: Core Fundamentals

Aim: To help them confidently build simple, clean APIs.
Topic	What to Cover

```
✅ Path & Query Parameters	/items/{id}, ?limit=10
✅ Request Body	POST/PUT with Pydantic models
✅ Response Models	Returning structured JSON using response_model=
✅ Status Codes	Using status_code=201, handling 404s
✅ Tags and Metadata	For Swagger docs, grouping endpoints
✅ Error Handling	HTTPException, custom exceptions
✅ Dependency Injection	Depends(), common logic (e.g., auth checks)
```

# Creating Database and Models

With your Virtual enviroment activated run

```
pip install sqlalchemy psycopg2-binary alembic

```
Add installed models to `requirements.txt`

```
pip freeze > requirements.txt
```

##  Configure SQLAlchemy and Database Connection
Create file ```database.py``` inside app/ folder

paste the following

```
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql://username:password@localhost:5432/your_db_name"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
```

## Create Your First Database Model
inside `app/models/user.py` create `user.py` if not existing and paste the following inside

```
from sqlalchemy import Column, Integer, String
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
```

Then import the created model in `app/models/__init__.py` like this:

```
from app.models.users import User

```

## Initialize Alembic

In the virtual enviroment, run alembic initialization in the terminal:

```
alembic init alembic

```

This creates an `alembic/` folder and `alembic.ini` in your root folder.

## Configure Alembic
Open `alembic.ini`

Find this line:

`sqlalchemy.url = driver://user:pass@localhost/dbname`

Replace it with your actual DB URL:

`sqlalchemy.url = postgresql://username:password@localhost:5432/your_db_name`
we will create an autual database later on


Then open `alembic/env.py` dont modify anything just paste the following at the top before `config = context.config` to import your Base:

```
from app.database import Base
from app import models

target_metadata = Base.metadata
```

## Set up Postgres Database on your pc


### 1. **Download PostgreSQL**

* Go to the official PostgreSQL download page:
  [https://www.postgresql.org/download/windows/](https://www.postgresql.org/download/windows/)

* Click **"Download the installer"** → you'll be redirected to EDB's website.

* Click the latest version (e.g., **PostgreSQL 16.x**) → Download the **Windows x86-64** version.

---

### Run the Installer

After downloading:

1. **Double-click** the installer file (`postgresql-16.x-windows-x64.exe`)
2. Follow the prompts:

   * **Installation Directory** → Keep default
   * **Components** → Make sure these are selected:

     * ✅ PostgreSQL Server
     * ✅ pgAdmin 4
     * ✅ Command Line Tools

---

### 3. **Set a Superuser Password**

You’ll be asked to set a password for the default PostgreSQL **superuser (`postgres`)**.

> ⚠️ **IMPORTANT**: Save this password somewhere — you’ll need it to access your database.

---

### 4. **Set Port Number**

* Use the default: `5432`
* Leave locale as default
* Click **Next** until installation starts.

---

### 5. **Wait for Installation to Complete**

Click **"Finish"** when it’s done.

You now have:

* PostgreSQL server
* pgAdmin GUI
* psql command line tool

---

## Step-by-Step: Set Up pgAdmin

---

### 6. **Open pgAdmin**

* Go to:
  **Start Menu → PostgreSQL → pgAdmin 4**

* It will launch in your browser (or system tray > right-click pgAdmin icon > "New pgAdmin Window")

---

### 7. **Create a Master Password**

This is **not** your PostgreSQL password. It’s for **pgAdmin only**, to unlock saved connections more like app password.

> Example: `admin123` (You can set anything, just remember it)

---

### 8. **Connect to the Local Server**

1. In pgAdmin left sidebar: Right-click on **“Servers” → Create → Server**
2. Fill in details:

#### 🔹 General Tab:

* **Name:** Local PostgreSQL (or any name)

#### 🔹 Connection Tab:

* **Host name/address:** `localhost`
* **Port:** `5432`
* **Username:** `postgres`
* **Password:** the one you set during installation

3. Click **Save**

You’ll now be connected to your PostgreSQL server 🎉

---

## Step-by-Step: Create a New Database

---

### 9. **Create a New Database**

1. Expand **Servers > Databases**
2. Right-click **Databases → Create → Database**
3. Fill in:

   * **Database name:** `mydb` (or any name, no spaces in between)
   * Leave owner as `postgres`
4. Click **Save**

🎉 You’ve now created your own database — ready for your FastAPI app.

---


## Create and Apply Migration

Go back to yur alembic env.py find this line

`sqlalchemy.url = postgresql://username:password@localhost:5432/your_db_name`

replace:
* username with the one you created earlier `postgres`
* password with the one you created (not the one for pgadmin)
* your_db_name with the database name you created `mydb`

## Create initial migration:

```
alembic revision --autogenerate -m "create users table"
```

You’ll see output about the detected changes.

## Apply the migration:

```
alembic upgrade head
```

Your users table should now be created in the DB 🎉

if any of the migration fails, revisit your database connection authentication details