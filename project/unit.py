from google.cloud import datastore

from constants import Constants as C

datastore_client = datastore.Client()
class Unit:
    def __getCost(self, strength, targetRange): 
        return strength * targetRange

    def exists(self, id):
        query = datastore_client.query(kind=C.kindA)
        query.keys_only()
        entities = query.fetch()
        for entity in entities:
            return True
        return False
    
    def getOne(self,id):
        query = datastore_client.query(kind=C.kindA)
        key = datastore_client.key(C.kindA, int(id))
        query.key_filter(key)
        entities = query.fetch()
        for entity in entities:
            return entity
        return -1

    def getOwner(self,id):
        query = datastore_client.query(kind=C.kindA)
        key = datastore_client.key(C.kindA, int(id))
        query.key_filter(key)
        entities = query.fetch()
        for entity in entities:
            return entity['owner']
        return -1

    def store(self, name, strength, targetRange, category, userId):
        key = datastore_client.key(C.kindA)
        entity = datastore.Entity(key=key)
        entity.update({
            "name": name, 
            "strength": strength, 
            "targetRange": targetRange,             
            "category": category,
            "cost": self.__getCost(strength,targetRange),
            "owner": userId,
        })
        try: 
            datastore_client.put(entity)
        except Exception as err: 
            print(err)
            return -1
        return entity.key.id_or_name
    
    def delete(self,id):
        key = datastore_client.key(C.kindA, int(id))
        if datastore_client.get(key) is not None:
            datastore_client.delete(key)
            return 204
        else:
            return 401

    def update(self, id, name, strength, targetRange, category, userId):
        query = datastore_client.query(kind=C.kindA)
        key = datastore_client.key(C.kindA, int(id))
        query.key_filter(key)
        entities = query.fetch()
        for entity in entities:
            entity.update({
                "name": name, 
                "strength": strength, 
                "targetRange": targetRange,             
                "category": category,
                "cost": self.__getCost(strength,targetRange),
                "owner": userId,
            })
            datastore_client.put(entity)
            return entity    
        return None

    def get(self,request,userId):
        limit = C.limit
        offset = int(request.args.get('offset', '0'))
        query = datastore_client.query(kind=C.kindA)
        query.add_filter('owner', '=', userId)
        iterator = None
        entities = None
        nextUri = None
        try: 
            iterator = query.fetch(limit=limit, offset=offset)
            pages = iterator.pages
            entities = list(next(pages))
        except:
            print('Failed to fetch ' + C.kindA)
        for entity in entities:
            entity.update({"id":entity.key.id_or_name})
            if iterator.next_page_token:
                nextUri = request.base_url + '?offset=' + str(offset + limit)
                entity.update({"next":nextUri})
        if nextUri is not None:
            response = {C.kindAGen:entities,"next":nextUri}
        else:
            response = {C.kindAGen:entities}
        return response