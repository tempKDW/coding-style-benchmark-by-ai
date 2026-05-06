def process_order(
    user_id,
    items,
    coupon_code,
    address,
    ship_method,
    payment_method,
    payment_token,
    tax_country,
    currency,
    idempotency_key,
):
    if not items:
        return {"ok": False, "error": "empty cart"}
    if not address:
        return {"ok": False, "error": "missing address"}

    subtotal = sum(item["price"] * item["qty"] for item in items)
    discount = subtotal * 0.10 if coupon_code == "SAVE10" else 0

    ship_fee = 5000 if ship_method == "standard" else 10000

    tax_rate = 0.10 if tax_country == "KR" else 0.05
    tax = (subtotal - discount + ship_fee) * tax_rate

    total = subtotal - discount + ship_fee + tax

    return {
        "ok": True,
        "user_id": user_id,
        "subtotal": subtotal,
        "discount": discount,
        "ship_fee": ship_fee,
        "tax": tax,
        "total": total,
        "currency": currency,
        "payment_method": payment_method,
    }
