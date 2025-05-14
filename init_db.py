from app import db, Startup, User

# Initialize the database
db.create_all()

# Seed data
startups = [
    Startup(name="Flipkart", industry="E-commerce", founded=2007, funding="₹1,60,00,00,000", valuation="₹3,760,00,00,000", status="Exited"),
    Startup(name="Paytm", industry="Fintech", founded=2010, funding="₹250,00,00,000", valuation="₹5500,00,00,000", status="Active"),
    Startup(name="Zomato", industry="Food Delivery", founded=2008, funding="₹296,00,00,000", valuation="₹5400,00,00,000", status="Active"),
    Startup(name="Ola", industry="Transportation", founded=2010, funding="₹320,00,00,000", valuation="₹7300,00,00,000", status="Active"),
    Startup(name="Byju's", industry="Edtech", founded=2011, funding="₹72,00,00,000", valuation="₹22000,00,00,000", status="Active")
]

users = [
    User(username="admin", password="admin123")
]

db.session.bulk_save_objects(startups + users)
db.session.commit()
print("Database initialized and seeded!")
