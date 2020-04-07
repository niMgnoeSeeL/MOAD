import configparser


class Config:
    def __init__(self, config_path):
        self.config = configparser.RawConfigParser()
        succ = self.config.read(filenames=config_path)
        if not len(succ):
            raise Exception('Unable to load config(path:{})'.format(
                config_path))

    def write(self, file_path):
        with open(file_path, 'w') as config_file:
            self.config.write(config_file)

    def set(self, session, option, value):
        return self.config.set(session, option, value)

    def getstr(self, session, option, default_value=None):
        if not self.config.has_section(session):
            return default_value
        if not self.config.has_option(session, option):
            return default_value
        try:
            raw_value = self.config.get(session, option)
            return raw_value.lstrip('"').rstrip('"')
        except:
            return default_value

    def getint(self, session, option, default_value=0):
        if not self.config.has_section(session):
            return default_value
        if not self.config.has_option(session, option):
            return default_value
        try:
            return self.config.getint(session, option)
        except:
            return default_value

    def getboolean(self, session, option, default_value=False):
        if not self.config.has_section(session):
            return default_value
        if not self.config.has_option(session, option):
            return default_value
        try:
            return self.config.getboolean(session, option)
        except:
            return default_value

    def getfloat(self, session, option, default_value=0.0):
        if not self.config.has_section(session):
            return default_value
        if not self.config.has_option(session, option):
            return default_value
        try:
            return self.config.getfloat(session, option)
        except:
            return default_value

    def getlist(self, session, option, default_value=None):
        if not self.config.has_section(session):
            return default_value
        if not self.config.has_option(session, option):
            return default_value
        try:
            str_value = self.config.get(session, option)
            if str_value == '':
                return default_value
            else:
                return str_value.lstrip().split('\n')
        except:
            return default_value
