
class A:
    def hello(self):
        print("A Hello World")

class Animal:
    def run(self):
        print("animal is running")


class Operson(Animal, A):
    def run(self):
        print("operson is running")

    def hello(self):
        print("person hello world")
        super().hello()


class Dog(Animal):
    def run(self):
        print("dog is running")

class Pig(Animal):
    def run(self):
        print("pig is running")


p = Operson()
p.run()
p.hello()

dog = Dog()
dog.run()

pig = Pig()
pig.run()