from json import decoder
import cx_Oracle
import hashlib

from django.http import response
from UserHandler.execution import connect


def getScheduleTable(UserCategory, UserID):
    connection = connect()
    cursor = connection.cursor()
    if UserID != None:
        query = '''SELECT * FROM PANACEA.PERSON WHERE USER_ID = :UserID'''
        cursor.execute(query, [UserID])
        result = cursor.fetchone()
        if result == None:
            response = {}
            response['success'] = False
            response['errorMessage'] = "Invalid User's ID"
            response['docData'] = None
            response['empData'] = None
            response['scheduleData'] = None
            return response
        elif UserCategory == "doctor":
            query = '''SELECT (P.FIRST_NAME || ' ' || P.LAST_NAME) AS NAME,D.DEPARTMENT, D.DESIGNATION,D.QUALIFICATION,
                        S.SCHEDULE_ID, TO_CHAR(S.SCHEDULE_DATE) AS "DATE",
                        T.START_TIME, T.END_TIME, T.SHIFT_TITLE
                        FROM PANACEA.PERSON P JOIN PANACEA.DOCTOR D ON(P.ID = D.ID)
                        LEFT OUTER JOIN PANACEA.SCHEDULE S ON(P.ID = S.ID)
                        LEFT OUTER JOIN PANACEA.TIME_TABLE T ON(S.TIME_ID = T.TIME_ID)
                        WHERE P.USER_ID = :docUserID
                        ORDER BY S.SCHEDULE_DATE DESC'''

            cursor.execute(query, [UserID])
            result = cursor.fetchall()
            # print(result)

            docData = {
                'name': result[0][0],
                'department': result[0][1],
                'designation': result[0][2],
                'qualification': result[0][3]
            }
            scheduleData = []
            for i in range(len(result)):
                scheduleData.append({'SCHEDULE_ID': result[i][4], 'SCHEDULE_DATE': result[i][5],
                                     'START_TIME': result[i][6], 'END_TIME': result[i][7], 'SHIFT_TITLE': result[i][8]})
            # print(scheduleData)
            response = {}
            response['success'] = True
            response['errorMessage'] = None
            response['docData'] = docData
            response['scheduleData'] = scheduleData
            return response
        elif UserCategory == "employee":
            query = '''SELECT (P.FIRST_NAME || ' ' || P.LAST_NAME) AS NAME, E.CATEGORY,
                        S.SCHEDULE_ID, TO_CHAR(S.SCHEDULE_DATE) AS "DATE",
                        T.START_TIME, T.END_TIME, T.SHIFT_TITLE
                        FROM PANACEA.PERSON P JOIN PANACEA.EMPLOYEE E ON(P.ID = E.ID)
                        LEFT OUTER JOIN PANACEA.SCHEDULE S ON(P.ID = S.ID)
                        LEFT OUTER JOIN PANACEA.TIME_TABLE T ON(S.TIME_ID = T.TIME_ID)
                        WHERE P.USER_ID = :docUserID
                        ORDER BY S.SCHEDULE_DATE DESC'''
            cursor.execute(query, [UserID])
            result = cursor.fetchall()
            empData = {
                'name': result[0][0],
                'category': result[0][1],
            }

            scheduleData = []
            for i in range(len(result)):
                scheduleData.append({'SCHEDULE_ID': result[i][2], 'SCHEDULE_DATE': result[i][3],
                                     'START_TIME': result[i][4], 'END_TIME': result[i][5], 'SHIFT_TITLE': result[i][6]})
            response = {}
            response['success'] = True
            response['errorMessage'] = None
            response['empData'] = empData
            response['scheduleData'] = scheduleData
            return response
    else:
        response = {}
        response['success'] = False
        response['errorMessage'] = "Please insert a valid User's ID"
        response['docData'] = None
        response['empdata'] = None
        response['scheduleData'] = None
        return response


def deleteSchedule(selectedSchedules, UserCategory, UserID):
    connection = connect()
    cursor = connection.cursor()

    # print(selectedSchedules)
    query = '''DELETE FROM PANACEA.SCHEDULE WHERE SCHEDULE_ID = :ID'''
    cursor.executemany(query, [(i,) for i in selectedSchedules])
    connection.commit()

    return getScheduleTable(UserCategory, UserID)


