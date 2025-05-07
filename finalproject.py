'''
Name: Gaby Cahill
Class and Section: CS 230-5
Data: Volcanoes
URL: PUT IN STREAMLIT LINK

Description: This program gives users initial knowledge about volcanoes including
their types, eruption history and patterns, locations, elevations, and more.
This website includes several interactive charts/graphs and maps, as well as
images that show the diversity of volcanoes. This application aims to be user-friendly
in order for them to guide their own experience in the website.
'''

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk

#read in data
#[PY1] - function with default parameter, load the volcano dataset
def read_data():
    #[DA1] clean the data - removed the header row as it was unnecessary to the data, two headers originally
    df = pd.read_csv("volcanoes(in).csv", skiprows=1, encoding='latin1') #this was the encoding for my particular csv
    return df.set_index("Volcano Number") #set "Volcano Number" as the index

def home_page():
    #home page with welcome message and volcano images to preview the data
    st.title("Volcanoes Around the World")
    st.write("Explore this website to learn more about volcanic regions, volcano types, and eruption history!")
    st.title("Learn More About Volcanoes")
    st.write("Welcome to the Volcanoes Around the World website! "
             "Volcanoes are geological formations of ash, molten rock, and "
             "gases that erupt from Earth's core. Volcanoes result from the eruption of"
             " magma which can occur when tectonic plates converge or diverge. "
             "This website will provide data about volcanoes including their volcanic activity, locations, "
             "elevations, and types.")
    st.subheader("Diversity of Volcanoes")
    #displaying volcano images with captions of what volcano it is
    st.image("cota.jpg", caption = "Cotopaxi Volcano", use_container_width=True)
    #write a sentence about the significance of the specific volcano
    st.write(f"The Cotopaxi Volcano is the most active volcano in Ecuador with an elevation of 5,897 m (19,347 ft).")

    st.image("maunaloa.jpg", caption = "Mauna Loa Volcano" , use_container_width=True)
    st.write("Covering half of the Island of Hawai'i, Mauna Loa volcano is the largest active volcano on Earth.")

    st.image("ves.jpg", caption = "Mount Vesuvius", use_container_width=True)
    st.write("Mount Vesuvius is located in Campania, Italy and when it erupted in 79 CE destroyed Pompeii.")

#volcano data page - showing basic metrics, filtering, iterrows, and pivot table
def volcano_data():
    df = read_data() #load in volcano dataset

    st.subheader("Basic Introduction of Volcanoes")

    num_vols = df.shape[0] #count number of volcanoes (rows)
    st.write(f"The total number of volcanoes in the dataset: {num_vols}")

    avg_elevation = df["Elevation (m)"].mean() #calculate the average elevation
    st.write(f"Average elevation of volcanoes: {avg_elevation:.2f} meters")

    # [DA2] - sort data - sorted by elevation
    sorted_df = df.sort_values(by="Elevation (m)", ascending=False) #sort by tallest height
    # [DA3] - top largest values in a column - top 5 tallest volcanoes
    st.write("Top 5 Tallest Volcanoes")
    st.dataframe(sorted_df[["Volcano Name", "Elevation (m)"]].head(5))

    st.subheader("Volcanoes Over 3000m in Japan or Indonesia")

    #[DA5] - filter with two conditions
    df_filtered = df[((df["Country"] == "Japan") | (df["Country"] == "Indonesia")) & (df["Elevation (m)"]> 3000)]
    #filter Japan and Indonesia volcanoes over 3000m
    st.write("Table of high-elevation volcanoes in either Japan or Indonesia")
    st.dataframe(df_filtered[["Volcano Name", "Country", "Elevation (m)"]]) #show filtered results

    # [DA8] - use iterrows()
    st.subheader("Here is a Preview of Volcano Names and Their Corresponding Countries:")
    st.write("5 volcanoes printed using '.iterrows()' to loop through the dataframe:")
    rows = [] #create empty list to hold row data
    for index, row in df.head(5).iterrows(): #loop through first 5 rows
        rows.append({
            "Volcano Name": row["Volcano Name"],
            "Country": row["Country"],
            "Elevation (m)": row["Elevation (m)"]
        }) #append selected columns to list
        preview_df = pd.DataFrame(rows) #convert to dataframe
        st.dataframe(preview_df)

    #[PY4] - list comprehension - extract names of volcanoes over 3000m
    high_df = df[df["Elevation (m)"] > 3000] #filter high volcanoes
    high_names = [name for name in high_df["Volcano Name"]] #list comprehension for names
    st.subheader("Volcanoes Over 3000 Meters")
    st.write("Volcanoes over 3000 meters in the dataset:")
    for name in high_names[:5]:
        st.write(f"- {name}") #make it a bullet point

    #[PY2] - pivot table - showing count of volcano types by tectonic setting
    st.subheader("Pivot Table: Volcano Count by Tectonic Setting Volcano Type")

    df_clean = df.dropna(subset=["Tectonic Setting", "Primary Volcano Type"])
    #remove rows with missing tectonic setting or volcano types
    pivot_table = df_clean.pivot_table(
        index="Tectonic Setting",
        columns="Primary Volcano Type",
        values="Volcano Name",
        aggfunc="count",
        fill_value=0
    ) #create pivot table counts

    st.dataframe(pivot_table)

