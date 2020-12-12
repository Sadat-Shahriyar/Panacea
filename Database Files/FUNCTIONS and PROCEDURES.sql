CREATE OR REPLACE PROCEDURE SCHEDULE_RANGE(EMPID IN NUMBER, TIMEID IN VARCHAR2, DAYS IN VARCHAR2, BLOCKID IN VARCHAR2, LENGTH IN VARCHAR2) IS
	START_DATE DATE;
	ANY_DAY VARCHAR2(100);
	MAXVAL NUMBER;
BEGIN
	START_DATE := TRUNC(SYSDATE);
	DELETE FROM PANACEA.SCHEDULE WHERE SCHEDULE_DATE>START_DATE AND ID = EMPID;
	FOR R IN 1..LENGTH
	LOOP
		SELECT TO_CHAR((START_DATE + R), 'dy') INTO ANY_DAY FROM dual;
		IF INSTR(DAYS, ANY_DAY)>0 THEN
			SELECT MAX(SCHEDULE_ID) INTO MAXVAL FROM PANACEA.SCHEDULE;
			MAXVAL := MAXVAL + 1;
			INSERT INTO SCHEDULE (SCHEDULE_ID, SCHEDULE_DATE, ID, TIME_ID, BLOCK_ID) VALUES (MAXVAL, START_DATE + R, EMPID, TIMEID, BLOCKID);
		END IF;
	END LOOP;
END;
/

CREATE OR REPLACE PROCEDURE INSERT_DIAGNOSIS(APP_SL IN NUMBER, SERVICE_ID IN VARCHAR2,SURG_DESC IN VARCHAR2, MEDICINE IN VARCHAR2, DIAG_DESC IN VARCHAR2) IS
	PAT_ID NUMBER;
	ID NUMBER;
	DIAG_ID NUMBER;
	SERVICE_RESULTS VARCHAR2(500);
	FIRST_INS NUMBER;
	SERVICE_CATEGORY VARCHAR2(50);
BEGIN
	SELECT PATIENT_ID INTO PAT_ID FROM APPOINTMENT WHERE APP_SL_NO = APP_SL;
	SERVICE_RESULTS := '';
	FIRST_INS := 1;
	DBMS_OUTPUT.PUT_LINE(SURG_DESC);
	DBMS_OUTPUT.PUT_LINE(SERVICE_ID);
	IF SERVICE_ID IS NOT NULL THEN
		DBMS_OUTPUT.PUT_LINE('HELLO1');
		FOR CUR IN (select regexp_substr(SERVICE_ID,'[^-]+', 1, level) AS "SERVICE_ID"
								 from dual
								 connect BY regexp_substr(SERVICE_ID, '[^-]+', 1, level)
								 is not null)
		 LOOP
				SELECT CATEGORY INTO SERVICE_CATEGORY FROM SERVICE WHERE SERVICE_ID = CUR.SERVICE_ID;
				IF SERVICE_CATEGORY = 'TEST' THEN
					DBMS_OUTPUT.PUT_LINE('HELLO');
					SELECT MAX(TEST_RESULT_ID) INTO ID FROM TEST_RESULTS;
					ID := ID + 1;
					INSERT INTO TEST_RESULTS(TEST_RESULT_ID, SERVICE_ID, COMPLETED,PATIENT_ID) VALUES(ID, CUR.SERVICE_ID,'F', PAT_ID);
				ELSE
					SELECT MAX(SURGERY_RESULT_ID) INTO ID FROM SURGERY_RESULTS;
					ID := ID + 1;
					INSERT INTO SURGERY_RESULTS(SURGERY_RESULT_ID, SERVICE_ID,SURGERY_DESC, COMPLETED) 
					VALUES(ID, CUR.SERVICE_ID, (SELECT SERVICE_DESC FROM SERVICE WHERE SERVICE_ID = CUR.SERVICE_ID),'F');
				END IF;
				
				IF FIRST_INS > 1 THEN
					SERVICE_RESULTS := SERVICE_RESULTS || '-' ||TO_CHAR(ID);
				ELSE
					SERVICE_RESULTS := SERVICE_RESULTS || TO_CHAR(ID);
				END IF;
				
				FIRST_INS := FIRST_INS + 1;
				ID := ID + 1;
		 END LOOP;
	 END IF;
	 
	 
	 IF SURG_DESC IS NOT NULL THEN
			DBMS_OUTPUT.PUT_LINE('HELLO');
			SELECT MAX(SURGERY_RESULT_ID) INTO ID FROM SURGERY_RESULTS;
			ID := ID + 1;
			INSERT INTO SURGERY_RESULTS(SURGERY_RESULT_ID,SURGERY_DESC, COMPLETED) 
			VALUES(ID, SURG_DESC,'F');
			
			IF FIRST_INS > 1 THEN
				SERVICE_RESULTS := SERVICE_RESULTS || '-' ||TO_CHAR(ID);
			ELSE
				SERVICE_RESULTS := SERVICE_RESULTS || TO_CHAR(ID);
			END IF;
	 END IF;
	
	 DBMS_OUTPUT.PUT_LINE(SERVICE_RESULTS);
	 
	 SELECT (MAX(DIAGNOSIS_ID) +1) INTO DIAG_ID FROM DIAGNOSIS;
	 
	 INSERT INTO DIAGNOSIS VALUES(DIAG_ID, SERVICE_RESULTS, MEDICINE, DIAG_DESC);
	 INSERT INTO CHECKUP VALUES((SELECT MAX(CHECKUP_ID) + 1 FROM CHECKUP), APP_SL, DIAG_ID, TRUNC(SYSDATE));
	
