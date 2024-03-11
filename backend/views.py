import json
import time
import uuid
import os
from dotenv import load_dotenv
from datetime import datetime
from datetime import timedelta
from django.contrib.auth.hashers import make_password
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.hashers import *
from django.db.models import Q
from django.core.mail import send_mail
from rest_framework import generics
from backend.models import *
from backend.checks import *
from backend.exceptions import *
from backend.loghandler import *
from backend.serializers import *

load_dotenv()

class TrainingPlanList(generics.ListAPIView):
    serializer_class = TrainingPlanSerializer

    def get_queryset(self):
        user = self.request.user
        return TrainingPlan.objects.filter(user=user)

@csrf_exempt
def register(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            unit = str(data.get("unit"))
            experience = str(data.get("experience"))
            check_registration(data)
            user = User(
                username=data.get("username"),
                password=make_password(data.get("password")),
                unit=unit.lower(),
                experience=experience.lower(),
                email=data.get("email")
            )

            # validate user fields
            user.full_clean()

            # save user to the database
            user.save()

            return JsonResponse({"token": user.token}, status=200)
        
        except PasswordTooShortError as e:
            logger.error(str(e))
            return JsonResponse({"error": str(e)}, status=404)
        
        except PasswordsDoNotMatchError as e:
            logger.error(str(e))
            return JsonResponse({"error": str(e)}, status=404)

        except Exception as e:
            logger.error(str(e))
            logger.debug(f"data: {data if 'data' in locals() else 'Not available'}")
            return JsonResponse({}, status=404)

    else:
        logger.error(f"invalid request method: {request.method}")
        return JsonResponse({}, status=400)

@csrf_exempt
def login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            check_login(data)
            user = User.objects.get(username=data.get("username"))

            # if user has no token, create one and return it
            # else return the existing token
            if user.token is None:
                user.token = str(uuid.uuid4())
                user.save()
            return JsonResponse({"token": user.token}, status=200) # login successful

        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)
        
    else:
        logger.error(f"invalid request method: {request.method}")
        return JsonResponse({}, status=400)
    
@csrf_exempt
def logout(request):
    # logout on all devices
    if request.method == 'POST':
        try:
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_token(token)
            user = User.objects.get(token=token)

            # set token to None to invalidate it,
            # user will have to login again to get a new token
            user.token = None
            user.save()

            return JsonResponse({}, status=200) # logout successful
        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)
        
    else:
        logger.error(f"invalid request method: {request.method}")
        return JsonResponse({}, status=400)
    
@csrf_exempt
def token_login(request):
    if request.method == 'POST':
        try:
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_token(token)
            return JsonResponse({}, status=200) # login successful

        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)
        
    else:
        logger.error(f"invalid request method: {request.method}")
        return JsonResponse({}, status=400)
     
@csrf_exempt
def register_username(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get("username")
            check_username(username)
            return JsonResponse({}, status=200) # username available

        except UsernameAlreadyExistsError as e:
            logger.error(str(e))
            logger.debug(f"data: {data if 'data' in locals() else 'Not available'}")
            return JsonResponse({"error": str(e)}, status=404)

        except Exception as e:
            logger.error(str(e))
            logger.debug(f"data: {data if 'data' in locals() else 'Not available'}")
            return JsonResponse({}, status=404)
        
    else:
        logger.error(f"invalid request method: {request.method}")
        return JsonResponse({}, status=400)

@csrf_exempt
def tracking(request):
    # get all trackings for a user
    if request.method == 'GET':
        try:
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_token(token)
            user = User.objects.get(token=token)

            trackings = Tracking.objects.filter(user=user)
            tracking_list = [
                {"id": str(tracking.id), "name": tracking.name, "updated": tracking.updated}
                for tracking in trackings
            ]

            return JsonResponse({"tracking_list": tracking_list}, status=200)

        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)

    # create tracking
    elif request.method == 'POST':
        try:
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_token(token)

            data = json.loads(request.body)
            tracking_name = data.get("tracking_name")
            check_field_length('name', tracking_name, Tracking)
            user = User.objects.get(token=token)
            
            # create tracking
            tracking = Tracking(
                name = tracking_name,
                user = user
            )

            # validate tracking fields
            tracking.full_clean()

            # save tracking to the database
            tracking.save()

            return JsonResponse({"id": tracking.id}, status=200) # created tracking successfully

        except Exception as e:
            logger.error(str(e))
            logger.debug(f"data: {data if 'data' in locals() else 'Not available'}")
            return JsonResponse({}, status=404)

    else:
        logger.error(f"invalid request method: {request.method}")
        return JsonResponse({}, status=400)
    
