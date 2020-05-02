import requests

ZOOM_URL="""https://us04wmcc.zoom.us/closedcaption?id=7697551967&ns=TWF1cmljaW8gQnVzdG9zJyBQZXJzb25hbCBNZWV0&expire=86400&sparams=id%2Cns%2Cexpire&signature=bA538ZKS5DeDnhst3JeuTK0uv7ABWD-3mwHFeaR3d2k.EwEAAAFx0teXKgABUYAYb0pCdlEzS0V2U0tLekxpOUFubGVFQT09QHlUVjhBeWVaNHV3Vy9WNmEyZTRJNjVvUlpuYkRMS0YreXVmQXVFZlhBZFI3YUFJdURvZmRPTEFpNlo2UlBPSXo&lang=en-US&seq="""

for i in range(10):
    URL = ZOOM_URL + str(i)
    response = requests.post(URL, data=str(i), headers={'content-type': 'text/plain'})
    print(response)