def getTimeTable():
    connection = connect()
    cursor = connection.cursor()
    query = '''SELECT * FROM PANACEA.TIME_TABLE'''

    cursor.execute(query)
    result = cursor.fetchall()
    # print(result)

    timeTableData = []
    response = {}

    if(result != None):
        for timeTable in result:
            timeTableData.append({"TIME_ID": timeTable[0], "START_TIME": timeTable[1],
                                  "END_TIME": timeTable[2], "SHIFT_TITLE": timeTable[3]})

    response['success'] = True
    response['errorMessage'] = ''
    response['timeTableData'] = timeTableData

    return response


def getWardTable(category):
    connection = connect()
    cursor = connection.cursor()
    # print(category)
    query = f'select BLOCK_ID from PANACEA.BLOCK where CATEGORY=\'{category}\''
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    blockList = []
    response = {}
    if (result):
        for block in result:
            blockList.append({'block': block[0]})
    response['success'] = True
    response['errorMessage'] = ''
    response['blockList'] = blockList

    return response


def getWardCategory():
    connection = connect()
    cursor = connection.cursor()
    query = '''select DISTINCT(CATEGORY) from BLOCK'''
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        wardCategory = []
        response = {}

        if (result):
            for category in result:
                wardCategory.append({'CATEGORY': category[0]})

        response['success'] = True
        response['errorMessage'] = ''
        response['wardCategory'] = wardCategory

        return response
    except cx_Oracle.Error as error:
        errorObj, = error.args
        response = {'success': False, 'errorMessage': errorObj.message}
        return response


def addSchedule(UserID, userCategory, timeID, date, blockID):
    connection = connect()
    cursor = connection.cursor()
    response = {}
    # print(date, docID)
    query = f"SELECT * FROM PANACEA.SCHEDULE WHERE SCHEDULE_DATE = TO_DATE('{date}','dd/MM/yyyy') AND ID = (SELECT ID FROM PANACEA.PERSON WHERE USER_ID = '{UserID}') AND TIME_ID = {timeID}"

    cursor.execute(query)
    result = cursor.fetchall()
    # print(len(result))
    if(len(result) != 0):
        response['success'] = False
        response['errorMessage'] = 'Duplicate schedule entry. Please insert a new value'
        response['scheduleData'] = None
        response['docData'] = None
        response['empData'] = None
        return response

    query = '''INSERT INTO PANACEA.SCHEDULE(SCHEDULE_ID,SCHEDULE_DATE,ID,TIME_ID, BLOCK_ID)
               VALUES(TO_NUMBER((SELECT MAX(SCHEDULE_ID) FROM SCHEDULE))+1, TO_DATE(''' + "'" + date + "'" ''', 'dd/MM/yyyy'),
               (SELECT ID FROM PERSON WHERE USER_ID = ''' + "'" + UserID + "'" + ")," + str(timeID) + ",\'"+str(blockID)+"\')"

    cursor.execute(query)
    connection.commit()

    return getScheduleTable(userCategory, UserID)


def addScheduleRange(userID, userCategory, timeID, days, blockID, scheduleLength):
    connection = connect()
    cursor = connection.cursor()
    query = '''SELECT ID FROM PANACEA.PERSON WHERE USER_ID = \''''+userID+"\'"
    cursor.execute(query)
    id_pk = cursor.fetchone()
    # print(id_pk[0], userCategory, timeID, days, blockID, scheduleLength)
    query = '''BEGIN
	                SCHEDULE_RANGE(:userID , :timeID, :days, :blockID, :scheduleLength);
                END;'''
    cursor.execute(query, [id_pk[0], timeID, days, blockID, scheduleLength])
    connection.commit()
    cursor.close()

    return getScheduleTable(userCategory, userID)


