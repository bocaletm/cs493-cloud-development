class Constants:
    NO_ID = 'Invalid id'
    NO_ID_BOAT = 'No boat with this boat_id exists'
    INCOMPLETE = 'The request object is missing at least one of the required attributes'
    INVALID_DATA = 'Invalid data for at least one of the required attributes'
    ID_UPDATE = 'Cannot set id attribute'
    EXTRA_ATTRIBUTES = 'Unrecognized attributes in request'
    DOCUMENTATION = ''
    limit = 3
    maxBoatLength = 1600
    minBoatLength = 10
    minStringLength = 3
    maxNameLength = 255
    maxTypeLength = 255
    NUM_BOAT_ATTRIBUTES = 3
    validChars = '^[a-zA-Z0-9 ]+$'