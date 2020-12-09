import json
import requests

def delete_user_callback(jsondata):
    from models import UserModel
    data = json.loads(jsondata)
    uuid = data.get('uuid')
    jwt = data.get('jwt')

    try:
        UserModel.delete_by_uuid(uuid)
        requests.post(
            'http://localhost:8080/api/logout/access',
            headers={"Authorization": f"Bearer {jwt}"}
        )
    except:
        raise ValueError(f"Something went wrong while deleting User by uuid {uuid}")
