import mysql.connector
import time
from flask import Flask, jsonify, request
from http.server import HTTPServer, BaseHTTPRequestHandler
from zeep import Client
from waitress import serve

app = Flask(__name__,
	static_url_path='',
	static_folder='web/static',
	template_folder='web/templates')

def get_mysql_connector():
    #print("Attempting to get mysql connector")
    #print(dir(mysql))
    #print(dir(mysql.connector))
    try:
        connection = mysql.connector.connect(user='admin', password='vuhKYP7W8b50bDEH6QR3', host='database-1.cm7we8q8gs13.us-east-1.rds.amazonaws.com', database='medvoice')
        return connection
    except mysql.connector.Error as err:
        print(err)
    return None

@app.route("/api/flowHistory", methods = ['GET', 'POST'])
def flowHistory():
    try:
        connection = get_mysql_connector()
        cursor = connection.cursor()
        if request.method == 'GET':
            print("Flow history GET received")
            query = "SELECT * FROM flowHistory;"
            cursor.execute(query)
            logreturn = cursor.fetchall()
            return jsonify(logreturn)
        if request.method == 'POST':
            print("Flow history post received")
            patientId = request.form.get("patientId")
            flowId = request.form.get("flowId")
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            query = "INSERT INTO flowHistory (patientId, videoId, timestamp) VALUES ("
            query += "'" + patientId + "',"
            query += "'" + flowId + "',"
            query += "'" + timestamp + "'"
            query += ");"
            print(query)
            cursor.execute(query)
            connection.commit()
            logreturn = cursor.fetchall()
            return jsonify(logreturn)
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        if connection:
            connection.close()
            cursor.close()

@app.route("/api/analyzerlog", methods = ['GET', 'POST'])
def analyzerlog():
    try:
        connection = get_mysql_connector()
        cursor = connection.cursor()
        if request.method == 'GET':
            print("Analyzer log get received")
            query = "SELECT * FROM analyzerlog;"
            cursor.execute(query)
            #connection.commit()
            logreturn = cursor.fetchall()
            return jsonify(logreturn)
        if request.method == 'POST':
            print("Analyzer log post received")
            input_question = request.form.get("input_question")
            case_name = request.form.get("case_name")
            response = request.form.get("response")
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            query = "INSERT INTO analyzerlog (timestamp, input_question, case_name, response) VALUES ("
            query += "'" + timestamp + "',"
            query += "'" + input_question + "',"
            query += "'" + case_name + "',"
            query += "'" + response + "'"
            query += ");"
            cursor.execute(query)
            connection.commit()
            logreturn = cursor.fetchall()
            return jsonify(logreturn)

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        if connection:
            connection.close()
            cursor.close()

@app.route("/api/patientlist", methods = ['GET'])
def patientlist():
    try:
        connection = get_mysql_connector()
        cursor = connection.cursor()

        if request.method == 'GET':
            query = "select patients.firstName, patients.lastname, patients.id, patients.birthday,"\
            "patientreadings.pulseOxVal, patientreadings.bpmVal, patientreadings.timestamp as readingtimestamp, "\
            "patientsymptoms.symptoms, patientsymptoms.timestamp as symptomtimestamp, "\
            "colorCodeHistory.color, patients.medicalProvisioner, patients.medicalConditions "\
            "from patients "\
            "left outer join patientreadings on patientreadings.patientid = patients.id "\
            "left outer join patientsymptoms on patientsymptoms.patientid = patients.id "\
            "left outer join colorCodeHistory on colorCodeHistory.patientid = patients.id"
            "order by readingtimestamp desc;"
            cursor.execute(query)

            patients_data = cursor.fetchall()
            retval = []
            usedids = []
            #filter for latest entry only per id
            for entry in patients_data:
                if (entry[2] not in usedids):
                    usedids.append(entry[2])
                    retval.append(entry)
                    return jsonify(retval)
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        if connection:
            connection.close()
            cursor.close()

