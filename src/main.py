import os

import psycopg2
from dotenv import load_dotenv
from pydantic import BaseModel
from datetime import date, datetime, timedelta, timezone
from typing import Dict, List, Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import (
    Body,
    Depends,
    FastAPI,
    HTTPException,
    Path,
    status,
    Response,
    Request,
    APIRouter,
)
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from psycopg2 import sql

load_dotenv()
app = FastAPI()
router = APIRouter(prefix="/dbproj")
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

STATUS_CODES = {"success": 200, "api_error": 400, "internal_error": 500}

# +-------------------+
# | Class definitions |
# +-------------------+


class Person(BaseModel):
    name: str
    cc: int
    email: str
    contact: int
    nif: int
    password: str

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

    def register(self) -> None:
        self.password = get_password_hash(self.password)
        cursor.execute(
            "INSERT INTO person (name, cc, email, contact, nif, hashed_password) VALUES (%s, %s, %s, %s, %s, %s)",
            (
                self.name,
                self.cc,
                self.email,
                self.contact,
                self.nif,
                self.password,
            ),
        )
        db.commit()

    # attrgetter(*gajo.__fields__.keys())(gajo), gajo as Person


class Patient(Person):
    health_user_id: int

    @staticmethod
    def get_top3() -> list[dict]:
        cursor.execute("SELECT * FROM get_top3_patients()")
        result = cursor.fetchall()
        if result is None:
            return None
        column_names = [column[0] for column in cursor.description]
        return [dict(zip(column_names, row)) for row in result]
        # return [Patient(**dict(zip(Patient.model_fields.keys(), row))) for row in result]


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

    @staticmethod
    def get_monthly_report() -> list[dict]:
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
        return {"status": STATUS_CODES["success"], "results": result}


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


def authenticate(email: str, password: str) -> Optional[Person]:
    user = Person.get_by_email(email)
    if not user:
        return
    if not verify_password(password, user.password):
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


async def get_current_patient(user_role=Depends(get_current_user)):
    user, role = user_role
    if role != "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    return user_role


async def get_current_assistant(user_role=Depends(get_current_user)):
    user, role = user_role
    if role != "assistant":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    return user_role


# +-------------------+
# | Endpoint handlers |
# +-------------------+


# test endpoint
@router.get("/person/{id}")
async def get_person(id: int) -> Person:
    return Person.get(id)


