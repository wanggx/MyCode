

class Person:

    empCount = 0

    def __init__(self, name, age):
        self.name = name
        self.age = age

    def display(self):
        Person.empCount += 1
        print(self.name, self.age)
        print(Person.empCount)