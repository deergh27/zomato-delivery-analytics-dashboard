import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu

st.set_page_config(page_title="Zomato App",layout="wide")

df=pd.read_csv("zomato.csv")

# print(df.info())
# print(df.isnull().sum())

df.dropna(subset=["City"],how="any", inplace=True,axis=0)

df["Festival"]=df["Festival"].fillna("No")


mean_multiple_delivery=round(df["multiple_deliveries"].mean(),2)
df.fillna({"multiple_deliveries":mean_multiple_delivery},inplace=True)

counts=df["Weather_conditions"].value_counts().idxmax()
# print(counts)
df["Weather_conditions"].fillna(counts,inplace=True)

df.dropna(subset=["Delivery_person_Ratings"],how="any", inplace=True,axis=0)
df.dropna(subset=["Time_Orderd"],how="any", inplace=True,axis=0)
# print(df.isnull().sum())

df.to_csv("zomato.csv",index=False)



with st.sidebar:
    selected=option_menu("Main Menu",["Home","Dataset","Overview","Dashboard","Data Assistant"],
                         icons=["house","table","eye","graph-up","robot"],
                         menu_icon="shop",default_index=0)

if selected == "Home":
    st.title("🍔 Zomato Delivery Analytics App")

    st.markdown("### 📊 Smart Insights into Food Delivery Performance")

    st.write("""
    This application helps analyze and understand food delivery operations using real-world data. 
    It provides meaningful insights into delivery efficiency, customer satisfaction, and operational trends across different cities.
    """)

    st.divider()

    st.subheader("🔍 What You Can Explore")
    st.markdown("""
    - 📦 Total orders and delivery performance  
    - ⭐ Delivery partner ratings  
    - ⏱ Delivery time analysis  
    - 🏙 City-wise order distribution  
    - 🚦 Impact of traffic and weather conditions  
    - 🍕 Popular order types  
    """)

    st.divider()

    st.subheader("📈 Key Highlights")
    st.markdown("""
    - Identify which cities generate the most orders  
    - Understand factors affecting delivery time  
    - Discover top-performing delivery partners  
    - Analyze customer satisfaction trends  
    - Compare delivery performance across conditions  
    """)

    st.divider()

    st.subheader("💡 Key Insights")
    st.markdown("""
    - 🏆 Most orders come from high-density cities  
    - 🍔 Certain order types dominate demand  
    - 🚦 Traffic conditions significantly impact delivery time  
    - 🌦 Weather conditions influence delivery efficiency  
    - ⭐ Higher ratings are linked with faster deliveries  
    """)

    st.divider()

    st.subheader("🧭 How to Use This App")
    st.markdown("""
    - **Dataset** → Explore and filter raw data  
    - **Overview** → View summarized insights  
    - **Dashboard** → Visualize trends and patterns  
    - **Data Assistant** → Ask questions about the data  
    """)

    st.divider()

    st.subheader("🎯 Purpose of This Project")
    st.write("""
    This project demonstrates how data analytics can improve decision-making in food delivery services 
    by identifying trends, optimizing operations, and enhancing customer experience.
    """)


if selected=="Dataset":
    st.title("Zomato Dataset")
    st.divider()

    col1,col2,col3 = st.columns(3)
    col1.metric("Total Rows",df.shape[0])
    col2.metric("Total Columns",df.shape[1])
    col3.metric("Missing Values",df.isnull().sum().sum())

    st.divider()

    st.subheader("Select Columns")
    selected_columns = st.multiselect("Select Columns",df.columns,default=df.columns)
    filtered_df = df[selected_columns]

    st.subheader("Search in Dataset")
    search_value = st.text_input("Search Any Value")
    if search_value:
        filtered_df = filtered_df[
            filtered_df.astype(str).apply(lambda row: row.str.contains(search_value, na=False).any(), axis=1)]

    #Column Filter

    st.subheader("Column Filter")
    col1,col2 = st.columns(2)
    with col1:
        filter_column = st.selectbox("Select Column",filtered_df.columns)
    with col2:
        filter_value = st.selectbox("Select Value",filtered_df[filter_column].dropna().unique())

    if st.button("Apply Filter"):
        filtered_df=filtered_df[filtered_df[filter_column]==filter_value]
    st.divider()

    # Row Display
    st.subheader("Row Display")

    row = st.slider("Number of rows to display",10,len(filtered_df),100)
    st.divider()

    # Dataset Table

    st.subheader("Dataset Table")
    st.dataframe(filtered_df.head(row),use_container_width=True)

    # Show full dataset

    if st.checkbox("Show Full Dataset"):
        st.dataframe(filtered_df,use_container_width=True)

    st.divider()

    # column statics

    st.subheader("column statastics")
    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns

    if len(numeric_cols)>0:
        selected_col=st.selectbox("Select Column",numeric_cols)
        st.write(filtered_df[selected_col].describe())
    st.divider()

    st.subheader("Download Data")

    csv=filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button("Download Dataset",csv,"filtered_dataset.csv","text/csv")

