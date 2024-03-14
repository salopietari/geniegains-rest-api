from backend.models import *

def get_model_data(user: CustomUser, model_class: models.Model, **kwargs) -> list:
    '''
    Retrieve all objects of type model_class 
    and data regarding them - return a list of dictionaries containing the data
    '''
    try:
        objects = model_class.objects.filter(user=user)
        data_list = []
        for obj in objects:
            data = {"id": str(obj.id), "name": obj.name, "updated": obj.updated}
            for key, value in kwargs.items():
                data[key] = getattr(obj, value)
            data_list.append(data)
        return data_list
    
    except Exception as e:
        raise Exception(e)
