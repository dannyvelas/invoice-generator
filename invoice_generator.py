#!/usr/bin/env python3
import os
import datetime
from fpdf import FPDF
import argparse
import calendar
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import json

def load_config(config_path):
    """Load configuration from a JSON file."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Create default config if it doesn't exist
        default_config = {
            "sender": {
                "company": "Your Company",
                "address": "Your Address",
                "city": "Your City",
                "phone": "Your Phone",
                "email": "your.email@example.com"
            },
            "receiver": {
                "company": "Client Company",
                "address": "Client Address",
                "city": "Client City"
            },
            "invoice": {
                "number": "001"
            },
            "services": [
                {
                    "description": "Service Description",
                    "quantity": 1,
                    "unit_price": 1000.00
                }
            ],
            "output": {
                "invoice_dir": "./invoices",
                "email_dir": "./emails"
            },
            "email": {
                "recipient": "client@example.com",
                "sender": "your.email@example.com",
                "subject_template": "Invoice for {month} {year}",
                "body_template": "Dear {client_name},\n\nI hope you are all well!\n\nAttached below is the invoice for {month} {year}. Please let me know if you have any questions or concerns.\n\nAll the best,\n{sender_name}"
            }
        }
        
        # Write default config
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
            
        print(f"Created default configuration at {config_path}. Please edit it with your information.")
        return default_config

def generate_invoice(config, invoice_date=None):
    """Generate a PDF invoice based on the given configuration."""
    # Use current date if no invoice date provided
    if invoice_date is None:
        invoice_date = datetime.date.today()
    
    # Create invoice directory if it doesn't exist
    os.makedirs(config["output"]["invoice_dir"], exist_ok=True)
    
    # Format dates
    invoice_date_str = invoice_date.strftime("%B %d, %Y")
    
    # Get invoice number from config or generate default
    if "invoice" in config and "number" in config["invoice"]:
        invoice_number = config["invoice"]["number"]
    else:
        print("error, could not find invoice number in config file")
        sys.exit(1)
        
    # Auto-increment invoice number for next time
    if "invoice" in config and "number" in config["invoice"]:
        try:
            # Try to convert to integer and increment
            new_number = int(config["invoice"]["number"]) + 1
            config["invoice"]["number"] = f"{new_number:03d}"
            
            # Save updated config
            with open("config.json", "w") as f:
                json.dump(config, f, indent=2)
        except ValueError:
            # If number_part is not an integer, don't increment
            pass
    
    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Set margins
    margin = 20
    pdf.set_margins(margin, margin, margin)
    
    # Add first line with left/center/right alignment
    pdf.set_font("Arial", "B", 16)
    
    # Left part - INVOICE
    pdf.cell(60, 10, "INVOICE", 0, 0, "L")
    
    # Middle part - invoice number
    pdf.cell(70, 10, f"#{invoice_number}", 0, 0, "C")
    
    # Right part - date
    pdf.cell(60, 10, invoice_date_str, 0, 1, "R")
    pdf.ln(10)
    
    # Add sender and receiver information
    pdf.set_font("Arial", "B", 12)
    pdf.cell(95, 10, "FROM:", 0, 0)
    pdf.cell(95, 10, "BILL TO:", 0, 1)
    
    # Sender details
    pdf.set_font("Arial", size=10)
    pdf.cell(95, 5, config["sender"]["company"], 0, 0)
    pdf.cell(95, 5, config["receiver"]["company"], 0, 1)
    pdf.cell(95, 5, config["sender"]["address"], 0, 0)
    pdf.cell(95, 5, config["receiver"]["address"], 0, 1)
    pdf.cell(95, 5, config["sender"]["city"], 0, 0)
    pdf.cell(95, 5, config["receiver"]["city"], 0, 1)
    pdf.cell(95, 5, f"Phone: {config['sender']['phone']}", 0, 1)
    pdf.cell(95, 5, f"Email: {config['sender']['email']}", 0, 1)
    pdf.ln(10)
    
    # Calculate total
    total_amount = sum(service["quantity"] * service["unit_price"] for service in config["services"])
    
    # position at left margin
    pdf.set_x(margin)

    # calculate widths
    table_width = 210 - (margin * 2)
    desc_width = table_width * 0.50  # 50% for description
    qty_width = table_width * 0.15   # 15% for quantity
    price_width = table_width * 0.15 # 15% for unit price
    amount_width = table_width * 0.20 # 20% for amount
    
    # Services table
    pdf.set_font("Arial", "B", 10)
    pdf.cell(desc_width   , 10 , "DESCRIPTION" , 'B' , 0 , "C")
    pdf.cell(qty_width    , 10 , "QUANTITY"    , 'B' , 0 , "C")
    pdf.cell(price_width  , 10 , "UNIT PRICE"  , 'B' , 0 , "C")
    pdf.cell(amount_width , 10 , "AMOUNT"      , 'B' , 1 , "C")

    # position at left margin
    pdf.set_x(margin)
    
    # Data rows
    pdf.set_font("Arial", size=10)
    for service in config["services"]:
        amount = service["quantity"] * service["unit_price"]
        pdf.cell(desc_width   , 10 , service["description"]          , 0 , 0 , "L")
        pdf.cell(qty_width    , 10 , str(service["quantity"])        , 0 , 0 , "C")
        pdf.cell(price_width  , 10 , f"${service['unit_price']:.2f}" , 0 , 0 , "R")
        pdf.cell(amount_width , 10 , f"${amount:.2f}"                , 0 , 1 , "R")
        # reset for next row
        pdf.set_x(margin)
    
    # Total row
    pdf.set_font("Arial", "B", 10)
    pdf.cell(desc_width + qty_width + price_width, 10, "TOTAL", "T", 0, "L")
    pdf.cell(amount_width, 10, f"${total_amount:.2f}", "T", 1, "R")
    
    # Add note
    pdf.ln(10)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 10, "Thank you for your business!", 0, 1, "C")
    
    # Generate filename
    month_year = invoice_date.strftime("%B_%Y")
    invoice_filename = f"Invoice_{month_year.replace(' ', '_')}.pdf"
    invoice_path = os.path.join(config["output"]["invoice_dir"], invoice_filename)
    
    # Save PDF
    pdf.output(invoice_path)
    print(f"Invoice saved to: {invoice_path}")
    
    return invoice_path, invoice_date, total_amount

def generate_email(config, invoice_path, invoice_date):
    """Generate an email file with the invoice attached."""
    # Create email directory if it doesn't exist
    os.makedirs(config["output"]["email_dir"], exist_ok=True)
    
    # Get month and year for email
    month = invoice_date.strftime("%B")
    year = invoice_date.strftime("%Y")
    
    # Format email subject and body
    subject = config["email"]["subject_template"].format(month=month, year=year)
    body = config["email"]["body_template"].format(
        client_name=config["receiver"]["name"],
        month=month,
        year=year,
        sender_name=config["sender"]["name"]
    )
    
    # Create email file
    email_filename = f"Email_{month}_{year}.txt"
    email_path = os.path.join(config["output"]["email_dir"], email_filename)
    
    with open(email_path, 'w') as f:
        f.write(f"To: {config['email']['recipient']}\n")
        f.write(f"From: {config['email']['sender']}\n")
        f.write(f"Subject: {subject}\n\n")
        f.write(body)
        f.write(f"\n\nAttachment: {os.path.basename(invoice_path)}")
    
    print(f"Email draft saved to: {email_path}")
    
    return email_path

def main():
    parser = argparse.ArgumentParser(description="Generate a PDF invoice and email draft")
    parser.add_argument("--date", help="Invoice date (YYYY-MM-DD), defaults to today", default=None)
    parser.add_argument("--config", help="Path to config file", default="config.json")
    args = parser.parse_args()
    
    # Parse invoice date if provided
    if args.date:
        invoice_date = datetime.datetime.strptime(args.date, "%Y-%m-%d").date()
    else:
        invoice_date = datetime.date.today()
    
    # Load configuration
    config = load_config(args.config)
    
    # Generate invoice
    invoice_path, invoice_date, _ = generate_invoice(config, invoice_date)
    
    # Generate email
    #email_path = generate_email(config, invoice_path, invoice_date)
    
    print("\nInvoice generation complete!")
    print(f"Invoice: {invoice_path}")
    print(f"Email draft: {email_path}")
    print("\nEdit your configuration file to customize sender, receiver, and services.")

if __name__ == "__main__":
    main()