@app.route("/api/patientdetail/<patient_id>", methods = ['GET'])
def patientdetail(patient_id):
    try:
        connection = get_mysql_connector()
        cursor = connection.cursor()

        if request.method == 'GET':
            query = "select patients.firstName, patients.lastname, patients.id, patients.birthday, patients.medicalprovisioner, "\
            "patients.medicalconditions,"\
            "patientreadings.pulseOxVal, patientreadings.bpmVal, patientreadings.timestamp as readingtimestamp, "\
            "patientsymptoms.symptoms, patientsymptoms.timestamp as symptomtimestamp "\
            "from patients "\
            "left outer join patientreadings on patientreadings.patientid = patients.id "\
            "left outer join patientsymptoms on patientsymptoms.patientid = patients.id "\
            "where patients.id = " + patient_id + " "\
            "order by readingtimestamp desc;"
            cursor.execute(query)

            patients_data = cursor.fetchall()
            return jsonify(patients_data)
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        if connection:
            connection.close()
            cursor.close()

@app.route("/api/patients", methods = ['GET', 'POST'])
def patients():
    try:
        connection = get_mysql_connector()
        cursor = connection.cursor()

        if request.method == 'GET':
            query = "SELECT * FROM patients"
            cursor.execute(query)

            patients_data = cursor.fetchall()
            return jsonify(patients_data)
        if request.method == 'POST':
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            firstName = request.form.get('firstname')
            lastName = request.form.get('lastname')
            birthday = request.form.get('birthday')
            email = request.form.get('email')

            print(request.form)
            query = "INSERT INTO patients (timestamp, pulseOxVal, bpmVal, patientid) VALUES ("
            query += "'" + timestamp + "',"
            query += ");"
            cursor.execute(query)
            connection.commit()
            colorcodes = cursor.fetchall()
            return jsonify(colorcodes)

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        if connection:
            connection.close()
            cursor.close()

@app.route("/api/patient/<patient_id>", methods = ['POST'])
def modPatient(patient_id):
    try:
        connection = get_mysql_connector()
        cursor = connection.cursor()

        if request.method == 'POST':
            query = "SELECT * FROM patients"
            cursor.execute(query)

            patients_data = cursor.fetchall()
            return jsonify(patients_data)

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        if connection:
            connection.close()
            cursor.close()

@app.route("/api/patientreadings", methods = ['GET', 'POST'])
def patientreadings():
    try:
        connection = get_mysql_connector()
        cursor = connection.cursor()
        if request.method == 'GET':
            query = "SELECT * FROM patientreadings"
            cursor.execute(query)
            patientreadings_data = cursor.fetchall()
            return jsonify(patientreadings_data)
        if request.method == 'POST':
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            print("POST RECEIVED")
            pulseOxVal = request.form.get('pulseoxval')
            bpmVal = request.form.get('bpmval')
            patientid = request.form.get('patientid')
            print(request.form)
            query = "INSERT INTO patientreadings (timestamp, pulseOxVal, bpmVal, patientid) VALUES ("
            query += "'" + timestamp + "',"
            query += "'" + pulseOxVal + "',"
            query += "'" + bpmVal + "',"
            query += "'" + patientid + "'"
            query += ");"
            cursor.execute(query)
            connection.commit()
            colorcodes = cursor.fetchall()
            print("WE GOOD")
            return jsonify(colorcodes)

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        if connection:
            connection.close()
            cursor.close()

@app.route("/api/patientsymptoms", methods = ['GET', 'POST'])
def patientsymptoms():
    try:
        connection = get_mysql_connector()
        cursor = connection.cursor()
        if request.method == 'GET':
	        query = "SELECT * FROM patientsymptoms"
        	cursor.execute(query)

       		patientsymptoms = cursor.fetchall()
        	return jsonify(patientsymptoms)

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        if connection:
            connection.close()
            cursor.close()

@app.route("/api/colorcodes", methods = ['GET', 'POST'])
def colorcodes():
    try:
        connection = get_mysql_connector()
        cursor = connection.cursor()
        if request.method == 'GET':
            query = "SELECT * FROM colorCodeHistory"
            cursor.execute(query)
            colorcodes = cursor.fetchall()
            return jsonify(colorcodes)
        if request.method == 'POST':
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            color = request.form.get('color')
            criteria = request.form.get('criteria')
            patientid = request.form.get('patientid')
            query = "INSERT INTO colorCodeHistory (timestamp, color, criteria, patientid) VALUES ("
            query += "'" + timestamp + "',"
            query += "'" + color + "',"
            query += "'" + criteria + "',"
            query += "'" + patientid + "'"
            query += ");"
            cursor.execute(query)
            connection.commit()
            colorcodes = cursor.fetchall()
            return jsonify(colorcodes)

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        if connection:
            connection.close()
            cursor.close()