@csrf_exempt
def tracking_id(request, id):
    # get every addition related to one tracking (?)
    if request.method == 'GET':
        try:
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_token(token)
            user = User.objects.get(token=token)
            check_user_permission(user, Tracking, id)
            tracking = Tracking.objects.get(id=id)

            # get all additions related to the tracking
            additions = Addition.objects.filter(tracking=tracking, user=user)
            
            # construct a list of dictionaries representing each addition and return it
            addition_list = [{'id': addition.id,
                     'user_id': addition.user.id,
                     'tracking_id': addition.tracking.id if addition.tracking else None,
                     'goal_id': addition.goal.id if addition.goal else None,
                     'created': addition.created,
                     'updated': addition.updated,
                     'number': str(addition.number),
                     'unit': addition.unit,
                     'note': addition.note} for addition in additions]
            
            return JsonResponse({'addition_list': addition_list}, status=200)

        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)
        
    # add an addition to tracking (?)
    elif request.method == 'POST':
        pass
    # delete tracking by id
    elif request.method == 'DELETE':
        try:
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_token(token)
            user = User.objects.get(token=token)
            check_user_permission(user, Tracking, id)

            # get & delete tracking
            tracking_to_be_deleted = Tracking.objects.get(id=id)
            tracking_to_be_deleted.delete()

            return JsonResponse({}, status=200) # tracking deleted successfully

        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)
    else:
        logger.error(f"invalid request method: {request.method}")
        return JsonResponse({}, status=404)
    
@csrf_exempt
def addition(request):
    # create addition
    if request.method == 'POST':
        try:
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_token(token)
            user = User.objects.get(token=token)
            data = json.loads(request.body)

            # get json data
            tracking_id = data.get('tracking_id')
            goal_id = data.get('goal_id')
            number = data.get('number')
            unit = data.get('unit')
            note = data.get('note')

            # if tracking_id in json data is not null get the tracking object
            # else tracking will be null
            if tracking_id:
                check_user_permission(user, Tracking, tracking_id)
                tracking = Tracking.objects.get(id=tracking_id)
            else:
                tracking = None

            # same for goal_id
            if goal_id:
                check_user_permission(user, Goal, goal_id)
                goal = Goal.objects.get(id=goal_id)
            else:
                goal = None

            # create addition
            addition = Addition(
                user=user,
                tracking=tracking,
                goal=goal,
                number=number,
                unit=unit,
                note=note,
                created=timezone.now(),
                updated=timezone.now()
            )

            # validate addition fields
            addition.full_clean()

            # save addition to the database
            addition.save()

            return JsonResponse({"id": addition.id}, status=200) # addition created successfully

        except Exception as e:
            logger.error(str(e))
            logger.debug(f"data: {data if 'data' in locals() else 'Not available'}")
            return JsonResponse({}, status=404)

    else:
        logger.error(f"invalid request method: {request.method}")
        return JsonResponse({}, status=404)
    
