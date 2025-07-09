import datetime
from datetime import date
import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
from chase_statement import Chase
from list_visualizer import List
from expense_summary_visualizer import Summary


TAB = ""
MONTHLY_OR_WEEKLY = "Monthly"

st.set_page_config(page_title="Simple Finance App", page_icon="$",layout = "wide")

category_file = "categories.json"

# Things we want to persist after each reload need to be stored in this state
if "categories" not in st.session_state:
    st.session_state.categories = {
        "Uncategorized": []
    }

if os.path.exists(category_file):
    with open(category_file,"r") as f:
        st.session_state.categories = json.load(f)

def save_categories():
    with open(category_file, "w") as f:
        json.dump(st.session_state.categories, f)

def categorize_transactions(df):
    df["Category"] = "Uncategorized"

    for category, keywords in st.session_state.categories.items():
        if category == "Uncategorized" or not keywords:
            continue

        lowered_keywords = [keyword.lower().strip() for keyword in keywords]

        for idx, row in df.iterrows():
            details =  row["Details"].lower()
            if details in lowered_keywords:
                df.at[idx, "Category"] = category

    return df

def load_transactions(file):

    try:
        df = pd.read_csv(file)
        df.columns = [col.strip() for col in df.columns]
        df["Details"] = df["Description"].str.strip().replace(r'\s+',' ', regex=True)
        df["Amount"] = df["Amount"].astype(str).str.replace(",","").astype(float)
        df["Date"] = pd.to_datetime(df["Date"],format="mixed")
        df = df.sort_values(by=["Date"])

        debit_credit = []

        for _ in df["Amount"]:

            if _ < 0:
                debit_credit.append("Credit")
            else:
                debit_credit.append("Debit")

        currency = ["USD" for number in df["Amount"]]

        # for date in df["Date"]:
        #
        #     df["Date"] = date.date()

        df["Currency"] = currency
        df["Debit/Credit"] = debit_credit

        return categorize_transactions(df)

    except:

        statement = Chase(file=file)
        df = statement.pdf_convert(file)

        return  categorize_transactions(df)


def add_keyword_to_category(category,keyword):
    keyword = keyword.strip()
    if keyword and keyword not in st.session_state.categories[category]:
        st.session_state.categories[category].append(keyword)
        save_categories()
        return True

def date_range(starting_date,ending_date,df):
    list_of_transactions = List()
    expense_visualizer = Summary()

    filtered_df = df.loc[
        (df['Date'] >= str(starting_date) + " 00:00:00")
        & (df['Date'] <= str(ending_date) + " 00:00:00") & (df["Debit/Credit"] == TAB)]

    expense_visualizer.create_summary(filtered_df)
    list_of_transactions.create_list(data_frame= filtered_df, key="category_editor_debit_date")

    def submit():
        # col1, col2, col3 = st.columns([20, 45, 7], vertical_alignment="bottom")
        # with col3:
        #     st.button("Apply Changes", type="primary", key="debit_save")

        st.session_state.my_text = st.text_input("New Category Name", key="debit_cat", on_change=submit, width=2000)
        st.session_state.widget = ""
    col1, col2, col3 = st.columns([20, 45, 7], vertical_alignment="bottom")
    with col3:
        st.button("Apply Changes", type="primary", key="debit_save")
    with col1:
        st.session_state.my_text = st.text_input("New Category Name", key="debit_cat", on_change=submit, width=2000)
        st.session_state.widget = ""
    edited_expense_visualizer = expense_visualizer.create_table(filtered_df)
    expense_visualizer.create_chart(filtered_df)


# def submit():
#     st.session_state.my_text = st.session_state.widget
#     st.session_state.widget = ""



def main():

    list_of_transactions = List()
    expense_visualizer = Summary()

    st.title("Chase / Amex Statement Dashboard")

    uploaded_file = st.file_uploader("Upload your transaction CSV file", type = ["csv","pdf"])

    if uploaded_file is not None:
        df = load_transactions(uploaded_file)

        if df is not None:
            debits_df = df[df["Debit/Credit"] == "Debit"].copy()
            credits_df = df[df["Debit/Credit"] == "Credit"].copy()


            st.session_state.debits_df = debits_df.copy()
            st.session_state.credits_df = credits_df.copy()


            tab1, tab2, tab3 = st.tabs(["Expenses (Debits)", "Payments (Credits)", "Monthly / Weekly Spending"])

