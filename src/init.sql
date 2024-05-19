CREATE TABLE
	patients (
		health_user_id BIGSERIAL NOT NULL,
		person_cc BIGINT,
		PRIMARY KEY (person_cc)
	);

CREATE TABLE
	employees (
		id_contrato SERIAL NOT NULL,
		person_cc BIGINT,
		PRIMARY KEY (person_cc)
	);

CREATE TABLE
	doctors (
		id_lic SERIAL NOT NULL,
		instituto VARCHAR(512) NOT NULL,
		employees_person_cc BIGINT,
		PRIMARY KEY (employees_person_cc)
	);

CREATE TABLE
	nurses (
		hierarchy_level INTEGER NOT NULL,
		employees_person_cc BIGINT,
		PRIMARY KEY (employees_person_cc)
	);

CREATE TABLE
	assistants (
		employees_person_cc BIGINT,
		PRIMARY KEY (employees_person_cc)
	);

CREATE TABLE
	hierarchy (
		level SERIAL,
		nome VARCHAR(512) NOT NULL,
		hierarchy_level INTEGER NOT NULL,
		PRIMARY KEY (level)
	);

CREATE TABLE
	appointments (
		id_app SERIAL,
		data TIMESTAMP NOT NULL,
		billings_id_bill INTEGER NOT NULL,
		doctors_employees_person_cc BIGINT NOT NULL,
		patients_person_cc BIGINT NOT NULL,
		PRIMARY KEY (id_app)
	);

CREATE TABLE
	hospitalizations (
		id_hos SERIAL,
		date_begin DATE NOT NULL,
		date_end DATE NOT NULL,
		room INTEGER NOT NULL,
		nurses_employees_person_cc BIGINT NOT NULL,
		billings_id_bill INTEGER NOT NULL,
		patients_person_cc BIGINT NOT NULL,
		PRIMARY KEY (id_hos)
	);

CREATE TABLE
	surgeries (
		id_sur SERIAL,
		name VARCHAR(512) NOT NULL,
		data TIMESTAMP NOT NULL,
		doctors_employees_person_cc BIGINT NOT NULL,
		hospitalizations_id_hos INTEGER NOT NULL,
		PRIMARY KEY (id_sur)
	);

CREATE TABLE
	roles (
		role_num SERIAL,
		role_name VARCHAR(512) NOT NULL,
		PRIMARY KEY (role_num)
	);

CREATE TABLE
	does_surgery (
		roles_role_num INTEGER,
		surgeries_id_sur INTEGER,
		nurses_employees_person_cc BIGINT,
		PRIMARY KEY (
			roles_role_num,
			surgeries_id_sur,
			nurses_employees_person_cc
		)
	);

CREATE TABLE
	prescriptions (id_pres SERIAL, PRIMARY KEY (id_pres));

CREATE TABLE
	is_comprised_app (
		amount INTEGER NOT NULL,
		medication_id_med INTEGER,
		prescriptions_id_pres INTEGER,
		PRIMARY KEY (medication_id_med, prescriptions_id_pres)
	);

CREATE TABLE
	medication (
		id_med SERIAL,
		name VARCHAR(512) NOT NULL,
		PRIMARY KEY (id_med)
	);

CREATE TABLE
	side_effects (
		id_side SERIAL,
		description VARCHAR(512) NOT NULL,
		PRIMARY KEY (id_side)
	);

CREATE TABLE
	corresponds (
		probability FLOAT (8) NOT NULL,
		severity FLOAT (8) NOT NULL,
		side_effects_id_side INTEGER,
		medication_id_med INTEGER,
		PRIMARY KEY (side_effects_id_side, medication_id_med)
	);

CREATE TABLE
	billings (
		id_bill SERIAL,
		total DOUBLE PRECISION NOT NULL,
		payed DOUBLE PRECISION NOT NULL,
		nif BIGINT NOT NULL,
		PRIMARY KEY (id_bill)
	);

CREATE TABLE
	specialization (
		name VARCHAR(512) NOT NULL,
		id_specialization SERIAL,
		specialization_id_specialization INTEGER NOT NULL,
		PRIMARY KEY (id_specialization)
	);

