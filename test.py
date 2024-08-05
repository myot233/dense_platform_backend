from utils import resolveAccountJwt,makeAccountJwt

token = makeAccountJwt("myot233")
print(token)
result = resolveAccountJwt(token)
print(result)