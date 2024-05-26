import json
from dotenv import load_dotenv
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import CustomUser, Conversation, QA
from .loghandler import logger
from .exceptions import QueryQuotaExceededError
from .services import get_model_data, ask_openai, create_object, create_title, update_object, delete_object, check_user_permission, translate_object
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
            conversations.sort(key=lambda x: (not x.get('favorite', False), x.get('updated_at')), reverse=True)
            conversations = conversations[::-1]
            return JsonResponse({"query_quota": user.query_quota, "conversations": conversations}, status=200)
        
        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=400)
    
    # create a new conversation (includes first message)
    def post(self, request):
        try:
            user = CustomUser.objects.get(email=self.request.user)
            data = json.loads(request.body)
            question = data.get("question")
            conversation = create_object(user, Conversation, data={"title": "Default title"})
            qa = ask_openai(user, question, conversation)
            create_title(qa, conversation)
            translate_object(conversation, data={"title": conversation.title})
            translate_object(qa, data={"question": qa.question, "answer": qa.answer})
            return JsonResponse({"conversation_id": conversation.id,
                                "answer": qa.answer, 
                                "query_quota": user.query_quota}, status=200)
        
        except QueryQuotaExceededError as e:
            logger.error(str(e))
            return JsonResponse({"error": str(e)}, status=402)

        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=400)

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
            return JsonResponse({}, status=400)
    
    # insert new chat message (question) to conversation 
    def post(self, request, id):
        try:
            user = CustomUser.objects.get(email=self.request.user)
            check_user_permission(user, Conversation, id)
            conversation = Conversation.objects.get(id=id)
            data = json.load(request)
            question = data.get('question')
            qa = ask_openai(user, question, conversation)
            translate_object(qa, data={"question": qa.question, "answer": qa.answer})
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
            return JsonResponse({}, status=400)
        
    # update conversation title and favorite status
    def patch(self, request, id):
        try:
            user = CustomUser.objects.get(email=self.request.user)
            data = json.load(request)

            if "title" in data:
                update_object(user, Conversation, id, {"title": data.get("title")})

            if "favorite" in data:
                update_object(user, Conversation, id, {"favorite": data.get("favorite")})
            
            return Response(status=204)
        
        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=400)
        
    # deletes a conversation
    def delete(self, request, id):
        try:
            user = CustomUser.objects.get(email=self.request.user)
            delete_object(user, Conversation, id)
            return Response(status=204)
        
        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=400)