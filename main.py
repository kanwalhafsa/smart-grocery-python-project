import streamlit as st
import pandas as pd
import plotly.express as px
from abc import ABC, abstractmethod
from typing import List, Dict
import uuid
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
import json
import os

# Abstract Base Class for Items
class Item(ABC):
    def __init__(self, name: str, price: float, category: str, unit: str):
        self.__id = str(uuid.uuid4())
        self.__name = name
        self.__price = price
        self.__category = category
        self.__unit = unit

    @property
    def id(self) -> str:
        return self.__id

    @property
    def name(self) -> str:
        return self.__name

    @property
    def price(self) -> float:
        return self.__price

    @property
    def category(self) -> str:
        return self.__category

    @property
    def unit(self) -> str:
        return self.__unit

    @abstractmethod
    def display(self) -> str:
        pass

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "category": self.category,
            "unit": self.unit
        }

# GroceryItem Class (Inherits from Item)
class GroceryItem(Item):
    def __init__(self, name: str, price: float, category: str, unit: str, quantity: float = 0):
        super().__init__(name, price, category, unit)
        self.__quantity = quantity

    @property
    def quantity(self) -> float:
        return self.__quantity

    def increase_quantity(self, amount: float = 1):
        self.__quantity += amount

    def decrease_quantity(self, amount: float = 1):
        if self.__quantity >= amount:
            self.__quantity -= amount

    def display(self) -> str:
        return f"{self.name}: ${self.price:.2f}/{self.unit}, Quantity: {self.quantity} {self.unit}, Category: {self.category}"

    def to_dict(self) -> Dict:
        base_dict = super().to_dict()
        base_dict["quantity"] = self.quantity
        return base_dict