@csrf_exempt
def exercise(request):
    # get all exercises
    if request.method == 'GET':
        try:
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_token(token)
            user = User.objects.get(token=token)
            
            # get all exercises for the user
            exercises = Exercise.objects.filter(user=user)

            # construct a list of dictionaries representing each exercise and return it
            exercise_list = [
                {"id": str(exercise.id), "name": exercise.name, "updated": exercise.updated}
                for exercise in exercises
            ]

            return JsonResponse({"exercise_list": exercise_list}, status=200)

        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)
        
    # create exercise
    elif request.method == 'POST':
        try:
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_token(token)
            user = User.objects.get(token=token)

            data = json.loads(request.body)
            check_field_length('name', data.get('name'), Exercise)

            # create exercise
            exercise = Exercise(
                user=user,
                name=data.get('name'),
                note=data.get('note'),
                type=data.get('type')
            )

            # validate exercise fields
            exercise.full_clean()

            # save exercise to the database
            exercise.save()

            return JsonResponse({"id": exercise.id}, status=200) # created exercise successfully

        except Exception as e:
            logger.error(str(e))
            logger.debug(f"data: {data if 'data' in locals() else 'Not available'}")
            return JsonResponse({}, status=404)

    else:
        logger.error(f"invalid request method: {request.method}")
        return JsonResponse({}, status=404)
    
@csrf_exempt
def exercise_id(request, id):
    # get details of an exercise by id
    if request.method == 'GET':
        try:
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_token(token)

            user = User.objects.get(token=token)
            check_user_permission(user, Exercise, id)

            exercise = Exercise.objects.get(id=id)

            return JsonResponse({"id": exercise.id,
                                 "note": exercise.note,
                                 "name": exercise.name,
                                 "created": exercise.created,
                                 "updated": exercise.updated}, status=200) # got details of an exercise successfully

        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)

    # jotain
    elif request.method == 'POST':
        pass

    # update / edit exercise by id
    elif request.method == 'PATCH':
        try:
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_token(token)
            user = User.objects.get(token=token)
            data = json.loads(request.body)

            check_user_permission(user, Exercise, id)
            check_field_length('name', data.get('name'), Exercise)

            # get exercise and update it
            exercise = Exercise.objects.get(id=id)
            exercise.name = data.get('name')
            exercise.note = data.get('note')
            exercise.type = data.get('type')
            exercise.updated = timezone.now()
            exercise.save()

            return JsonResponse({}, status=200) # exercise updated successfully

        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)
        
    # delete exercise by id
    elif request.method == 'DELETE':
        try:
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_token(token)
            user = User.objects.get(token=token)
            check_user_permission(user, Exercise, id)

            # get & delete exercise
            exercise_to_be_deleted = Exercise.objects.get(id=id)
            exercise_to_be_deleted.delete()

            return JsonResponse({}, status=200) # exercise deleted successfully

        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)
    
    else:
        logger.error(f"invalid request method: {request.method}")
        return JsonResponse({}, status=404)
    
@csrf_exempt
def goal(request):
    # get all goals
    if request.method == 'GET':
        try:
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_token(token)
            user = User.objects.get(token=token)

            # get all goals for the user
            goals = Goal.objects.filter(user=user)

            # construct a list of dictionaries representing each goal and return it
            goal_list = [
                {"id": str(goal.id), "name": goal.name}
                for goal in goals
            ]

            return JsonResponse({"goal_list": goal_list}, status=200) # got all goals successfully
        
        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)


    # create goal
    elif request.method == 'POST':
        try:
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_token(token)
            user = User.objects.get(token=token)
            data = json.loads(request.body)

            check_field_length('name', data.get("name"), Goal)

            # convert milliseconds since the epoch to normal timestamp
            normal_timestamp = convert_unix_timestamp(data.get("end"))
            
            goal = Goal(
                user=user,
                name=data.get('name'),
                number=data.get('number'),
                end=normal_timestamp,
                unit=data.get('unit')
            )

            # validate goal fields
            goal.full_clean()

            # save goal to the database
            goal.save()

            return JsonResponse({"id": goal.id}, status=200) # goal created successfully
        
        except Exception as e:
            logger.error(str(e))
            logger.debug(f"data: {data if 'data' in locals() else 'Not available'}")
            return JsonResponse({}, status=404)

    else:
        logger.error(f"invalid request method: {request.method}")
        return JsonResponse({}, status=404)
    
