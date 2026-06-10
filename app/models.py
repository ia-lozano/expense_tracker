from app import db
from decimal import Decimal
from sqlalchemy import String, Integer, Text, ForeignKey, Numeric
from sqlalchemy.orm import mapped_column, relationship, Mapped
from datetime import datetime

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(200), nullable=False)

    #Mapping foreign key to Expense
    expenses: Mapped[list["Expense"]] = relationship(back_populates="user",
                                               cascade="all, delete-orphan")

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return f'<User: {self.username} | ID: {self.id}>'
    
class Expense(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    expense_type: Mapped[str] = mapped_column(Text)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    date: Mapped[datetime] = mapped_column(default=datetime.now)

    #Mapping foreign key for user
    user: Mapped["User"] = relationship(back_populates="expenses")

    def __init__(self, user_id, expense_type, amount, description=None):
        self.user_id = user_id
        self.expense_type = expense_type
        self.amount = amount
        self.description = description
        

    def __repr__(self):
        return f'<Type: {self.expense_type} | Amount {self.amount} >'
    
'''
## Test query your db ##
    flask --app app shell
    from app.models import User, Expense
    from app import db

    # If u want to populate the db:
    user = User('username', 'password')
    users = User.query.all() -> returns an empty list
    db.session.add(user)
    db.session.commit()
    
    #If not, just query
    users = User.query.all()
    users
    User.query.get(1)

    #Ight imma head out
    exit()

'''