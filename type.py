age: int = 2
price: float = 99.9
name: str = "Ahad"
is_alive: bool = True

#annotations
def add(a: int, b: int) -> int: #this funtion returns an 'int'
    return a + b

#no enforcement like fastapi
print(add("x","y"))
