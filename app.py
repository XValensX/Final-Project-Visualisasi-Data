import streamlit as st
import pandas as pd
import plotly.express as px

# Load the dataset
@st.cache_data
def load_data():
    data = pd.read_csv('renewable_dataset.csv')
    return data

# Main function to run the Streamlit app
def main():
    st.title("Renewable Energy Household Dashboard")

    # Load data
    data = load_data()

    # Sort the data by Year
    data = data.sort_values(by='Year')

    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Data Overview", "Bar Charts", "Map with Filter"])

    # Data Overview Tab
    with tab1:
        st.subheader("Dataset Overview")
        st.dataframe(data)

    # Bar Charts Tab
    with tab2:
        st.subheader("Bar Charts")

        # Monthly Usage by Energy Source
        st.subheader("Monthly Usage by Energy Source")
        st.write("This chart shows the household's average monthly energy usage (in kWh) for different renewable energy sources.")

        # Create animated bar chart for Monthly Usage by Energy Source
        avg_usage = data.groupby(['Year', 'Energy_Source'])['Monthly_Usage_kWh'].mean().reset_index()
        fig_usage = px.bar(avg_usage, 
                            x='Energy_Source', 
                            y='Monthly_Usage_kWh',
                            animation_frame='Year',
                            range_y=[0, avg_usage['Monthly_Usage_kWh'].max() * 1.1],
                            title='Average Monthly Usage by Energy Source Over Years',
                            labels={'Monthly_Usage_kWh': 'Average Monthly Usage (kWh)'}
                        )
        fig_usage.update_layout(
            margin=dict(l=20, r=20, t=40, b=20), 
            transition_duration=1500, 
            yaxis_title='Average Monthly Usage (kWh)',
            xaxis_title='Energy Source',
            coloraxis_showscale=False
        )
        fig_usage.update_traces(marker_color='rgb(158,202,225)',
                                marker_line_color='rgb(8,48,107)',
                                marker_line_width=1.5, 
                                texttemplate='%{y:.2f}',
                                textposition='outside')
        st.plotly_chart(fig_usage, use_container_width=True, height=450)

        # Cost Savings by Income Level
        st.subheader("Cost Savings by Income Level")
        st.write("This chart illustrates the average monthly cost savings (in USD) for households based on their income level.")

        # Create animated bar chart for Cost Savings by Income Level
        avg_savings = data.groupby(['Year', 'Income_Level'])['Cost_Savings_USD'].mean().reset_index()
        fig_savings = px.bar(avg_savings, 
                              x='Income_Level', 
                              y='Cost_Savings_USD',
                              animation_frame='Year',
                              range_y=[0, avg_savings['Cost_Savings_USD'].max() * 1.1],
                              title='Average Cost Savings by Income Level Over Years',
                              labels={'Cost_Savings_USD': 'Average Cost Savings (USD)'}
                          )
        fig_savings.update_layout(
            margin=dict(l=20, r=20, t=40, b=20), 
            transition_duration=1500, 
            yaxis_title='Average Cost Savings (USD)',
            xaxis_title='Income Level',
            coloraxis_showscale=False
        )
        fig_savings.update_traces(marker_color='rgb(123,204,196)',
                                  marker_line_color='rgb(44,127,184)',
                                  marker_line_width=1.5, 
                                  texttemplate='%{y:.2f}',
                                  textposition='outside')
        st.plotly_chart(fig_savings, use_container_width=True, height=450)

        # Adoption Year Distribution
        st.subheader("Adoption Year Distribution")
        st.write("This chart displays the number of households that adopted renewable energy each year.")

        # Create a DataFrame for adoption counts
        adoption_years = data['Adoption_Year'].value_counts().reset_index()
        adoption_years.columns = ['Year', 'Count']

        # Create a cumulative count for the years
        adoption_years = adoption_years.sort_values('Year')
        adoption_years['Cumulative_Count'] = adoption_years['Count'].cumsum()

        # Prepare data for animation showing years up to the animated year
        all_years = sorted(adoption_years['Year'].unique())
        expanded_data = []

        for year in all_years:
            temp_data = adoption_years[adoption_years['Year'] <= year].copy()
            temp_data['Animation_Year'] = year
            expanded_data.append(temp_data)

        expanded_adoption_data = pd.concat(expanded_data)
        expanded_adoption_data['Year'] = expanded_adoption_data['Year'].astype(int)
        expanded_adoption_data['Animation_Year'] = expanded_adoption_data['Animation_Year'].astype(int)

        # Create the animated bar chart
        fig_adoption = px.bar(expanded_adoption_data, 
                               x='Year', 
                               y='Cumulative_Count',
                               animation_frame='Animation_Year',
                               title='Number of Households Adopting Renewable Energy by Year',
                               labels={'Cumulative_Count': 'Cumulative Number of Households'},
                               range_y=[0, expanded_adoption_data['Cumulative_Count'].max() * 1.1]
                           )

        fig_adoption.update_traces(
            texttemplate='%{y}', 
            textposition='outside',
            marker_color='rgb(190,174,212)',
            marker_line_color='rgb(128,0,128)',
            marker_line_width=1.5
        )
        fig_adoption.update_layout(
            yaxis_title='Cumulative Number of Households', 
            xaxis_title='Year',
            margin=dict(l=20, r=20, t=40, b=20), 
            transition_duration=1500
        )
        st.plotly_chart(fig_adoption, use_container_width=True, height=450)

    # Map with Filter Tab
    with tab3:
        st.subheader("Map with Filter")

        # Filters
        st.subheader("Filters")

        # Filter by Year
        years = data['Year'].unique()
        selected_year = st.selectbox("Select Year", years)

        # Filter by Variable
        variables = ['Monthly_Usage_kWh', 'Cost_Savings_USD', 'Household_Size', 'Income_Level', 'Urban_Rural'] 
        selected_variable = st.selectbox("Select Variable", variables)

        # Filter the data based on selections
        filtered_data = data[data['Year'] == selected_year]

        # Visualization: Average or Mode by Selected Variable
        if selected_variable in ['Monthly_Usage_kWh', 'Cost_Savings_USD', 'Household_Size']:
            title = f"Average {selected_variable} by Country"
            country_avg = filtered_data.groupby('Country')[selected_variable].mean().reset_index()
        else:
            title = f"Mode of {selected_variable} by Country"
            country_avg = filtered_data.groupby('Country')[selected_variable].agg(lambda x: x.mode()[0]).reset_index()

        # Create an interactive map for the filtered data
        fig_map = px.choropleth(country_avg, 
                                locations='Country', 
                                locationmode='country names',
                                color=selected_variable,
                                title=title,
                                labels={selected_variable: selected_variable.replace('_', ' ').title()}
                                )
        fig_map.update_layout(
            margin=dict(l=20, r=20, t=40, b=20),
            geo=dict(
                showframe=False, 
                showcoastlines=True, 
                projection_type='equirectangular',
                coastlinecolor="Gray",
                showland=True,
                landcolor="LightGray"
            )
        )
        fig_map.update_traces(marker_line_color='white', hovertemplate='%{location}<br>%{z:.2f}')
        st.plotly_chart(fig_map, use_container_width=True)

if __name__ == "__main__":
    main()
