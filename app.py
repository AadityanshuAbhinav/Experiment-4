import os
from flask import Flask, request, jsonify
from flask_restful import Api, Resource, reqparse, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
import werkzeug
from flask import abort

current_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(current_dir, "api_database.sqlite3") 
db = SQLAlchemy(app)
api = Api(app)

class Course(db.Model):
    __tablename__ = 'course'
    course_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_name = db.Column(db.String, nullable=False)
    course_code = db.Column(db.String, unique=True, nullable=False)
    course_description = db.Column(db.String)

class Student(db.Model):
    __tablename__ = 'student'
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    roll_number = db.Column(db.String, unique=True, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String)

class Enrollment(db.Model):
    __tablename__ = 'enrollment'
    enrollment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.course_id'), nullable=False)

class CourseResource(Resource):
    def get(self, course_id):
        course = Course.query.get(course_id)
        if course:
            return {
                'course_id': course.course_id,
                'course_name': course.course_name,
                'course_code': course.course_code,
                'course_description': course.course_description
            }
        else:
            return {'message': 'Course not found'}, 404

    def put(self, course_id):
        parser = reqparse.RequestParser()
        parser.add_argument('course_name', type=str, required=True)
        parser.add_argument('course_code', type=str, required=True)
        parser.add_argument('course_description', type=str)
        args = parser.parse_args()

        course = Course.query.get(course_id)
        if course:
            course.course_name = args['course_name']
            course.course_code = args['course_code']
            course.course_description = args['course_description']
            db.session.commit()
            return {
                'course_id': course.course_id,
                'course_name': course.course_name,
                'course_code': course.course_code,
                'course_description': course.course_description
            }
        else:
            return {'message': 'Course not found'}, 404

    def delete(self, course_id):
        course = Course.query.get(course_id)
        if course:
            db.session.delete(course)
            db.session.commit()
            return {'message': 'Successfully Deleted'}
        else:
            return {'message': 'Course not found'}, 404

api.add_resource(CourseResource, '/api/course/<int:course_id>')

class CourseListResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('course_name', type=str, required=True, help='Course Name is required')
        parser.add_argument('course_code', type=str, required=True, help='Course Code is required')
        parser.add_argument('course_description', type=str)
        args = parser.parse_args()

        # Check if the course_code is provided
        if not args['course_code']:
            return {'error_code': 'COURSE002', 'error_message': 'Course Code is required'}, 400

        # Check if the course_code already exists
        existing_course = Course.query.filter_by(course_code=args['course_code']).first()
        if existing_course:
            return {'error_message': 'Course Code already exists'}, 409

        course = Course(course_name=args['course_name'], course_code=args['course_code'], course_description=args['course_description'])
        db.session.add(course)

        try:
            db.session.commit()
            return {
                'course_id': course.course_id,
                'course_name': course.course_name,
                'course_code': course.course_code,
                'course_description': course.course_description
            }, 201
        except Exception as e:
            db.session.rollback()
            return {'error_code': 'COURSE001', 'error_message': 'Course Name is required'}, 400

api.add_resource(CourseListResource, '/api/course')

class StudentResource(Resource):
    def get(self, student_id):
        student = Student.query.get(student_id)
        if student:
            return {
                'student_id': student.student_id,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'roll_number': student.roll_number,            
            }
        else:
            return {'message': 'Student not found'}, 404
        
    def put(self, student_id):
        parser = reqparse.RequestParser()
        parser.add_argument('first_name', type=str, required=True)
        parser.add_argument('last_name', type=str, required=True)
        parser.add_argument('roll_number', type=str)
        args = parser.parse_args()

        student = Student.query.get(student_id)
        if student:
            student.first_name = args['first_name']
            student.last_name = args['last_name']
            student.roll_number = args['roll_number']
            db.session.commit()
            return {
                'student_id': student.student_id,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'roll_number': student.roll_number
            }
        else:
            return {'message': 'Student not found'}, 404
        
    def delete(self, student_id):
        student = Student.query.get(student_id)
        if student:
            db.session.delete(student)
            db.session.commit()
            return {'message': 'Successfully Deleted'}
        else:
            return {'message': 'Student not found'}, 404

api.add_resource(StudentResource, '/api/student/<int:student_id>')

class StudentListResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('first_name', type=str, required=True, help='First Name is required')
        parser.add_argument('last_name', type=str, required=True)
        parser.add_argument('roll_number', type=str, required=True, help='Roll Number is required')
        args = parser.parse_args()

        # Check if the roll_number is provided
        if not args['roll_number']:
            return {'error_code': 'STUDENT001', 'error_message': 'Roll Number is required'}, 400

        # Check if the roll_number already exists
        existing_student = Student.query.filter_by(roll_number=args['roll_number']).first()
        if existing_student:
            return {'error_message': 'Roll Number already exists'}, 409

        student = Student(first_name=args['first_name'], last_name=args['last_name'], roll_number=args['roll_number'])
        db.session.add(student)

        try:
            db.session.commit()
            return {
                'student_id': student.student_id,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'roll_number': student.roll_number
            }, 201
        except Exception as e:
            db.session.rollback()
            return {'error_code': 'STUDENT002', 'error_message': 'First Name is required'}, 400

api.add_resource(StudentListResource, '/api/student')

class EnrollmentResource(Resource):
    def get(self, student_id):
        enrollments = Enrollment.query.filter_by(student_id=student_id).all()
        if enrollments:
            enrollment_list = [{
                'enrollment_id': enrollment.enrollment_id,
                'student_id': enrollment.student_id,
                'course_id': enrollment.course_id,
            } for enrollment in enrollments]
            return enrollment_list
        else:
            return {'message': 'Student is not enrolled in any course'}, 404


    def post(self, student_id):
        parser = reqparse.RequestParser()
        parser.add_argument('course_id', type=int, required=True)

        args = parser.parse_args()

        # Check if the course exists
        existing_course = Course.query.get(args['course_id'])
        if not existing_course:
            return {'error_code': 'ENROLLMENT001', 'error_message': 'Course does not exist'}, 400

        # Check if the student exists
        existing_student = Student.query.get(student_id)
        if not existing_student:
            return {'error_code': 'ENROLLMENT002', 'error_message': 'Student does not exist'}, 400
        
        enrollment = Enrollment(student_id=student_id, course_id=args['course_id'])
        db.session.add(enrollment)

        try:
            db.session.commit()
            return {
                'enrollment_id': enrollment.enrollment_id,
                'student_id': enrollment.student_id,
                'course_id': enrollment.course_id,
            }, 201
        except Exception as e:
            db.session.rollback()
            return {'error_code': 'ENROLLMENT003', 'error_message': 'Enrollment failed'}, 500

api.add_resource(EnrollmentResource, '/api/student/<int:student_id>/course')

class EnrollmentListResource(Resource):
    def delete(self, student_id, course_id):
        enrollment = Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first()
        if enrollment:
            db.session.delete(enrollment)
            db.session.commit()
            return {'message': 'Successfully deleted'}
        else:
            return {'message': 'Enrollment for the student not found'}, 404

api.add_resource(EnrollmentListResource, '/api/student/<int:student_id>/course/<int:course_id>')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')