# GroceryManager Class (Manages grocery items, budget, history, and feedback)
class GroceryManager:
    def __init__(self, data_file: str = "grocery_data.json", feedback_file: str = "feedback_data.json"):
        self.__items: List[GroceryItem] = []
        self.__budgets: Dict[str, float] = {"Total": 0.0}
        self.__history: List[Dict] = []
        self.__data_file = data_file
        self.__feedback_file = feedback_file
        self.__feedbacks: List[Dict] = []
        self.__load_data()
        self.__load_feedback()

    def __load_data(self):
        try:
            if os.path.exists(self.__data_file):
                with open(self.__data_file, 'r') as f:
                    data = json.load(f)
                    # Check if data is a dictionary
                    if not isinstance(data, dict):
                        st.warning("Invalid JSON structure in grocery_data.json. Initializing default data.")
                        self.__initialize_items()
                        return
                    self.__items = [
                        GroceryItem(
                            name=item["name"],
                            price=item["price"],
                            category=item["category"],
                            unit=item["unit"],
                            quantity=item["quantity"]
                        ) for item in data.get("items", [])
                    ]
                    self.__budgets = data.get("budgets", {"Total": 0.0})
                    self.__history = data.get("history", [])
            else:
                self.__initialize_items()
        except json.JSONDecodeError:
            st.warning("Corrupted JSON file detected. Initializing default data.")
            self.__initialize_items()

    def __save_data(self):
        data = {
            "items": [item.to_dict() for item in self.__items],
            "budgets": self.__budgets,
            "history": self.__history
        }
        with open(self.__data_file, 'w') as f:
            json.dump(data, f, indent=4)

    def __load_feedback(self):
        try:
            if os.path.exists(self.__feedback_file):
                with open(self.__feedback_file, 'r') as f:
                    self.__feedbacks = json.load(f)
                    if not isinstance(self.__feedbacks, list):
                        self.__feedbacks = []
            else:
                self.__feedbacks = []
        except json.JSONDecodeError:
            self.__feedbacks = []

    def __save_feedback(self):
        with open(self.__feedback_file, 'w') as f:
            json.dump(self.__feedbacks, f, indent=4)

    def __initialize_items(self):
        initial_items = [
            GroceryItem("Milk", 3.5, "Dairy", "liter", 2),
            GroceryItem("Bread", 2.0, "Bakery", "piece", 1),
            GroceryItem("Rice", 10.0, "Grains", "kg", 0),
            GroceryItem("Tomato", 1.5, "Vegetables", "kg", 3),
            GroceryItem("Chips", 2.5, "Snacks", "piece", 0),
            GroceryItem("Juice", 4.0, "Beverages", "liter", 1),
        ]
        self.__items.extend(initial_items)
        self.__save_data()

    def add_item(self, item: GroceryItem):
        self.__items.append(item)
        self.__save_data()

    def delete_item(self, item_id: str):
        self.__items = [item for item in self.__items if item.id != item_id]
        self.__save_data()

    def set_budget(self, category: str, amount: float):
        self.__budgets[category] = amount
        if category != "Total":
            self.__budgets["Total"] = sum(v for k, v in self.__budgets.items() if k != "Total")
        self.__save_data()

    def check_budget(self, category: str = None) -> bool:
        if category:
            total_spent = sum(item.price * item.quantity for item in self.__items if item.category == category and item.quantity > 0)
            budget = self.__budgets.get(category, 0)
            return total_spent <= budget or budget == 0
        else:
            total_spent = self.get_total_cost()
            budget = self.__budgets.get("Total", 0)
            return total_spent <= budget or budget == 0

    def get_items(self, search_query: str = "") -> List[GroceryItem]:
        if search_query:
            return [item for item in self.__items if search_query.lower() in item.name.lower() or search_query.lower() in item.category.lower()]
        return self.__items

    def get_out_of_stock_items(self) -> List[GroceryItem]:
        return [item for item in self.__items if item.quantity == 0]

    def get_total_cost(self) -> float:
        return sum(item.price * item.quantity for item in self.__items if item.quantity > 0)

    def get_category_summary(self) -> Dict[str, float]:
        summary = {}
        for item in self.__items:
            if item.quantity > 0:
                summary[item.category] = summary.get(item.category, 0) + (item.price * item.quantity)
        return summary

    def save_shopping_trip(self):
        items_bought = [item for item in self.__items if item.quantity > 0]
        if items_bought:
            trip = {
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "items": [(item.name, item.quantity, item.unit, item.price) for item in items_bought],
                "total_cost": self.get_total_cost()
            }
            self.__history.append(trip)
            self.__save_data()

    def get_history(self) -> List[Dict]:
        return self.__history

    def export_to_csv(self) -> BytesIO:
        out_of_stock = self.get_out_of_stock_items()
        data = [{"Item": item.name, "Category": item.category, "Price": item.price, "Unit": item.unit} for item in out_of_stock]
        df = pd.DataFrame(data)
        buffer = BytesIO()
        df.to_csv(buffer, index=False)
        buffer.seek(0)
        return buffer

    def export_to_pdf(self) -> BytesIO:
        out_of_stock = self.get_out_of_stock_items()
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        c.setFont("Helvetica", 12)
        c.drawString(100, 750, "Shopping List (Out-of-Stock Items)")
        y = 730
        for item in out_of_stock:
            c.drawString(100, y, f"{item.name} ({item.category}) - ${item.price:.2f}/{item.unit}")
            y -= 20
        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer

    def add_feedback(self, name: str, message: str, rating: int):
        feedback = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "name": name,
            "message": message,
            "rating": rating
        }
        self.__feedbacks.append(feedback)
        self.__save_feedback()

    def get_feedbacks(self) -> List[Dict]:
        return self.__feedbacks

# Custom CSS for Mobile-Friendly and Aesthetic UI
custom_css = """
<style>
body {
    font-family: 'Arial', sans-serif;
}
.stApp {
    background-color: #f0f2f6;
}
h1, h2, h3 {
    color: #2e7d32;
}
.stButton>button {
    background-color: #4caf50;
    color: white;
    border-radius: 8px;
    padding: 8px 16px;
    margin: 5px;
}
.stButton>button:hover {
    background-color: #45a049;
}
.stTextInput>input, .stSelectbox, .stNumberInput>input, .stTextArea>textarea {
    border-radius: 5px;
    border: 1px solid #ccc;
    padding: 8px;
}
.stDataFrame {
    border: 1px solid #ddd;
    border-radius: 5px;
}
@media (max-width: 600px) {
    .stButton>button {
        width: 100%;
        margin: 5px 0;
    }
    .stDataFrame {
        font-size: 14px;
    }
    .stColumn {
        flex: 1 1 100%;
    }
}
</style>
"""

