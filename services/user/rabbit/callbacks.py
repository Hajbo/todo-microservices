import json

def create_user_callback(jsondata):
    from models import UserModel
    data = json.loads(jsondata)
    username = data.get('username')
    uuid = data.get('uuid')

    # Checking if user already exists
    if UserModel.find_by_username(username):
        raise ValueError(f"User {username} already exists")
    
    # Create new user
    new_user = UserModel(username=username, uuid=uuid)

    try:
        # Saving user in DB and Generating Access and Refresh token
        new_user.save_to_db()
    except:
        raise ValueError("Something went wrong")
