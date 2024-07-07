from flask import Flask,request,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app =Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///school.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db =SQLAlchemy(app)
migrate =Migrate(app,db)

class Manager(db.Model):
    id =db.Column(db.Integer ,primary_key =True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    employee =db.relationship("Employee",backref ="manager",lazy =True)

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key =True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    job_title =db.Column(db.String(100))
    manager_id =db.Column(db.Integer,db.ForeignKey('manager.id'),nullable =False)


# managers routes

@app.route("/managers", methods =['Get'])
def get_managers():
    managers =Manager.query.all()
    return jsonify([{"id":manager.id,"first_name":manager.first_name,"last_name":manager.last_name}for manager in managers])


# @app.route("/managers", methods =["POST"])
# def create_manager():
#     data = request.get_json()
#     manager = Manager(

#         first_name = data["first_name"],
#         last_name = data["last_name"])

#     db.session.add(manager)
#     db.session.commit()
#     return jsonify({"message":"Manager created successfully"}),201


@app.route("/managers", methods=["POST"])
def create_manager():
    if not request.is_json:
        return jsonify({"message": "Request must be JSON"}), 400

    data = request.get_json()
    if not data:
        return jsonify({"message": "No input data provided"}), 400

    try:
        first_name = data["first_name"]
        last_name = data["last_name"]
    except KeyError as e:
        return jsonify({"message": f"Missing key: {str(e)}"}), 400

    new_manager = Manager(first_name=first_name, last_name=last_name)

    try:
        db.session.add(new_manager)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error creating manager: {str(e)}"}), 500

    return jsonify({"message": "Manager created successfully"}), 201

@app.route("/managers/<int:id>",methods =['GET'])
def get_manager(id):
    manager =Manager.query.get(id)
    if not manager:
        return jsonify({"message": "Manager not found"}), 404
    
    # manager =Manager.query.filter_by(id ==id).first()
    return jsonify({"id":manager.id,"first_name": manager.first_name,"last_name": manager.last_name})

@app.route('/managers/<int:id>',methods =['PUT'])
def update_manager(id):
    data =request.get_json()
    manager =Manager.query.get(id)
    if not manager:
        return jsonify({'message':'Manager not found'}),404
    manager.first_name = data["first_name"]
    manager.last_name = data["first_name"]
    
    db.session.commit()
    return jsonify({'message':'Manager updated successfully'})

@app.route('/managers/<int:id>' ,methods =['DELETE'])
def delete_manager(id):
    manager =Manager.query.get(id)
    if not manager:
        return jsonify({'message' : "Manager not found"}),404
    db.session.delete(manager)
    db.session.commit()
    return jsonify({'Message':'Manager deleted successfull'})

@app.route('/managers/<int:id>/employees' ,methods =['GET'])
def get_manager_employees(id):
    manager =Manager.query.get(id)
    if not manager: 
        return jsonify({"Manager not found"}),404
    employees =Employee.query.filter_by(manager_id =id).all()
    return jsonify([{"id":employee.id,"first_name":employee.first_name,"last_name":employee.last_name,"job_title":employee.job_title} for employee in employees])


# employee routes
@app.route('/employees',methods =['GET'])
def get_students():
    employees = Employee.query.all()
    return jsonify(
        [
            {
                "id": employee.id,
                "first_name": employee.first_name,
                "last_name": employee.last_name,
                "manager_id": employee.manager_id,
                "job_title": employee.job_title
            }
            for employee in employees
        ]
    )


@app.route('/employees/<int:id>', methods = ['GET'])
def get_employee(id):
    employee =Employee.query.get(id)
    if not employee:
        return jsonify({"message": "Employee not found"}), 404
    return jsonify(
        [
            {
                "id": employee.id,
                "first_name": employee.first_name,
                "last_name": employee.last_name,
                "manager_id": employee.manager_id,
                "job_title": employee.job_title
            }
        ]
    )

@app.route('/employees' ,methods =['POST'])
def create_student():
    data = request.get_json()
    employee = Employee(
        first_name = data["first_name"],
        last_name = data["last_name"],
        job_title = data["job_title"],
        manager_id = data["manager_id"])

    db.session.add(employee)
    db.session.commit()
    return jsonify({"message":"Employee created successfully"}),201

@app.route('/employee/<int:id>',methods =['PUT'])
def update_student(id):
    data=request.get_json()
    employee = Employee.query.get(id)
    if not employee:
        return jsonify({"message": "Employee not found"}), 404
    employee.first_name = data['first_name']
    employee.last_name = data['last_name']
    employee.job_title = data["job_title"]
    employee.manager_id = data["manager_id"]
    
    db.session.commit()
    return jsonify({"message":"Employee updated successfully"})

@app.route('/employees/<int:id>' ,methods =['DELETE'])
def delete_employee(id):
    employee =Employee.query.get(id)
    if not employee:
        return jsonify({'message' : "employee not found"}),404
    db.session.delete(employee)
    db.session.commit()
    return jsonify({'Message':'Employee deleted successfully'})

@app.route('/employees/<int:id>/manager' ,methods =['GET'])
def get_employee_manager(id):
    employee =Employee.query.get(id)
    if not employee: 
        return jsonify({"Student not found"}),404
    manager =Manager.query.get(employee.manager_id )
    return jsonify([{"id":manager.id,"first_name":manager.first_name,"last_name":manager.last_name}])

if __name__ == "__main__":
    app.run(debug=True)
