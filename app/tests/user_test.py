import pytest 
from app.core.config import settings

@pytest.mark.parametrize("name,email,password,expected_status,expected_detail",[
    ("afzal","afzal@gmail.com","afzal123",200,None),
    ("salman","salman333699@gmail.com","123456",400,{"message": "Email is already registered"})  #Assume this email is already exist
])
def test_register_user(name,email,password,expected_status,expected_detail):
    response = settings.client.post("/users/register",json={
        "name":name,
        "email":email,
        "password":password
    })
    assert response.status_code == expected_status
    if expected_status == 200:
        assert response.json()["email"]==email
    else:
        assert response.json() == expected_detail    


# TEST FOR USER LOGIN
@pytest.mark.parametrize("email,password, expected_status,expected_detail",[
    ("salman333699@gmail.com","123456",200,None),
    ("salman333699@gmail.com","salman",400,{"message": "Incorrect password or username"}), #Incorrect password and username
    ("sufiyan@gmail.com","sufiyan",400,{"message": "User is not exist"})   # Non Existence User
])
def test_login_user(email,password, expected_status,expected_detail):
    response = settings.client.post("/users/login",data={
        "username":email,
        "password":password
    })
    assert response.status_code == expected_status
    if expected_status == 200:
        assert "access_token" in response.json()
    else:
        assert response.json() == expected_detail     

# Test for getting user by name
@pytest.mark.parametrize("name,expected_status,expected_detail",[
    ("salman",200,None),
    ("suifyan",400,{"message": "User is not exist"}) # Non Existence User
])
def test_get_user_by_name(name,expected_status,expected_detail):
    response= settings.client.get(f"/users/{name}")
    assert response.status_code == expected_status
    if expected_status ==200:
        assert response.json()["name"]==name
    else:
        assert response.json() == expected_detail         