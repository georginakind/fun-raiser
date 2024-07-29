from collections import defaultdict
from pathlib import Path
import sqlite3

import streamlit as st
import altair as alt
import pandas as pd
from vega_datasets import data

source = data.barley()

st.bar_chart(df, x="variety", y="yield", color="site", horizontal=True)


# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title="Fun Raiser",
    page_icon=":clinking_glasses:",  # This is an emoji shortcode. Could be a URL too.
)


# -----------------------------------------------------------------------------
# Declare some useful functions.


def connect_db():
    """Connects to the sqlite database."""

    DB_FILENAME = Path(__file__).parent / "inventory.db"
    db_already_exists = DB_FILENAME.exists()

    conn = sqlite3.connect(DB_FILENAME)
    db_was_just_created = not db_already_exists

    return conn, db_was_just_created


def initialize_data(conn):
    """Initializes the inventory table with some data."""
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT,
            price REAL,
            units_sold INTEGER,
            units_left INTEGER
        )
        """
    )

    cursor.execute(
        """
        INSERT INTO inventory
            (item_name, price, units_sold, units_left)
        VALUES
            -- Beverages
            ('Bottled Water (500ml)', 1.50, 115, 15)
           
        """
    )
    conn.commit()


def load_data(conn):
    """Loads the inventory data from the database."""
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM inventory")
        data = cursor.fetchall()
    except:
        return None

    df = pd.DataFrame(
        data,
        columns=[
            "id",
            "item_name",
            "price",
            "units_sold",
            "units_left"
        ],
    )

    return df


def update_data(conn, df, changes):
    """Updates the inventory data in the database."""
    cursor = conn.cursor()


# -----------------------------------------------------------------------------
# Draw the actual page, starting with the inventory table.

# Set the title that appears at the top of the page.
"""
# :clinking_glasses: Fun Raiser

**Welcome to GK Bday Fun Raiser!  Thank you for supporting a great cause.**  
Please, drink like lives depend on it (they do)

"""

st.info(
    """
    Use the table below to add, remove, and edit items.
    And don't forget to commit your changes when you're done.
    """
)

# Connect to database and create table if needed
conn, db_was_just_created = connect_db()

# Initialize data.
if db_was_just_created:
    initialize_data(conn)
    st.toast("Database initialized with some sample data.")

# Load data from database
df = load_data(conn)

# Display data with editable table
edited_df = st.data_editor(
    df,
    disabled=["id"],  # Don't allow editing the 'id' column.
    num_rows="dynamic",  # Allow appending/deleting rows.
    column_config={
        # Show dollar sign before price columns.
        "price": st.column_config.NumberColumn(format="$%.2f"),
        "cost_price": st.column_config.NumberColumn(format="$%.2f"),
    },
    key="inventory_table",
)

has_uncommitted_changes = any(len(v) for v in st.session_state.inventory_table.values())

st.button(
    "Commit changes",
    type="primary",
    disabled=not has_uncommitted_changes,
    # Update data in database
    on_click=update_data,
    args=(conn, df, st.session_state.inventory_table),
)


# -----------------------------------------------------------------------------
# Now some cool charts

# Add some space
""
""
""

st.subheader("Units left", divider="red")

""
""

# -----------------------------------------------------------------------------

st.bar_chart(source, x="variety", y="yield", color="site", horizontal=True)
