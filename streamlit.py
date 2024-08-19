import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu
from numerize.numerize import numerize
from io import BytesIO








st.set_page_config(page_title="Sales Dashboard TPF", 
                   page_icon="Logo TPF.png", 
                   layout="wide")

# Membaca dan merapikan DataFrame
perdaerah = pd.read_parquet("perdaerah.parquet")

# Mengonversi kolom DateTime dan mengisi nilai NaN
perdaerah['Posting Date'] = pd.to_datetime(perdaerah['Posting Date'])
perdaerah['Due Date'] = pd.to_datetime(perdaerah['Due Date'])
perdaerah['Payment Date'] = pd.to_datetime(perdaerah['Payment Date'])
perdaerah.fillna({
    'Customer/Vendor Name': 'Unknown',
    'Item No.': 'Unknown',
    'Item/Service Description': 'Unknown',
    'Unit': 'Unknown'
}, inplace=True)

# Konversi kolom yang diperlukan menjadi string
perdaerah['Year'] = perdaerah['Year'].astype(str)
perdaerah['Kategori'] = perdaerah['Kategori'].astype(str)

# Menambahkan kolom Month dan YearMonth
perdaerah['Month'] = perdaerah['Posting Date'].dt.to_period('M')
perdaerah['YearMonth'] = perdaerah['Posting Date'].dt.to_period('M').dt.to_timestamp()

# Filter Type
Type = st.sidebar.selectbox(
    "Berdasarkan:",
    ("Customers", "Items", "Daerah")
)

if Type == "Customers":
    # Filtering by Customer

    selectedyear = st.sidebar.multiselect("Pilih Tahun", perdaerah['Year'].unique(),default=perdaerah['Year'].max())
    selectedcust = st.sidebar.multiselect("Pilih Customers", perdaerah['Customer/Vendor Name'].unique())
    selectedsales = st.sidebar.multiselect("Pilih Sales Name", perdaerah['Sales Employee Name'].unique())
    selectedgroup = st.sidebar.multiselect("Pilih Group", perdaerah['Group Name'].unique())
    filtered_data = pd.DataFrame(perdaerah)
    #filtering
    if selectedyear:
        filtered_data = perdaerah[perdaerah['Year'].isin(selectedyear)]
    if selectedcust:
        filtered_data = filtered_data[filtered_data['Customer/Vendor Name'].isin(selectedcust)]
    if selectedsales:
        filtered_data = filtered_data[filtered_data['Sales Employee Name'].isin(selectedsales)]
    if selectedgroup:
        filtered_data = filtered_data[filtered_data['Group Name'].isin(selectedgroup)]



    #Add more jika ada lagi
    def Home():
        with st.expander("Sales Data"):
            showData = st.multiselect('Filter: ', filtered_data.columns, default=[])
            datatoexport = filtered_data[showData]
            st.dataframe(datatoexport)

            # Menyimpan data ke file Excel
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                datatoexport.to_excel(writer, index=False, sheet_name='Sheet1')
            
            # Menyiapkan file untuk diunduh
            output.seek(0)
            st.download_button(
                label='Export Data to Excel',
                data=output,
                file_name='Sales Data.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
    
    Home()
    total = filtered_data['Row Total'].sum()
    st.metric(label='Total Value', value=(f"Rp {total:,.0f}".replace(',', '.')))
if Type == "Daerah":
    # Filtering by Daerah
    filtered_data = pd.DataFrame(perdaerah)
    selectedyear = st.sidebar.multiselect("Pilih Tahun", perdaerah['Year'].unique(),default=perdaerah['Year'].max())
    selecteddaerah = st.sidebar.multiselect("Pilih Daerah", perdaerah['Daerah'].unique())
    selectedkategori = st.sidebar.multiselect("Pilih Kategori", perdaerah['Kategori'].unique())

    if selectedyear:
        filtered_data = perdaerah[perdaerah['Year'].isin(selectedyear)]
    if selecteddaerah:
        filtered_data = filtered_data[filtered_data['Daerah'].isin(selecteddaerah)]
    if selectedkategori:
        filtered_data = filtered_data[filtered_data['Kategori'].isin(selectedkategori)]

    def Home():
        with st.expander("Sales Data"):
            showData = st.multiselect('Filter: ', filtered_data.columns, default=[])
            datatoexport = filtered_data[showData]
            st.dataframe(datatoexport)

            # Menyimpan data ke file Excel
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                datatoexport.to_excel(writer, index=False, sheet_name='Sheet1')
            
            # Menyiapkan file untuk diunduh
            output.seek(0)
            st.download_button(
                label='Export Data to Excel',
                data=output,
                file_name='Sales Data.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    
    Home()

    col1, col2 = st.columns(2)
    with col1:
        total = filtered_data['Row Total'].sum()

        st.metric(label='Total Revenue', value=(f"Rp {total:,.0f}"))

        data = filtered_data.groupby(['Daerah', 'Kategori', 'Year'])['Row Total'].sum().reset_index()

        stat1 = px.bar(data, x="Daerah", y="Row Total", color="Kategori", title="Total Sales by Kategori", text=data['Row Total'])
        st.plotly_chart(stat1)
    with col2:
        st.metric(label='Best Kategori', value=(filtered_data.groupby('Kategori')['Row Total'].sum().idxmax()))

        data = filtered_data.groupby(['YearMonth','Daerah', 'Year'])['Row Total'].sum().reset_index()

        stat2 = px.line(data, x="YearMonth", y="Row Total", text=(data['YearMonth'].dt.strftime('%b %Y')), title= "Time Series by Daerah")
        st.plotly_chart(stat2)






