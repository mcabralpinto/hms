import os

import psycopg2
from dotenv import load_dotenv
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, FastAPI, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import binascii
import base64

load_dotenv()
app = FastAPI()
db = psycopg2.connect(
    host=os.getenv("POSTGRES_HOST"),
    database=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
)
cursor = db.cursor()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 60

context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer = OAuth2PasswordBearer(tokenUrl="token")


# +-------------------+
# | Class definitions |
# +-------------------+


class Person(BaseModel):
    name: str
    cc: int
    email: str
    contact: int
    nif: int
    hashed_password: str

    @staticmethod
    def get(cc: int) -> "Person":
        cursor.execute("SELECT * FROM person WHERE cc = %s", (cc,))
        result = cursor.fetchone()
        if result is None:
            return None
        return Person(**dict(zip(Person.model_fields.keys(), result)))

    @staticmethod
    def get_by_email(email: str) -> "Person":
        cursor.execute("SELECT * FROM person WHERE email = %s", (email,))
        result = cursor.fetchone()
        if result is None:
            return None
        return Person(**dict(zip(Person.model_fields.keys(), result)))

    def insert(self) -> None:
        self.hashed_password = get_password_hash(self.hashed_password)
        cursor.execute(
            "INSERT INTO person (name, cc, email, contact, nif, hashed_password) VALUES (%s, %s, %s, %s, %s, %s)",
            (
                self.name,
                self.cc,
                self.email,
                self.contact,
                self.nif,
                self.hashed_password,
            ),
        )
        db.commit()

    # attrgetter(*gajo.__fields__.keys())(gajo), gajo as Person


class Patient(Person):
    health_user_id: int


class Employee(Person):
    id_contrato: int


class Doctor(Employee):
    id_lic: int
    instituto: str

    @staticmethod
    def get(cc: int) -> "Doctor":
        cursor.execute(
            "SELECT person.*, employees.id_contrato, doctors.id_lic, doctors.instituto FROM person JOIN doctors ON doctors.employees_person_cc = person.cc JOIN employees ON employees.person_cc = person.cc WHERE employees.person_cc = %s",
            (cc,),
        )
        result = cursor.fetchone()
        if result is None:
            return None
        return Doctor(**dict(zip(Doctor.model_fields.keys(), result)))


class Nurse(Employee):
    hierarchy_level: int

    @staticmethod
    def get(cc: int) -> "Nurse":
        cursor.execute(
            "SELECT person.*, employees.id_contrato, nurses.hierarchy_level FROM person JOIN nurses ON nurses.employees_person_cc = person.cc JOIN employees ON employees.person_cc = person.cc WHERE employees.person_cc = %s",
            (cc,),
        )
        result = cursor.fetchone()
        if result is None:
            return None
        return Nurse(**dict(zip(Nurse.model_fields.keys(), result)))


class Assistant(Employee):

    @staticmethod
    def get(cc: int) -> "Assistant":
        cursor.execute(
            "SELECT person.*, employees.id_contrato FROM person JOIN assistants ON assistants.employees_person_cc = person.cc JOIN employees ON employees.person_cc = person.cc WHERE employees.person_cc = %s",
            (cc,),
        )
        result = cursor.fetchone()
        if result is None:
            return None
        return Assistant(**dict(zip(Assistant.model_fields.keys(), result)))


class Hierarchy(BaseModel):
    level: int
    nome: str
    hierarchy_level: int


class Appointment(BaseModel):
    id_app: int
    date: datetime
    billings_id_bill: int
    doctors_employees_person_cc: int
    patients_person_cc: int


class Hospitalization(BaseModel):
    id_hos: int
    date_begin: datetime
    date_end: datetime
    room: int
    nurses_employees_person_cc: int
    billings_id_bill: int
    patients_person_cc: int


class Surgery(BaseModel):
    id_sur: int
    name: str
    date: datetime
    doctors_employees_person_cc: int
    hospitalizations_id_hos: int


class Role(BaseModel):
    role_num: int
    role_name: str


class DoesSurgery(BaseModel):
    roles_role_num: int
    surgeries_id_sur: int
    nurses_employees_person_cc: int


class Prescription(BaseModel):
    id_pres: int


