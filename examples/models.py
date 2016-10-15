from kanagata import RestrictionBuilder

# group: name, users
# user: name, age, Option[skills], Option[school]
# skill: name
# school: name, groups
with RestrictionBuilder() as b:
    with b.define_dict("Group") as group:
        group.add_member("name", required=True)
        group.add_list("users", "User", required=True)

    with b.define_dict("User") as user:
        user.add_member("name", required=True)
        user.add_member("age", required=True)
        user.add_dict("school", "School", required=False)
        user.add_list("skills", "Skill", required=False)

    with b.define_dict("Skill") as skill:
        skill.add_member("name", required=True)

    with b.define_dict("School") as school:
        school.add_member("name")
        school.add_list("groups", "Group", required=True)