EXCEPTION
	WHEN NO_DATA_FOUND THEN
		DBMS_OUTPUT.PUT_LINE('NO DATA FOUND');
	WHEN OTHERS THEN
		DBMS_OUTPUT.PUT_LINE('UNKNOWN EXCEPTION');
END;
/


BEGIN
	INSERT_DIAGNOSIS(6,'1', 'remove molar teeth','NAPA','SUCCESSFUL');
END;
/

CREATE OR REPLACE TYPE SURGERY_RESULTS_ROW AS OBJECT(
	SURGERY_RESULT_ID NUMBER,
	SURGERY_DESC VARCHAR2(500),
	COMPLETED VARCHAR2(2),
	SURGERY_DATE DATE,
	STATUS VARCHAR2(20),
	RESULT VARCHAR2(200)
);
/


CREATE OR REPLACE TYPE SURGERY_RESULT_TABLE AS TABLE OF SURGERY_RESULTS_ROW;
/

--- returns every surgery that is done or pending by a doctor
CREATE OR REPLACE FUNCTION RETURN_SURGERY_RESULT_TABLE(DOC_ID IN NUMBER) 
RETURN SURGERY_RESULT_TABLE AS 
	RESULT SURGERY_RESULT_TABLE;
	SURGERY_DESCRIPTION VARCHAR2(500);
	COMPLT VARCHAR2(2);
	SURG_DATE DATE;
	SURG_STATUS VARCHAR2(20);
	SURG_COMMENT VARCHAR2(200);