#volcano map visualizations - eruption, elevation, rock type
def volcano_data_map():
    df = read_data()
    df = df.dropna(subset=["Latitude", "Longitude"]) #drop rows with missing coordinates

    #show only volcanoes from top 5 countries
    top_countries = df["Country"].value_counts().head(5).index.tolist()
    top_country_df = df[df["Country"].isin(top_countries)]

    #[ST1] - drop-down menu/selectbox for map type
    selected_map = st.selectbox("Choose a map type:", ["Eruption Map", "Elevation Map", "Rock Type Map"])
    zoom_level = 2

    if selected_map == "Elevation Map":
        st.title("Volcano Custom Icon Map of Elevation")

        ICON_URL = "https://upload.wikimedia.org/wikipedia/commons/4/4f/Gunung_Berapi_Erupsi.svg"  # Optional: Replace with any icon you like

        icon_data = {
            "url": ICON_URL,
            "width": 50,
            "height": 50,
            "anchorY": 1
        }

        top_country_df["icon_data"] = None
        for i in top_country_df.index:
            top_country_df.at[i, "icon_data"] = icon_data #assign icon to each row

        icon_layer = pdk.Layer(
            type="IconLayer",
            data=top_country_df,
            get_icon="icon_data",
            get_position='[Longitude, Latitude]',
            get_size=4,
            size_scale=10,
            pickable=True
        ) #define icon layer with position and appearance

        view_state = pdk.ViewState(
            latitude=top_country_df["Latitude"].mean(),
            longitude=top_country_df["Longitude"].mean(),
            zoom=zoom_level,
            pitch=0
        ) #center map on the average location

        tool_tip1 = {
            "html": "<b>{Volcano Name}</b><br/>Country: {Country}<br/> Volcanic Province: {Volcanic Province}<br/> Elevation: {Elevation (m)} m",
            "style": {"backgroundColor": "darkred", "color": "white"}
        } #define what is displayed in the box and its appearance

        volcano_map = pdk.Deck(
            map_style='mapbox://styles/mapbox/navigation-day-v1',
            layers=[icon_layer],
            initial_view_state=view_state,
            tooltip=tool_tip1
        ) #create pydeck map

        st.pydeck_chart(volcano_map) #[MAP1]

    elif selected_map == "Eruption Map":
        #all comments above apply to this map's structure too
        st.title("Volcano Scatterplot Map of Eruption Information")

        view_state = pdk.ViewState(
            latitude=top_country_df["Latitude"].mean(),
            longitude=top_country_df["Longitude"].mean(),
            zoom=zoom_level,
            pitch=0
        )

        layer1 = pdk.Layer(
            type='ScatterplotLayer',
            data=top_country_df,
            get_position='[Longitude, Latitude]',
            get_radius=30000,
            get_color=[255, 100, 0],
            pickable=True
        )
        #layer 1 and 2 use different colors/sizes for map points
        layer2 = pdk.Layer(
            'ScatterplotLayer',
            data=top_country_df,
            get_position='[Longitude, Latitude]',
            get_radius=10000,
            get_color=[0, 0, 255],
            pickable=True
        )

        tool_tip2 = {
            "html": "<b>{Volcano Name}</b><br/>Country: {Country}<br/>Activity Evidence: {Activity Evidence} <br/> Last Known Eruption: {Last Known Eruption}",
            "style": {"backgroundColor": "black", "color": "white"}
        }

        volcano_map = pdk.Deck(
            map_style='mapbox://styles/mapbox/streets-v12',
            initial_view_state=view_state,
            layers=[layer1, layer2],
            tooltip=tool_tip2
        )

        st.pydeck_chart(volcano_map) #[MAP2]

    elif selected_map == "Rock Type Map":
        st.title("Volcano Map of Dominant Rock Type")
        df = df.dropna(subset=["Latitude", "Longitude", "Dominant Rock Type"]) #remove missing lat/long or rock type

        unique_rocks = sorted(df["Dominant Rock Type"].dropna().unique()) #get unique rock types and sort
        selected_rocks = st.multiselect("Select a dominant rock type:", unique_rocks, default=unique_rocks[:1]) #user selects rock type

        if not selected_rocks:
            st.info("Please select at least one dominant rock type to display the map") #displays message when nothing is selected

        filtered_df = df[df["Dominant Rock Type"].isin(selected_rocks)] #filtered base on user selection
        st.write(f"Displaying {len(filtered_df)} volcanoes with rock type: {','.join(selected_rocks)}")

        #defining custom colors for the rock types - all color combos found online
        rock_colors= {
            "Foidite": [255,0,0],
            "Basalt / Picro-Basalt": [0,128,0],
            "Trachybasalt / Tephrite Basanite": [0,0,255],
            "Trachyte / Trachydacite": [255,165,0],
            "Phono-tephrite / Tephri-phonolite": [128,0,128],
            "Phonolite": [0,255,255],
            "Trachyandesite / Basaltic Trachyandesite": [255,192,203],
            "Andesite / Basaltic Andesite": [255,255,0],
            "Rhyolite": [139,69,19],
            "Dacite": [105,105,105]
        }
        #assign color to each volcano based on rock type
        colors = [] #empty list to hold assigned colors
        for rt in filtered_df["Dominant Rock Type"]: #loop through types
            if rt in rock_colors:
                colors.append(rock_colors[rt]) #add matching color
            else:
                colors.append([100,100,100]) #gray color
        filtered_df["color"] = colors #add color column to dataframe

        rock_layer = pdk.Layer(
            type='ScatterplotLayer',
            data=filtered_df,
            get_position='[Longitude, Latitude]',
            get_radius=40000,
            get_fill_color="color",
            pickable=True
        ) #create scatter layer for rock types

        view_state = pdk.ViewState(
            latitude=filtered_df["Latitude"].mean(),
            longitude=filtered_df["Longitude"].mean(),
            zoom =2
        ) #center the map

        tool_tip3 = {
            "html": "<b>{Volcano Name}</b><br/>Country: {Country}<br/>Rock Type: {Dominant Rock Type}",
            "style": {"backgroundColor": "navy", "color": "gold"}
        }

        rock_map = pdk.Deck(
            map_style='mapbox://styles/mapbox/light-v10',
            layers=[rock_layer],
            initial_view_state=view_state,
            tooltip = tool_tip3
        )

        st.pydeck_chart(rock_map) #[MAP3]

