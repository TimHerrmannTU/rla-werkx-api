import cryptography.fernet

DB_HOST = "server02"
DB_NAME = "werkx"
DB_USER = "werkx-tagebuch"
DB_PORT = 3306

encrypted_pass ="gAAAAABnGKeRGZtMvzPUbpZgtuVr_kfIkNCw7uHYY1C2qW-dQ0E29L5TjKQ6yy6qWKLER5eypZKoAQvUN6JrxtzGfuzxfpCQQg=="
private_key = b'i4MCrfsqT9kxs2do5Tr9fWpfiI3qLRsQRd6nihxoAWs='
fernet = cryptography.fernet.Fernet(private_key)
DB_PASS = fernet.decrypt(encrypted_pass.encode("utf-8")).decode("utf-8")

SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"