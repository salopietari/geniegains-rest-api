import json
from dotenv import load_dotenv
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from .models import *
from .loghandler import *
from .checks import *
from .exceptions import *
from .services import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions

load_dotenv()

@method_decorator(csrf_exempt, name='dispatch')
class conversation(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    # get conversation id's
    def get(self, request):
        try:
            user = CustomUser.objects.get(email=self.request.user)
            conversations = get_model_data(user, Conversation)
            return JsonResponse({"query_quota": user.query_quota, "conversations": conversations}, status=200)
        
        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)
    
    # create a new conversation (includes first message)
    def post(self, request):
        try:
            user = CustomUser.objects.get(email=self.request.user)
            data = json.loads(request.body)
            question = data.get("question")
            conversation = create_object(user, Conversation, data={"title": "Default title"})
            qa = ask_openai(user, question, conversation)
            create_title(qa, conversation)
            return JsonResponse({"conversation_id": conversation.id,
                                "answer": qa.answer, 
                                "query_quota": user.query_quota}, status=200)
        
        except QueryQuotaExceededError as e:
            logger.error(str(e))
            return JsonResponse({"error": str(e)}, status=402)

        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)

@method_decorator(csrf_exempt, name='dispatch')
class conversation_id(APIView):

    # find chat messages by id
    def get(self, request, id):
        try:
            user = CustomUser.objects.get(email=self.request.user)
            check_user_permission(user, Conversation, id)
            conversation = Conversation.objects.get(id=id)
            question_data = get_model_data(user, QA, additional_model=Conversation, additional_filter={"conversation_id": conversation})
            return JsonResponse({"conversations": question_data}, 
                                content_type="application/json", status=200)
        
        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)
    
    # insert new chat message (question) to conversation 
    def post(self, request, id):
        try:
            user = CustomUser.objects.get(email=self.request.user)
            check_user_permission(user, Conversation, id)
            check_user_query_quota(user)
            conversation = Conversation.objects.get(id=id)
            data = json.load(request)
            question = data.get('question')
            qa = ask_openai(user, question, conversation)
            return JsonResponse({
                "id": qa.id,
                "answer": qa.answer,
                "query_quota": user.query_quota
            }, content_type="application/json", status=200)
        
        except QueryQuotaExceededError as e:
            logger.error(str(e))
            return JsonResponse({"error": str(e)}, status=402)
        
        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)
        
    # update conversation title and favorite status
    def patch(self, request, id):
        try:
            user = CustomUser.objects.get(email=self.request.user)
            check_user_permission(user, Conversation, id)
            data = json.load(request)

            if "title" in data:
                update_object(user, Conversation, id, {"title": data.get("title")})
            
            return Response(status=204)
        
        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)
        
    # deletes a conversation
    def delete(self, request, id):
        try:
            user = CustomUser.objects.get(email=self.request.user)
            check_user_permission(user, Conversation, id)
            delete_object(user, Conversation, id)
            return Response(status=204)
        
        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)