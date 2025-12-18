import requests

url = "http://127.0.0.1:8000/profile?name=clint_cowden"

files = [
    ("files", ("info.pdf", open("C:\\Users\\divya\\Downloads\\clint_info.pdf", "rb"), "application/pdf")),
    ("files", ("background.pdf", open("C:\\Users\\divya\\Downloads\\Telegram Desktop\\checkpeople_Clint_Cowden_12_14_2025.pdf", "rb"), "application/pdf")),
    ("files", ("background2.pdf", open("C:\\Users\\divya\\Downloads\\Telegram Desktop\\Clint_C_Cowden-7318139f9f02948.pdf", "rb"), "application/pdf")),
    ("files", ("credit.pdf", open("C:\\Users\\divya\\Downloads\\Telegram Desktop\\Clint Cowden.pdf", "rb"), "application/pdf")),
]

response = requests.get(url)

print("STATUS:", response.status_code)
print("RESPONSE:")
print(response.json())
