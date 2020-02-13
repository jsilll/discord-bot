class json_user():
    
    def __init__(self, data):
        if isinstance(data, dict) and len(data) == 4:
            expected_keys = ["name", "xp", "admin", "last_vc"]
            for key in expected_keys:
                if key not in data:
                    raise ValueError("json_ user: wrong data format")
            self.name = data["name"]
            self.xp = data["xp"]
            self.admin = data["admin"]
            self.last_vc = data["last_vc"]
        else:
            raise ValueError("json_ user: wrong data format")
        

    def get_name(self):
        return self.name

    def set_name(self, name):
        if isinstance(name, str):
            self.name = name
        else:
            raise ValueError("name: argument must be string.")
    

    def get_xp(self):
        return self.xp

    def set_xp(self, xp):
        if isinstance(xp, int) and xp > 0:
            self.xp = xp
        else:
            raise ValueError("xp: argument must be int > 0.")


    def is_admin(self):
        return self.admin

    def set_admin(self, boolean):
        if isinstance(boolean, bool):
            self.admin = boolean
        else:
            raise ValueError("admin: argument must be boolean.")


    def get_last_vc(self):
        return self.last_vc

    def set_last_vc(self, datetime):
        if isinstance(datetime, str):
            self.last_vc = datetime
        else:
            raise ValueError("last_vc: argument must be a string.")
    

    def dict(self):
        res = {}
        res["name"] = self.name
        res["xp"] = self.xp
        res["admin"] = self.admin
        res["last_vc"] = self.last_vc
        return res

class json_channel():
    
    def __init__(self, data):
        if isinstance(data, dict) and len(data) == 1:
            expected_keys = ["listened"]
            for key in expected_keys:
                if key not in data:
                    raise ValueError("json_channel: wrong data format")
            self.listened = data["listened"]
        else:
            raise ValueError("json_channel: wrong data format.")
    

    def is_listened(self):
        return self.listened
    
    def set_listened(self, boolean):
        if isinstance(boolean, bool):
            self.listened = boolean
        else:
            raise ValueError("set_listened: argument must be a boolean.")


    def dict(self):
        res = {}
        res["listened"] = self.listened
        return res

class json_guild():
    
    def __init__(self, data):
        if isinstance(data, dict) and len(data) == 6:
            expected_keys = ["id", "name", "prefix", "users", "channels", "games"]
            for key in expected_keys:
                if key not in data:
                    raise ValueError("json_guild: wrong data format.")
            self.id = data["id"]
            self.name = data["name"]
            self.prefix = data["prefix"]

            self.users = {}
            for user_id in data["users"]:
                self.users[user_id] = json_user(data["users"][user_id])
            self.channels = {}
            for channel_name in data["channels"]:
                self.channels[channel_name] = json_channel(data["channels"][channel_name])            
            self.games = data["games"]

    def get_id(self):
        return self.id

    def set_id(self, string):
        if isinstance(string, str):
            self.id = string
        else:
            raise ValueError("id: argument must be an str.")


    def get_name(self):
        return self.name
    
    def set_name(self, name):
        if isinstance(name, str):
            self.name = name
        else:
            raise ValueError("name: argument must a string.")


    def get_prefix(self):
        return self.prefix
    
    def set_prefix(self, prefix):
        if isinstance(prefix, str):
            self.prefix = prefix
        else:
            raise ValueError("set_prefix: argument must be a str.")


    def get_users(self):
        res = []
        for user_id in self.users:
            res.append(user_id)
        return res

    def get_user(self, user_id):
        if isinstance(user_id, str):
            return self.users[user_id]
        else:
            raise ValueError("user: user_id must be a string.")
    
    def add_user(self, user_id, user_obj):
        if isinstance(user_id, str) and isinstance(user_obj, json_user):
            self.users[user_id] = user_obj
        else:
            raise ValueError("add_user: user_obj must a json_user object.")


    def get_channels(self):
        res = []
        for channel in self.channels:
            res.append(channel)
        return res

    def get_channel(self, channel_name):
        return self.channels[channel_name]

    def add_channel(self, channel_name, channel_obj):
        if isinstance(channel_name, str) and isinstance(channel_obj, json_channel):
            self.channels[channel_name] = channel_obj
        else:
            raise ValueError("add_channel: wrong data format.")

    def remove_channel(self, channel_name):
        if channel_name in self.channels:
            del self.channels[channel_name]
        else:
            raise ValueError("remove_channel: channel name not in self.channels.")
    

    def get_games(self):
        return self.games
    
    def add_game(self, new_game):
        if isinstance(new_game, str) and new_game not in self.games:
            self.games.append(new_game)

    def remove_game(self, game):
        if isinstance(game, str) and game in self.games:
            del self.games[self.games.index(game)]


    def dict(self):
        res = {}
        res["id"] = self.id
        res["name"] = self.name
        res["prefix"] = self.prefix
        res["users"] = {}
        for user_id in self.users:
            res["users"][user_id] = self.users[user_id].dict()
        res["channels"] = self.channels
        for channel_name in self.channels:
            res["channels"][channel_name] = self.channels[channel_name].dict()
        res["games"] = self.games
        return res