def getAppntWithSl(diagnosisID):
    connection = connect()
    cursor = connection.cursor()
    query = '''
    SELECT APP_SL_NO FROM CHECKUP WHERE DIAGNOSIS_ID = :diagnosisID
    '''
    cursor.execute(query, [diagnosisID])
    result = cursor.fetchone()

    appntSerial = result[0]

    query = '''SELECT * FROM 
            (
            SELECT (FIRST_NAME||' '||LAST_NAME) AS pNAME, EMAIL AS pEMAIL, PHONE_NUM AS pPHONE, GENDER AS pGENDER, 
            (ROUND(MONTHS_BETWEEN(SYSDATE, DATE_OF_BIRTH)/12)||' years '||FLOOR(MOD(MONTHS_BETWEEN(SYSDATE, DATE_OF_BIRTH), 12))||' months') as pAGE,
            ID AS pID
            FROM PERSON 
            WHERE ID = 
            (SELECT PATIENT_ID FROM APPOINTMENT WHERE 
            APP_SL_NO = :appntSerial)) P NATURAL JOIN  
            (SELECT (P.FIRST_NAME||' '||P.LAST_NAME) AS dNAME, D.DEPARTMENT, P.ID FROM 
            DOCTOR D JOIN PERSON P
            ON( D.ID = (SELECT DOCTOR_ID FROM APPOINTMENT WHERE 
            APP_SL_NO = :appntSerial) AND D.ID = P.ID)) D'''
    cursor.execute(query, [appntSerial, appntSerial])
    resultTemp = cursor.fetchall()
    cursor.close()

    # print(appntSerial)
    result = {
        'appointmentData': {
            'app_sl_no': appntSerial,
            'patientData': {
                'name': resultTemp[0][0],
                'email': resultTemp[0][1],
                'phone': resultTemp[0][2],
                'gender': "Male" if resultTemp[0][3] == "M" else "Female",
                'age': resultTemp[0][4],
                'id': resultTemp[0][5]
            },
            'appntDocData': {
                'name': resultTemp[0][6],
                'department': resultTemp[0][7],
                'id': resultTemp[0][8]
            },
        },
        'success': True,
        'errorMessage': '',
        'ok': True
    }
    print(result)
    return result


def getFreeDocOnDate(docID, selectDate):
    # print(docID, selectDate)
    connection = connect()
    cursor = connection.cursor()
    query = '''SELECT E.ID, E.NAME FROM (
            SELECT D.ID, (P.FIRST_NAME||' '||P.LAST_NAME) AS NAME FROM DOCTOR D JOIN PERSON P 
            ON D.DEPARTMENT =
            (SELECT D.DEPARTMENT FROM DOCTOR D
            JOIN PERSON P ON (D.ID = P.ID) AND P.ID = :docID) AND D.ID=P.ID) E
            WHERE E.ID NOT IN 
            (SELECT INCHARGE_DOC FROM SURGERY_SCHEDULE
            WHERE TO_CHAR(SUR_DATE) = :selectDate)'''

    cursor.execute(query, [docID, selectDate])
    resultTemp = cursor.fetchall()
    docData = []
    for R in resultTemp:
        docData.append({
            'id': R[0],
            'name': R[1],
        })
    result = {
        'docData': docData,
        'alertMessage': "Okay",
        'success': True,
    }
    return result


def getRoomList(searchDate, roomType, timeID):
    connection = connect()
    cursor = connection.cursor()
    query = '''SELECT R.ROOM_NO, R.TYPE FROM ROOM R JOIN BLOCK B
                ON R.BLOCK_ID = B.BLOCK_ID
                AND LOWER(B.CATEGORY) IN :roomType 
                AND R.ROOM_NO NOT IN
                (SELECT ROOM_NO FROM SURGERY_SCHEDULE
                WHERE TO_CHAR(SUR_DATE, 'DD/MM/YYYY') = :searchDate
                AND TIME_ID = :timeID)'''
    cursor.execute(query, [roomType, searchDate, timeID])
    resultTemp = cursor.fetchall()
    cursor.close()
    roomData = []
    for R in resultTemp:
        roomData.append({
            'room_no': R[0],
            'room_name': R[1]
        })
    result = {
        'roomData': roomData,
        'alertMesage': "Okay",
        'success': True
    }
    return result


