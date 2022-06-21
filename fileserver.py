import tornado.ioloop
import tornado.web
import os

root_path = "<YOUR-PATH>"
path = ""
dir_list = os.listdir("part/")

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")
        

class MainHandler(BaseHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")
        
    def check_user(self):
        username = ""
        if self.current_user:
            username = tornado.escape.xhtml_escape(self.current_user)
        return username;

    def get(self):
        global dir_list
        global path
        self.render("index.html", title=f"{path}", dirs = get_dirs(dir_list), files = get_files(dir_list), user = self.check_user())
        
    def post(self):
        global dir_list
        global path
        
        if self.get_argument("upload", None) != None:
            print("post")
            file = self.request.files['filearg'][0]
            original_fname = file['filename']
            output_file = open(path + original_fname, 'wb')
            output_file.write(file['body'])
            dir_list = os.listdir(path)
            self.render("index.html", title=f"{path}", dirs = get_dirs(dir_list), files = get_files(dir_list), user = self.check_user())
        
        if self.get_argument("back_Button", None) != None:
            if (path != root_path):
                path = os.path.split(path[:-1])[0] + '/'
            dir_list = os.listdir(path)
            self.render("index.html", title=f"{path}", dirs = get_dirs(dir_list), files = get_files(dir_list), user = self.check_user())
            
        for item in dir_list:
            if self.get_argument(item, None) != None:
                path = path + item + "/"
                dir_list = os.listdir(path)
                self.render("index.html", title=f"{path}", dirs = get_dirs(dir_list), files = get_files(dir_list), user = self.check_user())


class DownloadHandler(tornado.web.RequestHandler):
    def get(self, file):
        print('i download file handler : ',file)
        ifile  = open(path + file, "rb")
        self.set_header ('Content-Type', 'application/octet-stream')
        self.set_header ("Content-Disposition", f"attachment; filename={file}")
        self.write (ifile.read())
        
        
class LoginHandler(BaseHandler):
    def get(self):
        self.write('<html><body><h2>Login</h2><form action="/login" method="post">'
                   'Name: <input type="text" name="name"><br>'
                   'Password: <input type="password" name="password"><br>'
                   '<input type="submit" value="Sign in"><br>'
                   '</form></body></html>')
    def post(self):
        if self.get_argument("name") == "admin" and self.get_argument("password") == "admin":
            self.set_secure_cookie("user", self.get_argument("name"))
            self.redirect("/")
        else:
            self.write('<html><body><h2>Login</h2><form action="/login" method="post">'
                   'Name: <input type="text" name="name"><br>'
                   'Password: <input type="password" name="password"><br>'
                   '<b style="color:red;">Wrong login or password</b><br>'
                   '<input type="submit" value="Sign in"><br>'
                   '</form></body></html>')
        

class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect(self.get_argument("next", "/"))
                
        
def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/download/(.*)",  DownloadHandler),
        (r"/login", LoginHandler),
        (r"/logout", LogoutHandler)
    ], cookie_secret="n345jn45k3n53k54j34j5n32n")
    
def get_dirs(list_all):
	global path
	dirs = []
	for item in list_all:
		if os.path.isdir(path + item):
			dirs.append(item)
	return dirs
	
def get_files(list_all):
	global path
	files = []
	for item in list_all:
		if os.path.isfile(path + item):
			files.append(item)
	return files

if __name__ == "__main__":
    path = root_path
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
