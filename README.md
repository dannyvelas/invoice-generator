# Invoice PDF Generator

A simple tool to automate the creation of PDF invoices and email drafts.

## Features

- Generates professional PDF invoices
- Creates email drafts with the invoice attached
- Configurable sender and receiver information
- Customizable services and pricing
- Command-line interface for easy automation

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/lv-pdf-generator.git
   cd lv-pdf-generator
   ```

2. Install the required dependencies:
   ```
   pip install fpdf
   ```

## Configuration

On first run, the script will create a default `config.json` file that you can customize:

```json
{
  "sender": {
    "name": "Your Name",
    "company": "Your Company",
    "address": "Your Address",
    "city": "Your City",
    "phone": "Your Phone",
    "email": "your.email@example.com"
  },
  "receiver": {
    "name": "Client Name",
    "company": "Client Company",
    "address": "Client Address",
    "city": "Client City"
  },
  "services": [
    {
      "description": "Service Description",
      "quantity": 1,
      "unit_price": 1000.00
    }
  ],
  "output": {
    "invoice_dir": "~/Invoices",
    "email_dir": "~/Emails"
  },
  "email": {
    "recipient": "client@example.com",
    "sender": "your.email@example.com",
    "subject_template": "Invoice for {month} {year}",
    "body_template": "Dear {client_name},\n\nI hope you are all well!\n\nAttached below is the invoice for {month} {year}. Please let me know if you have any questions or concerns.\n\nAll the best,\n{sender_name}"
  }
}
```

## Usage

Run the script to generate an invoice for the current month:

```
python invoice_generator.py
```

To generate an invoice for a specific date:

```
python invoice_generator.py --date 2025-04-01
```

To use a different configuration file:

```
python invoice_generator.py --config my_config.json
```

## Output

The script will:

1. Create a PDF invoice in the specified invoice directory
2. Generate an email draft in the specified email directory
3. Print the paths to the generated files

## Automating Monthly Invoices

You can use cron (Linux/Mac) or Task Scheduler (Windows) to run this script automatically each month.

Example cron entry to run on the 1st of each month at 9am:

```
0 9 1 * * python /path/to/invoice_generator.py
```