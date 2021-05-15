from psucontrol.models import PSU

def check_permissions(psu, user):
    """
    function to check the access level of a user
    returns:
        0 no access
        5 permitted user
        10 owner
    """

    if user.is_superuser:
        # treat superusers higher than owners
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


def get_psus_with_permission(user, min_level):
    """
    returns all PSUs to which a given user has access
    """
    psus = []
    for p in PSU.objects.all():
        if check_permissions(p, user) > min_level:
            psus.append(p)
    return psus
