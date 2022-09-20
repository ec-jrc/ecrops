
class Printable:
    """This class is printable through a ___str___ function that returns a string containing its attributes. It is used
    as an empty container """
    def __str__(self):
        attrs = vars(self)
        return ' , '.join("%s: %s" % item for item in attrs.items())