CREATE TABLE
	person (
		name VARCHAR(512) NOT NULL,
		cc BIGINT,
		email VARCHAR(512),
		contact BIGINT NOT NULL,
		nif BIGINT,
		password VARCHAR(255) NOT NULL,
		PRIMARY KEY (cc)
	);

CREATE TABLE
	doctors_specialization (
		doctors_employees_person_cc BIGINT,
		specialization_id_specialization INTEGER,
		PRIMARY KEY (
			doctors_employees_person_cc,
			specialization_id_specialization
		)
	);

CREATE TABLE
	prescriptions_hospitalizations (
		prescriptions_id_pres INTEGER NOT NULL,
		hospitalizations_id_hos INTEGER,
		PRIMARY KEY (hospitalizations_id_hos)
	);

CREATE TABLE
	appointments_prescriptions (
		appointments_id_app INTEGER,
		prescriptions_id_pres INTEGER NOT NULL,
		PRIMARY KEY (appointments_id_app)
	);

ALTER TABLE patients ADD UNIQUE (health_user_id);

ALTER TABLE patients ADD CONSTRAINT patients_fk1 FOREIGN KEY (person_cc) REFERENCES person (cc);

ALTER TABLE employees ADD UNIQUE (id_contrato);

ALTER TABLE employees ADD CONSTRAINT employees_fk1 FOREIGN KEY (person_cc) REFERENCES person (cc);

ALTER TABLE doctors ADD UNIQUE (id_lic);

ALTER TABLE doctors ADD CONSTRAINT doctors_fk1 FOREIGN KEY (employees_person_cc) REFERENCES employees (person_cc);

ALTER TABLE nurses ADD CONSTRAINT nurses_fk1 FOREIGN KEY (hierarchy_level) REFERENCES hierarchy (level);

ALTER TABLE nurses ADD CONSTRAINT nurses_fk2 FOREIGN KEY (employees_person_cc) REFERENCES employees (person_cc);

ALTER TABLE assistants ADD CONSTRAINT assistants_fk1 FOREIGN KEY (employees_person_cc) REFERENCES employees (person_cc);

ALTER TABLE hierarchy ADD UNIQUE (nome);

ALTER TABLE hierarchy ADD CONSTRAINT hierarchy_fk1 FOREIGN KEY (hierarchy_level) REFERENCES hierarchy (level);

ALTER TABLE appointments ADD CONSTRAINT appointments_fk1 FOREIGN KEY (billings_id_bill) REFERENCES billings (id_bill);

ALTER TABLE appointments ADD CONSTRAINT appointments_fk2 FOREIGN KEY (doctors_employees_person_cc) REFERENCES doctors (employees_person_cc);

ALTER TABLE appointments ADD CONSTRAINT appointments_fk3 FOREIGN KEY (patients_person_cc) REFERENCES patients (person_cc);

ALTER TABLE hospitalizations ADD UNIQUE (billings_id_bill);

ALTER TABLE hospitalizations ADD CONSTRAINT hospitalizations_fk1 FOREIGN KEY (nurses_employees_person_cc) REFERENCES nurses (employees_person_cc);

ALTER TABLE hospitalizations ADD CONSTRAINT hospitalizations_fk2 FOREIGN KEY (billings_id_bill) REFERENCES billings (id_bill);

ALTER TABLE hospitalizations ADD CONSTRAINT hospitalizations_fk3 FOREIGN KEY (patients_person_cc) REFERENCES patients (person_cc);

ALTER TABLE surgeries ADD UNIQUE (name);

ALTER TABLE surgeries ADD CONSTRAINT surgeries_fk1 FOREIGN KEY (doctors_employees_person_cc) REFERENCES doctors (employees_person_cc);

ALTER TABLE surgeries ADD CONSTRAINT surgeries_fk2 FOREIGN KEY (hospitalizations_id_hos) REFERENCES hospitalizations (id_hos);

ALTER TABLE roles ADD UNIQUE (role_name);

ALTER TABLE does_surgery ADD CONSTRAINT does_surgery_fk1 FOREIGN KEY (roles_role_num) REFERENCES roles (role_num);

ALTER TABLE does_surgery ADD CONSTRAINT does_surgery_fk2 FOREIGN KEY (surgeries_id_sur) REFERENCES surgeries (id_sur);

ALTER TABLE does_surgery ADD CONSTRAINT does_surgery_fk3 FOREIGN KEY (nurses_employees_person_cc) REFERENCES nurses (employees_person_cc);