def addSurSchedule(appnt_serial_no, inchargeDocID, patient_id,
                   room_no, timeID, duration, selectedDate, surgery_result_id):
    connection = connect()
    cursor = connection.cursor()
    # perform check if ref appnt id already exists...
    # selectedDate = f"'{selectedDate}'"
    # print(appnt_serial_no, inchargeDocID, patient_id, room_no, timeID, duration, selectedDate)

    query = f'''
    SELECT COUNT(*)
    FROM SURGERY_SCHEDULE 
    WHERE ROOM_NO = {room_no} AND TIME_ID = {timeID} AND SUR_DATE = TO_DATE('{selectedDate}', 'DD/MM/YYYY')
    '''

    print(room_no, timeID, selectedDate)
    cursor.execute(query)
    result = cursor.fetchone()[0]
    print(result)
    if result > 0:
        return {'success': False, 'errorMessage': 'There is already a surgery scheduled at the time slot. Please select a different one'}

    query = '''
    DECLARE
        ID NUMBER;
    BEGIN
        INSERT INTO SURGERY_SCHEDULE(APP_REF_NO, INCHARGE_DOC, PATIENT_ID, ROOM_NO, TIME_ID, DURATION_HRS, SUR_DATE)
        VALUES (:appnt_serial_no, :inchargeDocID, :patient_id, :room_no, :timeID, :duration, TO_DATE(:selectedDate, 'DD/MM/YYYY'));

        SELECT MAX(SUR_SCHE_NO) INTO ID FROM SURGERY_SCHEDULE;


        UPDATE SURGERY_RESULTS SET COMPLETED = 'A', SUR_SCHE_NO = ID
        WHERE SURGERY_RESULT_ID = :surgery_result_id;
    END;
    '''
    # try (try-catch) block
    cursor.execute(query, [appnt_serial_no, inchargeDocID,
                           patient_id, room_no, timeID, duration, selectedDate, surgery_result_id])
    connection.commit()

    return {'success': True, 'message': "Surgery Schedule Added Successfully"}


def getPatientDetails(patientID):
    connection = connect()
    cursor = connection.cursor()
    query = '''SELECT (FIRST_NAME||' '||LAST_NAME) AS pNAME, EMAIL AS pEMAIL, PHONE_NUM AS pPHONE, GENDER AS pGENDER, 
            (ROUND(MONTHS_BETWEEN(SYSDATE, DATE_OF_BIRTH)/12)||' years '||FLOOR(MOD(MONTHS_BETWEEN(SYSDATE, DATE_OF_BIRTH), 12))||' months') as pAGE,
            ID AS pID FROM PERSON 
            WHERE USER_ID = (:patientID)'''
    # print(query, patientID)
    cursor.execute(query, [patientID])
    resultTemp = cursor.fetchall()
    cursor.close()
    # print(resultTemp)

    result = {
        'patientData': {
            'name': resultTemp[0][0],
            'email': resultTemp[0][1],
            'phone': resultTemp[0][2],
            'gender': "Male" if resultTemp[0][3] == "M" else "Female",
            'age': resultTemp[0][4],
            'id': resultTemp[0][5]
        },
        'success': True,
    }

    return result


def getAdmitRoomList(ward, roomType):
    connection = connect()
    cursor = connection.cursor()
    query = '''SELECT R.ROOM_NO, R.TYPE, R.CHARGE FROM ROOM R, BLOCK B
                WHERE R.BLOCK_ID = B.BLOCK_ID AND
                R.TYPE = (:roomType) AND
                B.CATEGORY = (:ward) AND 
                R.ROOM_NO NOT IN (
                SELECT RA.ROOM_NO
                FROM ROOM_ADMISSION RA
                GROUP BY(RA.ROOM_NO)
                HAVING COUNT(RA.ROOM_NO) =
                (SELECT R.NO_OF_BEDS FROM ROOM R
                WHERE R.ROOM_NO = RA.ROOM_NO))'''
    cursor.execute(query, [roomType, ward])
    resultTemp = cursor.fetchall()
    cursor.close()
    roomData = []
    for R in resultTemp:
        roomData.append({
            'room_no': R[0],
            'room_type': R[1],
            'charge': R[2],
        })
    result = {
        'roomData': roomData,
        'alertMesage': "Okay",
        'success': True
    }
    return result


