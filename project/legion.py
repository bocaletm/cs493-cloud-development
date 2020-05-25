from google.cloud import datastore

from constants import Constants as C
from unit import Unit

datastore_client = datastore.Client()
class Legion:
    _unit = Unit()

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
            return entity['owner']
        return -1

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
            units = entity.get('units',[])
            units.append(unitId)
            entity.update({
                "units": units,
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
            if iterator.next_page_token:
                nextUri = request.base_uri + '?offset=' + str(offset + limit)
                entity.update({"next":nextUri})
        if nextUri is not None:
            response = {C.kindBGen:entities,"next":nextUri}
        else:
            response = {C.kindBGen:entities}
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
                subEntity = self._unit.getOne(id)
                subEntity.update({"id":id})
                subEntities.append(subEntity)
            response = {C.kindAGen:subEntities}
        return response