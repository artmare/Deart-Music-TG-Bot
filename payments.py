import uuid

def generate_payment_link(user_id, tariff):
    # Здесь должна быть интеграция с реальной платёжной системой (Stripe, YooKassa, CryptoBot и т.д.)
    # Для примера — просто уникальная ссылка-заглушка
    payment_id = str(uuid.uuid4())
    return f"https://pay.example.com/pay?uid={user_id}&tariff={tariff}&pid={payment_id}"

def check_payment(payment_id):
    # Здесь должна быть реальная проверка оплаты через API платёжной системы
    # Для примера — всегда True (оплата прошла)
    return True
