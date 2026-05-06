class Account:
    def __init__(self, id, balance, frozen=False):
        self.id = id
        self.balance = balance
        self.frozen = frozen

    def deposit(self, amount):
        if self.frozen:
            raise ValueError("frozen")
        self.balance += amount

    def withdraw(self, amount):
        if self.frozen:
            raise ValueError("frozen")
        if self.balance < amount:
            raise ValueError("insufficient")
        self.balance -= amount

    def freeze(self, reason):
        self.frozen = True

    def transfer_to(self, other, amount):
        self.withdraw(amount)
        other.deposit(amount)