ALTER TABLE is_comprised_app ADD CONSTRAINT is_comprised_app_fk1 FOREIGN KEY (medication_id_med) REFERENCES medication (id_med);

ALTER TABLE is_comprised_app ADD CONSTRAINT is_comprised_app_fk2 FOREIGN KEY (prescriptions_id_pres) REFERENCES prescriptions (id_pres);

ALTER TABLE medication ADD UNIQUE (name);

ALTER TABLE corresponds ADD CONSTRAINT corresponds_fk1 FOREIGN KEY (side_effects_id_side) REFERENCES side_effects (id_side);

ALTER TABLE corresponds ADD CONSTRAINT corresponds_fk2 FOREIGN KEY (medication_id_med) REFERENCES medication (id_med);

ALTER TABLE specialization ADD UNIQUE (name);

ALTER TABLE specialization ADD CONSTRAINT specialization_fk1 FOREIGN KEY (specialization_id_specialization) REFERENCES specialization (id_specialization);

ALTER TABLE person ADD UNIQUE (email, contact);

ALTER TABLE doctors_specialization ADD CONSTRAINT doctors_specialization_fk1 FOREIGN KEY (doctors_employees_person_cc) REFERENCES doctors (employees_person_cc);

ALTER TABLE doctors_specialization ADD CONSTRAINT doctors_specialization_fk2 FOREIGN KEY (specialization_id_specialization) REFERENCES specialization (id_specialization);

ALTER TABLE prescriptions_hospitalizations ADD CONSTRAINT prescriptions_hospitalizations_fk1 FOREIGN KEY (prescriptions_id_pres) REFERENCES prescriptions (id_pres);

ALTER TABLE prescriptions_hospitalizations ADD CONSTRAINT prescriptions_hospitalizations_fk2 FOREIGN KEY (hospitalizations_id_hos) REFERENCES hospitalizations (id_hos);

ALTER TABLE appointments_prescriptions ADD CONSTRAINT appointments_prescriptions_fk1 FOREIGN KEY (appointments_id_app) REFERENCES appointments (id_app);

ALTER TABLE appointments_prescriptions ADD CONSTRAINT appointments_prescriptions_fk2 FOREIGN KEY (prescriptions_id_pres) REFERENCES prescriptions (id_pres);

insert into
	person (name, cc, email, contact, nif, password)
