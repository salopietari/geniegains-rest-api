import json
import time
import os
from dotenv import load_dotenv
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Q
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.utils.decorators import method_decorator
from knox.models import AuthToken
from rest_framework import permissions
from rest_framework.views import APIView
from backend.models import CustomUser, CustomUserManager, Tracking, Addition, Exercise, Goal, Movement, TrainingPlan, ExerciseMovementConnection
from backend.checks import check_user_permission, check_username, check_email, check_register
from backend.exceptions import PasswordTooShortError, PasswordsDoNotMatchError, UsernameAlreadyExistsError, EmailAlreadyExistsError
from backend.loghandler import logger
from backend.services import get_model_data, create_object, delete_object, convert_unix_time_to_normal, reset_query_quota, translate_object

load_dotenv()

user_manager = CustomUserManager()

@method_decorator(csrf_exempt, name='dispatch')
class register(APIView):
    #register
    def post(self, request):
        try:
            data = json.loads(request.body)
            check_register(data)

            # create a CustomUser object (don't save to db)
            user = CustomUser(
                email=data.get("email"),
                password=data.get("password"),
                username=data.get("username"),
                unit=data.get("unit"),
                experience=data.get("experience")
            )

            # validate password
            validate_password(user.password, user)
            
            # validate all fields
            user.full_clean()

            # actually create the user (automatically saves it to db)
            user = user_manager.create_user(
                email=user.email,
                password=user.password, 
                username=user.username, 
                unit=user.unit, 
                experience=user.experience
            )
            
            token = AuthToken.objects.create(user)[1]
            return JsonResponse({"token": token}, status=200)
        
        except PasswordTooShortError as e:
            logger.error(str(e))
            return JsonResponse({"error": str(e)}, status=400)
        
        except PasswordsDoNotMatchError as e:
            logger.error(str(e))
            return JsonResponse({"error": str(e)}, status=400)
        
        except ValueError as e:
            logger.error(str(e))
            return JsonResponse({"error": str(e)}, status=400)
        
        except ValidationError as e:
            logger.error(str(e))
            return JsonResponse({"error": str(e)}, status=400)

        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class login(APIView):
    # login using email and password
    def post(self, request):
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            user = CustomUser.objects.get(email=email)
            if user is not None and check_password(password, user.password):
                token = AuthToken.objects.create(user=user)[1]
                return JsonResponse({'token': token}, status=200)
            return JsonResponse({}, status=400)

        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=400)

@method_decorator(csrf_exempt, name='dispatch') 
class token_login(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    # login using token
    def post(self, request):
        try:
            user = CustomUser.objects.get(email=self.request.user)
            return JsonResponse({}, status=200) # login successful

        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=400)

