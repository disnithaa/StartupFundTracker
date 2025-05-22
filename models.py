from flask_login import UserMixin
from db import db
from datetime import datetime
from sqlalchemy.types import DECIMAL
from werkzeug.security import check_password_hash

class Expense(db.Model):
    __tablename__ = 'expenses'
    expense_id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('expense_categories.category_id'))
    amount = db.Column(DECIMAL(15,2), nullable=False)
    vendor = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    receipt_url = db.Column(db.String(255))
    created_by = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='SET NULL'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ExpenseCategory(db.Model):
    __tablename__ = 'expense_categories'
    category_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(255))
    color_code = db.Column(db.String(7), default='#6c757d')
    expenses = db.relationship('Expense', backref='category', lazy=True)

class Report(db.Model):
    __tablename__ = 'reports'
    report_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.Enum('Monthly', 'Quarterly', 'Annual', 'Custom', 'Investor'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='SET NULL'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Fund(db.Model):
    __tablename__ = 'funds'
    fund_id = db.Column(db.Integer, primary_key=True)
    source_name = db.Column(db.String(100), nullable=False)
    amount = db.Column(DECIMAL(15,2), nullable=False)  # Fixed Decimal type
    funding_round = db.Column(db.Enum('Seed', 'Series A', 'Series B', 'Series C', 'IPO', 'Other'), nullable=False)
    date_received = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text)
    attachment_url = db.Column(db.String(255))
    created_by = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='SET NULL'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Startup(db.Model):
    __tablename__ = 'startups'
    
    startup_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    industry = db.Column(db.String(100), nullable=False)
    founded_year = db.Column(db.Integer, nullable=False)
    headquarters = db.Column(db.String(255), nullable=False)
    total_funding = db.Column(db.String(50), nullable=False)
    valuation = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Active')
    
    def to_dict(self):
        return {
            'startup_id': self.startup_id,
            'name': self.name,
            'industry': self.industry,
            'founded_year': self.founded_year,
            'headquarters': self.headquarters,
            'total_funding': self.total_funding,
            'valuation': self.valuation,
            'status': self.status
        }

class Investor(db.Model):
    __tablename__ = 'Investors'
    investor_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    investment_firm = db.Column(db.String(255))
    investor_type = db.Column(db.Enum('Angel', 'Venture Capital', 'Private Equity', 'Corporate'))

class FundingRound(db.Model):
    __tablename__ = 'FundingRounds'
    round_id = db.Column(db.Integer, primary_key=True)
    startup_id = db.Column(db.Integer, db.ForeignKey('startups.startup_id', ondelete='CASCADE'))
    round_type = db.Column(db.Enum('Seed', 'Series A', 'Series B', 'Series C', 'IPO'))
    amount_raised = db.Column(DECIMAL(15, 2))  # Fixed Decimal type
    funding_date = db.Column(db.Date)
    lead_investor_id = db.Column(db.Integer, db.ForeignKey('Investors.investor_id', ondelete='SET NULL'))

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True)  # Changed from id to user_id
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='Viewer')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_id(self):
        return str(self.user_id)  # Changed from id to user_id

class Notification(db.Model):
    __tablename__ = 'notifications'

    notification_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)