class IsComprisedApp(BaseModel):
    amount: int
    medication_id_med: int
    prescriptions_id_pres: int


class Medication(BaseModel):
    id_med: int
    name: str


class SideEffect(BaseModel):
    id_side: int
    description: str


class Corresponds(BaseModel):
    probability: float
    severity: float
    side_effects_id_side: int
    medication_id_med: int


class Billing(BaseModel):
    id_bill: int
    total: float
    payed: float
    nif: int


class Specialization(BaseModel):
    name: str
    id_specialization: int
    specialization_id_specialization: int


class DoctorSpecialization(BaseModel):
    doctors_employees_person_cc: int
    specialization_id_specialization: int


class PrescriptionHospitalization(BaseModel):
    prescriptions_id_pres: int
    hospitalizations_id_hos: int


class AppointmentPrescription(BaseModel):
    appointments_id_app: int
    prescriptions_id_pres: int


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    cc: Optional[int] = None
    role: Optional[str] = None


# +----------------+
# | JWT Operations |
# +----------------+


def verify_password(plain_password: str, hashed_password: str):
    return context.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    return context.hash(password)


# def safe_base64_decode(s):
#     # Add padding if necessary
#     while len(s) % 4 != 0:
#         s += '='
#     return base64.urlsafe_b64decode(s)


def authenticate(email: str, password: str) -> Optional[Person]:
    user = Person.get_by_email(email)
    if not user:
        return
    if not verify_password(password, user.hashed_password):
        return
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
        
    try:
        payload = jwt.decode(token[7:], SECRET_KEY, algorithms=[ALGORITHM])
        cc: int = payload.get("cc")
        role: str = payload.get("role")
        if cc is None or role is None:
            raise credentials_exception
        token_data = TokenData(cc=cc, role=role)
    except JWTError:
        raise credentials_exception
    user = Person.get(cc=token_data.cc)
    if user is None:
        raise credentials_exception
    return user, role


async def get_current_employee(user_role=Depends(get_current_user)):
    user, role = user_role
    if role == "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    return user_role


@app.post("/token", response_model=Token)
async def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if Nurse.get(cc=user.cc) is not None:
        role = "nurse"
    elif Assistant.get(cc=user.cc) is not None:
        role = "assistant"
    elif Doctor.get(cc=user.cc) is not None:
        role = "doctor"
    else:
        role = "patient"
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"cc": user.cc, "role": role}, expires_delta=access_token_expires
    )
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return {"access_token": access_token, "token_type": "bearer"}


# +-------------------+
# | Endpoint handlers |
# +-------------------+


@app.get("/person/{id}")
async def get_person(
    id: int, current_user: Person = Depends(get_current_employee)
) -> Person:
    return Person.get(id)


@app.put("/person")
async def insert_person(
    person: Person, current_user: Person = Depends(get_current_employee)
) -> None:
    person.insert()

@app.get("/dbproj/top3")
async def get_top3_patients(current_user: Person = Depends(get_current_employee)):
    user, role = current_user
    if role != "assistant":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    cursor.execute("SELECT * FROM get_top3_patients()")
    result = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    result = [dict(zip(column_names, row)) for row in result]
    return result

@app.get("/dbproj/report")
async def get_monthly_report(current_user: Person = Depends(get_current_employee)):
    user, role = current_user
    if role != "assistant":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    query = """
    SELECT month, name, total_surgeries
    FROM    
    (
        SELECT 
        TO_CHAR(date_trunc('month', surgeries.data), 'YYYY-MM') AS month, 
        person.name, 
        COUNT(*) AS total_surgeries,
        RANK() OVER (PARTITION BY TO_CHAR(date_trunc('month', surgeries.data), 'YYYY-MM') ORDER BY COUNT(*) DESC) as rank

        FROM surgeries
        JOIN person ON person.cc = surgeries.doctors_employees_person_cc
        WHERE surgeries.data >= (NOW() - INTERVAL '1 year')
        GROUP BY TO_CHAR(date_trunc('month', surgeries.data), 'YYYY-MM'), person.name

    )AS sub

    WHERE rank = 1 ORDER BY month DESC;
    """
    cursor.execute(query)
    result = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    result = [dict(zip(column_names, row)) for row in result]
    return {"status": 200, "results": result}