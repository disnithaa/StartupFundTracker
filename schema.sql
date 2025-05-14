-- Create database (if not exists)
CREATE DATABASE IF NOT EXISTS StartupFundingTracker;
USE StartupFundingTracker;

-- Drop tables if they exist (to start fresh)
DROP TABLE IF EXISTS ExitStrategies;
DROP TABLE IF EXISTS Acquisitions;
DROP TABLE IF EXISTS StartupValuations;
DROP TABLE IF EXISTS FundingSources;
DROP TABLE IF EXISTS EquityDetails;
DROP TABLE IF EXISTS Founders;
DROP TABLE IF EXISTS StartupInvestors;
DROP TABLE IF EXISTS FundingRounds;
DROP TABLE IF EXISTS Investors;
DROP TABLE IF EXISTS Startups;

-- Startups table with UNIQUE constraint on name
CREATE TABLE Startups (
    startup_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL UNIQUE,
    industry VARCHAR(100),
    founded_year INT,
    headquarters VARCHAR(255),
    total_funding VARCHAR(50),
    valuation VARCHAR(50),
    status VARCHAR(20) DEFAULT 'Active'
);

-- Investors table
CREATE TABLE Investors (
    investor_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    investment_firm VARCHAR(255),
    investor_type ENUM('Angel', 'Venture Capital', 'Private Equity', 'Corporate')
);

-- Funding Rounds table
CREATE TABLE FundingRounds (
    round_id INT PRIMARY KEY AUTO_INCREMENT,
    startup_id INT,
    round_type ENUM('Seed', 'Series A', 'Series B', 'Series C', 'IPO'),
    amount_raised DECIMAL(15,2),
    funding_date DATE,
    lead_investor_id INT,
    FOREIGN KEY (startup_id) REFERENCES Startups(startup_id) ON DELETE CASCADE,
    FOREIGN KEY (lead_investor_id) REFERENCES Investors(investor_id) ON DELETE SET NULL
);

-- Startup-Investor Relationship Table
CREATE TABLE StartupInvestors (
    id INT PRIMARY KEY AUTO_INCREMENT,
    startup_id INT,
    investor_id INT,
    investment_amount DECIMAL(15,2),
    FOREIGN KEY (startup_id) REFERENCES Startups(startup_id) ON DELETE CASCADE,
    FOREIGN KEY (investor_id) REFERENCES Investors(investor_id) ON DELETE CASCADE
);

-- Founders table
CREATE TABLE Founders (
    founder_id INT PRIMARY KEY AUTO_INCREMENT,
    startup_id INT,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(100),
    FOREIGN KEY (startup_id) REFERENCES Startups(startup_id) ON DELETE CASCADE
);

-- Equity table
CREATE TABLE EquityDetails (
    equity_id INT PRIMARY KEY AUTO_INCREMENT,
    investor_id INT,
    startup_id INT,
    equity_percentage DECIMAL(5,2),
    FOREIGN KEY (investor_id) REFERENCES Investors(investor_id) ON DELETE CASCADE,
    FOREIGN KEY (startup_id) REFERENCES Startups(startup_id) ON DELETE CASCADE
);

-- Funding Sources
CREATE TABLE FundingSources (
    source_id INT PRIMARY KEY AUTO_INCREMENT,
    funding_round_id INT,
    investor_id INT,
    contribution DECIMAL(15,2),
    FOREIGN KEY (funding_round_id) REFERENCES FundingRounds(round_id) ON DELETE CASCADE,
    FOREIGN KEY (investor_id) REFERENCES Investors(investor_id) ON DELETE CASCADE
);

-- Startup Valuation
CREATE TABLE StartupValuations (
    valuation_id INT PRIMARY KEY AUTO_INCREMENT,
    startup_id INT,
    valuation DECIMAL(15,2),
    valuation_date DATE,
    FOREIGN KEY (startup_id) REFERENCES Startups(startup_id) ON DELETE CASCADE
);

-- Acquisitions
CREATE TABLE Acquisitions (
    acquisition_id INT PRIMARY KEY AUTO_INCREMENT,
    acquired_startup_id INT,
    acquirer_name VARCHAR(255),
    acquisition_price DECIMAL(15,2),
    acquisition_date DATE,
    FOREIGN KEY (acquired_startup_id) REFERENCES Startups(startup_id) ON DELETE CASCADE
);