BEGIN
	RESULT := SURGERY_RESULT_TABLE();
	FOR CUR IN (SELECT SERVICE_RESULTS 
							FROM DIAGNOSIS
							WHERE DIAGNOSIS_ID IN(SELECT DIAGNOSIS_ID 
																		FROM CHECKUP
																		WHERE APP_SL_NO IN(SELECT APP_SL_NO 
																											 FROM APPOINTMENT
																											 WHERE DOCTOR_ID = DOC_ID))
							ORDER BY DIAGNOSIS_ID DESC)
	LOOP
		FOR CUR1 IN (select regexp_substr(CUR.SERVICE_RESULTS,'[^-]+', 1, level) AS "SERVICE_ID"
									from dual
									connect BY regexp_substr(CUR.SERVICE_RESULTS, '[^-]+', 1, level)
									is not null)
		LOOP
			IF CUR1.SERVICE_ID LIKE '601%' THEN
				SELECT SURGERY_DESC,COMPLETED, SURGERY_DATE, STATUS, RESULT  INTO SURGERY_DESCRIPTION, COMPLT,SURG_DATE, SURG_STATUS,SURG_COMMENT
				FROM SURGERY_RESULTS
				WHERE SURGERY_RESULT_ID = TO_NUMBER(CUR1.SERVICE_ID,'99999999');
				
				RESULT.EXTEND;
				RESULT(RESULT.COUNT) := SURGERY_RESULTS_ROW(TO_NUMBER(CUR1.SERVICE_ID,'99999999'),SURGERY_DESCRIPTION, COMPLT,SURG_DATE,
																										SURG_STATUS,SURG_COMMENT);			
				
			END IF;
		END LOOP;
	END LOOP;
	
	RETURN RESULT;
	
END RETURN_SURGERY_RESULT_TABLE;
/


CREATE OR REPLACE TYPE TEST_RESULT_ROW AS OBJECT(
	APP_SL_NO NUMBER,
	TEST_RESULT_ID NUMBER,
	SERVICE_NAME VARCHAR2(100),
	TEST_COMPLETE_DATE DATE,
	TEST_RESULT VARCHAR2(500),
	COMPLETED VARCHAR2(2)
);

CREATE OR REPLACE TYPE TEST_RESULT_TABLE AS TABLE OF TEST_RESULT_ROW;
/


CREATE OR REPLACE FUNCTION RETURN_TEST_RESULT_TABLE(PAT_ID IN VARCHAR2)
RETURN TEST_RESULT_TABLE AS 
	RESULT TEST_RESULT_TABLE;
	APPNT_SL_NO NUMBER;
	TEST_ID NUMBER;
	TEST_NAME VARCHAR2(100);
	TEST_DATE DATE;
	TEST_RESULT VARCHAR2(500);
	TEST_COMPLETED VARCHAR2(2);
	SERV_RES VARCHAR2(500);
BEGIN
	RESULT := TEST_RESULT_TABLE();
	
	FOR CUR IN (SELECT APP_SL_NO FROM APPOINTMENT WHERE PATIENT_ID = (SELECT ID FROM PERSON WHERE USER_ID = PAT_ID))
	LOOP
		
			FOR CUR1 IN (SELECT DIAGNOSIS_ID FROM CHECKUP WHERE APP_SL_NO = CUR.APP_SL_NO)
			LOOP
					IF CUR1.DIAGNOSIS_ID IS NOT NULL THEN
							SELECT SERVICE_RESULTS INTO SERV_RES FROM DIAGNOSIS WHERE DIAGNOSIS_ID = CUR1.DIAGNOSIS_ID;
							FOR CUR2 IN (select regexp_substr(SERV_RES,'[^-]+', 1, level) AS "SERVICE_ID"
													from dual
													connect BY regexp_substr(SERV_RES, '[^-]+', 1, level)
													is not null)
							LOOP
-- 									DBMS_OUTPUT.PUT_LINE(CUR2.SERVICE_ID);
									IF CUR2.SERVICE_ID LIKE '501%' THEN
												
											SELECT T.TEST_RESULT_ID, S.SERVICE_NAME, T.TEST_DATE, T.RESULT, T.COMPLETED
											INTO TEST_ID,TEST_NAME,TEST_DATE,TEST_RESULT,TEST_COMPLETED
											FROM TEST_RESULTS T JOIN SERVICE S ON(T.SERVICE_ID = S.SERVICE_ID)
											WHERE T.TEST_RESULT_ID = TO_NUMBER(CUR2.SERVICE_ID, '99999999');
											
											RESULT.EXTEND;
											RESULT(RESULT.COUNT) := TEST_RESULT_ROW(CUR.APP_SL_NO,TEST_ID,TEST_NAME,TEST_DATE,TEST_RESULT,TEST_COMPLETED);	
											
									END IF;
							END LOOP;
							
					END IF;
			END LOOP;
	
	END LOOP;
	
	
	RETURN RESULT;
