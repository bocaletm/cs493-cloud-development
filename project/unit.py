from google.cloud import datastore

from constants import Constants as C

datastore_client = datastore.Client()
class Unit:
    def unitFromLegion(self,legion_id):
        query = datastore_client.query(kind=C.kindA)
        query.add_filter('legion', '=', legion_id)
        entities = query.fetch()
        for entity in entities:
            return entity.key.id_or_name
        return None
        
    def getCost(self, strength, targetRange): 
        return strength * targetRange

    def getLegion(self,id):
        query = datastore_client.query(kind=C.kindA)
        key = datastore_client.key(C.kindA, int(id))
        query.key_filter(key)
        entities = query.fetch()
        for entity in entities:   
            return entity.get('legion',None)

    def count(self,userId):
        query = datastore_client.query(kind=C.kindA)
        query.add_filter('owner', '=', userId)
        query.keys_only()
        entities = query.fetch()
        count = 0
        for entity in entities:
            count+=1
        return count

    def exists(self, id):
        query = datastore_client.query(kind=C.kindA)
        key = datastore_client.key(C.kindA, int(id))
        query.key_filter(key)
        query.keys_only()
        entities = query.fetch()
        for entity in entities:
            return True
        return False
    
    def getOne(self,request,id):
        query = datastore_client.query(kind=C.kindA)
        key = datastore_client.key(C.kindA, int(id))
        query.key_filter(key)
        entities = query.fetch()
        for entity in entities:
            if request.base_url.find(str(entity.key.id_or_name)) > -1:
                selfUri = request.base_url
            else:
                selfUri = request.base_url + '/' + str(entity.key.id_or_name)
            entity.update({"self":selfUri})
            entity.update({"id":entity.key.id_or_name})
            return entity
        return None

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
            "category": category,
            "cost": self.getCost(strength,targetRange),
            "legion": None,
            "name": name, 
            "owner": userId,
            "strength": strength, 
            "targetRange": targetRange,             
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
                "cost": self.getCost(strength,targetRange),
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
            selfUri = request.base_url + '/' + str(entity.key.id_or_name)
            entity.update({"self":selfUri})
            if iterator.next_page_token:
                nextUri = request.base_url + '?offset=' + str(offset + limit)
        if nextUri is not None:
            response = {C.kindAGen:entities,"count":self.count(userId),"next":nextUri}
        else:
            response = {C.kindAGen:entities,"count":self.count(userId)}
        return response

    def put(self,legion_id,unit_id):
        query = datastore_client.query(kind=C.kindA)
        key = datastore_client.key(C.kindA, int(unit_id))
        query.key_filter(key)
        entities = query.fetch()
        for entity in entities:
            entity.update({
                "legion": legion_id,
            })
            datastore_client.put(entity)
            return entity    
        return None

    def remove(self,id):
        query = datastore_client.query(kind=C.kindA)
        key = datastore_client.key(C.kindA, int(id))
        query.key_filter(key)
        entities = query.fetch()
        for entity in entities:
            entity.update({
                "legion": None,
            })
            datastore_client.put(entity)
            return entity    
        return None