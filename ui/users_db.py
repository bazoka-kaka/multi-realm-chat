class UsersDB():
    users_list=[{"user":"mario","password":"mario1"},{"user":"peach","password":"peach1"},{"user": "messi", "password": "surabaya"},{"user" :"lineker", "password": "surabaya"}, {"user" :"henderson", "password": "surabaya"}]
    groups_list=[{"name": "test", "messages": []}]
    
    def read_group(self,group_name:str):
        for i in self.groups_list:
            if i['name'] == group_name:
                return True
        return False
    
    def get_messages(self,group_name):
        for i in self.groups_list:
            if i['name'] == group_name:
                return i['messages']
        return False
    
    def set_messages(self,group_name:str,group_messages):
        for index, i in enumerate(self.groups_list):
            if i['name'] == group_name:
                self.groups_list[index] = {"name": group_name, "messages": group_messages}
                return True
        return False
    
    def write_group(self,group_name:str):
        self.groups_list.append({"name": group_name, "messages": []})
        return True

    def read_db(self,user_name:str,password:str):
        #print("Iniciando sesion.... ")
        for i in self.users_list:
            if (i["user"]==user_name and i["password"]==password):
                return True
        return False

    def write_db(self,user_name:str,password:str):
        self.users_list.append({"user":user_name,"password":password})
        return True