# Streamlit App
def main():
    st.set_page_config(layout="wide", page_title="Grocery Tracker", page_icon="🛒")
    st.markdown(custom_css, unsafe_allow_html=True)
    st.title("🛒 Grocery Expense Tracker")

    # Initialize session state
    if 'manager' not in st.session_state:
        st.session_state.manager = GroceryManager()

    manager = st.session_state.manager

    # Sidebar for navigation
    page = st.sidebar.selectbox("Select Page", ["Grocery Items", "Out-of-Stock Items", "Cost Calculator", "Shopping History", "Feedback"])

    if page == "Grocery Items":
        st.header("Grocery Items")

        # Search Bar
        search_query = st.text_input("Search Items (by name or category)", placeholder="Type to search...")
        
        # Add New Item
        st.subheader("Add New Item")
        with st.form(key="add_item_form"):
            new_name = st.text_input("Item Name")
            new_price = st.number_input("Price ($)", min_value=0.0, step=0.01)
            new_category = st.selectbox("Category", ["Dairy", "Bakery", "Grains", "Vegetables", "Snacks", "Beverages", "Other"])
            new_unit = st.selectbox("Unit", ["kg", "liter", "piece"])
            submit = st.form_submit_button("Add Item")
            if submit and new_name and new_price > 0:
                manager.add_item(GroceryItem(new_name, new_price, new_category, new_unit))
                st.success(f"Added {new_name}!")

        # Set Budget
        st.subheader("Set Budget")
        with st.form(key="budget_form"):
            budget_category = st.selectbox("Category", ["Total", "Dairy", "Bakery", "Grains", "Vegetables", "Snacks", "Beverages", "Other"])
            budget_amount = st.number_input("Budget Amount ($)", min_value=0.0, step=0.01)
            budget_submit = st.form_submit_button("Set Budget")
            if budget_submit:
                manager.set_budget(budget_category, budget_amount)
                st.success(f"Budget set for {budget_category}: ${budget_amount:.2f}")

        # Display Items
        st.subheader("All Items")
        items = manager.get_items(search_query)
        if items:
            for item in items:
                col1, col2, col3, col4, col5, col6 = st.columns([3, 1, 1, 1, 1, 1])
                col1.write(item.display())
                col2.write(f"Price: ${item.price:.2f}/{item.unit}")
                col3.write(f"Qty: {item.quantity} {item.unit}")
                qty_change = col4.number_input("Change Qty", min_value=0.0, value=1.0, step=0.5, key=f"qty_{item.id}")
                if col4.button("+", key=f"inc_{item.id}"):
                    item.increase_quantity(qty_change)
                    st.rerun()
                if col5.button("-", key=f"dec_{item.id}"):
                    item.decrease_quantity(qty_change)
                    if item.quantity == 0:
                        st.warning(f"Warning: {item.name} is now out of stock!")
                    st.rerun()
                if col6.button("Delete", key=f"del_{item.id}"):
                    manager.delete_item(item.id)
                    st.rerun()
        else:
            st.write("No items found.")

    elif page == "Out-of-Stock Items":
        st.header("Out-of-Stock Items (Shopping List)")
        out_of_stock = manager.get_out_of_stock_items()
        if out_of_stock:
            data = [{"Item": item.name, "Category": item.category, "Price": item.price, "Unit": item.unit} for item in out_of_stock]
            st.dataframe(pd.DataFrame(data))
            st.subheader("Export Shopping List")
            col1, col2 = st.columns(2)
            with col1:
                csv_buffer = manager.export_to_csv()
                st.download_button("Download CSV", csv_buffer, "shopping_list.csv", "text/csv")
            with col2:
                pdf_buffer = manager.export_to_pdf()
                st.download_button("Download PDF", pdf_buffer, "shopping_list.pdf", "application/pdf")
        else:
            st.write("No items are out of stock.")

    elif page == "Cost Calculator":
        st.header("Cost Calculator")
        total_cost = manager.get_total_cost()
        st.write(f"**Total Cost**: ${total_cost:.2f}")

        if not manager.check_budget():
            st.warning(f"Warning: Total expenses (${total_cost:.2f}) exceed total budget (${manager._GroceryManager__budgets.get('Total', 0):.2f})!")
        
        st.subheader("Category-wise Breakdown")
        summary = manager.get_category_summary()
        if summary:
            data = [{"Category": cat, "Total Cost": total, "Within Budget": manager.check_budget(cat)} for cat, total in summary.items()]
            st.dataframe(pd.DataFrame(data))
            for cat, total in summary.items():
                if not manager.check_budget(cat):
                    st.warning(f"Warning: {cat} expenses (${total:.2f}) exceed budget (${manager._GroceryManager__budgets.get(cat, 0):.2f})!")
        
        st.subheader("Visual Dashboard")
        if summary:
            pie_data = pd.DataFrame(list(summary.items()), columns=["Category", "Total Cost"])
            fig_pie = px.pie(pie_data, names="Category", values="Total Cost", title="Category-wise Spending")
            st.plotly_chart(fig_pie)
            item_counts = {}
            for item in manager.get_items():
                if item.quantity > 0:
                    item_counts[item.name] = item.quantity
            if item_counts:
                bar_data = pd.DataFrame(list(item_counts.items()), columns=["Item", "Quantity"])
                fig_bar = px.bar(bar_data, x="Item", y="Quantity", title="Most-Used Items")
                st.plotly_chart(fig_bar)

    elif page == "Shopping History":
        st.header("Shopping History")
        if st.button("Save Current Shopping Trip"):
            manager.save_shopping_trip()
            st.success("Shopping trip saved!")
        history = manager.get_history()
        if history:
            for trip in history:
                st.subheader(f"Date: {trip['date']}")
                st.write(f"Total Cost: ${trip['total_cost']:.2f}")
                data = [{"Item": name, "Quantity": qty, "Unit": unit, "Price": price} for name, qty, unit, price in trip['items']]
                st.dataframe(pd.DataFrame(data))
        else:
            st.write("No shopping history available.")

    elif page == "Feedback":
        st.header("Feedback")
        st.write("We value your feedback! Please share your suggestions or experience with the app.")
        with st.form(key="feedback_form"):
            feedback_name = st.text_input("Name (Optional)", placeholder="Enter your name")
            feedback_message = st.text_area("Feedback", placeholder="Enter your feedback or suggestions")
            feedback_rating = st.selectbox("Rating", [1, 2, 3, 4, 5], format_func=lambda x: f"{x} Star{'s' if x > 1 else ''}")
            feedback_submit = st.form_submit_button("Submit Feedback")
            if feedback_submit and feedback_message:
                manager.add_feedback(feedback_name, feedback_message, feedback_rating)
                st.success("Thank you for your feedback!")
            elif feedback_submit:
                st.error("Please enter a feedback message.")

        # Display Feedbacks (for admin view, can be toggled off)
        if st.checkbox("Show Feedbacks (Admin View)"):
            feedbacks = manager.get_feedbacks()
            if feedbacks:
                st.subheader("Submitted Feedbacks")
                for fb in feedbacks:
                    st.write(f"**Timestamp**: {fb['timestamp']}")
                    st.write(f"**Name**: {fb['name'] or 'Anonymous'}")
                    st.write(f"**Feedback**: {fb['message']}")
                    st.write(f"**Rating**: {fb['rating']} Stars")
                    st.write("---")
            else:
                st.write("No feedbacks submitted yet.")

if __name__ == "__main__":
    main()