END RETURN_TEST_RESULT_TABLE;
/


CREATE OR REPLACE TYPE SURGERY_RESULT_ROW_PATIENT AS OBJECT(
	APP_SL_NO NUMBER,
	SURGERY_RESULT_ID NUMBER,
	SURGERY_DATE DATE,
	SURGERY_DESC VARCHAR2(500),
	COMPLETED VARCHAR2(2),
	STATUS VARCHAR2(15),
	RESULT VARCHAR2(200)
);
/

CREATE OR REPLACE TYPE SURGERY_RESULT_TABLE_PATIENT AS TABLE OF SURGERY_RESULT_ROW_PATIENT;
/

CREATE OR REPLACE FUNCTION RETURN_SURGERY_RESULT_PATIENT(PAT_ID IN VARCHAR2) 
RETURN SURGERY_RESULT_TABLE_PATIENT AS 
		RESULT SURGERY_RESULT_TABLE_PATIENT;
		SURG_ID NUMBER;
		SURG_DATE DATE;
		SURG_DESC VARCHAR2(500);
		SURG_COMPLETED VARCHAR2(2);
		SURG_STATUS VARCHAR2(15);
		SURG_RESULT VARCHAR2(200);
BEGIN
		RESULT := SURGERY_RESULT_TABLE_PATIENT();
		FOR CUR IN (SELECT D.SERVICE_RESULTS, C.APP_SL_NO
								FROM CHECKUP C JOIN DIAGNOSIS D ON(C.DIAGNOSIS_ID = D.DIAGNOSIS_ID)
								WHERE C.APP_SL_NO IN (SELECT APP_SL_NO FROM APPOINTMENT WHERE PATIENT_ID = (SELECT ID FROM PERSON WHERE USER_ID = PAT_ID)))
		LOOP
				FOR CUR1 IN (select regexp_substr(CUR.SERVICE_RESULTS,'[^-]+', 1, level) AS "SERVICE_ID"
											from dual
											connect BY regexp_substr(CUR.SERVICE_RESULTS, '[^-]+', 1, level)
											is not null)
				LOOP
						IF CUR1.SERVICE_ID LIKE '601%' THEN
								SELECT SURGERY_RESULT_ID, SURGERY_DATE, SURGERY_DESC,COMPLETED, STATUS, RESULT
								INTO SURG_ID, SURG_DATE, SURG_DESC, SURG_COMPLETED, SURG_STATUS, SURG_RESULT
								FROM SURGERY_RESULTS
								WHERE SURGERY_RESULT_ID = TO_NUMBER(CUR1.SERVICE_ID, '999999999');
								
								RESULT.EXTEND;
								RESULT(RESULT.COUNT) := SURGERY_RESULT_ROW_PATIENT(CUR.APP_SL_NO,SURG_ID,SURG_DATE,SURG_DESC,
																																	 SURG_COMPLETED,SURG_STATUS,SURG_RESULT);	
						END IF;
				END LOOP;
		END LOOP;
		
		RETURN RESULT;
END;
/



-- SELECT * FROM TABLE(RETURN_SURGERY_RESULT_PATIENT('P25001')) WHERE APP_SL_NO = 44;




-- DROP FUNCTION RETURN_SURGERY_RESULT_PATIENT;
-- DROP TYPE SURGERY_RESULT_TABLE_PATIENT;
-- DROP TYPE SURGERY_RESULT_ROW_PATIENT;

CREATE OR REPLACE FUNCTION CHECK_LOGIN(USR_ID IN VARCHAR2, PASSWORD IN VARCHAR2)
RETURN NUMBER IS
		PASS VARCHAR2(50);
		PASS_HASH VARCHAR2(50);
BEGIN
		SELECT PASSWORD INTO PASS
		FROM PERSON
		WHERE USER_ID = USR_ID;
		
		PASS_HASH := dbms_crypto.hash(utl_raw.cast_to_raw(PASSWORD), dbms_crypto.HASH_MD5);
		
		
		IF PASS = PASS_HASH THEN
			RETURN 1;
		ELSE
			RETURN 0;
		END IF;
		
