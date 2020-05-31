from google.cloud import datastore
import time

from constants import Constants as C
from unit import Unit


datastore_client = datastore.Client()

class User:
    def count(self):
        query = datastore_client.query(kind=C.kindC)
        query.keys_only()
        entities = query.fetch()
        count = 0
        for entity in entities:
            count+=1
        return count

    def get(self,request): 
        limit = C.limit
        offset = int(request.args.get('offset', '0'))
        query = datastore_client.query(kind=C.kindC)
        iterator = None
        entities = None
        nextUri = None
        try: 
            iterator = query.fetch(limit=limit, offset=offset)
            pages = iterator.pages
            entities = list(next(pages))
        except:
            print('Failed to fetch ' + C.kindC)
        for entity in entities:
            entity.update({"id":entity.key.id_or_name})
            selfUri = request.base_url + '/' + str(entity.key.id_or_name)
            entity.update({"self":selfUri})
            if iterator.next_page_token:
                nextUri = request.base_url + '?offset=' + str(offset + limit)
        if nextUri is not None:
            response = {C.kindCGen:entities,"count":self.count(),"next":nextUri}
        else:
            response = {C.kindCGen:entities,"count":self.count()}
        return response

    def conditionalCreate(self,user_id):
        query = datastore_client.query(kind=C.kindC)
        query.add_filter('sub', '=', user_id)
        entities = query.fetch()
        for entity in entities:
            entity.update({
                "lastLogin": int(time.time())
            })
            try: 
                datastore_client.put(entity)
                return 1
            except Exception as err: 
                print(err)
                return -1
        key = datastore_client.key(C.kindC)
        entity = datastore.Entity(key=key)
        entity.update({
            "sub": user_id, 
            "budget": C.startingBudget,
            "lastLogin": int(time.time())
        })
        try: 
            datastore_client.put(entity)
            return 2
        except Exception as err: 
            print(err)
            return -1