elif selected=="Overview":
    st.subheader("Overview")

    rating=df["Delivery_person_Ratings"].mean()
    time=df["Time_taken (min)"].mean()
    order=df["Type_of_order"].value_counts().idxmax()
    city=df["City"].value_counts().idxmax()

    col1,col2,col3,col4 = st.columns(4)

    col1.metric("# Average Rating",f"{rating:.1f}")
    col2.metric("# Average Time Taken To Deliver",f"{time:.1f}")
    col3.metric("# Highly Ordered",f"{order}")
    col4.metric("# Highly Ordered City Type",f"{city}")

    st.subheader("City Performance")

    city_metrics = df.groupby("City").agg(
        Total_Orders=("ID", "count"),
        Avg_Delivery_Time=("Time_taken (min)", "mean"),
        Avg_Rating=("Delivery_person_Ratings", "mean")
    ).sort_values("Total_Orders", ascending=False)

    st.dataframe(
        city_metrics.style.format({
            "Avg_Delivery_Time": "{:.1f} min",
            "Avg_Rating": "{:.2f}"
        }).background_gradient(cmap="Pastel1"),
        use_container_width=True
    )

    st.divider()

    # DELIVERY PERSON PERFORMANCE

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top Delivery Persons (by Orders)")

        top_delivery = (df["Delivery_person_ID"].value_counts().head(10).to_frame(name="Total Orders"))

        st.dataframe(top_delivery, use_container_width=True)

    # VEHICLE ANALYSIS

    with col2:
        st.subheader("Vehicle Distribution")
        total_orders = len(df)
        vehicle_df = df["Type_of_vehicle"].value_counts().to_frame(name="Count")

        vehicle_df["%"] = (vehicle_df["Count"] / total_orders) * 100

        st.dataframe(vehicle_df, use_container_width=True)

    st.divider()

    # ORDER TYPE ANALYSIS

    st.subheader("Order Type Performance")

    order_type_df = df.groupby("Type_of_order").agg(
        Orders=("ID", "count"),
        Avg_Time=("Time_taken (min)", "mean")
    ).sort_values("Orders", ascending=False)

    st.dataframe(order_type_df, use_container_width=True)

    st.divider()

    # DATA QUALITY

    with st.expander("Data Quality Audit"):
        col1, col2 = st.columns(2)

        col1.write(f"Duplicate Records: {df.duplicated().sum()}")
        col2.write(f"Missing Values: {df.isnull().sum().sum()}")

        st.info("Check missing values in time and ratings columns.")
        st.success("Delivery Overview Generated Successfully")


