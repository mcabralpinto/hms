import os

import psycopg2
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

load_dotenv()
app = FastAPI()
db = psycopg2.connect(
    host=os.getenv("POSTGRES_HOST"),
    database=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
)
cursor = db.cursor()


class Person(BaseModel):
    name: str
    age: int

    @staticmethod
    def get(id: int) -> "Person":
        cursor.execute("SELECT * FROM person WHERE id = %s", (id,))
        result = cursor.fetchone()
        return Person(name=result[1], age=result[2])

    def insert(self) -> None:
        cursor.execute(
            "INSERT INTO person (name, age) VALUES (%s, %s)",
            (self.name, self.age),
        )
        db.commit()

    # attrgetter(*gajo.__fields__.keys())(gajo), gajo as Person


@app.get("/person/{id}")
def get_person(id: int) -> Person:
    return Person.get(id)


@app.put("/person")
def insert_person(person: Person) -> None:
    person.insert()
