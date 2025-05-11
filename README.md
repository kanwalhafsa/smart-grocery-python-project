# Smart Grocery

Smart Grocery is a user-friendly web application built with Streamlit to help users manage their grocery shopping efficiently. The app allows users to track grocery items, manage budgets, export shopping lists, visualize spending patterns, and provide feedback. It is designed to simplify grocery planning with a responsive interface suitable for both desktop and mobile devices.

## Features

- **Grocery Item Management**:
  - Add, update, and delete grocery items with details like name, quantity, price, and category.
  - Store grocery data persistently in `grocery_data.json`.

- **Out-of-Stock Items**:
  - View and manage a shopping list of out-of-stock items.
  - Export shopping lists as CSV or PDF files using `reportlab`.

- **Cost Calculator and Budget Tracking**:
  - Track total grocery expenses and set budget limits.
  - Visualize spending patterns with interactive pie charts and bar graphs using `plotly`.

- **Shopping History**:
  - Save and view past shopping trips.
  - Track purchase history stored in `grocery_data.json`.

- **Feedback System**:
  - Submit feedback with name, message, and rating.
  - Store feedback data in `feedback_data.json` for future reference.

- **Responsive UI**:
  - Mobile-friendly interface for easy access on smartphones and tablets.
  - Optimized for both desktop and mobile browsers.

## Technologies Used

### Dependencies
The following Python packages are required to run the Smart Grocery app:

| Package       | Version | Purpose                                      |
|---------------|---------|----------------------------------------------|
| `streamlit`   | 1.42.1  | Web framework for building the app interface |
| `pandas`      | 2.2.3   | Data manipulation and CSV export             |
| `plotly`      | 6.0.1   | Interactive visualizations (charts, graphs)  |
| `reportlab`   | 4.4.0   | PDF generation for shopping list export      |

### Additional Tools
- **Python**: Version 3.13.x
- **Virtual Environment**: For dependency isolation
- **VS Code**: Recommended IDE with Python and Pylance extensions
- **JSON**: For persistent data storage (`grocery_data.json`, `feedback_data.json`)

## Installation

Follow these steps to set up and run the Smart Grocery app locally.

### Prerequisites
- Python 3.13.x installed ([Download Python](https://www.python.org/downloads/)).
- Git (optional, for cloning the repository).
- A code editor like VS Code.

### Steps
1. **Clone the Repository** (if hosted on GitHub):
   ```bash
   git clone https://github.com/your-username/smart-grocery.git
   cd smart-grocery