elif selected == "Dashboard":
    st.title("Advanced Delivery Dashboard")
    st.divider()

    tab1, tab2 = st.tabs(["Dashboard", "Advanced Dashboard"])
    with tab2:
        st.subheader("Order Hierarchy (Order Type → City)")

        fig1 = px.sunburst(
            df,
            path=["Type_of_order", "City"],
            color_continuous_scale="Blues"
        )

        fig1.update_layout(height=500)
        st.plotly_chart(fig1, use_container_width=True)
        st.divider()

        # TREEMAP
        st.subheader("City vs Weather Distribution")

        fig2 = px.treemap(
            df,
            path=["City", "Weather_conditions"],
        )

        fig2.update_layout(margin=dict(t=20, b=0, l=0, r=0), height=420)
        st.plotly_chart(fig2, use_container_width=True)

        st.divider()

        # BOXPLOT
        st.subheader("Delivery Time Spread by Traffic Condition")

        fig3 = px.box(
            df,
            x="Road_traffic_density",
            y="Time_taken (min)",
            color="Road_traffic_density"
        )

        fig3.update_layout(height=420)
        st.plotly_chart(fig3, use_container_width=True)

        st.divider()

        # SANKEY DIAGRAM
        st.subheader("Delivery Flow Analysis (City → Vehicle)")

        import plotly.graph_objects as go

        top_cities = df["City"].value_counts().head(5).index
        filtered = df[df["City"].isin(top_cities)]

        flow = filtered.groupby(["City", "Type_of_vehicle"]).size().reset_index(name="count")

        source_labels = flow["City"].unique().tolist()
        target_labels = flow["Type_of_vehicle"].unique().tolist()

        labels = source_labels + target_labels

        source = flow["City"].apply(lambda x: labels.index(x)).tolist()
        target = flow["Type_of_vehicle"].apply(lambda x: labels.index(x)).tolist()
        value = flow["count"].tolist()

        fig4 = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=18,
                line=dict(color="gray", width=0.5),
                label=labels
            ),
            link=dict(
                source=source,
                target=target,
                value=value
            )
        )])

        fig4.update_layout(height=450)
        st.plotly_chart(fig4, use_container_width=True)

    with tab1:
        st.title("Delivery Analytics Dashboard")

        col1, col2 = st.columns(2)

        # Orders by City
        with col1:
            city_count = df["City"].value_counts().reset_index()
            city_count.columns = ["City", "Total Orders"]

            fig = px.bar(
                city_count,
                x="City",
                y="Total Orders",
                color="City",
                title="Orders by City"
            )
            st.plotly_chart(fig, use_container_width=True)

        # Total Delivery Time by City
        with col2:
            traffic_time = df.groupby("Road_traffic_density")["Time_taken (min)"].mean().reset_index()

            fig = px.bar(
                traffic_time,
                x="Road_traffic_density",
                y="Time_taken (min)",
                color="Road_traffic_density",
                title="Average Delivery Time by Traffic Condition"
            )

            st.plotly_chart(fig, use_container_width=True)

        col3, col4 = st.columns(2)

        # Vehicle Distribution
        with col3:
            vehicle = df["Type_of_vehicle"].value_counts()

            fig = px.pie(
                names=vehicle.index,
                values=vehicle.values,
                hole=0.5,
                title="Vehicle Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)

        # Festival Distribution
        with col4:
            festival = df["Festival"].value_counts()

            fig = px.pie(
                names=festival.index,
                values=festival.values,
                title="Festival vs Non-Festival"
            )
            st.plotly_chart(fig, use_container_width=True)

        st.divider()


        # Ratings Distribution

        fig = px.histogram(
            df,
            x="Delivery_person_Ratings",
            nbins=20,
            title="Ratings Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)

        st.divider()

        col7, col8 = st.columns(2)

        # Top Delivery Persons
        with col7:
            order_type = (
                df["Type_of_order"]
                .value_counts()
                .reset_index()
            )

            order_type.columns = ["Order Type", "Count"]

            fig = px.bar(
                order_type,
                x="Order Type",
                y="Count",
                color="Order Type",
                title="Order Type Distribution"
            )

            st.plotly_chart(fig, use_container_width=True)

        # Avg Delivery Time by City
        with col8:
            fig = px.histogram(
                df,
                x="Time_taken (min)",
                nbins=20,
                title="Delivery Time Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)

    st.divider()


if selected == "Data Assistant":
    st.title("🤖 Data Assistant")
    st.divider()

    st.markdown("Ask questions like: orders, rating, time, city, weather, traffic, vehicle, festival, age")

    question = st.text_input("Ask your question")

    if question:
        q = question.lower()
        if "orders" in q:
            st.success(f"Total Orders: {len(df)}")

        elif "rating" in q:
            st.success(f" Average Rating: {df['Delivery_person_Ratings'].mean():.2f}")

        elif "time" in q:
            st.success(f"Average Delivery Time: {df['Time_taken (min)'].mean():.2f} min")

        elif "city" in q:
            city = df["City"].value_counts()
            fig = px.pie(names=city.index, values=city.values, title="Orders by City")
            st.plotly_chart(fig, use_container_width=True)

        elif "weather" in q:
            weather = df["Weather_conditions"].value_counts()
            fig = px.bar(x=weather.index, y=weather.values, title="Weather Distribution")
            st.plotly_chart(fig, use_container_width=True)

        elif "traffic" in q:
            traffic = df["Road_traffic_density"].value_counts()
            fig = px.bar(x=traffic.index, y=traffic.values, title="Traffic Conditions")
            st.plotly_chart(fig, use_container_width=True)

        elif "vehicle" in q:
            vehicle = df["Type_of_vehicle"].value_counts()
            fig = px.pie(names=vehicle.index, values=vehicle.values, title="Vehicle Distribution")
            st.plotly_chart(fig, use_container_width=True)

        elif "festival" in q:
            festival = df["Festival"].value_counts()
            fig = px.pie(names=festival.index, values=festival.values, title="Festival vs Non-Festival")
            st.plotly_chart(fig, use_container_width=True)

        elif "age" in q:
            fig = px.histogram(df, x="Delivery_person_Age", nbins=20, title="Delivery Person Age Distribution")
            st.plotly_chart(fig, use_container_width=True)

        elif "order type" in q or "food" in q:
            order = df["Type_of_order"].value_counts()
            fig = px.bar(x=order.index, y=order.values, title="Order Type Distribution")
            st.plotly_chart(fig, use_container_width=True)

        elif "top city" in q:
            top_city = df["City"].value_counts().idxmax()
            st.success(f"Top City by Orders: {top_city}")

        elif "top vehicle" in q:
            top_vehicle = df["Type_of_vehicle"].value_counts().idxmax()
            st.success(f"Most Used Vehicle: {top_vehicle}")

        elif "fast" in q:
            fastest = df["Time_taken (min)"].min()
            st.success(f"Fastest Delivery Time: {fastest} min")

        elif "slow" in q:
            slowest = df["Time_taken (min)"].max()
            st.success(f"Slowest Delivery Time: {slowest} min")

        else:
            st.warning("Try asking about orders, rating, time, city, weather, traffic, vehicle, festival, age")