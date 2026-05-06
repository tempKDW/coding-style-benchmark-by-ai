def vip_discount(price):
    return price * 0.15


def new_user_discount(price):
    return price * 0.05


POLICIES = {
    "VIP": vip_discount,
    "NEW": new_user_discount,
}


def calculate_discount(price, user_type, coupon_amount=0):
    policy = POLICIES.get(user_type)
    discount = policy(price) if policy else 0
    return discount + coupon_amount


def final_price(price, user_type, coupon_amount=0):
    discount = calculate_discount(price, user_type, coupon_amount)
    return price - discount