@app.route("/api/analyzer", methods = ['POST'])
def analyzer():
    try:
        wsdl_url = 'http://prod-analyzer.medrespond.net/MedRespond/SIAnalyzer3_mv3190/MedRespond.SIAnalyzer.asmx?WSDL'
        client = Client(wsdl_url)
        input_question = request.form.get('input_question')
        case_name = request.form.get('case_name')
        log(f"Question: {input_question}")
        log(f"Case: {case_name}")
        result = client.service.getQuestionResponses(SessionID=1234, CaseName=case_name, InputQuestion=input_question)
        log(f"Response: {result}")
        logAnalyze(input_question, case_name, result['ResponseIDs']['string'][0])
        return result['ResponseIDs']['string'][0]
    except Exception as e:
        print(f"Error calling SOAP service: {e}")
        return None
@app.route("/api/test", methods = ['GET', 'POST'])
def test():
    try:
        #connection = get_mysql_connector()
        #cursor = connection.cursor()
        if request.method == 'GET':
            print("Test Received")
            return "Success"
        else:
            print(request)
            print(request.form)
            test_value = request.form.get('test')
            print(f"Value: {test_value}")
            return "Success"
    except Exception as e:
        print(f"Failed to run test route")
        return None

@app.route("/api/deviceids", methods = ['GET'])
def deviceid():
    print("Got deviceid call")
    try:
        print("1")
        connection = get_mysql_connector()
        print("2")
        cursor = connection.cursor()
        if request.method == 'GET':
            print("Get received")
            query = "SELECT * FROM deviceInfo"
            cursor.execute(query)
            deviceids = cursor.fetchall()
            return jsonify(deviceids)
        else:
            print("Post received")
            query = "INSERT INTO deviceInfo(deviceid) VALUES ('Test')";
            cursor.execute(query)
            connection.commit()
            deviceids = cursor.fetchall()
            return jsonify(deviceids)
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        if connection:
            connection.close()
            cursor.close()

@app.route("/api/deviceids/<device_id>", methods = ['GET', 'POST'])
def deviceids(device_id):
    try:
        connection = get_mysql_connector()
        cursor = connection.cursor()
        if request.method == 'GET':
            query = "SELECT COUNT(*), id FROM deviceInfo WHERE deviceid = '"
            query += device_id
            query += "';"
            print(query)
            cursor.execute(query)
            devicelist = cursor.fetchall()
            return jsonify(devicelist)
        else:
            query = "INSERT INTO deviceInfo(deviceid) VALUES ('"
            query += device_id
            query += "');"
            print(query)
            cursor.execute(query)
            connection.commit()
            devicelist = cursor.fetchall()
            return jsonify(devicelist)
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        if connection:
            connection.close()
            cursor.close()

def log(text):
    print(text)
    with open("logfile.txt", "a") as f:
        f.write(text)    

def logAnalyze(input, case, response):
    print(input)
    print(case)
    print(response)
    try:
        connection = get_mysql_connector()
        cursor = connection.cursor()
        query = "INSERT INTO analyzerlog(timestamp, input_question, case_name, response) VALUES('"
        query += time.strftime('%Y-%m-%d %H:%M:%S') + "',"
        query += "'" + input + "',"
        query += "'" + case + "',"
        print("Problem zone")
        query += "'" + response + "');"
        print("success")
        print(query)
        cursor.execute(query)
        connection.commit()
        print("complete")
        return jsonify("Log complete")
    except mysql.connector.Error as err:
        print("Exception")
        print(str(err))
        return jsonify({"error": str(err)}), 500
    finally:
        if connection:
            connection.close()
            cursor.close()

if __name__ == "__main__":
    print("Running application...")
    #app.run(debug=True)
    
    serve(app, port=22099)
