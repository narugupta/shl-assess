from app.api.dependencies import (

    get_container,

    get_planner,

    get_retriever,

    get_generator,

)

print()

print("=" * 80)

print("FIRST CALL")

print("=" * 80)

container1 = get_container()

print()

print(id(container1))

print(id(get_planner()))

print(id(get_retriever()))

print(id(get_generator()))

print()

print("=" * 80)

print("SECOND CALL")

print("=" * 80)

container2 = get_container()

print()

print(id(container2))

print(id(get_planner()))

print(id(get_retriever()))

print(id(get_generator()))

print()

print("Same container:", container1 is container2)