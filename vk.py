import vk_api
import datetime
import getpass


GET_POSTS_COMMAND = 'posts'


class ConsoleVK:
    def __init__(self):
        login, password = input('Telephone number: '), getpass.getpass()
        self.vk_session = vk_api.VkApi(login, password, auth_handler=self.two_factor_authentication_handler)
        self.user = ''
        self.count = 0

        try:
            self.vk_session.auth(token_only=True)
        except vk_api.AuthError as error_msg:
            print(error_msg)
            return

        self.vk = self.vk_session.get_api()

        self.COMMANDS = {
            'friends': self.get_list_of_friends,
            'albums': self.get_list_of_albums_names,
            'groups': self.get_list_of_groups,
            GET_POSTS_COMMAND: self.get_posts
        }

    def run(self):
        while True:
            request = input('Enter command: ').split()
            command = request[0]
            if command == GET_POSTS_COMMAND:
                try:
                    command, self.user, self.count = request
                except ValueError:
                    self.user = None
                    self.count = request[1]
            else:
                try:
                    command, self.user = request
                except ValueError:
                    self.user = None
            try:
                print('\n'.join(self.COMMANDS[command]()))
            except KeyError:
                print('Incorrect command')

    def get_list_of_friends(self):
        if self.user is None:
            friends = self.vk.friends.get(order='name', fields='first_name,last_name')['items']
        else:
            friends = self.vk.friends.get(user_id=int(self.user), order='name', fields='first_name,last_name')['items']
        return list(map(lambda friend: f"{friend['first_name']} {friend['last_name']} | id: {friend['id']}", friends))

    def get_list_of_albums_names(self):
        if self.user is None:
            albums = self.vk.photos.getAlbums()['items']
        else:
            albums = self.vk.photos.getAlbums(owner_id=int(self.user))['items']
        return list(map(lambda album: f"{album['title']}", albums))

    def get_list_of_groups(self):
        if self.user is None:
            groups = self.vk.groups.get(order='name', fields='name,type', extended=1)['items']
        else:
            groups = self.vk.groups.get(order='name', fields='name,type', user_id=int(self.user), extended=1)['items']
        return list(map(lambda group: f"{group['name']} | type: {group['type']} | id: {group['id']}", groups))

    def get_posts(self):
        if self.user is None:
            posts = self.vk.wall.get(count=self.count, fields='from_id,date,text', extended=1)['items']
        else:
            posts = self.vk.wall.get(count=self.count, fields='from_id,date,text', owner_id=int(self.user),
                                     extended=1)['items']
        res = []
        for post in posts:
            from_id = post['from_id']
            user = self.vk.users.get(user_ids=from_id, fields='first_name,last_name')[0]
            timestamp = post['date']
            date = datetime.datetime.fromtimestamp(timestamp)
            res.append(f"from: {user['first_name']} {user['last_name']}\ndate: {date}\n {post['text']}\n")
        return res

    @staticmethod
    def two_factor_authentication_handler():
        code = input("Enter auth code: ")
        remember_device = True
        return code, remember_device


def main():
    ConsoleVK().run()


if __name__ == '__main__':
    main()
