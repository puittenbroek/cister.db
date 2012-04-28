ADMINS = [
    21673,
    100010,
    6384,
    205,
]

SETTINGS = ADMINS
EDITORS = ADMINS

def groupfinder(username, request):

    groups = []
    if username in ADMINS:
        groups.append(('group:admin'))

    if username in EDITORS:
        groups.append(('group:editor'))

    if username:
        # For now, if you have a userid, you are a user ;) 
        groups.append(('group:user'))
    return groups