def getRoomTypesForWard(ward):
    connection = connect()
    cursor = connection.cursor()
    query = '''SELECT DISTINCT(R.TYPE) FROM ROOM R, BLOCK B
            WHERE R.BLOCK_ID = B.BLOCK_ID AND B.CATEGORY = (:ward)'''
    cursor.execute(query, [ward])
    resultTemp = cursor.fetchall()
    cursor.close()
    roomTypes = []
    for R in resultTemp:
        roomTypes.append({
            'room_type': R[0],
        })
    result = {
        'roomTypes': roomTypes,
        'alertMesage': "Okay",
        'success': True
    }
    return result


def admitPatient(patientID, room_no, admission_date):
    connection = connect()
    cursor = connection.cursor()
    query = '''SELECT ROOM_NO FROM ROOM_ADMISSION
                WHERE PATIENT_ID = (select ID from Person where USER_ID = (:patientID)) AND RELEASE_DATE IS NULL AND 
								ROOM_NO NOT IN (SELECT R.ROOM_NO FROM ROOM R JOIN BLOCK B ON R.BLOCK_ID = B.BLOCK_ID AND B.CATEGORY = 'SURGERY')'''
    cursor.execute(query, [patientID])
    resultTemp = cursor.fetchall()
    if len(resultTemp) > 0:
        return {'success': True, 'alertMessage': "Error in Insertion. Patient Already Admitted!"}
    query = '''INSERT INTO ROOM_ADMISSION(PATIENT_ID, ROOM_NO, ADMISSION_DATE, PAID)
                VALUES ((select ID from Person where USER_ID = (:patientID)), :room_no, TO_DATE(:admission_date, 'DD/MM/YYYY'), 'F')'''
    cursor.execute(query, [patientID, room_no, admission_date])
    connection.commit()
    cursor.close()
    return {'success': True, 'alertMessage': "Patient Successfully Admitted"}


def getUserDetails(UserID):
    connection = connect()
    cursor = connection.cursor()
    if 'E' in UserID:
        query = '''SELECT (P.FIRST_NAME||' '||P.LAST_NAME), P.EMAIL, P.PHONE_NUM, P.GENDER, P.ADDRESS,  
	            (ROUND(MONTHS_BETWEEN(SYSDATE, P.DATE_OF_BIRTH)/12)||' years '||FLOOR(MOD(MONTHS_BETWEEN(SYSDATE, P.DATE_OF_BIRTH), 12))||' months') as AGE,
	            E.CATEGORY, E.TRAINING FROM PERSON P JOIN EMPLOYEE E ON P.ID = E.ID AND P.USER_ID = :userID'''
        cursor.execute(query)
        resultTemp = cursor.fetchall()
        cursor.close()
        return {'userData': {
            {'title': 'Name', 'value': resultTemp[0][0]},
            {'title': 'Email', 'value': resultTemp[0][1]},
            {'title': 'Phone Number', 'value': resultTemp[0][2]},
            {'title': 'Gender',
                'value': "Male" if resultTemp[0][3] == 'M' else "Female"},
            {'title': 'Address', 'value': resultTemp[0][4]},
            {'title': 'Age', 'value': resultTemp[0][5]},
            {'title': 'Category', 'value': resultTemp[0][6]},
            {'title': 'Training', 'value': resultTemp[0][7]}, },
            'success': True,
        }
    elif 'D' in UserID:
        query = '''SELECT (P.FIRST_NAME||' '||P.LAST_NAME), P.EMAIL, P.PHONE_NUM, P.GENDER, P.ADDRESS,
	        (ROUND(MONTHS_BETWEEN(SYSDATE, P.DATE_OF_BIRTH)/12)||' years '||FLOOR(MOD(MONTHS_BETWEEN(SYSDATE, P.DATE_OF_BIRTH), 12))||' months') as AGE,
	        D.DEPARTMENT, D.QUALIFICATION FROM PERSON P JOIN DOCTOR D ON P.ID = D.ID AND P.USER_ID = :userID'''
        cursor.execute(query)
        resultTemp = cursor.fetchall()
        cursor.close()
        return {{'userData': {
            {'title': 'Name', 'value': resultTemp[0][0]},
            {'title': 'Email', 'value': resultTemp[0][1]},
            {'title': 'Phone Number', 'value': resultTemp[0][2]},
            {'title': 'Gender',
                'value': "Male" if resultTemp[0][3] == 'M' else "Female"},
            {'title': 'Address', 'value': resultTemp[0][4]},
            {'title': 'Age', 'value': resultTemp[0][5]},
            {'title': 'Department', 'value': resultTemp[0][6]},
            {'title': 'Qualification', 'value': resultTemp[0][7]}, },
            'success': True,
        }}
    else:
        cursor.close()
        return {'success': False, 'alertMessage': "User Id does not belong to appropiate category"}


