from sqlalchemy import Column, Integer, Text, DateTime, String, Boolean, ForeignKey, func
from sqlalchemy.orm import relationship, declarative_base
from flask_login import UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, validators
from flask import Blueprint, render_template, request, redirect, url_for
from app import db_manager

# alias
Base = declarative_base()

bp = Blueprint('routes', __name__)

class Account(Base):
    __tablename__ = "accounts"
    account_id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, server_default=func.now())
    users = relationship("User", back_populates="account")

class Role(Base):
    __tablename__ = "roles"
    role_id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)

    def __repr__(self):
        return f"<Role {self.name}>"

class UserRole(Base):
    __tablename__ = "users_x_roles"
    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.role_id"), primary_key=True)
    assigned_at = Column(DateTime, nullable=False, server_default=func.now())

class User(UserMixin, Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True)
    username = Column(Text)
    email = Column(String, nullable=False, unique=True)
    password_hash = Column(String(128), nullable=False)
    confirmed = Column(Boolean, nullable=False, server_default="false")
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    account_id = Column(Integer, ForeignKey("accounts.account_id"), nullable=False)
    account = relationship("Account", back_populates="users")
    roles = relationship("Role", secondary="users_x_roles")

    def get_id(self):
        return self.user_id

    def __repr__(self):
        return f"<User {self.email}>"

class Person(Base):
    __tablename__ = "person"
    person_id = Column(Integer, primary_key=True)
    car_brand = Column(Text, nullable=False)
    surname = Column(Text, nullable=False)
    email = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<Person {self.car_brand}>"

class FormPerson(FlaskForm):
    car_brand = StringField('Car Brand', [
        validators.InputRequired(),
        validators.Length(max=30),
        validators.Regexp(r'^[a-zA-Z0-9 ]*$', message="Only ASCII characters without punctuation are allowed.")
    ])
    surname = StringField('Surname', [
        validators.InputRequired(),
        validators.Length(max=30),
        validators.Regexp(r'^[a-zA-Z0-9 ]*$', message="Only ASCII characters without punctuation are allowed.")
    ])
    email = StringField('Email', [
        validators.InputRequired(),
        validators.Length(max=50),
        validators.Email(message="Invalid email address.")
    ])

@bp.route("/person", methods=["GET", "POST"])
def formular():
    form = FormPerson()
    if form.validate_on_submit():
        # Save records to the database
        new_person = Person(car_brand=form.car_brand.data, surname=form.surname.data, email=form.email.data)
        db.add(new_person)
        db.commit()
        return "Record saved to database"
    else:
        return render_template("formularPerson.html", form=form)

@bp.route("/persons", methods=["GET", "POST"])
def list_persons():
    if request.method == "POST":
        selected_ids = request.form.getlist("selected_ids")
        if selected_ids:
            Person.query.filter(Person.person_id.in_(selected_ids)).delete(synchronize_session=False)
            db.commit()
            return redirect(url_for("routes.list_persons"))
    
    persons = Person.query.all()
    return render_template("list_persons.html", persons=persons)