class UsersDB():
    users_list=[{"user":"mario","password":"mario1"},{"user":"peach","password":"peach1"},{"user": "messi", "password": "surabaya"},{"user" :"lineker", "password": "surabaya"}, {"user" :"henderson", "password": "surabaya"}]

    def read_db(self,user_name:str,password:str):
        #print("Iniciando sesion.... ")
        for i in self.users_list:
            if (i["user"]==user_name and i["password"]==password):
                return True
        return False

    def write_db(self,user_name:str,password:str):
        self.users_list.append({"user":user_name,"password":password})
        return True