def getBlocksPerCategory(block_category):
    connection = connect()
    cursor = connection.cursor()
    query = '''SELECT BLOCK_ID FROM BLOCK WHERE CATEGORY=(:block_category)'''
    try:
        cursor.execute(query, [block_category])
        resultTemp = cursor.fetchall()
        cursor.close()
        roomTypes = []
        for R in resultTemp:
            roomTypes.append({
                'block_id': R[0],
            })
        result = {
            'blocks': roomTypes,
            'alertMesage': "Okay",
            'success': True
        }
        return result
    except cx_Oracle.Error as err:
        result = {
            'success': False,
            'alertMessage': err
        }
        return result


def addIncharge(block_id, inChargeUserID):
    connection = connect()
    cursor = connection.cursor()
    query_pre = '''SELECT ID FROM PERSON WHERE USER_ID=(:inChargeUserID)'''
    query = '''UPDATE BLOCK SET INCHARGE_ID = (SELECT ID FROM PERSON WHERE USER_ID = (:inChargeUserID)) WHERE BLOCK_ID = (:block_id)'''
    try:
        cursor.execute(query_pre, [inChargeUserID])
        result = cursor.fetchall()
        if len(result) == 0:
            return {
                'success': False,
                'alertMessage': 'User ID invalid'
            }
        else:
            cursor.execute(query, [inChargeUserID, block_id])
            connection.commit()
            cursor.close()
            result = {
                'alertMessage': "Incharge for Block Successfully Registered",
                'success': True
            }
            return result
    except cx_Oracle.Error as err:
        result = {
            'success': False,
            'alertMessage': err
        }
        return result


def scheduleHisEmp(employeeID):
    connection = connect()
    cursor = connection.cursor()

    response = {}
    query = '''SELECT TO_CHAR(SCH.SCHEDULE_DATE, 'DD/MM/YYYY') AS WORKING_DAY, T.SHIFT_TITLE AS CATEGORY, 
                T.START_TIME, T.END_TIME, B.CATEGORY AS WARD
                FROM SCHEDULE SCH JOIN TIME_TABLE T ON (SCH.TIME_ID = T.TIME_ID 
                AND SCH.ID = (SELECT ID FROM PERSON WHERE USER_ID = (:employeeID))
                AND SCH.SCHEDULE_DATE<SYSDATE)
                JOIN BLOCK B ON B.BLOCK_ID =SCH.BLOCK_ID
                ORDER BY SCH.SCHEDULE_DATE DESC'''

    try:
        cursor.execute(query, [employeeID])
        resultTemp = cursor.fetchall()
        cursor.close()

        headers = [["Working Date", "Time Shift", "Start Time(24 H)", "End Time(24 H)", "Ward"]]
        result = []
        for R in resultTemp:
            result_row = []
            for elements in R:
                result_row.append(elements)
            result.append(result_row)
        
        response['tableData'] = result
        response['tableHeader'] = headers
        response['success'] = True
        return response
    except cx_Oracle.Error as error:
        errorObj, = error.args
        response = {'success': False, 'alertMessage': errorObj.message}
        return response


