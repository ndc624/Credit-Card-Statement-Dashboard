import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os


class List:



    def create_list(self,data_frame,key):

        df = data_frame
        st.session_state.df = data_frame.copy()

        edited_df = st.data_editor(
            st.session_state.df[["Date" ,"Details" ,"Amount" ,"Category"]],
            column_config={
                "Date": st.column_config.DateColumn("Date" ,format="MM/DD/YYYY"),
                "Amount": st.column_config.NumberColumn("Amount" ,format = "%.2f USD"),
                "Category" :st.column_config.SelectboxColumn(
                    "Category",
                    options=list(st.session_state.categories.keys())
                )
            },
            hide_index=True,
            use_container_width=True,
            key= key
        )


        return edited_df

