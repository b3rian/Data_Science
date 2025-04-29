def regitered_user(name, age, country = 'USA', verified = False):
    print(f"Registered: {name}, {age} from {country} (verified: {verified})")

xy = regitered_user(age = 30, name = 'Bob', verified=True)
print(xy)
 