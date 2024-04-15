import re
import os
import copy
from django.utils import timezone
from backend.google_translate_api import detect_language, translate_text
from backend.exceptions import QueryQuotaExceededError
from backend.models import CustomUser, models, QA, Conversation, Movement
from backend.checks import check_user_permission, check_user_query_quota
from django.db.models import Q
from django.db import transaction
from datetime import datetime
from openai import OpenAI
from typing import Union

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

def get_model_data(user: CustomUser, model: models.Model, additional_model: models.Model=None, additional_filter: dict=None) -> list:
    '''
    Retrieve all objects of type "model" belonging to the "user" and 
    filtered by "additional_model" and/or "additional_filter" (optional).
    Returns a list of dictionaries where each key represents an object of "model", 
    with the values of the key being the values of the object
    '''
    try:
        # filter objects by additional_model and additional_filter
        if additional_model is not None and additional_filter is not None:
            objects = model.objects.filter(user=user, **additional_filter)
        # filter objects by additional_filter only
        elif additional_model is None and additional_filter is not None:
            objects = model.objects.filter(Q(user=user) | Q(**additional_filter)).distinct()
        # default case: get all objects of user
        else:
            objects = model.objects.filter(user=user)

        data_list = []
        for obj in objects:
            obj_data = {}
            for field in obj._meta.fields:
                if isinstance(field, models.ForeignKey):
                    continue
                obj_data[field.name] = getattr(obj, field.name)
            data_list.append(obj_data)
        return data_list
    
    except Exception as e:
        raise Exception(e)
    
def create_object(user: CustomUser, model: models.Model, data: dict[str: any]) -> models.Model:
    '''
    Create an object of type model with the data provided
    '''
    try:
        object = model(**data)
        object.user = user
        object.full_clean()
        with transaction.atomic():
            object = model.objects.create(
                user=user,
                **data)
            object.save()
        return object

    except Exception as e:
        raise Exception(e)
    
def update_object(user: CustomUser, model: models.Model, object_id: int, data: dict[str: any]) -> None:
    '''
    Update the object of type model with id object_id with the data provided
    '''
    try:
        object = model.objects.get(id=object_id)
        check_user_permission(user, model, object_id)
        for key, value in data.items():
            setattr(object, key, value)
        object.full_clean()
        object.save()
    
    except Exception as e:
        raise Exception(e)
        
def translate_object(object: Union[Movement, Conversation, QA], data: dict[str:str]) -> None:
    '''
    Translate object's (which should be of model Movement, Conversation or QA)
    fields which are provided in data (where Key = Model's field, Value = Value provided by user)
    to languages (English, Japanese, Finnish) using Google Cloud Translation API.

    These are the fields that should be translated:
    Movement: name, category
    Conversation: title
    QA: question, answer
    '''
    try:
        # iterate over provided data
        for field, value in data.items():
            # get the language of the original value
            detected_language = detect_language(value)
            # iterate over languages value needs to be translated to
            for language in ['en', 'ja', 'fi']:
                # if language (e.g. 'en') is not the same as the detected language (e.g. 'fi')
                # translate the value to the language (e.g. 'en')
                if language != detected_language:
                    translation = translate_text(value, language)
                    setattr(object, field + "_" + language, translation)
                # if language is the same as the detected language
                # just set the value to the object
                else:
                    setattr(object, field + "_" + language, value)
            # this is a very cheap fix to make sure that conversation endpoints
            # save question and answer in a QA object in the original value
            # FIXME: this is a very bad way to do this
            if type(object) == QA:
                object.question = data['question']
                object.answer = data['answer']
        object.save()

    except Exception as e:
        raise e

def delete_object(user: CustomUser, model: models.Model, object_id: int) -> None:
    '''
    Delete the object of type model with id object_id if the user has permission to do so
    '''
    try:
        object = model.objects.get(id=object_id)
        check_user_permission(user, model, object_id)
        object.delete()
    
    except Exception as e:
        raise Exception(e)
    
def convert_unix_time_to_normal(seconds: int) -> str:
    '''
    Convert a unix timestamp (seconds that have elapsed since the Unix epoch, 
    which is defined as 00:00:00 UTC on January 1, 1970, not counting leap seconds) 
    to a normal date string
    '''
    try:
        normal_date = seconds/1000
        normal_date = datetime.fromtimestamp(normal_date)
        return normal_date
    
    except Exception as e:
        raise Exception(e)
    
def reset_query_quota(user: CustomUser) -> None:
    '''
    Reset user's query quota to the defined default in models.py 
    if the last query was not made today
    '''
    try:
        if user.last_query.date() < timezone.now().date():
            user.query_quota = user._meta.get_field('query_quota').default
            user.save()

    except Exception as e:
        raise Exception(e)
    
def decrement_query_quota(user: CustomUser) -> None:
    '''
    Decrement user's query quota by 1
    and update the last query to the current time
    '''
    try:
        user.query_quota -= 1
        user.last_query = timezone.now()
        user.save()

    except Exception as e:
        raise Exception(e)
    
def ask_openai(user: CustomUser, question: str, conversation: Conversation) -> QA:
    '''
    Ask OpenAI a question and save the response in a QA object and return it.
    '''
    try:
        check_user_query_quota(user)
        if len(question) > QA._meta.get_field('question').max_length:
            raise Exception("Question is too long")
        qa = create_object(user, QA, {"question": question, "conversation": conversation})

        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": "You are a helpful gym personl trainer, your job is to answer any questions the user might have. ALWAYS RESPOND IN THE SAME LANGUAGE AS THE QUESTION."},
                {"role": "user", "content": f"{question}"},
            ]
        )

        decrement_query_quota(user)
        qa.answer = response.choices[0].message.content
        qa.save()
        conversation.updated = timezone.now()
        conversation.save()
        return qa
    
    except QueryQuotaExceededError as e:
        raise QueryQuotaExceededError(e)
    
    except Exception as e:
        raise Exception(e)
    
def create_title(qa: QA, conversation: Conversation):
    '''
    Use AI to create an appropriate title for a new conversation
    '''
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": "You need to create a title for a conversation based on the question and answer, the title should be short and descriptive. Answer with only the title."},
                {"role": "user", "content": f"Question: {qa.question}\n Answer: {qa.answer}"},
            ]
        )
        title = strip_string(response.choices[0].message.content)
        conversation.title = title
        conversation.save()

    except Exception as e:
        raise Exception(e)
    
def strip_string(input_string: str) -> str:
    '''
    Strip input_string of all non-alphanumeric characters
    '''
    try:
        pattern = re.compile(r'[^a-zA-Z0-9\s]')
        stripped_string = re.sub(pattern, '', input_string)
        return stripped_string
    
    except Exception as e:
        raise Exception(e)