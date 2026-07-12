from flask import Blueprint, jsonify, request

from models.models import db, User, Trek, Booking



api = Blueprint("api", __name__)       #separate API for jsonify

#get data of all treks and jsonify them 
#==============================================

@api.route("/api/treks", methods=["GET"])      
def get_treks():

    treks = Trek.query.all()

    trek_list = []

    for trek in treks:

        trek_list.append({
            "id": trek.id,
            "trek_name": trek.trek_name,
            "location": trek.location,
            "difficulty": trek.difficulty,
            "duration_days": trek.duration_days,
            "available_slots": trek.available_slots,
            "status": trek.status
        })

    return jsonify(trek_list)

#get data of single trek by using trek id  and jsonify them 
#==============================================

@api.route("/api/treks/<int:trek_id>", methods=["GET"])
def get_single_trek(trek_id):

    trek = Trek.query.get_or_404(trek_id)   #if exist get otherwise show error

    trek_data = {
        "id": trek.id,
        "trek_name": trek.trek_name,
        "location": trek.location,
        "difficulty": trek.difficulty,
        "duration_days": trek.duration_days,
        "available_slots": trek.available_slots,
        "status": trek.status
    }

    return jsonify(trek_data)

#create new trek and jsonify them 
#==============================================

@api.route("/api/treks", methods=["POST"])
def create_trek():

    data = request.get_json()   #request.get_json() means client is sending new json data to api and stored in a data variable
                                #use that for flask/python or other things
    new_trek = Trek(
        trek_name=data["trek_name"],
        location=data["location"],
        difficulty=data["difficulty"],
        duration_days=data["duration_days"],
        available_slots=data["available_slots"],
        status=data["status"]
    )

    db.session.add(new_trek)
    db.session.commit()

    return jsonify({
        "message": "Trek created successfully",      #this msg for client with trek id in json format
        "trek_id": new_trek.id
    }), 201                                       #201 is a HTTP status code means resource successfully created 


#get data of  treks and jsonify them 
#==============================================

@api.route("/api/treks/<int:trek_id>", methods=["PUT"])
def update_trek(trek_id):

    trek = Trek.query.get_or_404(trek_id)

    data = request.get_json()

    trek.trek_name = data["trek_name"]
    trek.location = data["location"]
    trek.difficulty = data["difficulty"]
    trek.duration_days = data["duration_days"]
    trek.available_slots = data["available_slots"]
    trek.status = data["status"]

    db.session.commit()

    return jsonify({
        "message": "Trek updated successfully"
    })

#Delete the data of  treks and jsonify them 
#==============================================

@api.route("/api/treks/<int:trek_id>", methods=["DELETE"])
def delete_trek_api(trek_id):

    trek = Trek.query.get_or_404(trek_id)

    db.session.delete(trek)
    db.session.commit()

    return jsonify({
        "message": "Trek deleted successfully"
    })

#get data of all users and jsonify them 
#==============================================

@api.route("/api/users", methods=["GET"])
def get_users():

    users = User.query.all()

    user_list = []

    for user in users:

        user_list.append({
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role,
            "status": user.status
        })

    return jsonify(user_list)


#get data of all bookings and jsonify them 
#==============================================

@api.route("/api/bookings", methods=["GET"])
def get_bookings():

    bookings = Booking.query.all()

    booking_list = []

    for booking in bookings:

        booking_list.append({
            "id": booking.id,
            "user_id": booking.user_id,
            "trek_id": booking.trek_id,
            "booking_date": booking.booking_date,
            "booking_status": booking.booking_status,
            "payment_status": booking.payment_status
        })

    return jsonify(booking_list)