END;

SELECT CHECK_LOGIN(USER_ID, 'E28101') FROM PERSON WHERE USER_ID = 'E28101';


-- RETURN ALL DATA FOR AN APPOINTMENT

CREATE OR REPLACE TYPE APPOINTMENT_DETAILS_ROW AS OBJECT(
	PATIENT_ID NUMBER,
	DOCTOR_NAME VARCHAR2(50),
	DEPARTMENT VARCHAR2(50),
	APPOINTMENT_DATE VARCHAR2(20),
	SCHEDULE_DATE VARCHAR2(20),
	PROB_DESC VARCHAR2(500),
	MEDICINE VARCHAR2(100),
	TESTS VARCHAR2(200)
);
/

DROP TYPE APPOINTMENT_DETAILS_TABLE;

CREATE OR REPLACE TYPE APPOINTMENT_DETAILS_TABLE AS TABLE OF APPOINTMENT_DETAILS_ROW;
/

CREATE OR REPLACE FUNCTION RETURN_APPNT_DETAILS_TABLE(PATIENT_USER_ID IN VARCHAR2)
RETURN APPOINTMENT_DETAILS_TABLE AS 
	RESULT APPOINTMENT_DETAILS_TABLE;
	SERVICE_NO NUMBER;
	TEST_NAME VARCHAR2(100);
	ALL_TESTS VARCHAR2(500);
BEGIN 
	RESULT := APPOINTMENT_DETAILS_TABLE();
	FOR CUR IN (SELECT (D.FIRST_NAME||' '||D.LAST_NAME) AS DOCTOR_NAME, (SELECT DEPARTMENT FROM DOCTOR WHERE ID = A.DOCTOR_ID) AS DEPARTMENT,
						A.PROB_DESC, A.PATIENT_ID, A.APP_SL_NO, 
						TO_CHAR(A.APPNT_DATE, 'DD/MM/YYYY') AS APPNT_DATE, TO_CHAR(SCH.SCHEDULE_DATE, 'DD/MM/YYYY') AS VISITING_DATE, 
						CH.CHECKUP_ID, DIAG.DIAGNOSIS_ID, DIAG.SERVICE_RESULTS, DIAG.MEDICINE
						FROM APPOINTMENT A JOIN PERSON D ON D.ID = A.DOCTOR_ID AND A.PATIENT_ID = (SELECT ID FROM PERSON WHERE USER_ID = PATIENT_USER_ID)
						AND A.STATUS = 'accepted' JOIN SCHEDULE SCH ON (A.SCHEDULE_ID = SCH.SCHEDULE_ID) JOIN CHECKUP CH
						ON (A.APP_SL_NO = CH.APP_SL_NO AND TRUNC(SCH.SCHEDULE_DATE) = TRUNC(CH.CHECKUP_DATE)) 
						JOIN DIAGNOSIS DIAG ON (CH.DIAGNOSIS_ID = DIAG.DIAGNOSIS_ID)
						ORDER BY A.APP_SL_NO)
	LOOP
		FOR CUR1 IN (select regexp_substr(CUR.SERVICE_RESULTS,'[^-]+', 1, level) AS "SERVICE_ID"
									from dual
									connect BY regexp_substr(CUR.SERVICE_RESULTS, '[^-]+', 1, level)
									is not null)
			LOOP
				IF CUR1.SERVICE_ID LIKE '501%' THEN							
					SELECT SERVICE_ID INTO SERVICE_NO FROM TEST_RESULTS WHERE TEST_RESULT_ID = TO_NUMBER(CUR1.SERVICE_ID, '99999999');
					SELECT SERVICE_NAME INTO TEST_NAME FROM SERVICE WHERE SERVICE_ID = SERVICE_NO;
					ALL_TESTS := (ALL_TESTS||'-'||TEST_NAME);						
				END IF;
			END LOOP;
		RESULT.EXTEND;
		RESULT(RESULT.COUNT) := APPOINTMENT_DETAILS_ROW(CUR.PATIENT_ID,CUR.DOCTOR_NAME,CUR.DEPARTMENT,CUR.APPNT_DATE, CUR.VISITING_DATE, CUR.PROB_DESC,
																										CUR.MEDICINE,ALL_TESTS);	
	END LOOP;
	
	RETURN RESULT;
