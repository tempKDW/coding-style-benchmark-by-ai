DISCOUNT_RATES = {
    "VIP": 0.15,
    "NEW": 0.05,
}


def calculate_discount(price, user_type, coupon_amount=0):
    rate = DISCOUNT_RATES.get(user_type, 0)
    discount = price * rate
    discount += coupon_amount
    return discount


def final_price(price, user_type, coupon_amount=0):
    discount = calculate_discount(price, user_type, coupon_amount)
    return price - discount
