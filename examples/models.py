from kanagata import RestrictionBuilder

# group: name, users
# user: name, age, Option[skills], Option[school]
# skill: name
# school: name, groups
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
b.build().expose(globals())  # Group, User, Skill, School
