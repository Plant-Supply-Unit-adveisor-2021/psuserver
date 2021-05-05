def check_permissions(psu, user):
    """
    function to check the access level of a user
    returns:
        0 no access
        5 permitted user
        10 owner
    """

    if user.is_staff or user.is_superuser:
        # treat staff and superusers higher than owners
        return 20

    elif psu.owner == user:
        # user owner of psu
        return 10

    elif user in psu.permitted_users.all():
        # user is permitted user
        return 5

    else:
        # no access
        return 0
