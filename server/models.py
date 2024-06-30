from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)

class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)

    # add relationship
    pizzas = db.relationship('RestaurantPizza', back_populates='restaurant', cascade="all, delete-orphan")

    # add serialization rules
    serialize_rules = ('-pizzas.restaurant',)

    def __repr__(self):
        return f"<Restaurant {self.name}>"

    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'restaurant_pizzas': [restaurant_pizza.to_dict(include_restaurant=False) for restaurant_pizza in self.pizzas]
        }
        return data

class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    ingredients = db.Column(db.String)

    # add relationship
    restaurants = db.relationship('RestaurantPizza', back_populates='pizza', cascade="all, delete-orphan")

    # add serialization rules
    serialize_rules = ('-restaurants.pizza',)

    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"

    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'ingredients': self.ingredients
        }
        return data

class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'))
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizzas.id'))

    # add relationships
    restaurant = db.relationship('Restaurant', back_populates='pizzas')
    pizza = db.relationship('Pizza', back_populates='restaurants')

    # add serialization rules
    serialize_rules = ('-restaurant.pizzas', '-pizza.restaurants')

    # add validation
    @validates('price')
    def validate_price(self, key, price):
        if not (1 <= price <= 30):
            raise ValueError
        return price

    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"

    def to_dict(self, include_restaurant=True):
        data = {
            'id': self.id,
            'price': self.price,
            'pizza_id': self.pizza_id,
            'restaurant_id': self.restaurant_id,
            'pizza': self.pizza.to_dict()
        }
        if include_restaurant:
            data['restaurant'] = {'id': self.restaurant.id, 'name': self.restaurant.name}
        return data
