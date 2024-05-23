# HMS - DB Project

## Getting Started

### Prerequisites

- Ensure you have Python installed on your system. You can download it from [python.org](https://www.python.org/downloads/).
- [Git](https://git-scm.com/downloads) should be installed for version control.

### Setting up the development environment

1. **Create a virtual environment**

   Create a Python virtual environment to manage dependencies:

   ```bash
   python -m venv env
   ```

2. **Activate the virtual environment**

   - On **Windows**:

     ```powershell
     .\env\Scripts\activate
     ```

   - On **Linux** or **macOS**:

     ```bash
     source env/bin/activate
     ```

3. **Upgrade pip**

   Ensure you have the latest version of pip:

   ```bash
   python -m pip install --upgrade pip
   ```

4. **Install dependencies**

   Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

5. **Create a .env file**

   Copy the contents of `.env.example` into a new file called `.env`.

   ```bash
   cp .env.example .env
   ```

   Remember to fill in the values in the newly created `.env` file, such as database URL and any other environment-specific variables.

## Running the Database

To run the database using Docker, execute the following command:

```bash
docker-compose up -d
```

## For Linux/UNIX users

1. **If you are having trouble with permissions use sudo**
```bash
sudo docker-compose down 
sudo docker-compose up -d db
sudo docker-compose up api
```

2. **The first time you open the db you may want to use**
```
sudo docker-compose up --build
```
Followed by a CTRL-C and then do the steps above


3. **If you are having trouble installing psycopg2**

```
change psycopg2 to psycopg2-binary in requirements.txt
```