#volcano charts - will find a bar chart, pie chart, and line chart
def volcano_charts():
    df = read_data()
    st.title("Top 5 Countries by Number of Volcanoes")
    countries = df["Country"].value_counts().head(5) #get top 5 countries

    st.subheader("Bar Chart of Volcano Counts by Country")

    fig1, ax1 = plt.subplots()
    ax1.bar(countries.index, countries.values, color = "orange")
    ax1.set_xlabel("Country")
    ax1.set_ylabel("Number of Volcanoes")
    ax1.set_title("Top 5 Countries with the Most Volcanoes")

    st.pyplot(fig1) #[VIZ1] - bar chart

    st.title("Volcano Landform Types by Province")

    df= df.dropna(subset=["Volcano Landform", "Volcanic Province"]) #drops nulls
    provinces = df["Volcanic Province"].dropna().unique() #user selects province
    select_prov = st.selectbox("Select a Volcanic Province:", sorted(provinces))

    filtered_df = df[df["Volcanic Province"] == select_prov] #filter based on province
    landform_count = filtered_df["Volcano Landform"].value_counts().sort_index() #counts landforms

    labels = landform_count.index
    sizes = landform_count.values

    st.subheader(f"Volcano Landform Distribution in {select_prov}")
    fig2,ax2 = plt.subplots()

    wedges, text, autotexts = ax2.pie(
        sizes,
        labels = None,
        autopct='%1.1f%%', #display percent sign
        startangle=90,
        colors=plt.cm.Paired.colors #color scheme found online
    )
    ax2.set_title(f"Composition of Volcano Types in the {select_prov}")
    ax2.legend(wedges, labels, title="Landform Types", loc="center left", bbox_to_anchor=(1,0,0.5,1))
    st.pyplot(fig2) #[VIZ2] - pie chart

    st.subheader("Average Volcano Elevation by Country")
    countries = sorted(df["Country"].dropna().unique())
    selected_countries = st.multiselect("Selected Countries:", countries, default= countries[:10]) #select countries, display first 10

    if selected_countries:
        filtered_df = df[df["Country"].isin(selected_countries)]
        avg_elevation_by_country = filtered_df.groupby("Country")["Elevation (m)"].mean().sort_values(ascending=True) #compute means

        fig3,ax3 = plt.subplots()
        ax3.plot(avg_elevation_by_country.index, avg_elevation_by_country.values, marker = "o", linestyle= "-", color = "green")
        ax3.set_xlabel("Country")
        ax3.set_ylabel("Average Elevation (m)")
        ax3.set_title("Average Elevation by Selected Country")
        ax3.tick_params(axis = 'x', rotation=45)

        st.pyplot(fig3) #[VIZ3] - line chart
    else:
        st.info("Please select at least one country to display the chart")

#run the app and display all different pages in the navigation sidebar
def main():

    st.sidebar.title("Navigation Window")
    page = st.sidebar.radio("Choose a page:", ["Home", "Volcano Data", "Volcano Maps", "Volcano Charts"])
    #show pages available for selection
    if page == "Home":
        home_page()
    elif page == "Volcano Data":
        volcano_data()
    elif page == "Volcano Maps":
        volcano_data_map()
    elif page == "Volcano Charts":
        volcano_charts()
main()
