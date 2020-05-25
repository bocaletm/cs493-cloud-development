class Constants:
    NO_ID = 'Invalid id'
    INCOMPLETE = 'The request object is missing at least one of the required attributes'
    INVALID_DATA = 'Invalid data for at least one of the required attributes'
    ID_UPDATE = 'Cannot set id attribute'
    EXTRA_ATTRIBUTES = 'Unrecognized attributes in request'
    TOKEN_UNAUTHORIZED = 'Token not authorized to modify entity'
    NOT_EXISTS = 'does not exist'
    BAD_METHOD = 'Method not allowed'
    MIME_ERR = 'Unsupported mimetype in request'
    BEARER_ERR = 'Bearer token malformed'
    INVALID_TOKEN = 'Invalid token'
    NO_TOKEN = 'Missing token'
    UNKNOWN_AUTH = 'Unknown authorization error'
    ID_MISMATCH = 'The owner_id does not match the id in the token'
    DOCUMENTATION = ''
    limit = 5
    minStringLength = 3
    maxNameLength = 255
    maxCategoryLength = 255
    NUM_KINDA_ATTRIBUTES = 4
    NUM_KINDB_ATTRIBUTES = 3
    validChars = '^[a-zA-Z0-9 ]+$'
    kindA = 'Unit'
    kindAGen = 'units'
    kindB = 'Legion'
    kindBGen = 'legions'
    AUTH_SCOPES = ['https://www.googleapis.com/auth/userinfo.email', 'openid',
             'https://www.googleapis.com/auth/userinfo.profile']
    AUTH_ISSUER = 'accounts.google.com'
    TERRAINS = ["desert","mountains","plains","tundra","wetlands"]
    ENTITY_NOT_FOUND = kindA + ' or ' + kindB + ' does not exist.'