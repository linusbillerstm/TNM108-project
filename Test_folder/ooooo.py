from google import genai
client = genai.Client(api_key="AIzaSyBNVnoRHvXyIgLb90Odx66sbV91ngN9I8I")

print("My Available Models:")
for model in client.models.list():
    print(model.name)