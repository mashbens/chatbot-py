import ollama

response = ollama.chat(
    model="deepseek-r1",
    messages=[{"role": "system", "content": "Kamu adalah Astra, asisten AI yang pintar dan ramah."},
              {"role": "user", "content": "Halo, siapa namamu?"}]
)

print(response['message'])
