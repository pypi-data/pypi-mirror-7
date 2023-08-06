from collections import defaultdict
import pandas as pd
import numpy as np
from time import time

class Recommender(object):
    """
    Cold Start Recommender
    """
    def __init__(self, mongo_host=None, mongo_db_name=None, mongo_replica_set=None, default_rating=3, min_rating=1, max_rating=5):
        if mongo_host is not None:
            from pymongo import MongoClient
            assert (mongo_db_name != None)
            if mongo_replica_set is not None:
                from pymongo import MongoReplicaSetClient
                mongo_client = MongoReplicaSetClient(mongo_host, replicaSet=mongo_replica_set)
                self.db = mongo_client[mongo_db_name]
            else:
                mongo_client = MongoClient(mongo_host)
                self.db = mongo_client[mongo_db_name]
        else:
            self.db = None
        self.info_used = set() # Info used in addition to item_id. It is filled each time an item is inserted with item_info
        self.default_rating = default_rating
        self.min_rating = min_rating
        self.max_rating = max_rating
        self._items_cooccurence = pd.DataFrame  # cooccurrence of items
        self._categories_cooccurence = {} # cooccurrence of categories
        self.cooccurence_updated = 0.0
        self.item_ratings = defaultdict(dict)  # matrix of ratings for a item
        self.user_ratings = defaultdict(dict)  # matrix of ratings for a user
        self.items = defaultdict(dict)  # matrix of item's information {item_id: {"cat1": "my_cat"....}
        # categories --same as above, but separated as they are not always available
        self.tot_categories_user_ratings = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        self.tot_categories_item_ratings = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        self.n_categories_user_ratings = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        self.n_categories_item_ratings = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        self.items_by_popularity = []
        self.items_by_popularity_updated = 0.0

    def _coll_name(self, k, typ):
        """
        e.g. user_author_ratings
        """
        return str(typ) + '_' + str(k) + '_ratings'


    def _create_cooccurence(self):
        """
        Create or update the co-occurence matrix
        :return:
        """
        df_tot_cat_item = {}
        # TO BE DELETED df_n_cat_item = {}
        if not self.db:
            # Items' vectors
            df_item = pd.DataFrame(self.item_ratings).fillna(0).astype(int)
            # Categories' vectors
            if len(self.info_used) > 0:
                for i in self.info_used:
                    df_tot_cat_item[i] = pd.DataFrame(self.tot_categories_item_ratings[i]).fillna(0).astype(int)
        else:  # read if from Mongodb
            # here we *must* use user_ratings, so indexes are the users, columns the items...
            df_item = pd.DataFrame.from_records(list(self.db['user_ratings'].find())).set_index('_id').fillna(0).astype(int)
            if len(self.info_used) > 0:
                for i in self.info_used:
                    user_coll_name = self._coll_name(i, 'user')
                    if self.db['tot_' + user_coll_name].find_one():
                        df_tot_cat_item[i] = pd.DataFrame.from_records(list(self.db['tot_' + user_coll_name].find())).set_index('_id').fillna(0).astype(int)
        df_item = (df_item / df_item).replace(np.inf, 0)  # normalize to one to build the co-occurence
        self._items_cooccurence = df_item.T.dot(df_item)
        if len(self.info_used) > 0:
            for i in self.info_used:
                if type(df_tot_cat_item.get(i)) == pd.DataFrame:
                    df_tot_cat_item[i] = (df_tot_cat_item[i] / df_tot_cat_item[i]).replace(np.inf, 0)
                    self._categories_cooccurence[i] = df_tot_cat_item[i].T.dot(df_tot_cat_item[i])
        self.cooccurence_updated = time()


    def insert_item(self, item, _id="_id"):
        """
        Insert the whole document either in self.items or in db.items
        :param item: {_id: item_id, cat1: ...} or {item_id_key: item_id, cat1: ....}
        :return: None
        """
        if not self.db:
            self.items[item[_id]] = item
        else:
            for k, v in item.items():
                if k is not "_id":
                    self.db["items"].update({"_id": item[_id]},
                                            {"$set": {k: v}},
                                            upsert=True)


    def reconcile_ids(self, id_old, id_new):
        """
        Create id_new if not there, add data of id_old into id_new.
        Compute the co-occurence matrix.
        NB id_old is removed!
        :param id_new:
        :param id_old:
        :return: None
        """
        id_new = str(id_new).replace(".", "")
        id_old = str(id_old).replace(".", "")
        if not self.db:
            # user-item
            for key, value in self.user_ratings[id_old].items():
                self.user_ratings[id_new][key] = self.user_ratings[id_old][key]
            self.user_ratings.pop(id_old)

            for k, v in self.item_ratings.items():
                if v.has_key(id_old):
                    v[id_new] = v.pop(id_old)
            # user-categories
            if len(self.info_used) > 0:
                for i in self.info_used:
                    for key, value in self.tot_categories_user_ratings[i][id_old].items():
                        self.tot_categories_user_ratings[i][id_new][key] = self.tot_categories_user_ratings[i][id_old][key]
                    self.tot_categories_user_ratings[i].pop(id_old)

                    for k, v in self.tot_categories_item_ratings[i].items():
                        if v.has_key(id_old):
                            v[id_new] = v.pop(id_old)

                    for key, value in self.n_categories_user_ratings[i][id_old].items():
                        self.n_categories_user_ratings[i][id_new][key] = self.n_categories_user_ratings[i][id_old][key]
                    self.n_categories_user_ratings[i].pop(id_old)

                    for k, v in self.n_categories_item_ratings[i].items():
                        if v.has_key(id_old):
                            v[id_new] = v.pop(id_old)
        else:  # work on mongo...
            user_ratings = self.db['user_ratings'].find_one({"_id": id_old}, {"_id": 0})
            if user_ratings:
                for key, value in user_ratings.items():
                    self.db['user_ratings'].update(
                        {"_id": id_new},
                        {"$set": {key: value}},
                        upsert=True
                    )
                self.db['user_ratings'].remove({"_id": id_old})

            self.db['item_ratings'].update(
                {id_old: {"$exists": True}},
                {"$rename": {id_old: id_new}},
                multi=True
            )

            if len(self.info_used) > 0:
                for k in self.info_used:
                    users_coll_name = self._coll_name(k, 'user')
                    items_coll_name = self._coll_name(k, 'item')
                    # tot and n user ratings....
                    tot_user_ratings = self.db['tot_' + users_coll_name].get({"_id": id_old})
                    if tot_user_ratings:
                        for key, value in tot_user_ratings.items():
                            self.db['tot_' + users_coll_name].update(
                                {"_id": id_new},
                                {"$set": {key: value}},
                                upsert=True
                            )
                        self.db['tot_' + users_coll_name].remove({"_id": id_old})
                    n_user_ratings = self.db['n_' + users_coll_name].get({"_id": id_old})
                    if n_user_ratings:
                        for key, value in n_user_ratings.items():
                            self.db['n_' + users_coll_name].update(
                                {"_id": id_new},
                                {"$set": {key: value}},
                                upsert=True
                            )
                        self.db['n_' + users_coll_name].remove({"_id": id_old})

                    self.db['tot_' + items_coll_name].update(
                        {id_old: {"$exists": True}},
                        {"$rename": {"id_new": "id_old"}},
                        multi=True
                    )

                    self.db['n_' + items_coll_name].update(
                        {id_old: {"$exists": True}},
                        {"$rename": {"id_new": "id_old"}},
                        multi=True
                    )
        self._create_cooccurence()


    def compute_items_by_popularity(self, fast=False):
        """
        As per name, get self.
        :return: list of popular items, 0=most popular
        """
        if fast and (time() - self.most_popular_items_updated) < 3600:
            return self.items_by_popularity

        if not self.db:
            df_item = pd.DataFrame(self.item_ratings).fillna(0).astype(int).sum()

        else:  # read if from Mongodb
            df_item = pd.DataFrame.from_records(list(self.db['user_ratings'].find())).set_index('_id').sum()

        df_item.sort(ascending=False)
        self.items_by_popularity = list(df_item.index)


    def get_similar_item(self, item_id, user_id=None, algorithm='simple'):
        """
        Simple: return the row of the co-occurence matrix ordered by score or,
        if user_id is not None, multiplied times the user_id rating
        (not transposed!) so to weigh the similarity score with the
        rating of the user
        :param item_id: Id of the item
        :param user_id: Id of the user
        :param algorithm: keep it simple...
        :return:
        """
        user_id = str(user_id).replace('.', '')
        pass


    def remove_rating(self, user_id, item_id):
        """
        Remove ratings from item and user. This cannot be undone for categories
        (only thing we could do is subtracting the average value from sum and n-1)
        :param user_id:
        :param item_id:
        :return:
        """
        user_id = str(user_id).replace('.', '')
        if not self.db:
            self.user_ratings[user_id].pop(item_id, None)
            self.item_ratings[item_id].pop(user_id, None)
            self.items[item_id] = {}  # just insert the bare id. quite useless because it is a defaultdict, but in case .keys() we can count the # of items
        else:
            self.db['user_ratings'].remove(
                {"_id": user_id, item_id: {"$exists": True}})

            self.db['item_ratings'].remove(
                {"_id": item_id, user_id: {"$exists": True}})


    def insert_rating(self, user_id, item_id, rating=3, item_info=[], only_info=False):
        """
        item is treated as item_id if it is not a dict, otherwise we look
        for a key called item_id_key if it is a dict.

        item_info can be any further information given with the dict item.
        e.g. author, category etc

        NB NO DOTS IN user_id, or they will taken away. Fields in mongodb cannot have dots..

        If only_info==True, only the item_info's are put in the co-occurence, not item_id.
         This is necessary when we have for instance a "segmentation page" where we propose
         well known items to get to know the user. If s/he select "Harry Potter" we only want
         to retrieve the info that s/he likes JK Rowling, narrative, magic etc

        :param user_id: id of user. NO DOTS, or they will taken away. Fields in mongodb cannot have dots.
        :param item: is either id or a dict with item_id_key
        :param rating: float parseable
        :param item_info: any info given with dict(item), e.g. ['author', 'category', 'subcategory']
        :param only_info: not used yet
        :return: [recommended item_id_values]
        """
        # If only_info==True, only the item_info's are put in the co-occurence, not item_id.
        # This is necessary when we have for instance a "segmentation page" where we propose
        # well known items to get to know the user. If s/he select "Harry Potter" we only want
        # to retrieve the info that s/he likes JK Rowling, narrative, magic etc

        # Now fill the dicts or the Mongodb collections if available
        user_id = str(user_id).replace('.', '')
        if not self.db:   # fill dicts and work only in memory
            if self.items.get(item_id):
                item = self.items.get(item_id)
                # Do categories only if the item is stored
                if len(item_info) > 0:
                    for k,v in item.items():
                        if k in item_info:
                            self.info_used.add(k)
                            # we cannot set the rating, because we want to keep the info
                            # that a user has read N books of, say, the same author,
                            # category etc.
                            # We could sum all the ratings and count the a result as "big rating".
                            # Reading N books of author A and rating them 5 would be the same as reading
                            # 5*N books of author B and rating them 1.
                            # Still:
                            # 1) we don't want ratings for category to skyrocket, so we have to take the average
                            # 2) if a user changes their idea on rating a book, it should not add up. Average
                            #   is not perfect, but close enough. Take total number of ratings and total rating
                            self.tot_categories_user_ratings[k][user_id][v] += int(rating)
                            self.n_categories_user_ratings[k][user_id][v] += 1
                            # for the co-occurence matrix is not necessary to do the same for item, but better do it
                            # in case we want to compute similarities etc using categories
                            self.tot_categories_item_ratings[k][v][user_id] += int(rating)
                            self.n_categories_item_ratings[k][v][user_id] += 1
            else:
                self.insert_item({"_id": item_id})
            # Do item always, at least is for categories profiling
            if not only_info:
                self.user_ratings[user_id][item_id] = float(rating)
                self.item_ratings[item_id][user_id] = float(rating)
        # MongoDB
        else:
            # Do categories only if the item is found stored
            if self.db['items'].find_one({"_id": item_id}):
                item = self.db['items'].find_one({"_id": item_id})
                if len(item_info) > 0:
                    for k, v in item.items():
                        if k in item_info and v is not None:  # sometimes the value IS None
                            users_coll_name = self._coll_name(k, 'user')
                            items_coll_name = self._coll_name(k, 'item')
                            self.info_used.add(k)
                            # see comments above
                            self.db['tot_' + users_coll_name].update({'_id': user_id},
                                                                     {'$inc': {v: float(rating)}},
                                                                      upsert=True)
                            self.db['n_' + users_coll_name].update({'_id': user_id},
                                           {'$inc': {v: 1}},
                                            upsert=True)
                            self.db['tot_' + items_coll_name].update({'_id': v},
                                           {'$inc': {user_id: float(rating)}},
                                            upsert=True)
                            self.db['n_' + items_coll_name].update({'_id': v},
                                           {'$inc': {user_id: 1}},
                                            upsert=True)
                            self.db['items'].update(
                                {"_id": item_id},
                                {"$set": {k: v}},
                                upsert=True
                            )
            else:
                self.insert_item({"_id": item_id})  # Obviously there won't be categories...

            if not only_info:
                self.db['user_ratings'].update(
                    {"_id": user_id},
                    {"$set": {item_id: float(rating)}},
                    upsert=True
                )
                self.db['item_ratings'].update(
                    {"_id": item_id},
                    {"$set": {user_id: float(rating)}},
                    upsert=True
                )


    def get_recommendations(self, user_id, max_recs=50, fast=False, algorithm='item_based'):
        """
        algorithm item_based:
            - Compute recommendation to user using item co-occurence matrix (if the user
            rated any item...)
            - If there are less than max_recs recommendations, the remaining
            items are given according to popularity. Scores for the popular ones
            are given as
                            score[last recommended]*index[last recommended]/n
            where n is the position in the list.
            - Recommended items above receive a further score according to categories
        :param user_id: the user id as in the mongo collection 'users'
        :param max_recs: number of recommended items to be returned
        :param fast: Compute the co-occurence matrix only if it is one hour old or
                     if matrix and user vector have different dimension
        :return: list of recommended items
        """
        user_id = str(user_id).replace('.', '')
        df_tot_cat_user = {}
        df_n_cat_user = {}
        rec = pd.Series()
        item_based = False  # has user rated some items?
        info_based = []  # user has rated the category (e.g. the category "author" etc)
        if not self.db:
            if self.user_ratings.get(user_id):  # compute item-based rec only if user has rated smt
                item_based = True
                #Just take user_id for the user vector
                df_user = pd.DataFrame(self.user_ratings).fillna(0).astype(int)[[user_id]]
            if len(self.info_used) > 0:
                for i in self.info_used:
                    if self.tot_categories_user_ratings[i].get(user_id):
                        info_based.append(i)
                        df_tot_cat_user[i] = pd.DataFrame(self.tot_categories_user_ratings[i]).fillna(0).astype(int)[[user_id]]
                        df_n_cat_user[i] = pd.DataFrame(self.n_categories_user_ratings[i]).fillna(0).astype(int)[[user_id]]
        else:  # read if from Mongodb
            if self.db['user_ratings'].find_one({"_id": user_id}):
                item_based = True
                #Take only user_id
                df_user = pd.DataFrame.from_records(list(self.db['item_ratings'].find())).set_index('_id').fillna(0).astype(int)[[user_id]]
            if len(self.info_used) > 0 and False: #XXX
                for i in self.info_used:
                    item_coll_name = self._coll_name(i, 'item')
                    if self.db['tot_' + item_coll_name].find_one({"_id": user_id}):
                        info_based.append(i)
                        df_tot_cat_user[i] = pd.DataFrame.from_records(list(self.db['tot_' + item_coll_name].find())).set_index('_id').fillna(0).astype(int)[[user_id]]
                        df_n_cat_user[i] = pd.DataFrame.from_records(list(self.db['n_' + item_coll_name].find())).set_index('_id').fillna(0).astype(int)[[user_id]]
        if item_based:
            if not fast or (time() - self.cooccurence_updated > 3600):
                self._create_cooccurence()
            try:
                # this might fail for fast in case a user has rated an item
                # but the co-occurence matrix has not been updated
                # therefore the matrix and the user-vector have different
                # dimension
                rec = self._items_cooccurence.T.dot(df_user[user_id])
            except:
                self._create_cooccurence()
                rec = self._items_cooccurence.T.dot(df_user[user_id])
            # Add to rec items according to popularity
            rec.sort(ascending=False)

            if len(rec) < max_recs:
                self.compute_items_by_popularity(fast)
                for v in self.items_by_popularity:
                    if len(rec) == max_recs:
                        break
                    elif v not in rec.index:
                        n = len(rec)
                        rec.set_value(v, rec.values[n - 1]*n/(n+1))  # supposing score goes down according to Zipf distribution
        else:
            self.compute_items_by_popularity(fast)
            for i, v in enumerate(self.items_by_popularity):
                if len(rec) == max_recs:
                    break
                rec.set_value(v, self.max_rating / (i+1))  # As comment above, starting from max_rating

        # Now, the worse case we have rec=popular with score starting from max_rating
        # and going down as 1/i (this is item_based == False)

        global_rec = rec.copy()
        if len(self.info_used) > 0:
            cat_rec = {}
            for cat in info_based:
                user_vec = df_tot_cat_user[cat][user_id] / df_n_cat_user[cat][user_id].replace(0, 1)
                try:
                    cat_rec[cat] = self._categories_cooccurence[cat].T.dot(user_vec)
                    cat_rec[cat].sort(ascending=False)
                except:
                    self._create_cooccurence()
                    cat_rec[cat] = self._categories_cooccurence[cat].T.dot(user_vec)
                    cat_rec[cat].sort(ascending=False)
                for k, v in rec.iteritems():
                    try:
                        if not self.db:
                            item_info_value = self.items[k][cat]
                        else:
                            item_info_value = self.db['items'].find_one({"_id": k}, {"_id": 0, cat: 1})[cat]
                        global_rec[k] = v + cat_rec[cat][item_info_value]
                    except:
                        print "ERROR on item", k, ", category", cat
        global_rec.sort(ascending=False)
        #return list(rec[df_user[user_id] == 0].index)
        if item_based:
            # list(rec[df_user[user_id] == 0].index)[:max_recs],
            return list(global_rec[df_user[user_id] == 0].index)[:max_recs]
        else:
            # list(rec.index)[:max_recs]
            return list(global_rec.index)[:max_recs]


    def get_user_info(self, user_id):
        """
        Return user's rated items: {'item1': 3, 'item3': 1...}
        :param user_id:
        :return:
        """
        if self.db:
            r = self.db['user_ratings'].find_one({"_id": user_id}, {"_id": 0})
            return r if r else {}
        else:
            return self.user_ratings[user_id]