-- Exit Strategies
CREATE TABLE ExitStrategies (
    exit_id INT PRIMARY KEY AUTO_INCREMENT,
    startup_id INT,
    exit_type ENUM('Acquisition', 'IPO', 'Merger', 'Shutdown'),
    exit_date DATE,
    FOREIGN KEY (startup_id) REFERENCES Startups(startup_id) ON DELETE CASCADE
);

-- Insert Indian Startup Data (without duplicates) - Original 10 + 2 new
TRUNCATE TABLE Startups;

INSERT INTO Startups (name, industry, founded_year, headquarters, total_funding, valuation, status) VALUES 
('Flipkart', 'E-commerce', 2007, 'Bengaluru, India', '₹1,60,00,00,000', '₹3,760,00,00,000', 'Exited'),
('Paytm', 'Fintech', 2010, 'Noida, India', '₹250,00,00,000', '₹5500,00,00,000', 'Active'),
('Zomato', 'Food Delivery', 2008, 'Gurgaon, India', '₹296,00,00,000', '₹5400,00,00,000', 'Active'),
('Ola', 'Transportation', 2010, 'Bengaluru, India', '₹320,00,00,000', '₹7300,00,00,000', 'Active'),
('Byju''s', 'Edtech', 2011, 'Bengaluru, India', '₹72,00,00,000', '₹22000,00,00,000', 'Active'),
('Swiggy', 'Food Delivery', 2014, 'Bengaluru, India', '₹450,00,00,000', '₹10700,00,00,000', 'Active'),
('Nykaa', 'E-commerce', 2012, 'Mumbai, India', '₹180,00,00,000', '₹2300,00,00,000', 'Active'),
('Dream11', 'Gaming', 2008, 'Mumbai, India', '₹340,00,00,000', '₹8000,00,00,000', 'Active'),
('PhonePe', 'Fintech', 2015, 'Bengaluru, India', '₹420,00,00,000', '₹12000,00,00,000', 'Active'),
('Unacademy', 'Edtech', 2015, 'Bengaluru, India', '₹150,00,00,000', '₹3440,00,00,000', 'Active'),
('Razorpay', 'Fintech', 2014, 'Bengaluru, India', '₹260,00,00,000', '₹7500,00,00,000', 'Active'),
('CRED', 'Fintech', 2018, 'Bengaluru, India', '₹290,00,00,000', '₹6800,00,00,000', 'Active');

-- Insert Indian Investors (and major global investors in India) - Original 10 + 2 new
INSERT INTO Investors (name, investment_firm, investor_type) VALUES 
('Ratan Tata', 'Ratan Tata Investments', 'Angel'),
('Nandan Nilekani', NULL, 'Angel'),
('SoftBank', 'SoftBank Vision Fund', 'Private Equity'),
('Tiger Global', 'Tiger Global Management', 'Private Equity'),
('Sequoia India', 'Sequoia Capital India', 'Venture Capital'),
('Accel India', 'Accel Partners India', 'Venture Capital'),
('Nexus Venture', 'Nexus Venture Partners', 'Venture Capital'),
('Kalaari Capital', 'Kalaari Capital', 'Venture Capital'),
('ChrysCapital', 'ChrysCapital', 'Private Equity'),
('InfoEdge', 'InfoEdge Ventures', 'Corporate'),
('Ribbit Capital', 'Ribbit Capital', 'Venture Capital'),  -- New investor 1
('DST Global', 'DST Global', 'Private Equity');          -- New investor 2

-- Insert Funding Rounds (realistic amounts in USD) - Original 10 + 2 new
INSERT INTO FundingRounds (startup_id, round_type, amount_raised, funding_date, lead_investor_id) VALUES 
(1, 'Series A', 1000000.00, '2009-06-01', 5),
(1, 'Series B', 10000000.00, '2010-12-15', 4),
(1, 'Series C', 150000000.00, '2012-08-20', 3),
(2, 'Series A', 5000000.00, '2013-03-10', 5),
(2, 'Series B', 25000000.00, '2014-11-05', 3),
(3, 'Series A', 5000000.00, '2013-01-15', 4),
(3, 'Series B', 37000000.00, '2015-04-22', 3),
(4, 'Series A', 5000000.00, '2011-09-30', 5),
(4, 'Series B', 40000000.00, '2014-10-14', 4),
(5, 'Series A', 9000000.00, '2015-09-01', 5),
(11, 'Seed', 2000000.00, '2015-03-15', 6),               -- New funding round 1
(12, 'Series A', 12000000.00, '2019-06-20', 11);        -- New funding round 2

