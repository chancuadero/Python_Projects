import qrcode

url = input("Enter the text or URL: ").strip()
filename = input("Enter the filename: ").strip()

img = qrcode.make(url)
img.save(filename)
print(f"QR Code saved as {filename}")