from models import User

user = User(name="foo", age=20, skills=[])
print(user)  # {'name': 'foo', 'age': 20, 'skills': []}

try:
    user2 = User(name="bar")
    # ValueError: User: required fields {'age'} are not found
except ValueError:
    pass


try:
    user["xxx"] = "bar"
    # ValueError: User: unsupported field 'xxx', field members=['name', 'age', 'school', 'skills']
except ValueError:
    pass

user["skills"].append({"name": "math"})
print(user)  # {'skills': [{'name': 'math'}], 'age': 20, 'name': 'foo'}

try:
    user["skills"].append({})
    # ValueError: Skill: required fields {'name'} are not found
except ValueError:
    pass