@method_decorator(csrf_exempt, name='dispatch')  
class register_username(APIView):
    # check if username is available (used in registration)
    def post(self, request):
        try:
            data = json.loads(request.body)
            username = data.get("username")
            check_username(username)
            return JsonResponse({}, status=200) # username available

        except UsernameAlreadyExistsError as e:
            logger.error(str(e))
            logger.debug(f"data: {data if 'data' in locals() else 'Not available'}")
            return JsonResponse({"error": str(e)}, status=400)

        except Exception as e:
            logger.error(str(e))
            logger.debug(f"data: {data if 'data' in locals() else 'Not available'}")
            return JsonResponse({}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class register_email(APIView):
    # check if email is available (used in registration)
    def post(self, request):
        try:
            data = json.loads(request.body)
            email = data.get("email")
            check_email(email)
            return JsonResponse({}, status=200) # email available

        except EmailAlreadyExistsError as e:
            logger.error(str(e))
            logger.debug(f"data: {data if 'data' in locals() else 'Not available'}")
            return JsonResponse({"error": str(e)}, status=400)

        except Exception as e:
            logger.error(str(e))
            logger.debug(f"data: {data if 'data' in locals() else 'Not available'}")
            return JsonResponse({}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class tracking(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    # get all trackings for a user
    def get(self, request):
        try:
            user = CustomUser.objects.get(email=self.request.user)
            tracking_list = get_model_data(user, Tracking)
            return JsonResponse({"tracking_list": tracking_list}, status=200)

        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=400)

    # create tracking
    def post(self, request):
        try:
            user = CustomUser.objects.get(email=self.request.user)
            data = json.loads(request.body)
            tracking = create_object(user, Tracking, data)
            return JsonResponse({"id": tracking.id}, status=200) # created tracking successfully

        except Exception as e:
            logger.error(str(e))
            logger.debug(f"data: {data if 'data' in locals() else 'Not available'}")
            return JsonResponse({}, status=400)

@method_decorator(csrf_exempt, name='dispatch')  
class tracking_id(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    # get every addition related to one tracking (?)
    def get(self, request, id):
        try:
            user = CustomUser.objects.get(email=self.request.user)
            check_user_permission(user, Tracking, id)
            addition_list = get_model_data(user, Addition, Tracking, additional_filter={"tracking": id})
            return JsonResponse({'addition_list': addition_list}, status=200)

        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=400)
        
    # delete tracking by id
    def delete(self, request, id):
        try:
            user = CustomUser.objects.get(email=self.request.user)
            delete_object(user, Tracking, id)
            return JsonResponse({}, status=200) # tracking deleted successfully

        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=400)

@method_decorator(csrf_exempt, name='dispatch') 
class addition(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    # create addition
    def post(self, request):
        try:
            user = CustomUser.objects.get(email=self.request.user)
            data = json.loads(request.body)
            addition = create_object(user, Addition, data)
            return JsonResponse({"id": addition.id}, status=200) # addition created successfully

        except Exception as e:
            logger.error(str(e))
            logger.debug(f"data: {data if 'data' in locals() else 'Not available'}")
            return JsonResponse({}, status=400)

@method_decorator(csrf_exempt, name='dispatch')  
class exercise(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    # get all exercises
    def get(self, request):
        try:
            user = CustomUser.objects.get(email=self.request.user)
            exercise_list = get_model_data(user, Exercise)
            return JsonResponse({"exercise_list": exercise_list}, status=200)

        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=400)
        
    # create exercise
    def post(self, request):
        try:
            user = CustomUser.objects.get(email=self.request.user)
            data = json.loads(request.body)
            exercise = create_object(user, Exercise, data)
            return JsonResponse({"id": exercise.id}, status=200) # created exercise successfully

        except Exception as e:
            logger.error(str(e))
            logger.debug(f"data: {data if 'data' in locals() else 'Not available'}")
            return JsonResponse({}, status=400)
        
@method_decorator(csrf_exempt, name='dispatch')
class exercise_id(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    # get details of an exercise by id
    def get(self, request, id):
        try:
            user = CustomUser.objects.get(email=self.request.user)
            check_user_permission(user, Exercise, id)

            exercise = Exercise.objects.get(id=id)

            return JsonResponse({"id": exercise.id,
                                 "note": exercise.note,
                                 "name": exercise.name,
                                 "created": exercise.created,
                                 "updated": exercise.updated}, status=200) # got details of an exercise successfully

        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=400)

    # update / edit exercise by id
    def patch(self, request, id):
        try:
            user = CustomUser.objects.get(email=self.request.user)
            data = json.loads(request.body)

            check_user_permission(user, Exercise, id)

            # get exercise and update it
            exercise = Exercise.objects.get(id=id)
            if data.get('name'):
                exercise.name = data.get('name')
            if data.get('note'):
                exercise.note = data.get('note')
            if data.get('type'):
                exercise.type = data.get('type')
            exercise.updated = timezone.now()
            exercise.save()

            return JsonResponse({}, status=200) # exercise updated successfully

        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=400)
        
    # delete exercise by id
    def delete(self, request, id):
        try:
            user = CustomUser.objects.get(email=self.request.user)
            delete_object(user, Exercise, id)
            return JsonResponse({}, status=200) # exercise deleted successfully

        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class goal(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    # get all goals
    def get(self, request, format=None):
        try:
            user = CustomUser.objects.get(email=self.request.user)
            goal_list = get_model_data(user, Goal)
            return JsonResponse({"goal_list": goal_list}, status=200) # got all goals successfully
        
        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=400)

    # create goal
    def post(self, request, format=None):
        try:
            user = CustomUser.objects.get(email=self.request.user)
            data = json.loads(request.body)
            
            # convert end timestamp to normal date string
            normal_timestamp = convert_unix_time_to_normal(data.get("end"))
            data["end"] = normal_timestamp
            goal = create_object(user, Goal, data)
            return JsonResponse({"id": goal.id}, status=200) # goal created successfully
        
        except Exception as e:
            logger.error(str(e))
            logger.debug(f"data: {data if 'data' in locals() else 'Not available'}")
            return JsonResponse({}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class goal_id(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    # get details of a goal by id
    def get(self, request, id):
        try:
            user = CustomUser.objects.get(email=self.request.user)
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
            return JsonResponse({}, status=400)
        
    # delete goal by id
    def delete(self, request, id):
        try:
            user = CustomUser.objects.get(email=self.request.user)
            delete_object(user, Goal, id)
            return JsonResponse({}, status=200) # goal deleted successfully

        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=400)
        
@method_decorator(csrf_exempt, name='dispatch')
class goal_additions_id(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    # get all additions regarding a goal by goal id
    def get(self, request, id):
        try:
            user = CustomUser.objects.get(email=self.request.user)
            check_user_permission(user, Goal, id)
            addition_list = get_model_data(user, Addition, Goal, additional_filter={"goal": id})
            return JsonResponse({"additions_list": addition_list}, status=200)

        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class movement(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    # get all movement(s)
    def get(self, request):
        try:
            user = CustomUser.objects.get(email=self.request.user)
            movement_list = get_model_data(user, Movement, additional_filter={"experience_level": user.experience})
            return JsonResponse({"movement_list": movement_list}, status=200) # got all movements successfully
        
        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=400)

    # create movement
    def post(self, request):
        try:
            user = CustomUser.objects.get(email=self.request.user)
            data = json.loads(request.body)
            movement = create_object(user, Movement, data)
            translate_object(movement, data)
            return JsonResponse({"id": movement.id}, status=200) # movement created successfully
        
        except Exception as e:
            logger.error(str(e))
            logger.debug(f"data: {data if 'data' in locals() else 'Not available'}")
            return JsonResponse({}, status=400)
        
@method_decorator(csrf_exempt, name='dispatch')
class movement_id(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    # delete movement by id
    def delete(self, request, id):
        try:
            user = CustomUser.objects.get(email=self.request.user)
            delete_object(user, Movement, id)
            return JsonResponse({}, status=204)
        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class trainingplan(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    # get all training plan(s)
    def get(self, request):
        try:
            user = CustomUser.objects.get(email=self.request.user)

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
            return JsonResponse({}, status=400)
        
    # create training plan
    def post(self, request):
        try:
            user = CustomUser.objects.get(email=self.request.user)

            # data
            data = json.loads(request.body)
            movements = data.get("movements")
            del data["movements"]

            # check permission for each movement
            for movement in movements:
                check_user_permission(user, Movement, movement)

            training_plan = create_object(user, TrainingPlan, data)
            
            # add movements to training plan
            for movement_id in movements:
                movement = Movement.objects.get(id=movement_id)
                training_plan.movements.add(movement)

            return JsonResponse({"id": training_plan.id}, status=200)

        except Exception as e:
            logger.error(str(e))
            logger.debug(f"data: {data if 'data' in locals() else 'Not available'}")
            return JsonResponse({}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class trainingplan_id(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    # get training plan by id
    def get(self, request, id):
        try:
            user = CustomUser.objects.get(email=self.request.user)
            check_user_permission(user, TrainingPlan, id)

            # get training plan and its associated movements
            training_plan = TrainingPlan.objects.get(id=id)
            movements = training_plan.movements.all()

            # construct a list of dictionaries representing each movement and return it
            movement_list = [{"id": movement.id, "name": movement.name} for movement in movements]

            return JsonResponse({"id": training_plan.id, "name": training_plan.name, "movements": movement_list}, status=200)
        
        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=400)
        
    # update / edit training plan by id
    def patch(self, request, id):
        try:
            user = CustomUser.objects.get(email=self.request.user)
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

            # update training plan name
            if data.get('name'):
                training_plan.name = data.get('name')

            training_plan.updated = timezone.now()
            training_plan.full_clean()
            training_plan.save()

            return JsonResponse({}, status=200)
        
        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=400)

    # delete training plan
    def delete(self, request, id):
        try:
            user = CustomUser.objects.get(email=self.request.user)
            delete_object(user, TrainingPlan, id)
            return JsonResponse({}, status=200)

        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class exercisemovementconnection(APIView):
    permission_classes = (permissions.IsAuthenticated,)
 
    # get all emcs for user
    # ONKS TÄÄ TURHA ENDPOINT? KÄYTETÄÄNKÖ TÄTÄ EDES FRONTENDISSÄ MISSÄÄN ???
    def get(self, request):
        try:
            user = CustomUser.objects.get(email=self.request.user)
            emc_list = get_model_data(user, ExerciseMovementConnection)
            return JsonResponse({"exercisemovementconnection_list": emc_list}, status=200)

        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=400)
        
    # create exercisemovementconnection
    def post(self, request):
        try:
            user = CustomUser.objects.get(email=self.request.user)

            # data
            data = json.loads(request.body)
            exercise_id = data.get("exercise_id")
            movement_id = data.get("movement_id")
            data["time"] = timedelta(minutes=data.get("time"))

            check_user_permission(user, Exercise, exercise_id)
            check_user_permission(user, Movement, movement_id)

            emc = create_object(user, ExerciseMovementConnection, data)

            return JsonResponse({"id": emc.id}, status=200)
        
        except Exception as e:
            logger.error(str(e))
            logger.debug(f"data: {data if 'data' in locals() else 'Not available'}")
            return JsonResponse({}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class exercisemovementconnection_id(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    # get all emcs by exercise id
    def get(self, request, id):
        try:
            user = CustomUser.objects.get(email=self.request.user)
            check_user_permission(user, Exercise, id)
            emcs_list = get_model_data(user, ExerciseMovementConnection, Exercise, additional_filter={"exercise": id})
            return JsonResponse({"emcs_list": emcs_list}, status=200)
            
        except Exception as e:
            logger.error(str(e))
            logger.debug(f"id: {id if 'id' in locals() else 'Not available'}")
            return JsonResponse({}, status=400)
        
    # update / edit exercisemovementconnection by exercise id
    def patch(self, request, id):
        try:
            user = CustomUser.objects.get(email=self.request.user)

            # data
            data = json.loads(request.body)
            emc_id = data.get("id")

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
            if data.get("reps"):
                emc.reps = data.get("reps")
            if data.get("weight"):
                emc.weight = data.get("weight")
            if data.get("video"):
                emc.video = data.get("video")
            if data.get("time"):
                time = data.get("time")
            emc.updated = timezone.now()
            emc.save()

            return JsonResponse({}, status=200)
        
        except Exception as e:
            logger.error(str(e))
            logger.debug(f"id: {id if 'id' in locals() else 'Not available'}")
            logger.debug(f"data: {data if 'data' in locals() else 'Not available'}")
            return JsonResponse({}, status=400)
        
    # delete emc by id
    def delete(self, request, id):
        try:
            user = CustomUser.objects.get(email=self.request.user)
            delete_object(user, ExerciseMovementConnection, id)
            return JsonResponse({}, status=204)

        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class user(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    # get user details
    def get(self, request):
        try:
            user = CustomUser.objects.get(email=self.request.user)
            reset_query_quota(user)
            return JsonResponse({"username": user.username, "email": user.email, "unit": user.unit, "experience": user.experience, "query_quota": user.query_quota}, status=200)

        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=400)
        
    # update user details
    def patch(self, request):
        try:
            user = CustomUser.objects.get(email=self.request.user)
            data = json.loads(request.body)

            # define fields to update
            fields_to_update = ['email', 'username', 'unit', 'experience', 'password']

            # update user details based on the fields provided in the request data
            for field in fields_to_update:
                if field in data and data[field]:
                    # handle changing password
                    if field == 'password':
                        setattr(user, field, make_password(data['password']))   # set new password
                        AuthToken.objects.filter(user=user).delete()            # delete old token
                        token = AuthToken.objects.create(user)[1]               # create new token
                        user.full_clean()                                       # validate user
                        user.save()                                             # save user
                        return JsonResponse({"token": token}, status=200)       # password changed successfully, return new token
                    else:
                        setattr(user, field, data[field])

            # validate fields and save user
            user.full_clean()
            user.save()
            return JsonResponse({"message": "User updated successfully"}, status=200)

        
        except Exception as e:
            logger.error(str(e))
            logger.debug(f"data: {data if 'data' in locals() else 'Not available'}")
            return JsonResponse({}, status=400)

    # delete user
    def delete(self, request):
        try:
            user = CustomUser.objects.get(email=self.request.user)
            data = json.loads(request.body)
            password = data.get("password")
            if check_password(password, user.password):
                user.delete()
                return JsonResponse({}, status=204)
            raise PasswordsDoNotMatchError("Password is incorrect")
        
        except PasswordsDoNotMatchError as e:
            logger.error(str(e))
            logger.debug(f"data: {data if 'data' in locals() else 'Not available'}")
            return JsonResponse({"error": "Password is incorrect"}, status=400)
        
        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class feedback(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            user = CustomUser.objects.get(email=self.request.user)
            data = json.loads(request.body)

            # send email
            email_subject = f"GymJunkie feedback"
            email_message = f"User: {user.username}\nFeedback: {data.get('text')}"
            send_mail(
                email_subject,
                email_message,
                os.getenv("EMAIL_HOST_USER"), # sender
                ['gymjunkiefeedback@gmail.com', 'feedback-d167392e-5c79-4fed-ba53-3d337a85a3c4@email.devit.software'],  # recipients (gymjunkie email and discord bot)
                fail_silently=True, # True = don't raise exception if email fails to send
            )
            return JsonResponse({}, status=200)
        
        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=400)