# change to return it exactly as in the project statement
@router.put("/user", response_model=Token)
async def login_for_access_token(
    response: Response, form_data: OAuth2PasswordRequestForm = Depends()
):
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
    response.set_cookie(
        key="access_token", value=f"Bearer {access_token}", httponly=True
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register/{role}")
async def register_person(
    role: str,
    person: Person = Body(...),
    institute: Optional[str] = Body(None),
    specialization: Optional[str] = Body(None),
    master_specialization: Optional[str] = Body(None),
    hierarchy: Optional[str] = Body(None),
    hierarchy_above: Optional[str] = Body(None),
    current_user: Person = Depends(get_current_assistant)
) -> None:
    try:
        hashed_pass = get_password_hash(person.password)
        if role == "patient":
            query = (
                "call addPatient('%s'::varchar, %d, '%s'::varchar, %d, %d, '%s'::varchar);"
                % (
                    person.name,
                    person.cc,
                    person.email,
                    person.contact,
                    person.nif,
                    hashed_pass,
                )
            )
        elif role == "doctor":
            if specialization is None:
                response = {
                    "status": STATUS_CODES["api_error"],
                    "errors": "Request has missing parameter",
                }
                return response
            if master_specialization is None:
                query = (
                    f"call addDoctor('%s', %d, '%s', %d, %d, '%s'::varchar, '%s', '%s');"
                    % (
                        person.name,
                        person.cc,
                        person.email,
                        person.contact,
                        person.nif,
                        hashed_pass,
                        institute,
                        specialization,
                    )
                )
            else:
                query = (
                    f"call addDoctor('%s', %d, '%s', %d, %d, '%s'::varchar, '%s', '%s', '%s');"
                    % (
                        person.name,
                        person.cc,
                        person.email,
                        person.contact,
                        person.nif,
                        hashed_pass,
                        institute,
                        specialization,
                        master_specialization,
                    )
                )
        elif role == "assistant":
            query = (
                f"call addAssistant('%s'::varchar, %d, '%s'::varchar, %d, %d, '%s'::varchar);"
                % (
                    person.name,
                    person.cc,
                    person.email,
                    person.contact,
                    person.nif,
                    hashed_pass,
                )
            )
        elif role == "nurse":
            if hierarchy is None:
                response = {
                    "status": STATUS_CODES["api_error"],
                    "errors": "Request has missing parameter",
                }
                return response
            if hierarchy_above is None:
                query = (
                    f"call addNurse('%s'::varchar, %d, '%s'::varchar, %d, %d, '%s'::varchar, '%s');"
                    % (
                        person.name,
                        person.cc,
                        person.email,
                        person.contact,
                        person.nif,
                        hashed_pass,
                        hierarchy,
                    )
                )
            else:
                query = (
                    f"call addNurse('%s'::varchar, %d, '%s'::varchar, %d, %d, '%s'::varchar, '%s', '%s');"
                    % (
                        person.name,
                        person.cc,
                        person.email,
                        person.contact,
                        person.nif,
                        hashed_pass,
                        hierarchy,
                        hierarchy_above,
                    )
                )
        cursor.execute(query)
        db.commit()
        response = {
            "status": STATUS_CODES["success"],
            "results": f"User_id:{person.cc}",
        }
    except psycopg2.DatabaseError as e:
        response = {"status": STATUS_CODES["internal_error"], "errors": str(e)}
        db.rollback()
    except Exception as e:
        response = {"status": STATUS_CODES["api_error"], "errors": str(e)}
    return response


@app.get("/dbproj/see/{role}")
async def see_table(role: str, current_user: Person = Depends(get_current_assistant)):
    try:
        query = "Select * from %s;" % (role)
        cursor.execute(query)
        result = cursor.fetchall()
        db.commit()
        column_names = [column[0] for column in cursor.description]
        result = [dict(zip(column_names, row)) for row in result]
        response = {"status": STATUS_CODES["success"], "results": result}
    except (Exception, psycopg2.DatabaseError) as e:
        response = {"status": STATUS_CODES["internal_error"], "errors": str(e)}
        db.rollback()
    return response


@app.get("/dbproj/appointments/{user_id}")
async def see_appointments(
    user_id: int, current_user: Person = Depends(get_current_assistant)
):
    user, role = current_user
    if user.cc == user_id:
        try:
            query = """ 
                    select id_app as id, doctors_employees_person_cc as doctor_id, data as date, billings_id_bill as bill_id
                    from appointments left join person on appointments.patients_person_cc = person.cc
                    where person.cc = '%d';
                    """ % (
                user_id
            )
            cursor.execute(query)
            result = cursor.fetchall()
            db.commit()
            column_names = [column[0] for column in cursor.description]
            result = [dict(zip(column_names, row)) for row in result]
            response = {"status": STATUS_CODES["success"], "results": result}
        except (Exception, psycopg2.DatabaseError) as e:
            response = {"status": STATUS_CODES["internal_error"], "errors": str(e)}
            db.rollback()
    else:
        response = {
            "status": STATUS_CODES["api_error"],
            "errors": "Not enough permissions",
        }
    return response


@router.get("/top3")
async def get_top3_patients(current_user: Person = Depends(get_current_assistant)):
    return Patient.get_top3()


@router.get("/report")
async def get_monthly_report(current_user: Person = Depends(get_current_assistant)):
    return Surgery.get_monthly_report()


@router.get("/daily/{date}")
async def get_daily_summary(
    date: date = Path(..., format="%Y-%m-%d"),
    current_user: Person = Depends(get_current_assistant),
):
    response = {"status": STATUS_CODES["success"], "errors": None, "results": None}

    # Call the SQL function
    try:
        with db.cursor() as cur:
            cur.execute("SELECT * FROM get_daily_summary(%s)", (date,))
            result = cur.fetchone()
    except Exception as e:
        response["status"] = STATUS_CODES["internal_error"]
        response["errors"] = str(e)
        raise HTTPException(status_code=STATUS_CODES["internal_error"], detail=str(e))

    # Check if the function returned an error
    if result is None:
        response["status"] = STATUS_CODES["internal_error"]
        response["errors"] = "Error executing SQL function"
        raise HTTPException(
            status_code=STATUS_CODES["internal_error"],
            detail="Error executing SQL function",
        )

    result_dict = {
        "surgeries": result[0],
        "prescriptions": result[1],
        "amount": result[2],
    }
    response["results"] = result_dict
    return response


@router.post("/surgery")
async def post_surgery(
    patient_id: int = Body(...),
    doctor: int = Body(...),
    nurses: List[List[Union[int, str]]] = Body(...),
    date: str = Body(...),
    surgery_name: str = Body(...),
    hospitalization_date_begin: str = Body(...),
    hospitalization_date_end: str = Body(...),
    hospitalization_room: int = Body(...),
    hospitalization_nurse_id: int = Body(...),
    current_user: Person = Depends(get_current_assistant),
):
    response = {"status": STATUS_CODES["success"], "errors": None, "results": None}

    # Convert nurses to a string that represents an array of composite types in PostgreSQL
    nurses_str = ", ".join(
        f"ROW({nurse[0]}, '{nurse[1]}')::nurse_role" for nurse in nurses
    )
    # Convert date to a format suitable for the SQL function
    date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")

    # Convert hospitalization dates to a format suitable for the SQL function
    hospitalization_date_begin = datetime.strptime(
        hospitalization_date_begin, "%Y-%m-%d"
    ).date()
    hospitalization_date_end = datetime.strptime(
        hospitalization_date_end, "%Y-%m-%d"
    ).date()

    # Call the SQL function
    try:
        with db.cursor() as cur:
            query = sql.SQL(
                f"SELECT * FROM schedule_surgery(%s, %s, ARRAY[{nurses_str}]::nurse_role[], %s, %s, %s, %s, %s, %s)"
            )
            cur.execute(
                query,
                (
                    patient_id,
                    doctor,
                    date,
                    surgery_name,
                    hospitalization_date_begin,
                    hospitalization_date_end,
                    hospitalization_room,
                    hospitalization_nurse_id,
                ),
            )
            result = cur.fetchone()
            db.commit()
    except Exception as e:
        db.rollback()
        response["status"] = STATUS_CODES["internal_error"]
        response["errors"] = str(e)
        raise HTTPException(status_code=STATUS_CODES["internal_error"], detail=str(e))

    # Check if the function returned an error
    if result is None:
        response["status"] = STATUS_CODES["internal_error"]
        response["errors"] = "Error executing SQL function"
        raise HTTPException(
            status_code=STATUS_CODES["internal_error"],
            detail="Error executing SQL function",
        )

    result_dict = {
        "hospitalization_id": result[2],
        "surgery_id": result[3],
        "patient_id": result[4],
        "doctor_id": result[5],
        "date": (
            result[6].strftime("%Y-%m-%d %H:%M:%S") if result[6] is not None else None
        ),
    }
    response["status"] = STATUS_CODES["success"]
    response["errors"] = result[1]
    response["results"] = result_dict
    # Return the result
    return response


@router.post("/surgery/{hospitalization_id}")
async def post_surgery(
    hospitalization_id: int = Path(...),
    patient_id: int = Body(...),
    doctor: int = Body(...),
    nurses: List[List[Union[int, str]]] = Body(...),
    date: str = Body(...),
    surgery_name: str = Body(...),
    current_user: Person = Depends(get_current_assistant),
):
    response = {"status": STATUS_CODES["success"], "errors": None, "results": None}

    # Convert nurses to a string that represents an array of composite types in PostgreSQL
    nurses_str = ", ".join(
        f"ROW({nurse[0]}, '{nurse[1]}')::nurse_role" for nurse in nurses
    )

    # Convert date to a format suitable for the SQL function
    date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")

    # Call the SQL function
    try:
        with db.cursor() as cur:
            query = sql.SQL(
                f"SELECT * FROM schedule_surgery(%s, %s, ARRAY[{nurses_str}]::nurse_role[], %s, %s, %s)"
            )
            cur.execute(
                query, (patient_id, doctor, date, hospitalization_id, surgery_name)
            )
            db.commit()
            result = cur.fetchone()
    except Exception as e:
        response["status"] = STATUS_CODES["internal_error"]
        response["errors"] = str(e)
        db.rollback()
        raise HTTPException(status_code=STATUS_CODES["internal_error"], detail=str(e))

    # Check if the function returned an error
    if result is None:
        response["status"] = STATUS_CODES["internal_error"]
        response["errors"] = "Error executing SQL function"
        raise HTTPException(
            status_code=STATUS_CODES["internal_error"],
            detail="Error executing SQL function",
        )

    result_dict = {
        "hospitalization_id": result[2],
        "surgery_id": result[3],
        "patient_id": result[4],
        "doctor_id": result[5],
        "date": (
            result[6].strftime("%Y-%m-%d %H:%M:%S") if result[6] is not None else None
        ),
    }
    response["status"] = STATUS_CODES["success"]
    response["errors"] = result[1]
    response["results"] = result_dict
    return response


@router.post("/bills/{bill_id}")
async def post_bill(
    bill_id: int = Path(...),
    amount: str = Body(..., embed=True),
    current_user: Person = Depends(get_current_patient),
):
    response = {"status": STATUS_CODES["success"], "errors": None, "results": None}
    # Try to convert amount to float
    try:
        amount = float(amount)
    except ValueError:
        response["status"] = STATUS_CODES["api_error"]
        response["errors"] = "Amount must be a number"
        raise HTTPException(
            status_code=STATUS_CODES["api_error"], detail="Amount must be a number"
        )

    # Call the SQL function
    try:
        with db.cursor() as cur:
            statement = "SELECT pay_bill(%s, %s)"
            values = (bill_id, amount)
            cur.execute(statement, values)
            db.commit()
            result = cur.fetchone()
    except Exception as e:
        response["status"] = STATUS_CODES["internal_error"]
        response["errors"] = str(e)
        db.rollback()
        raise HTTPException(status_code=STATUS_CODES["internal_error"], detail=str(e))

    # Check if the function returned an error
    if result is None:
        response["status"] = STATUS_CODES["internal_error"]
        response["errors"] = "Error executing SQL function"
        raise HTTPException(
            status_code=STATUS_CODES["internal_error"],
            detail="Error executing SQL function",
        )

    result_dict = {
        "Missing amount": result[0],
    }
    response["status"] = STATUS_CODES["success"]
    response["results"] = result_dict
    # Return the result
    return response


@router.post("/appointment")
async def schedule_appointment(
    doctor_id: int = Body(...),
    date: str = Body(...),
    current_user: Person = Depends(get_current_user),
):
    user, role = current_user
    response = {"status": STATUS_CODES["success"], "errors": None, "results": None}

    # Call the SQL function
    try:
        with db.cursor() as cur:
            statement = "SELECT * FROM schedule_appointment(%s, %s, %s)"
            values = (doctor_id, date, user.cc)
            cur.execute(statement, values)
            db.commit()
            result = cur.fetchone()
    except Exception as e:
        response["status"] = STATUS_CODES["internal_error"]
        response["errors"] = str(e)
        db.rollback()
        raise HTTPException(status_code=STATUS_CODES["internal_error"], detail=str(e))

    # Check if the function returned an error
    if result is None:
        response["status"] = STATUS_CODES["internal_error"]
        response["errors"] = "Error executing SQL function"
        raise HTTPException(
            status_code=STATUS_CODES["internal_error"],
            detail="Error executing SQL function",
        )

    result_dict = {
        "appointment_id": result[2],
        "bill_id": result[3],
    }
    response["status"] = STATUS_CODES["success"]
    response["errors"] = result[1]
    response["results"] = result_dict

    # Return the result
    return response


app.include_router(router)
