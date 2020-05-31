from google.cloud import datastore

from constants import Constants as C
from unit import Unit

datastore_client = datastore.Client()
class Legion:
    _unit = Unit()

    def removeUnits(self,id):
        query = datastore_client.query(kind=C.kindB)
        key = datastore_client.key(C.kindB, int(id))
        query.key_filter(key)
        entities = query.fetch()
        subEntityIDs = None
        for entity in entities:
            subEntityIDs = entity[C.kindAGen]
            for subId in subEntityIDs:
                self._unit.remove(subId)

    def legionFromUnit(self,unit_id):
        query = datastore_client.query(kind=C.kindB)
        query.add_filter('units', '=', unit_id)
        entities = query.fetch()
        for entity in entities:
            return entity.key.id_or_name
        return None

    def count(self,userId):
        query = datastore_client.query(kind=C.kindB)
        query.add_filter('owner', '=', userId)
        query.keys_only()
        entities = query.fetch()
        count = 0
        for entity in entities:
            count+=1
        return count

    def exists(self, id):
        query = datastore_client.query(kind=C.kindB)
        query.keys_only()
        entities = query.fetch()
        for entity in entities:
            return True
        return False

    def getOwner(self,id):
        query = datastore_client.query(kind=C.kindB)
        key = datastore_client.key(C.kindB, int(id))
        query.key_filter(key)
        entities = query.fetch()
        for entity in entities:
            return entity.get('owner',-1)
        return -1

    def getOne(self,request,id):
        query = datastore_client.query(kind=C.kindB)
        key = datastore_client.key(C.kindB, int(id))
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

    def store(self, name, level, terrainBonus, userId):
        key = datastore_client.key(C.kindB)
        entity = datastore.Entity(key=key)
        entity.update({
            "name": name, 
            "level": level, 
            "terrainBonus": terrainBonus,             
            "units": [],
            "owner": userId,
        })
        try: 
            datastore_client.put(entity)
        except Exception as err: 
            print(err)
            return -1
        return entity.key.id_or_name
    
    def delete(self,id):
        key = datastore_client.key(C.kindB, int(id))
        if datastore_client.get(key) is not None:
            self.removeUnits(id)
            datastore_client.delete(key)
            return 204
        else:
            return 401

    def update(self, id, name, level, terrainBonus, userId):
        query = datastore_client.query(kind=C.kindB)
        key = datastore_client.key(C.kindB, int(id))
        query.key_filter(key)
        entities = query.fetch()
        for entity in entities:
            entity.update({
                "name": name, 
                "level": level, 
                "terrainBonus": terrainBonus,             
                "owner": userId,
            })
            datastore_client.put(entity)
            return entity    
        return None

    def putUnit(self, id, unitId):
        query = datastore_client.query(kind=C.kindB)
        key = datastore_client.key(C.kindB, int(id))
        query.key_filter(key)
        entities = query.fetch()
        for entity in entities:
            units = set(entity.get('units',[]))
            units.add(unitId)
            self._unit.put(id,unitId)
            entity.update({
                "units": list(units),
            })
            datastore_client.put(entity)
            return entity    
        return None

    def deleteUnit(self,id,unitId):
        query = datastore_client.query(kind=C.kindB)
        key = datastore_client.key(C.kindB, int(id))
        query.key_filter(key)
        entities = query.fetch()
        for entity in entities:
            units = entity.get('units',[])
            self._unit.remove(unitId)
            units.remove(unitId)
            entity.update({
                "units": units,
            })
            datastore_client.put(entity)
            return entity    
        return None
    
    def get(self,request,userId):
        limit = C.limit
        offset = int(request.args.get('offset', '0'))
        query = datastore_client.query(kind=C.kindB)
        query.add_filter('owner', '=', userId)
        iterator = None
        entities = None
        nextUri = None
        try: 
            iterator = query.fetch(limit=limit, offset=offset)
            pages = iterator.pages
            entities = list(next(pages))
        except:
            print('Failed to fetch ' + C.kindB)
        for entity in entities:
            entity.update({"id":entity.key.id_or_name})
            selfUri = request.base_url + '/' + str(entity.key.id_or_name)
            entity.update({"self":selfUri})
            if iterator.next_page_token:
                nextUri = request.base_url + '?offset=' + str(offset + limit)
        if nextUri is not None:
            response = {C.kindBGen:entities,"count":self.count(userId),"next":nextUri}
        else:
            response = {C.kindBGen:entities,"count":self.count(userId)}
        return response

    def getSubentities(self,request,id):
        query = datastore_client.query(kind=C.kindB)
        key = datastore_client.key(C.kindB, int(id))
        query.key_filter(key)
        entities = query.fetch()
        response = None
        subEntityIDs = None
        subEntities = []
        for entity in entities:
            subEntityIDs = entity['units']
            for id in subEntityIDs:
                head, part, tail = request.base_url.partition('/legions')
                request.base_url = (head + '/units')
                subEntity = self._unit.getOne(request,id)
                subEntity.update({"id":id})
                subEntities.append(subEntity)
            response = {C.kindAGen:subEntities}
        return response