-- Insert Startup-Investor Relationships - Original 10 + 2 new
INSERT INTO StartupInvestors (startup_id, investor_id, investment_amount) VALUES 
(1, 5, 1000000.00),
(1, 4, 5000000.00),
(1, 3, 50000000.00),
(2, 5, 2000000.00),
(2, 3, 20000000.00),
(3, 4, 3000000.00),
(3, 3, 20000000.00),
(4, 5, 3000000.00),
(4, 4, 20000000.00),
(5, 5, 5000000.00),
(11, 6, 1500000.00),                                     -- New investment 1
(12, 11, 8000000.00);                                   -- New investment 2

-- Insert Founders (real Indian founders) - Original 10 + 2 new
INSERT INTO Founders (startup_id, name, role) VALUES 
(1, 'Sachin Bansal', 'Co-founder'),
(1, 'Binny Bansal', 'Co-founder'),
(2, 'Vijay Shekhar Sharma', 'Founder & CEO'),
(3, 'Deepinder Goyal', 'Founder & CEO'),
(4, 'Bhavish Aggarwal', 'Co-founder'),
(4, 'Ankit Bhati', 'Co-founder'),
(5, 'Byju Raveendran', 'Founder & CEO'),
(6, 'Sriharsha Majety', 'Co-founder'),
(6, 'Nandan Reddy', 'Co-founder'),
(7, 'Falguni Nayar', 'Founder & CEO'),
(11, 'Harshil Mathur', 'Co-founder'),                   -- New founder 1
(11, 'Shashank Kumar', 'Co-founder'),                   -- New founder 2
(12, 'Kunal Shah', 'Founder & CEO');                    -- New founder 3 (extra for CRED)

-- Insert Equity Details (sample percentages) - Original 10 + 2 new
INSERT INTO EquityDetails (investor_id, startup_id, equity_percentage) VALUES 
(5, 1, 15.00),
(4, 1, 10.00),
(3, 1, 20.00),
(5, 2, 12.50),
(3, 2, 18.75),
(4, 3, 15.00),
(3, 3, 22.50),
(5, 4, 17.50),
(4, 4, 15.25),
(5, 5, 20.00),
(6, 11, 18.00),                                         -- New equity 1
(11, 12, 25.00);                                       -- New equity 2

-- Insert Funding Sources - Original 10 + 2 new
INSERT INTO FundingSources (funding_round_id, investor_id, contribution) VALUES 
(1, 5, 1000000.00),
(2, 4, 8000000.00),
(2, 5, 2000000.00),
(3, 3, 100000000.00),
(3, 4, 50000000.00),
(4, 5, 5000000.00),
(5, 3, 25000000.00),
(6, 4, 5000000.00),
(7, 3, 37000000.00),
(8, 5, 5000000.00),
(11, 6, 1500000.00),                                    -- New funding source 1
(12, 11, 8000000.00),                                  -- New funding source 2
(12, 3, 4000000.00);                                   -- Extra funding source

-- Insert Startup Valuations (in USD billions) - Original 10 + 2 new
INSERT INTO StartupValuations (startup_id, valuation, valuation_date) VALUES 
(1, 37.60, '2023-01-01'),
(2, 5.50, '2023-01-01'),
(3, 5.40, '2023-01-01'),
(4, 7.30, '2023-01-01'),
(5, 22.00, '2023-01-01'),
(6, 10.70, '2023-01-01'),
(7, 2.30, '2023-01-01'),
(8, 8.00, '2023-01-01'),
(9, 12.00, '2023-01-01'),
(10, 3.44, '2023-01-01'),
(11, 7.50, '2023-01-01'),                               -- New valuation 1
(12, 6.80, '2023-01-01');                              -- New valuation 2