def scheduleOnWardDate(wardCategory, sch_on_date):
    connection = connect()
    cursor = connection.cursor()
    response = {}
    query = '''SELECT SCH.SCHEDULE_ID, (P.FIRST_NAME||' '||P.LAST_NAME) AS NAME, EMPLOYEE_TYPE(P.USER_ID) AS ROLE, 
                (SELECT SHIFT_TITLE FROM TIME_TABLE WHERE TIME_ID = SCH.TIME_ID) AS SHIFT, SCH.BLOCK_ID
                FROM PERSON P JOIN SCHEDULE SCH ON (
                SCH.SCHEDULE_DATE = TO_DATE(:sch_on_date, 'DD/MM/YYYY') AND
                P.ID = SCH.ID AND 
                SCH.BLOCK_ID IN (SELECT BLOCK_ID FROM BLOCK WHERE CATEGORY=(:wardCategory)))
                ORDER BY SCH.SCHEDULE_ID DESC'''

    try:
        # cursor.execute(query, [sch_on_date, wardCategory])
        cursor.execute(query, [sch_on_date, wardCategory])
        resultTemp = cursor.fetchall()
        cursor.close()

        headers = [["Schedule ID", "Name", "Category", "Shift", "Block ID"]]
        result = []
        for R in resultTemp:
            result_row = []
            for elements in R:
                result_row.append(elements)
            result.append(result_row)
        
        response['tableData'] = result
        response['tableHeader'] = headers
        response['success'] = True
        return response
    except cx_Oracle.Error as error:
        response = {'success': False, 'alertMessage': "Failed"}
        return response


def getUserSchedule(data):
    connection = connect()
    cursor = connection.cursor()
    try:
        query = '''
        SELECT S.SCHEDULE_ID, TO_CHAR(S.SCHEDULE_DATE), T.START_TIME, T.END_TIME, T.SHIFT_TITLE 
        FROM SCHEDULE S JOIN TIME_TABLE T ON(S.TIME_ID = T.TIME_ID)
        WHERE S.ID = (SELECT ID FROM PERSON WHERE USER_ID = :userID)
        AND S.SCHEDULE_DATE >= SYSDATE
        '''

        cursor.execute(query, [data['userID']])
        result = cursor.fetchall()

        schedules = []

        for schedule in result:
            schedules.append({'schedule_id': schedule[0], 'schedule_date': schedule[1], 'start_time': schedule[2],
                              'end_time': schedule[3], 'shift_title': schedule[4]})
        response = {'success': True,
                    'errorMessage': '', 'schedules': schedules}
        print(response)
        return response

    except cx_Oracle.Error as error:
        errorObj, = error.args
        response = {'success': False, 'errorMessage': errorObj.message}
        print(response)
        return response