@csrf_exempt
def goal_id(request, id):
    # get details of a goal by id
    if request.method == 'GET':
        try:
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_token(token)

            user = User.objects.get(token=token)
            goal = Goal.objects.get(id=id, user=user)

            # convert end timestamp to unix timestamp (milliseconds since the epoch)
            end_timestamp = int(time.mktime(goal.end.timetuple())) * 1000
            created_timestamp = int(time.mktime(goal.created.timetuple())) * 1000
            additions = Addition.objects.filter(goal=goal, user=user)
            data = [{
                "note": addition.note, "number": float(addition.number), "created": int(time.mktime(addition.created.timetuple())) * 1000}
                for addition in additions
            ]

            return JsonResponse({"id": goal.id,
                                 "unit":goal.unit,
                                "name": goal.name,
                                "end": end_timestamp,
                                "created": created_timestamp,
                                "number": goal.number,"data":data}, status=200)
        
        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)

    # get all additions regarding one goal by id
    elif request.method == 'POST':
        try:
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_token(token)
            user = User.objects.get(token=token)

            check_user_permission(user, Goal, id)
            goal = Goal.objects.get(id=id)

            # get all additions related to the goal
            additions = Addition.objects.filter(goal=goal, user=user)

            # construct a list of dictionaries representing each addition and return it
            addition_list = [{
                "note": addition.note, "number": addition.number, "created": int(time.mktime(addition.created.timetuple())) * 1000}
                for addition in additions
            ]

            return JsonResponse({"additions_list": addition_list}, status=200)

        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)
        
    # delete goal by id
    elif request.method == 'DELETE':
        try:
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_token(token)

            user = User.objects.get(token=token)
            check_user_permission(user, Goal, id)

            # get & delete goal
            goal = Goal.objects.get(user=user)
            goal.delete()
            
            return JsonResponse({}, status=200) # goal deleted successfully

        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)

    else:
        logger.error(f"invalid request method: {request.method}")
        return JsonResponse({}, status=404)
    
@csrf_exempt
def movement(request):
    # get all movement(s)
    if request.method == 'GET':
        try:
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_token(token)
            user = User.objects.get(token=token)

            # get all movements for the user and the movements suitable for the user's experience level
            movements = Movement.objects.filter(
                Q(user_id=user.id) | Q(experience_level=user.experience)
            ).distinct()

            # construct a list of dictionaries representing each movement and return it
            movement_list = [
                { "id": movement.id, "name": movement.name, "category": movement.category}
                for movement in movements
            ]

            return JsonResponse({"movement_list": movement_list}, status=200) # got all movements successfully
        
        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)

    # create movement
    elif request.method == 'POST':
        try:
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_token(token)
            user = User.objects.get(token=token)

            data = json.loads(request.body)
            movement_name = data.get("name")
            movement_category = str(data.get("category"))
            check_field_length('name', movement_name, Movement)

            movement = Movement(
            user=user,
            name=movement_name,
            category=movement_category.lower()  # Convert category to lowercase
            )

            # validate movement fields
            movement.full_clean()

            # save movement to the database
            movement.save()

            return JsonResponse({"id": movement.id}, status=200) # movement created successfully
        
        except Exception as e:
            logger.error(str(e))
            logger.debug(f"data: {data if 'data' in locals() else 'Not available'}")
            return JsonResponse({}, status=404)

    else:
        logger.error(f"invalid request method: {request.method}")
        return JsonResponse({}, status=404)
    
