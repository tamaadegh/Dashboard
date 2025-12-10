
class IdOrNoneConverter:
    regex = '(\d+|none)'

    def to_python(self, value):
        if value == 'none':
            return None
        return int(value)

    def to_url(self, value):
        if value is None:
            return 'none'
        return str(value)