END;
/


--SELECT * FROM TABLE(RETURN_APPNT_DETAILS_TABLE('P25002'));

-- CREATE ALL TESTS GIVEN BY A DOC

CREATE OR REPLACE TYPE DOC_ALL_TEST_ROW AS OBJECT(
	TEST_RESULT_ID NUMBER,
	PATIENT_NAME VARCHAR2(30),
	APP_SL_NO NUMBER,
	SERVICE_NAME VARCHAR2(100),
	TEST_COMPLETE_DATE VARCHAR2(10),
	TEST_RESULT VARCHAR2(500),
	COMPLETED VARCHAR2(2)
);

CREATE OR REPLACE TYPE DOC_ALL_TEST_TABLE AS TABLE OF DOC_ALL_TEST_ROW;
/

-- CREATE OR REPLACE TYPE LALA AS OBJECT(
-- 	APPNT_SUMMARY DOC_ALL_TEST_TABLE
-- );
-- /
-- DROP TYPE LALA;

CREATE OR REPLACE FUNCTION RETURN_DOC_ALL_TEST_TABLE(DOC_USERID IN VARCHAR2)
RETURN DOC_ALL_TEST_TABLE AS 
	RESULT DOC_ALL_TEST_TABLE;
	SERVICE_NO NUMBER;
	TEST_NAME VARCHAR2(100);
	TEST_DATE VARCHAR2(10);
	TEST_RESULT VARCHAR2(100);
	COMPLETE VARCHAR2(4);
BEGIN
	RESULT := DOC_ALL_TEST_TABLE();
	
	FOR CUR IN (SELECT A.APP_SL_NO, (P.FIRST_NAME||' '||P.LAST_NAME) AS PATIENT_NAME, D.SERVICE_RESULTS, D.DIAG_DESC
							FROM APPOINTMENT A JOIN CHECKUP CH
							ON (A.DOCTOR_ID = (SELECT ID FROM PERSON WHERE USER_ID = DOC_USERID) AND A.APP_SL_NO = CH.APP_SL_NO) 
							JOIN DIAGNOSIS D ON (D.DIAGNOSIS_ID = CH.DIAGNOSIS_ID)
							JOIN PERSON P ON (P.ID = A.PATIENT_ID))
	LOOP
		FOR CUR1 IN (select regexp_substr(CUR.SERVICE_RESULTS,'[^-]+', 1, level) AS "SERVICE_ID"
								from dual
								connect BY regexp_substr(CUR.SERVICE_RESULTS, '[^-]+', 1, level)
								is not null)
		LOOP
			IF CUR1.SERVICE_ID LIKE '501%' THEN							
				SELECT SERVICE_ID, NVL(TO_CHAR(TEST_DATE, 'DD/MM/YYYY'), 'N/A'), NVL(RESULT,'N/A'), COMPLETED INTO SERVICE_NO, TEST_DATE, 
				TEST_RESULT, COMPLETE FROM TEST_RESULTS WHERE TEST_RESULT_ID = TO_NUMBER(CUR1.SERVICE_ID, '99999999');
-- 				SELECT SERVICE_ID INTO SERVICE_NO FROM TEST_RESULTS WHERE TEST_RESULT_ID = TO_NUMBER(CUR1.SERVICE_ID, '99999999');
				SELECT SERVICE_NAME INTO TEST_NAME FROM SERVICE WHERE SERVICE_ID = SERVICE_NO;
				RESULT.EXTEND;
				RESULT(RESULT.COUNT) := DOC_ALL_TEST_ROW(TO_NUMBER(CUR1.SERVICE_ID, '99999999'), CUR.PATIENT_NAME, CUR.APP_SL_NO, TEST_NAME,
																									TEST_DATE, TEST_RESULT, COMPLETE); 
			END IF;
		END LOOP;
	END LOOP;
	
	RETURN RESULT;
