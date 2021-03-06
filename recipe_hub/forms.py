from flask_login import current_user
from flask_wtf import FlaskForm
from sqlalchemy import and_
from wtforms import BooleanField, PasswordField, SelectField, StringField, SubmitField
from wtforms.fields.html5 import DateField, IntegerField
from wtforms.fields.simple import HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, ValidationError

from recipe_hub.db_funcs import get_all_units, get_unit_id, validate_password
from recipe_hub.mappings import Ingredient, Product, Recipe, User


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    fullname = StringField('Full Name', validators=[DataRequired()])
    birthday = DateField('Date of Birth', validators=[Optional()])
    submit = SubmitField('Sign Up')

    def validate_username(self, username: str) -> None:
        user = User.query.filter(User.username.ilike(username.data)).first()
        if user:
            raise ValidationError('Chosen username is unavailable. Please choose a diffrent one')

    def validate_email(self, email: str) -> None:
        user = User.query.filter(User.email == email.data.lower()).first()
        if user:
            raise ValidationError('An account already exists for the chosen email. Please chooses a different email or login.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

    def validate_email(self, email: str) -> None:
        if not self.email.errors:
            user = User.query.filter(User.email == email.data.lower()).first()
            if not user:
                raise ValidationError('No account exists for the provided email.')


class ProductForm(FlaskForm):
    name = StringField('Recipe Name', validators=[DataRequired()])
    amount = IntegerField('Final Amount', validators=[DataRequired()])
    unit = SelectField('Final Unit', choices=get_all_units(), coerce=get_unit_id, validators=[DataRequired()])
    public = BooleanField('Publish Publically')
    submit = SubmitField('Add')
    
    def validate_name(self, name: str) -> None:
        product = Product.query.filter(and_(Product.user_id == current_user.user_id,
                                               Product.name == name.data.lower())).first()
        if product:
            raise ValidationError('A product with the chosen name already exists on your profile. Please choose a different name.')


class RecipeForm(FlaskForm):
    product_id = HiddenField()
    ingredient = StringField('Ingredient', validators=[DataRequired()])
    amount = IntegerField('Amount', validators=[DataRequired()])
    unit = SelectField('Unit', choices=get_all_units(), coerce=get_unit_id, validators=[DataRequired()])
    submit = SubmitField('+')
    
    def validate_ingredient(self, ingredient: str) -> None:
        ingredient_object = Ingredient.query.filter(and_(Ingredient.name == ingredient.data.lower(),
                                                     Ingredient.unit_id == self.unit.data)).first()
        if ingredient_object is not None:
            recipe = Recipe.query.filter(and_(Recipe.product_id == self.product_id.data,
                                                Recipe.ingredient_id == ingredient_object.ingredient_id)).first()
            if recipe:
                raise ValidationError('The given ingredient is already found in the recipe.')


class UsernameForm(FlaskForm):
    username = StringField('New Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    submit = SubmitField('Change Username')
    
    def validate_username(self, username: str) -> None:
        if username.data == current_user.username:
            raise ValidationError('Please choose a new username.')
        user = User.query.filter(and_(User.username.ilike(username.data),
                                         User.username != current_user.username)).first()
        if user:
            raise ValidationError('Chosen username is unavailable. Please choose a diffrent one')


class EmailForm(FlaskForm):
    email = StringField('New Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    submit = SubmitField('Change Email')
    
    def validate_email(self, email: str) -> None:
        if email.data.lower() == current_user.email:
            raise ValidationError('Please choose a new email.')
        user = User.query.filter(User.email == email.data.lower()).first()
        if user:
            raise ValidationError('An account already exists for the chosen email.')


class PasswordForm(FlaskForm):
    cur_password = PasswordField('Current Password', validators=[DataRequired(), Length(min=8)])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(message='Field must be equal to new password.'), EqualTo('new_password')])
    submit = SubmitField('Change Password')
    
    def validate_new_password(self, new_password: str) -> None:
        if validate_password(current_user.email, new_password.data):
            raise ValidationError('Please choose a new password.')


class NameForm(FlaskForm):
    fullname = StringField('Full Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    submit = SubmitField('Change Name')
    
    def validate_fullname(self, fullname: str) -> None:
        if fullname.data.lower() == current_user.full_name:
            raise ValidationError('Please choose a new name.')


class BirthdayForm(FlaskForm):
    birthday = DateField('Date of Birth', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    submit = SubmitField('Change Date of Birth')
    
    def validate_birthday(self, birthday: str) -> None:
        if birthday.data == current_user.date_of_birth.date():
            raise ValidationError('Please choose a new date.')