values
	(
		'utente1',
		111111111,
		'utente1@gmail.com',
		911111111,
		211111111,
		'$2b$12$2Ub8XafyuQ5may4KHGa47OzTr370pdoKQ.pvMd/FCKSYDgQA0eoAy'
	),
	(
		'utente2',
		222222222,
		'utente2@gmail.com',
		922222222,
		222222222,
		'$2b$12$KrCa0gy1UA2BpEtPOAQFM.Pif24nQS47OVEX2svy2gMWp0pPiJHvC'
	),
	(
		'utente3',
		333333333,
		'utente3@gmail.com',
		933333333,
		233333333,
		'$2b$12$uwW496fDMuCG9XzEmeVy1.6t1aGkLtLcDyDJfPl4.9b51/sxKa5aO'
	),
	(
		'utente4',
		444444444,
		'utente4@gmail.com',
		944444444,
		244444444,
		'$2b$12$/oVIsmICORLVGRn00IFOY.bzSbd4Sq7zDR/rDcN7/6sT7bBIxJ5.y'
	),
	(
		'utente5',
		555555555,
		'utente5@gmail.com',
		955555555,
		255555555,
		'$2b$12$k1JJXmTj//jN.9qizY2FLOOZaQ1zuum8tZj80Af5tjP2UnjVSFS26'
	),
	(
		'utente6',
		666666666,
		'utente6@gmail.com',
		966666666,
		266666666,
		'$2b$12$xy2cCSXYDkkG/jl3a6zXUuL7G44CwH5ZapCOOHLZe1cGV0wxNpqeu'
	),
	(
		'utente7',
		777777777,
		'utente7@gmail.com',
		977777777,
		277777777,
		'$2b$12$cr.OhrwiAwuV4010s7kzxez4JNGBjHMP25ym6tocD.UuAWCPfxm4e'
	),
	(
		'utente8',
		888888888,
		'utente8@gmail.com',
		988888888,
		288888888,
		'$2b$12$5LbEwogA.F7A3R7ERjVO/u3HOEDVQraHQajM5qmvNt6gfM171xml.'
	),
	(
		'utente9',
		999999999,
		'utente9@gmail.com',
		999999999,
		299999999,
		'$2b$12$eucrZCYm0EE1qoZB2hV/Sudt9gCdEQygRIMCWBlwcuHBRoUeDQLP6'
	),
	(
		'utente10',
		101010101,
		'utente10@gmail.com',
		910101010,
		210101010,
		'$2b$12$hm.RfLC1IlV1ikUuqHaKPuvs18MI4tRtdvCnZGEuL0rHMs9UQr9O.'
	),
	(
		'medico1',
		121212121,
		'medico1@gmail.com',
		912121212,
		212121212,
		'$2b$12$BXQTaTa9cA4JdnOQo13XHe1EskRy2UMq.KnZJ9fhIyvV14vjah1l6'
	),
	(
		'medico2',
		131313131,
		'medico2@gmail.com',
		913131313,
		213131313,
		'$2b$12$ZVyYAhkbBCqp3HbMbEo00OsDwJNmfUGAEn3pGIV36LUwZBi4LXEja'
	),
	(
		'medico3',
		141414141,
		'medico3@gmail.com',
		914141414,
		214141414,
		'$2b$12$qlrTR4pgeBjla5XaSLMXZuU97Ekn2/aBrvjlGoPC6wMwT/bNkLAEe'
	),
	(
		'enfermeiro1',
		115115115,
		'enfermeiro1@gmail.com',
		911511511,
		211511511,
		'$2b$12$4i3fTOl2Ta/aYAqN7stg1uBflLUKMt/2IzILTltrCCTMTMEWVzz9K'
	),
	(
		'enfermeiro2',
		116116116,
		'enfermeiro2@gmail.com',
		911611611,
		211611611,
		'$2b$12$czi38tw7czRhTUbQYt4NMuupbTmDtRvlUjyA69sA4HPTmrNEmG4wa'
	),
	(
		'enfermeiro3',
		117117117,
		'enfermeiro3@gmail.com',
		911711711,
		211711711,
		'$2b$12$8ABKTsCA98/JbnV3dTtCveJff2kZAyIHWwYOxeitnN/fMum3VPhYW'
	),
	(
		'enfermeiro4',
		118118118,
		'enfermeiro4@gmail.com',
		911811811,
		211811811,
		'$2b$12$7rQkfNEw0lZqFwPZwd4T5O3VGF28PZJb41KAAx4rkKb.Xq8uNevuG'
	),
	(
		'enfermeiro5',
		119119119,
		'enfermeiro5@gmail.com',
		911911911,
		211911911,
		'$2b$12$ckfZ3CYIyvE3ysh/Nv73yeF9Zo.vXApkmsu5oPYPZrWuC4KvKM..C'
	),
	(
		'assistente1',
		111111112,
		'assistente1@gmail.com',
		911111112,
		211111112,
		'$2b$12$qb7L3XFUuE/xPLW3SsCpju222M4FmeyeY/uVrwivU.k7CKvVu3jIa'
	),
	(
		'assistente2',
		111111113,
		'assistente2@gmail.com',
		911111113,
		211111113,
		'$2b$12$Ukve1dx1d3JwgX/VaJKlPejy2Ocr.ojqLMm/e1gM0KOaNC1WcvLjO'
	);

insert into
	employees (person_cc, id_contrato)
values
	(121212121, 1),
	(131313131, 2),
	(141414141, 3),
	(115115115, 4),
	(116116116, 5),
	(117117117, 6),
	(118118118, 7),
	(119119119, 8),
	(111111112, 9),
	(111111113, 10);

alter SEQUENCE employees_id_contrato_seq
RESTART WITH 11;

insert into
	assistants (employees_person_cc)
values
	(111111112),
	(111111113);

insert into
	doctors (id_lic, instituto, employees_person_cc)
values
	(1, 'Coimbra', 121212121),
	(2, 'Lisboa', 131313131),
	(3, 'Porto', 141414141);

alter SEQUENCE doctors_id_lic_seq
RESTART WITH 4;

