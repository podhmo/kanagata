kanagata
========================================

Providing extracted dict (subclass of collections.UserDict).


how to use
----------------------------------------

(todo: description)

models.py

.. code-block:: python

  from kanagata import RestrictionBuilder

  # group: name, users
  # user: name, age, Option[skills], Option[school]
  # skill: name
  b = RestrictionBuilder()

  group = b.define_dict("Group")
  group.add_member("name", required=True)
  group.add_list("users", "User", required=True)

  user = b.define_dict("User")
  user.add_member("name", required=True)
  user.add_member("age", required=True)
  user.add_dict("school", "School", required=False)
  user.add_list("skills", "Skill", required=False)

  skill = b.define_dict("Skill")
  skill.add_member("name", required=True)

  school = b.define_dict("School")
  school.add_member("name")
  school.add_list("groups", "Group", required=True)

  b.build().expose(globals())  # Group, User, Skill, School are exported

.. code-block:: python

  from models import User

  # user can have only name, age, skills. (skills is optional)

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

  # user.skills can have only name.

  user["skills"].append({"name": "math"})
  print(user)  # {'skills': [{'name': 'math'}], 'age': 20, 'name': 'foo'}

  try:
      user["skills"].append({})
      # ValueError: Skill: required fields {'name'} are not found
  except ValueError:
      pass