def getWardDetailsDisp(blockID):
    connection = connect()
    cursor = connection.cursor()
    try:
        query = '''SELECT P.ID, P.USER_ID FROM BLOCK B JOIN PERSON P ON 
                    (B.BLOCK_ID = (:blockID) AND B.INCHARGE_ID = P.ID)'''

        cursor.execute(query, [blockID])
        result = cursor.fetchall()
        print(result, blockID)
        if (len(result) != 0):
            actual_id = result[0][0]
            user_id = result[0][1]
            if "D" in user_id:
                query = '''SELECT (P.FIRST_NAME||' '||P.LAST_NAME) AS NAME, P.EMAIL, P.PHONE_NUM, P.ADDRESS, 
                        (ROUND(MONTHS_BETWEEN(SYSDATE, P.DATE_OF_BIRTH)/12)||' years '||FLOOR(MOD(MONTHS_BETWEEN(SYSDATE, P.DATE_OF_BIRTH), 12))||' months') as AGE,
                        D.DEPARTMENT, D.DESIGNATION, D.QUALIFICATION FROM PERSON P JOIN DOCTOR D ON
                        (P.ID = D.ID AND P.ID = :actual_id)'''
            else:
                query = '''SELECT (P.FIRST_NAME||' '||P.LAST_NAME) AS NAME, P.EMAIL, P.PHONE_NUM, P.ADDRESS, 
                            (ROUND(MONTHS_BETWEEN(SYSDATE, P.DATE_OF_BIRTH)/12)||' years '||FLOOR(MOD(MONTHS_BETWEEN(SYSDATE, P.DATE_OF_BIRTH), 12))||' months') as AGE,
                            E.CATEGORY, E.EDUCATION, E.TRAINING FROM PERSON P JOIN EMPLOYEE E
                            ON (P.ID = E.ID AND P.ID = :actual_id)'''
            cursor.execute(query, [actual_id])
            result = cursor.fetchall()
            inchargeInfo = {
                'name': result[0][0],
                'email': result[0][1],
                'phn': result[0][2],
                'address': result[0][3],
                'age': result[0][4],
            }
            if "D" in user_id:
                inchargeInfo['department'] = result[0][5]
                inchargeInfo['designation'] = result[0][6]
                inchargeInfo['qualification'] = result[0][7]
                inchargeInfo['type'] = "doctor"
            else:
                inchargeInfo['category'] = result[0][5]
                inchargeInfo['education'] = result[0][6]
                inchargeInfo['training'] = result[0][7]
                inchargeInfo['type'] = "employee"
        else:
            inchargeInfo = {}
        # all employees in this ward today
        query = '''SELECT (P.FIRST_NAME||' '||P.LAST_NAME) AS NAME, P.EMAIL, P.PHONE_NUM, D.DESIGNATION AS CATEGORY
                    FROM PERSON P JOIN DOCTOR D ON (P.ID = D.ID)
                    JOIN SCHEDULE SCH ON (SCH.ID = P.ID AND SCH.BLOCK_ID = (:blockID) AND SCH.SCHEDULE_DATE = TRUNC(SYSDATE))
                    UNION
                    SELECT (P.FIRST_NAME||' '||P.LAST_NAME) AS NAME, P.EMAIL, P.PHONE_NUM, E.CATEGORY AS CATEGORY
                    FROM PERSON P JOIN EMPLOYEE E ON (P.ID = E.ID)
                    JOIN SCHEDULE SCH ON (SCH.ID = P.ID AND SCH.BLOCK_ID = (:blockID) AND SCH.SCHEDULE_DATE = TRUNC(SYSDATE))'''
        cursor.execute(query, [blockID])
        result = cursor.fetchall()
        # print(result)
        employeeInWard = []
        for R in result:
            result_row = []
            for elem in R:
                result_row.append(elem)
            employeeInWard.append(result_row)
        employeeHeader = [["Name", "Email", "Phone Number", "Category"]]
            
        # all patients in this ward
        query = '''SELECT (SELECT (FIRST_NAME||' '||LAST_NAME) FROM PERSON WHERE ID= RA.PATIENT_ID), 
                (SELECT USER_ID FROM PERSON WHERE ID= RA.PATIENT_ID),
                TO_CHAR(RA.ADMISSION_DATE, 'DD/MM/YYYY') FROM ROOM_ADMISSION RA JOIN
                ROOM R ON (R.ROOM_NO = RA.ROOM_NO AND RA.RELEASE_DATE IS NULL) JOIN BLOCK B
                ON (B.BLOCK_ID = R.BLOCK_ID AND B.BLOCK_ID = :blockID)'''
        cursor.execute(query, [blockID])
        result = cursor.fetchall()

        patientInWard = []
        for R in result:
            result_row = []
            for elem in R:
                result_row.append(elem)
            patientInWard.append(result_row)
        patientHeader = [["Name", "Patient ID", "Admission Date"]]
        
        response = {}
        response['patientInWard'] = patientInWard
        response['employeeInWard'] = employeeInWard
        response['employeeHeader'] = employeeHeader
        response['patientHeader'] = patientHeader
        response['inchargeInfo'] = inchargeInfo
        response['success'] = True
        response['switch9'] = True
        return response

    except cx_Oracle.Error as error:
        errorObj, = error.args
        print(error)
        response = {'success': False, 'errorMessage': errorObj.message}
        return response