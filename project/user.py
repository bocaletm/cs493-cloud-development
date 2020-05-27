from google.cloud import datastore

from constants import Constants as C
from unit import Unit

datastore_client = datastore.Client()

class User:
    def conditionalCreate(self,user_id):
        query = datastore_client.query(kind=C.kindC)
        query.add_filter('sub', '=', user_id)
        entities = query.fetch()
        for entity in entities:
            return 1
        key = datastore_client.key(C.kindC)
        entity = datastore.Entity(key=key)
        entity.update({
            "sub": user_id, 
            "budget": C.startingBudget,
        })
        try: 
            datastore_client.put(entity)
        except Exception as err: 
            print(err)
            return -1