class Parser():
    def new_bullet(classargs, playerid):
        args = ''
        for i in classargs:
            if isinstance(i, tuple):
                x = ''
                for a in i:
                    x += str(a) + '/'
                i = x
            args += str(i) + ','
        data = "new_bullet;" + args + ";" + playerid
        return data
    def parse(data, player_id):
        #find type
        data.replace('Empty', '')
        print(data)
        try:
            header = data.split(';')[0]
            data = data.split(';')[1]
            playerid = data.split(';')[2]
        except:
            header = 'None'
            data = data
            playerid = 'Unknown'

        if header.find('new_bullet'):
            data = data.split(',')
            return [header, data, playerid]
        else:
            return [header, data, playerid]       