@csrf_exempt
def trainingplan(request):
    # get all training plan(s)
    if request.method == 'GET':
        try:
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_token(token)
            user = User.objects.get(token=token)

            # get all training plans for the user and the training plans suitable for the user's experience level
            trainingplans = TrainingPlan.objects.filter(
                Q(user=user) | Q(experience_level=user.experience)
            ).distinct()

            # iterate through each training plan, extract its associated movements, 
            # and construct a dictionary representing each training plan along with its movements,
            # then append each dictionary to the trainingplan_list and return it
            trainingplan_list = []
            for trainingplan in trainingplans:
                movements_list = []
                for movement in trainingplan.movements.all():
                    movements_list.append({"id": movement.id, "name": movement.name})
                trainingplan_dict = {
                    "id": trainingplan.id,
                    "training_plan_name": trainingplan.name,
                    "movements": movements_list
                }
                trainingplan_list.append(trainingplan_dict)

            return JsonResponse({"trainingplan_list": trainingplan_list}, status=200)
        
        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)
        
    # create training plan
    elif request.method == 'POST':
        try:
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_token(token)
            user = User.objects.get(token=token)

            # data
            data = json.loads(request.body)
            name = data.get("name")
            movements = data.get("movements")

            # check permission
            for movement in movements:
                check_user_permission(user, Movement, movement)

            # create training plan
            training_plan = TrainingPlan(
                user=user, 
                name=name
            )

            # validate training plan fields
            training_plan.full_clean()

            # save training plan to the database
            training_plan.save()
            
            # add movements to training plan
            for movement_id in movements:
                movement = Movement.objects.get(id=movement_id)
                training_plan.movements.add(movement)

            return JsonResponse({"id": training_plan.id}, status=200)

        except Exception as e:
            logger.error(str(e))
            logger.debug(f"data: {data if 'data' in locals() else 'Not available'}")
            return JsonResponse({}, status=404)
        
    else:
        logger.error(f"invalid request method: {request.method}")
        return JsonResponse({}, status=404)
        
@csrf_exempt
def trainingplan_id(request, id):
    # get training plan by id
    if request.method == 'GET':
        try:
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_token(token)
            user = User.objects.get(token=token)
            check_user_permission(user, TrainingPlan, id)

            # get training plan and its associated movements
            training_plan = TrainingPlan.objects.get(id=id)
            movements = training_plan.movements.all()

            # construct a list of dictionaries representing each movement and return it
            movement_list = [{"id": movement.id, "name": movement.name} for movement in movements]

            return JsonResponse({"id": training_plan.id, "name": training_plan.name, "movements": movement_list}, status=200)
        
        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)
        
    # update / edit training plan by id
    elif request.method == 'PATCH':
        try:
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_token(token)
            user = User.objects.get(token=token)
            data = json.loads(request.body)
            check_user_permission(user, TrainingPlan, id)
            training_plan = TrainingPlan.objects.get(id=id)

            # remove movements if provided in the request data
            if 'movements_to_remove' in data:
                for movement_id in data['movements_to_remove']:
                    check_user_permission(user, Movement, movement_id)
                    movement = Movement.objects.get(id=movement_id)
                    training_plan.movements.remove(movement)

            # add movements if provided in the request data
            if 'movements_to_add' in data:
                for movement_id in data['movements_to_add']:
                    check_user_permission(user, Movement, movement_id)
                    movement = Movement.objects.get(id=movement_id)
                    training_plan.movements.add(movement)

            training_plan.name = data.get('name')

            training_plan.updated = timezone.now()
            training_plan.save()

            return JsonResponse({}, status=200)
        
        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)

    # delete training plan
    elif request.method == 'DELETE':
        try:
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_token(token)
            user = User.objects.get(token=token)
            check_user_permission(user, TrainingPlan, id)

            # get & delete training plan
            training_plan = TrainingPlan.objects.get(id=id)
            training_plan.delete()
            return JsonResponse({}, status=200)

        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)

    else:
        logger.error(f"invalid request method: {request.method}")
        return JsonResponse({}, status=404)
    