-- Insert Acquisitions (major Indian startup acquisitions) - Original 2 + 1 new
INSERT INTO Acquisitions (acquired_startup_id, acquirer_name, acquisition_price, acquisition_date) VALUES 
(1, 'Walmart', 16000000000.00, '2018-05-09'),
(9, 'Walmart', 7000000000.00, '2020-12-18'),
(10, 'Unacademy Group', 500000000.00, '2021-06-15');    -- New acquisition

-- Insert Exit Strategies - Original 2 + 1 new
INSERT INTO ExitStrategies (startup_id, exit_type, exit_date) VALUES 
(1, 'Acquisition', '2018-05-09'),
(9, 'Acquisition', '2020-12-18'),
(10, 'Acquisition', '2021-06-15');                      -- New exit strategy



-- Enhanced database schema with all required features
-- Reset users table
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,  -- Ensure this matches the model
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'Viewer',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add index for user email lookups
CREATE INDEX idx_user_email ON users(email);

-- Add test admin user if not exists
INSERT INTO users (name, email, password_hash, role, created_at)
VALUES ('Admin', 'admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY.5AICWWPrZmIi', 'Admin', NOW());

CREATE TABLE notifications (
    notification_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    title VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE funds (
    fund_id INT PRIMARY KEY AUTO_INCREMENT,
    source_name VARCHAR(100) NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    funding_round ENUM('Seed', 'Series A', 'Series B', 'Series C', 'IPO', 'Other') NOT NULL,
    date_received DATE NOT NULL,
    notes TEXT,
    attachment_url VARCHAR(255),
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL
);

CREATE TABLE expense_categories (
    category_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(255),
    color_code VARCHAR(7) DEFAULT '#6c757d'
);

CREATE TABLE expenses (
    expense_id INT PRIMARY KEY AUTO_INCREMENT,
    category_id INT NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    vendor VARCHAR(100) NOT NULL,
    date DATE NOT NULL,
    description TEXT,
    receipt_url VARCHAR(255),
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES expense_categories(category_id),
    FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL
);

CREATE TABLE budgets (
    budget_id INT PRIMARY KEY AUTO_INCREMENT,
    category_id INT NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    period ENUM('Monthly', 'Quarterly', 'Yearly', 'Custom') NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES expense_categories(category_id),
    FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL,
    CHECK (end_date > start_date)
);

CREATE TABLE reports (
    report_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    type ENUM('Monthly', 'Quarterly', 'Annual', 'Custom', 'Investor') NOT NULL,
    start_date DATE,
    end_date DATE,
    file_url VARCHAR(255) NOT NULL,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL
);

CREATE TABLE system_settings (
    setting_id INT PRIMARY KEY AUTO_INCREMENT,
    setting_key VARCHAR(50) NOT NULL UNIQUE,
    setting_value TEXT NOT NULL,
    description VARCHAR(255),
    is_public BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE audit_log (
    log_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    action VARCHAR(50) NOT NULL,
    table_name VARCHAR(50) NOT NULL,
    record_id INT,
    old_values JSON,
    new_values JSON,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
);

-- Add indexes
CREATE INDEX idx_startup_name ON Startups(name);
CREATE INDEX idx_funding_date ON FundingRounds(funding_date);
CREATE INDEX idx_investor_name ON Investors(name);

-- Add full-text search
ALTER TABLE Startups ADD FULLTEXT(name, industry);
ALTER TABLE Investors ADD FULLTEXT(name, investment_firm);

-- Add constraints
ALTER TABLE FundingRounds ADD CHECK (amount_raised > 0);
ALTER TABLE StartupInvestors ADD CHECK (investment_amount > 0);

-- Update users table if needed
ALTER TABLE users 
    MODIFY COLUMN user_id INT PRIMARY KEY AUTO_INCREMENT,
    MODIFY COLUMN name VARCHAR(100) NOT NULL,
    MODIFY COLUMN email VARCHAR(100) NOT NULL UNIQUE,
    MODIFY COLUMN password_hash VARCHAR(255) NOT NULL,
    MODIFY COLUMN role ENUM('Admin', 'Finance', 'Viewer') NOT NULL DEFAULT 'Viewer',
    MODIFY COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

select * from users;
