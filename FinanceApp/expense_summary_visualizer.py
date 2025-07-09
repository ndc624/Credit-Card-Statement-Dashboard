import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os


class Summary:

    def create_summary(self,data_frame):

        df = data_frame
        st.session_state.df = data_frame.copy()

        st.subheader("Your Expenses")
        total_expenses = df["Amount"].sum()
        st.metric(f"Total Expenses", f"{total_expenses:,.2f} USD")


    def create_table(self,data_frame):

        df = data_frame
        st.session_state.df = data_frame.copy()

        st.subheader("Expense Summary")
        category_totals = st.session_state.df.groupby("Category")["Amount"].sum().reset_index()
        category_totals = category_totals.sort_values("Amount", ascending=False)

        st.dataframe(
            category_totals,
            column_config={
                "Amount": st.column_config.NumberColumn("Amount", format="%.2f USD")
            },
            use_container_width=True,
            hide_index=True
        )
    def create_chart(self,data_frame):

        st.session_state.data_frame = data_frame.copy()

        category_totals = st.session_state.data_frame.groupby("Category")["Amount"].sum().reset_index()
        category_totals = category_totals.sort_values("Amount", ascending=False)


        fig = px.pie(
            category_totals,
            values="Amount",
            names="Category",
            title="Expenses by Category"
        )
        st.plotly_chart(fig,key=data_frame)