insert into
	specialization (
		name,
		id_specialization,
		specialization_id_specialization
	)
values
	('cardiologia', 1, 1),
	('cardioqualquercoisa', 2, 1),
	('neurologia', 3, 3);

alter SEQUENCE specialization_id_specialization_seq
RESTART WITH 4;

insert into
	doctors_specialization (
		doctors_employees_person_cc,
		specialization_id_specialization
	)
values
	(121212121, 1),
	(131313131, 2),
	(141414141, 3);

insert into
	hierarchy (level, nome, hierarchy_level)
values
	(1, 'Chefe', 1),
	(2, 'Assistente', 1),
	(3, 'Estagiario', 2),
	(4, 'Continuo', 2);

alter SEQUENCE hierarchy_level_seq
RESTART WITH 5;

insert into
	nurses (employees_person_cc, hierarchy_level)
values
	(115115115, 1),
	(116116116, 2),
	(117117117, 3),
	(118118118, 2),
	(119119119, 4);

insert into
	roles (role_num, role_name)
values
	(1, 'role1'),
	(2, 'role2'),
	(3, 'role3');

alter SEQUENCE roles_role_num_seq
RESTART WITH 4;

insert into
	patients (health_user_id, person_cc)
values
	(1, 111111111),
	(2, 222222222),
	(3, 333333333),
	(4, 444444444),
	(5, 555555555),
	(6, 666666666),
	(7, 777777777),
	(8, 888888888),
	(9, 999999999),
	(10, 101010101);

alter SEQUENCE patients_health_user_id_seq
RESTART WITH 11;

insert into
	medication (id_med, name)
values
	(1, 'medicamento1'),
	(2, 'medicamento2'),
	(3, 'medicamento3'),
	(4, 'medicamento4');

alter SEQUENCE medication_id_med_seq
RESTART WITH 5;

insert into
	side_effects (id_side, description)
values
	(1, 'efeito_secundario1'),
	(2, 'efeito_secundario2'),
	(3, 'efeito_secundario3');

alter SEQUENCE side_effects_id_side_seq
RESTART WITH 4;

insert into
	corresponds (
		probability,
		severity,
		side_effects_id_side,
		medication_id_med
	)
values
	(10, 4.5, 1, 1),
	(12.5, 7.5, 1, 2),
	(40, 1.5, 2, 2),
	(90, 0.5, 2, 3),
	(20, 3, 3, 4);

insert into
	billings (id_bill, total, payed, nif)
values
	(1, 100, 0, 211111111),
	(2, 500, 500, 211111111),
	(3, 1000, 50, 222222222),
	(4, 10000, 6000, 211111111);

alter SEQUENCE billings_id_bill_seq
RESTART WITH 5;

insert into
	prescriptions (id_pres)
values
	(1),
	(2);

alter SEQUENCE prescriptions_id_pres_seq
RESTART WITH 3;

insert into
	is_comprised_app (amount, medication_id_med, prescriptions_id_pres)
values
	(1, 1, 1),
	(2, 2, 1),
	(3, 3, 2);

insert into
	appointments (
		id_app,
		data,
		billings_id_bill,
		doctors_employees_person_cc,
		patients_person_cc
	)
values
	(1, '2024-04-16 12:00:00', 1, 121212121, 111111111),
	(2, '2024-04-17 11:00:00', 2, 131313131, 111111111),
	(3, '2024-04-17 10:00:00', 3, 141414141, 222222222);

alter SEQUENCE appointments_id_app_seq
RESTART WITH 4;

insert into
	hospitalizations (
		id_hos,
		date_begin,
		date_end,
		room,
		nurses_employees_person_cc,
		billings_id_bill,
		patients_person_cc
	)
values
	(
		1,
		'2024-04-16',
		'2024-04-17',
		1,
		115115115,
		4,
		111111111
	),
	(
		2,
		'2024-04-16',
		'2024-04-17',
		2,
		116116116,
		2,
		222222222
	);

alter SEQUENCE hospitalizations_id_hos_seq
RESTART WITH 3;

insert into
	prescriptions_hospitalizations (prescriptions_id_pres, hospitalizations_id_hos)
values
	(1, 1),
	(1, 2);

insert into
	appointments_prescriptions (appointments_id_app, prescriptions_id_pres)
values
	(1, 1),
	(2, 2);