# DEBITS TAB
            with tab1:
    # COLUMNS
                col1, col2, col3 = st.columns([1,1,1],vertical_alignment="bottom")

                with col1:
                    starting_date = st.date_input("Choose Starting Date", value=None, width=200, format="MM/DD/YYYY",
                                key="st_debit")
                with col2:
                    ending_date = st.date_input("Choose Ending Date", value=None, width=200, format="MM/DD/YYYY",
                                key="ed_debit")
                with col3:
                    save_date_button_debit = st.button("Confirm Dates", type="primary", key="sd_debit")

    # RESET BUTTON AND NOT SAVE BUTTON
                reset_button = st.button("Reset", type="secondary",key="reset_debit")
                not_save_button = not save_date_button_debit

    # BASE STATE (YOUR EXPENSES / TOTAL EXPENSES / DATA FRAME / APPLY CHANGES BUTTON)
                if not save_date_button_debit:
                    expense_visualizer.create_summary(debits_df)
                    edited_df = list_of_transactions.create_list(data_frame=debits_df, key= "edited_df_debit")
                    col1, col2, col3 = st.columns([20,45,7], vertical_alignment="bottom")
                    with col3:
                        save_button_debit = st.button("Apply Changes", type="primary", key="debit_save")

                if not save_date_button_debit:

                    if "my_text" not in st.session_state:
                        st.session_state.my_text = ""

                    def submit():
                        st.session_state.widget = ""

                    with col1:
                        new_category = st.text_input("New Category Name", key="debit_cat_1",on_change=submit,width=2000)

                    my_text = st.session_state.my_text

    # ADD CATEGORY
                    if my_text is not None and new_category:
                        if new_category not in st.session_state.categories:
                            st.session_state.categories[new_category] = []
                            save_categories()
                            st.rerun()
    # BASE STATE (EXPENSE SUMMARY / EXPENSES BY CATEGORY)
                if not save_date_button_debit:
                    edited_expense_visualizer_debit = expense_visualizer.create_table(debits_df)
                    expense_visualizer.create_chart(debits_df)

    # CONFIRM DATE BUTTON CHOSEN
                if save_date_button_debit:
                    try:
                        edited_df = None
                        global TAB
                        TAB = "Debit"
                        date_range(starting_date, ending_date, df)
                    except TypeError:
                        return not_save_button
    # RESET BUTTON CHOSEN
                if reset_button:
                    return not_save_button

    # APPLY CHANGES BUTTON CHOSEN
                if save_button_debit:
                    for idx, row in edited_df.iterrows():
                        new_category = row["Category"]
                        if row["Category"] == st.session_state.debits_df.at[idx, "Category"]:
                            continue

                        details = row["Details"]
                        st.session_state.debits_df.at[idx,"Category"] = new_category
                        add_keyword_to_category(new_category,details)



# CREDITS TAB
            with tab2:
    # COLUMNS
                col1, col2, col3 = st.columns([1, 1, 1], vertical_alignment="bottom")

                with col1:
                    starting_date = st.date_input("Choose Starting Date", value=None, width=200, format="MM/DD/YYYY",
                                                  key="st_credit")
                with col2:
                    ending_date = st.date_input("Choose Ending Date", value=None, width=200, format="MM/DD/YYYY",
                                                key="ed_credit")
                with col3:
                    save_date_button_credit = st.button("Confirm Dates", type="primary", key="sd_credit")

    # RESET BUTTON AND NOT SAVE BUTTON
                reset_button = st.button("Reset", type="secondary", key="reset_credit")
                not_save_button = not save_date_button_credit

    # BASE STATE (YOUR EXPENSES / TOTAL EXPENSES / DATA FRAME / APPLY CHANGES BUTTON)
                if not save_date_button_credit:
                    expense_visualizer.create_summary(credits_df)
                    edited_df = list_of_transactions.create_list(data_frame=credits_df, key= "edited_df_credit")
                    col1, col2, col3 = st.columns([20, 45, 7], vertical_alignment="bottom")
                    with col3:
                        save_button_credit = st.button("Apply Changes", type="primary", key="credit_save")

                if not save_date_button_credit:

                    if "my_text" not in st.session_state:
                        st.session_state.my_text = ""

                    def submit():
                        st.session_state.widget = ""

                    with col1:
                        new_category = st.text_input("New Category Name", key="credit_cat_1",on_change=submit,width=2000)


                    my_text = st.session_state.my_text

    # ADD CATEGORY
                    if my_text is not None and new_category:
                        if new_category not in st.session_state.categories:
                            st.session_state.categories[new_category] = []
                            save_categories()
                            st.rerun()
    # BASE STATE (EXPENSE SUMMARY / EXPENSES BY CATEGORY)
                if not save_date_button_credit:
                    edited_expense_visualizer_credit = expense_visualizer.create_table(credits_df)


    # CONFIRM DATE BUTTON CHOSEN
                if save_date_button_credit:
                    try:
                        edited_df = None
                        TAB = "Credit"
                        date_range(starting_date, ending_date, df)
                    except TypeError:
                        # st.toast("No Dates Selected")
                        return not_save_button
    # RESET BUTTON CHOSEN
                if reset_button:
                    return not_save_button
    # APPLY CHANGES BUTTON CHOSEN
                if save_button_credit:
                    for idx, row in edited_df.iterrows():
                        new_category = row["Category"]
                        if row["Category"] == st.session_state.credits_df.at[idx, "Category"]:
                            continue

                        details = row["Details"]
                        st.session_state.credits_df.at[idx, "Category"] = new_category
                        add_keyword_to_category(new_category, details)




            with (tab3):
    # WEEKLY / MONTHLY BAR GRAPHS
                
                global MONTHLY_OR_WEEKLY
                weekly_amount = []
                monthly_amount = []

    # WEEKLY AND MONTHLY SUMS
                debits_df['Date'] = pd.to_datetime(debits_df['Date']) - pd.to_timedelta(7, unit='d')
                weekly_sum = debits_df.groupby([pd.Grouper(key='Date', freq='W')])['Amount'].sum()
                monthly_sum = debits_df.groupby([pd.Grouper(key='Date', freq='ME')])['Amount'].sum()

    # SWITCH TO MONTHLY / WEEKLY BUTTON
                switch_button = st.empty()
                switch = switch_button.button(f"Switch to Monthly Spending",type="primary",key=1)

                if switch:

                    weekly_sum = monthly_sum
                    MONTHLY_OR_WEEKLY = "Weekly"
                    switch_button.empty()
                    st.button(f"Switch to Weekly Spending", type="primary", key=2)

                fig = px.bar(weekly_sum, x=weekly_sum.index, y=weekly_sum)
                st.plotly_chart(fig, key="data_frame_bar")

        return None
    return None


main()
