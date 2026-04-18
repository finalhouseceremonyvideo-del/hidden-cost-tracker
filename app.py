import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Try loading AI
use_ai = False
try:
    from openai import OpenAI
    api_key = os.getenv("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")
    if api_key:
        client = OpenAI(api_key=api_key)
        use_ai = True
except:
    use_ai = False

# Page setup
st.set_page_config(page_title="Hidden Cost Tracker", layout="wide")

st.title("🔍 Hidden Cost Tracker")
st.subheader("Detect Hidden Cost & Productivity Leaks")

st.success("Connected to enterprise data source ✅")

# Load data
df = pd.read_csv("sample_data.csv")

st.write("### 📊 Company Data")
st.dataframe(df)

if st.button("Analyze Hidden Loss"):

    total_employees = len(df)

    idle_df = df[df["Hours_Active"] == 0]
    idle_count = len(idle_df)

    low_prod_df = df[df["Tasks_Completed"] == 0]
    low_prod_count = len(low_prod_df)

    cost_loss = idle_df["License_Cost"].sum()

    # KPIs
    st.write("## 🚨 Key Metrics")

    col1, col2, col3 = st.columns(3)
    col1.metric("💸 Monthly Loss", f"₹{cost_loss}")
    col2.metric("👥 Idle Employees", idle_count)
    col3.metric("📉 Low Productivity", low_prod_count)

    st.write("---")

    # 📊 Chart 1: Cost Distribution
    tool_cost = df.groupby("Tool")["License_Cost"].sum().reset_index()

    fig1 = px.pie(
        tool_cost,
        values="License_Cost",
        names="Tool",
        title="💸 Cost Distribution by Tool"
    )
    st.plotly_chart(fig1, use_container_width=True)

    # 📊 Chart 2: Productivity
    fig2 = px.bar(
        df,
        x="Employee",
        y="Tasks_Completed",
        title="📊 Employee Productivity"
    )
    st.plotly_chart(fig2, use_container_width=True)

    # 📊 Chart 3: Workforce Status
    df["Status"] = df["Hours_Active"].apply(lambda x: "Idle" if x == 0 else "Active")

    status_count = df["Status"].value_counts().reset_index()
    status_count.columns = ["Status", "Count"]

    fig3 = px.pie(
        status_count,
        values="Count",
        names="Status",
        hole=0.5,
        title="👥 Workforce Status"
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.write("---")

    # 🤖 Insights
    st.write("## 🤖 Insights")

    if use_ai:
        try:
            prompt = f"""
            Analyze this company data:

            Total Employees: {total_employees}
            Idle Employees: {idle_count}
            Low Productivity: {low_prod_count}
            Monthly Loss: ₹{cost_loss}

            Give:
            1. Key Problems
            2. Business Impact
            3. Recommendations
            """

            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}]
            )

            st.success("AI Insights Generated ✅")
            st.write(response.choices[0].message.content)

        except:
            st.error("AI failed, showing fallback insights")
            use_ai = False

    if not use_ai:
        st.warning("Using Smart Rule-Based Insights")

        st.write(f"""
        • The company is losing approximately ₹{cost_loss} per month due to unused licenses.

        • {idle_count} employees are inactive but consuming resources.

        • {low_prod_count} employees show zero productivity.

        👉 Recommendations:
        - Reallocate unused licenses
        - Monitor idle workforce
        - Improve task distribution
        """)

    st.success("Analysis Completed ✅")