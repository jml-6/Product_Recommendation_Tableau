# Product_Recommendation_Tableau
An exhaustive recommendation of three different products for a technology company's next project. The process was as follows:

1) import each product's data from a Hubspot API from sales of the products (requests library)
2) clean the dataframe for only closed deals, find the price/quantity for each (numpy arrays)
3) create price and revenue curves (sklearn.linear_model)
4) calculate the optimal price (revenueOptimizer in the LinearRegression library in sklearn)
5) connect a SQL database with salesperson data (sqlite3 library)
6) find the salesperson with the most sales (groupby)
7) extract product, machine, and parts tables from SQL for the Sankey chart (sqlite3.connect, select, left join)
8) classify the df decision tree for each component (DecisionTreeClassifier)
9) scrape market data for the market mapping (BeautifulSoup)
10) standardize the data/scores (MinMaxScaler)
11) create the principal component analysis grouping (sklearn.decomposition)
12) cluster the data by calculating sum of squared differences (KMeans)
13) export the dataframes to csvs (to_csv)

Next, a base for the dashboard was designed in Figma. This was downloaded into Tableau, where each component piece was placed into the dashboard with its analysis. External research was done on the market sizing and growth. The Sankey chart was created using the following calculations in Tableau:

1) ToPad: Creates points for both our left and right side
    if  [Table Name] = 1 then 1 else 49 end
2) Padded: Creates points between the left and right sides. Create bins from ToPad with bin size as 1
3) t: evenly spaces all marks across the view
    (index()-25)/4
      Put [t] in Columns
      Then put [Padded] in details. Compute [t] using [Padded]
4) Left Side: Determines the starting point of the lines
    RUNNING_SUM(sum([Value]))/Total(sum([Value]))
5) Right Side: Determines the ending points of the lines
    RUNNING_SUM(sum([Value]))/Total(sum([Value]))
6) Sigmoid: Creates a curve function
    1/(1+EXP(1)^-[t])
7) Curve: Draws a curve from the starting points to the ending points
    [Left Side]+(([Right Side]-[Left Side])*[Sigmoid])
      Put [Curve] Rows
      Add [left segment] to details
      Add [right segment] to details
Then: 
8) Edit Table Calculateions
  Nested Calculation: [Left Side]
    Use Specific Dimensions
    Order: [left segment] > [right segment] > [Padded]
  Nested Calculation: [Right Side]
    Use Specific Dimensions
    Order: [right segment] > [left segment] > [Padded]
  Nested Calculation: [t]
    Use Specific Dimensions
    Order: [Padded]
9) Cost Flow: Give the lines size relative to the costs
  WINDOW_AVG(sum([Value]))
    Put [Cost Flow] on sizes
    Compute using [Padded]
    
Each piece of data used an extract, and was published to Tableau Public [here](https://public.tableau.com/views/Linford_StratDash/Faraday_Dashboard?:language=en-US&:display_count=n&:origin=viz_share_link).

Note: this was a guided project authored by Stephen Sorenson. Many thanks for his amazing work. 