@csrf_exempt
def exercisemovementconnection(request):
    # get all emcs for user
    if request.method == 'GET':
        try:
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_token(token)
            user = User.objects.get(token=token)
            exercisemovementconnections = ExerciseMovementConnection.objects.filter(user=user)
            exercisemovementconnection_list = [
                {"id": str(exercisemovementconnection.id),
                 "created": exercisemovementconnection.created,
                 "updated": exercisemovementconnection.updated,
                 "exercise_id": exercisemovementconnection.exercise.id,
                 "exercise_name": exercisemovementconnection.exercise.name,
                 "movement_id": exercisemovementconnection.movement.id,
                 "movement_name": exercisemovementconnection.movement.name,
                 "reps": exercisemovementconnection.reps,
                 "weight": exercisemovementconnection.weight,
                 "video": exercisemovementconnection.video,
                 "time" :exercisemovementconnection.time
                 }
                for exercisemovementconnection in exercisemovementconnections
            ]

            return JsonResponse({"exercisemovementconnection_list": exercisemovementconnection_list}, status=200)

        except Exception as e:
            logger.error(str(e))
            logger.debug(f"token: {token if 'token' in locals() else 'Not available'}")
            return JsonResponse({}, status=404)
        
    # create exercisemovementconnection
    elif request.method == 'POST':
        try:
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_token(token)
            user = User.objects.get(token=token)

            # data
            data = json.loads(request.body)
            exercise_id = data.get("exercise_id")
            movement_id = data.get("movement_id")
            reps = data.get("reps")
            weight = data.get("weight")
            video = data.get("video")
            time = data.get("time")

            # check permission
            check_user_permission(user, Exercise, exercise_id)
            check_user_permission(user, Movement, movement_id)

            # get exercise and movement objects
            exercise = Exercise.objects.get(id=exercise_id)
            movement = Movement.objects.get(id=movement_id)

            # create exercisemovementconnection
            exercisemovementconnection = ExerciseMovementConnection(
                user=user,
                exercise=exercise,
                movement=movement,
                reps=reps,
                weight=weight,
                video=video,
                time=timedelta(minutes=time)
            )

            # validate exercisemovementconnection fields
            exercisemovementconnection.full_clean()

            # save exercisemovementconnection to the database
            exercisemovementconnection.save()

            return JsonResponse({"id": exercisemovementconnection.id}, status=200)
        
        except Exception as e:
            logger.error(str(e))
            logger.debug(f"token: {token if 'token' in locals() else 'Not available'}")
            logger.debug(f"data: {data if 'data' in locals() else 'Not available'}")
            return JsonResponse({}, status=404)

    else:
        logger.error(f"invalid request method: {request.method}")
        return JsonResponse({}, status=404)
    
# id is exercise id
@csrf_exempt
def exercisemovementconnection_id(request, id):
    # get all emcs by exercise id
    if request.method == 'GET':
        try:
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_token(token)
            user = User.objects.get(token=token)
            check_user_permission(user, Exercise, id)

            # get exercise
            exercise = Exercise.objects.get(id=id)
            
            # get all emcs related to the exercise
            emcs = ExerciseMovementConnection.objects.filter(exercise=exercise)

            # construct a list of dictionaries representing each emc and return it
            emcs_list = [{"id": emc.id,
                          "exercise_id": emc.exercise.id,
                          "exercise_name": emc.exercise.name,
                          "movement_id": emc.movement.id,
                          "movement_name": emc.movement.name,
                          "created": emc.created,
                          "updated": emc.updated,
                          "reps": emc.reps,
                          "weight": emc.weight,
                          "video": emc.video,
                          "time": emc.time}
                          for emc in emcs]
            
            return JsonResponse({"emcs_list": str(emcs_list)}, status=200)
            
        except Exception as e:
            logger.error(str(e))
            logger.debug(f"token: {token if 'token' in locals() else 'Not available'}")
            logger.debug(f"id: {id if 'id' in locals() else 'Not available'}")
            return JsonResponse({}, status=404)
        
    # update / edit exercisemovementconnection by exercise id
    elif request.method == 'PATCH':
        try:
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_token(token)
            user = User.objects.get(token=token)

            # data
            data = json.loads(request.body)
            emc_id = data.get("id")
            reps = data.get("reps")
            weight = data.get("weight")
            video = data.get("video")
            time = data.get("time")

            # check permission 
            check_user_permission(user, Exercise, id)
            check_user_permission(user, ExerciseMovementConnection, emc_id)

            # get emc and exercise objects
            emc = ExerciseMovementConnection.objects.get(id=emc_id)
            exercise = Exercise.objects.get(id=id)

            # update exercise
            exercise.updated = timezone.now()
            exercise.save()

            # update emc
            emc.reps = reps
            emc.weight = weight
            emc.video = video
            emc.time = timedelta(minutes=time)
            emc.updated = timezone.now()
            emc.save()

            return JsonResponse({}, status=200)
        
        except Exception as e:
            logger.error(str(e))
            logger.debug(f"token: {token if 'token' in locals() else 'Not available'}")
            logger.debug(f"id: {id if 'id' in locals() else 'Not available'}")
            logger.debug(f"data: {data if 'data' in locals() else 'Not available'}")
            return JsonResponse({}, status=404)

    else:
        logger.error(f"invalid request method: {request.method}")
        return JsonResponse({}, status=404)
    