END ;
/


select * from TABLE(RETURN_DOC_ALL_TEST_TABLE('D21001'));
-- NEW 
CREATE OR REPLACE FUNCTION EMPLOYEE_TYPE(EMP_USERID IN VARCHAR2)
RETURN VARCHAR2 AS 
	EMPLOYEE_TYPE VARCHAR2(20);
BEGIN 
	IF EMP_USERID LIKE 'D%' THEN
		EMPLOYEE_TYPE := 'DOCTOR';
	ELSIF EMP_USERID LIKE 'P%' THEN
		EMPLOYEE_TYPE := 'PATIENT';
	ELSIF EMP_USERID LIKE 'E%' THEN
		SELECT CATEGORY INTO EMPLOYEE_TYPE FROM EMPLOYEE 
		WHERE ID = (SELECT ID FROM PERSON WHERE USER_ID = EMP_USERID);
	ELSE
		EMPLOYEE_TYPE := 'NONE';
	END IF;
	RETURN EMPLOYEE_TYPE;
END;
/

-- BEGIN
-- 	DBMS_OUTPUT.PUT_LINE(EMPLOYEE_TYPE('E28007'));
-- END;

BEGIN
	FOR CUR IN (SELECT * FROM MEDICINE)
	LOOP
		UPDATE MEDICINE SET PRICE_PIECE = (SELECT TRUNC((DBMS_RANDOM.VALUE(1.32, 135.25)), 2) FROM DUAL) WHERE MED_ID=CUR.MED_ID;
	END LOOP;
END;

BEGIN
	FOR CUR IN (SELECT * FROM DOCTOR WHERE DESIGNATION='Registrar')
	LOOP
		UPDATE DOCTOR SET VISITING_FEE = 1000 WHERE ID=CUR.ID;
	END LOOP;
END;
		
-- NEW
-- NOT NEEDED
-- CREATE OR REPLACE TYPE PAT_CHECKUP_ROW AS OBJECT(
-- 	DOC_NAME VARCHAR2(100),
-- 	DEPARTMENT VARCHAR2(30),
-- 	VISITING_FEE NUMBER,
-- 	VISITING_DATE VARCHAR2(10),
-- 	DESCRIPTION VARCHAR2(100)
-- );
-- /
-- 
-- CREATE OR REPLACE TYPE PAT_SUR_DATA_ROW AS OBJECT(
-- 	ROOM_NO NUMBER,
-- 	OPERATION_DATE VARCHAR2(10),
-- 	CHARGE NUMBER
-- );
-- /
-- 
-- CREATE OR REPLACE TYPE PAT_ROOM_DATA_ROW AS OBJECT(
-- 	ROOM_NO NUMBER,
-- 	ADMISSION_DATE VARCHAR2(10),
-- 	DAYS_BETWEEN NUMBER,
-- 	CHARGE_PER_DAY NUMBER
-- );
-- 
-- CREATE OR REPLACE TYPE MED_DATA_ROW AS OBJECT(
-- 	MED_NAME VARCHAR2(20),
-- 	QUANTITY NUMBER,
-- 	PRICE_PER_PC NUMBER(10, 2)
-- );
-- /
-- 
-- CREATE OR REPLACE TYPE PAT_CHECKUP_TABLE AS TABLE OF PAT_CHECKUP_ROW;
-- /
-- CREATE OR REPLACE TYPE PAT_SUR_DATA_TABLE AS TABLE OF PAT_SUR_DATA_ROW;
-- /
-- CREATE OR REPLACE TYPE PAT_ROOM_DATA_TABLE AS TABLE OF PAT_ROOM_DATA_ROW;
-- /
-- CREATE OR REPLACE TYPE MED_DATA_TABLE AS TABLE OF MED_DATA_ROW;
-- /




	