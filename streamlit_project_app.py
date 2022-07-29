def main():
        conn = sf.connect(
                account='sba23770',
                user='TDEWING19',
                password='Federals_20',
                database='ECONOMY_DATA_ATLAS',
                schema='ECONOMY',
                warehouse='COMPUTE_WH')

        # Inflation
        inflation_query = '''SELECT \"Date\", \"ECONOMY\".\"BEANIPA\".\"Value\" as \"infVal\" FROM \"ECONOMY\".\"BEANIPA\" WHERE \"Table Name\" = \'Price Indexes For Personal Consumption Expenditures By Major Type Of Product\'        AND \"Indicator Name\" = \'Personal consumption expenditures (PCE)\' AND \"Frequency\" = \'A\' ORDER BY \"Date\"'''
        inflation_df = pd.read_sql_query(inflation_query, conn)

        gdp_query = '''SELECT \"Date\", \"ECONOMY\".\"BEANIPA\".\"Value\" as \"gdpVal\" FROM \"ECONOMY\".\"BEANIPA\" WHERE \"Table Name\" = \'Percent Change From Preceding Period In Real Gross Domestic Product\' AND \"Indicator Name\" = \'Gross domestic product (GDP)\' AND \"Frequency\" = \'Q\' ORDER BY \"Date\"'''
        gdp_df = pd.read_sql_query(gdp_query, conn)

        # Exchange Rate
        ex_query = '''SELECT \"Date\", \"ECONOMY\".\"EXRATESCC2018\".\"Value\" as \"exVal\" FROM \"ECONOMY\".\"EXRATESCC2018\" WHERE \"Currency\" = \'EUR/USD\' AND \"Indicator Name\" = \'Close\' AND \"Frequency\" = \'D\' AND \"Date\" > \'2000-01-01\' ORDER BY \"Date\"'''
        ex_df = pd.read_sql_query(ex_query, conn)

        # Unemployment Rates
        unemployment_query = '''SELECT \"Date\", \"ECONOMY\".\"BLSUSLFSCPS2019\".\"Value\" as \"unemVal\" FROM \"ECONOMY\".\"BLSUSLFSCPS2019\" WHERE \"Series Name\"= \'Unemployment Rate - (Seas)\' AND \"Frequency\" = \'M\' ORDER BY \"Date\"'''
        unemployment_df = pd.read_sql_query(unemployment_query, conn)

        #Join
        result_df = ex_df.join(inflation_df.set_index('Date'), on='Date').join(gdp_df.set_index('Date'), on='Date').join(unemployment_df.set_index('Date'), on='Date').dropna()
        result_df.to_csv("result_df.csv")

        #Model Building
        reg = linear_model.LinearRegression()
        reg.fit(result_df[['infVal', 'gdpVal', 'unemVal']], result_df.exVal)

        #Streamlit
        st.title("US GB Exhange Rate Prediction")
        st.write("""### We need some info to make the prediction""")
        inflation = st.number_input(label="Inflation Rate", step = 1., format = "%.2f")
        gdp = st.number_input(label="GDP", step=1., format="%.2f")
        unemployment = st.number_input(label="Unemployment Rate", step=1., format="%.2f")
        calculate = st.button("Calculate Exchange Rate")
        if calculate:
                exchange = reg.predict([[inflation, gdp, unemployment]])
                st.subheader(f"The estimated exchange rate is {exchange[0]}")
                st.write("""### Mean Exchange Rate Based on Inflation Rate""")
                line_graph = result_df.groupby(["infVal"])["exVal"].mean().sort_values(ascending=True)
                st.line_chart(line_graph)

                st.write("""### Mean Exchange Rate Based on GDP""")
                line_graph = result_df.groupby(["gdpVal"])["exVal"].mean().sort_values(ascending=True)
                st.line_chart(line_graph)

                st.write("""### Mean Exchange Rate Based on Unemployment Rate""")
                line_graph = result_df.groupby(["unemVal"])["exVal"].mean().sort_values(ascending=True)
                st.line_chart(line_graph)

if __name__ == "__main__":
    main()