@csrf_exempt
def user(request):
    # get user details
    if request.method == 'GET':
        try:
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_token(token)
            user = User.objects.get(token=token)
            return JsonResponse({"username": user.username, "email": user.email, "unit": user.unit, "experience": user.experience}, status=200)

        except Exception as e:
            logger.error(str(e))
            logger.debug(f"token: {token if 'token' in locals() else 'Not available'}")
            return JsonResponse({}, status=404)
        
    # update user details
    elif request.method == 'PATCH':
        try:
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_token(token)
            user = User.objects.get(token=token)
            data = json.loads(request.body)

            # define fields to update
            fields_to_update = ['email', 'username', 'password', 'unit', 'experience']

            # update user details based on the fields provided in the request data
            for field in fields_to_update:
                if field in data and data[field]:
                    if field == 'password':
                        setattr(user, field, make_password(data['password']))
                    else:
                        setattr(user, field, data[field])

            # validate fields and save user
            user.full_clean()
            user.save()
            return JsonResponse({"message": "User updated successfully"}, status=200)

        
        except Exception as e:
            logger.error(str(e))
            logger.debug(f"token: {token if 'token' in locals() else 'Not available'}")
            logger.debug(f"data: {data if 'data' in locals() else 'Not available'}")
            return JsonResponse({}, status=404)

    # delete user
    elif request.method == 'DELETE':
        try:
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_token(token)
            user = User.objects.get(token=token)
            data = json.loads(request.body)
            password = data.get("password")
            if check_password(password, user.password):
                user.delete()
                return JsonResponse({}, status=200)
            raise PasswordsDoNotMatchError("Password is incorrect")
        
        except PasswordsDoNotMatchError as e:
            logger.error(str(e))
            logger.debug(f"token: {token if 'token' in locals() else 'Not available'}")
            logger.debug(f"data: {data if 'data' in locals() else 'Not available'}")
            return JsonResponse({"error": "Password is incorrect"}, status=404)
        
        except Exception as e:
            logger.error(str(e))
            logger.debug(f"token: {token if 'token' in locals() else 'Not available'}")
            return JsonResponse({}, status=404)

    else:
        logger.error(f"invalid request method: {request.method}")
        return JsonResponse({}, status=404)
    
@csrf_exempt
def feedback(request):
    if request.method == 'POST':
        try:
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_token(token)
            user = User.objects.get(token=token)
            data = json.loads(request.body)

            # send email
            email_subject = f"GymJunkie feedback"
            email_message = f"User: {user.username}\nFeedback: {data.get('text')}"
            send_mail(
                email_subject,
                email_message,
                os.getenv("EMAIL_HOST_USER"), # sender
                ['gymjunkiefeedback@gmail.com'], # recipient
                fail_silently=True, # True = don't raise exception if email fails to send
            )
            
            return JsonResponse({}, status=200)
        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)
        
    else:
        logger.error(f"invalid request method: {request.method}")
        return JsonResponse({}, status=404)

# converts unix timestamp to normal date
@csrf_exempt
def convert_unix_timestamp(timestamp):
    try:
        # divided unix timestamp by 1000
        timestamp /= 1000
        # convert unix time stamp to datetime object
        normal_date = datetime.fromtimestamp(timestamp)
        return normal_date
    
    except Exception as e:
        raise Exception(e)