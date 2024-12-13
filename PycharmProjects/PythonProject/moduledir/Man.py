from moduledir.Person import Person


class Man(Person):

    def __init__(self, first_name, last_name, age):
        super().__init__(first_name, age)
        self.last_name = last_name