# Importing Libraries
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import os
from shiny import App, render, ui
from shinywidgets import output_widget, render_widget
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# Importing cleaned data
baseDir = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(baseDir + "/cleanData.csv")
df["activityDate"] = pd.to_datetime(df["activityDate"], unit = "ns")
df["activityDateText"] = df["activityDate"].dt.strftime("%d %b %Y")

userSummary = pd.read_csv(baseDir + "/userSummary.csv")

# Converting ID to string so it works nicely in dropdowns
df["ID"] = df["ID"].astype(str)
userSummary["ID"] = userSummary["ID"].astype(str)

# Choices for inputs
uniqueUsers = df["ID"].unique()
userChoices = {"All users":"All users"}

for user in uniqueUsers:
    userChoices[user] = user

metricChoices = {"totalSteps":"Total Steps", "totalDistance":"Total Distance", "calories":"Calories", "activeMinutes":"Active Minutes",
                "sedentaryMinutes":"Sedentary Minutes"}

relationshipChoices = {"totalSteps":"Total Steps", "totalDistance":"Total Distance", "veryActiveMinutes":"Very Active Minutes",
                      "fairlyActiveMinutes":"Fairly Active Minutes", "lightlyActiveMinutes":"Lightly Active Minutes",
                      "activeMinutes":"Active Minutes", "sedentaryMinutes":"Sedentary Minutes"}

clusterChoices = {"totalSteps":"Total Steps", "totalDistance":"Total Distance", "veryActiveMinutes":"Very Active Minutes",
                 "lightlyActiveMinutes":"Lightly Active Minutes", "sedentaryMinutes":"Sedentary Minutes", "calories":"Calories"}

# App UI
appUI = ui.page_navbar(

    # Page 1 - landing page
    ui.nav_panel("Landing Page",

    ui.div(
        ui.h1("Fitness Activity Dashboard"),
        ui.h3("Exploring daily activity patterns from fitness tracker data"),
        ui.p(
            "This interactive dashboard allows you to explore daily physical activity, "
            "compare individuals, and investigate how steps, distance, activity intensity, "
            "and sedentary behaviour relate to calories burned."),
        class_ = "hero-section"),

    ui.layout_columns(
        ui.card(
            ui.h3("Project Aim"),
            ui.p(
                "The aim of this dashboard is to help you understand "
                "patterns in fitness data through visualisations."),
            ui.p(
                "The app focuses on activity trends, calorie relationships, and user-level "
                "differences in behaviour.")),

        ui.card(
            ui.h3("Target Audience"),
            ui.p(
                "This dashboard is designed for users interested in fitness, health behaviour, "
                "and data-driven activity tracking."),
            ui.p(
                "It does not require technical knowledge and is intended to be easy to explore.")),

        col_widths = (6, 6)),

    ui.layout_columns(
        ui.card(
            ui.h3("What Can You Explore?"),
            ui.tags.ul(
                ui.tags.li("Overall activity levels across the dataset"),
                ui.tags.li("Daily and weekly activity trends"),
                ui.tags.li("Relationships between steps, distance, active minutes, and calories"),
                ui.tags.li("Differences between individual users"),
                ui.tags.li("User groups created using K-means clustering"))),

        ui.card(
            ui.h3("Dataset Summary"),
            ui.tags.ul(
                ui.tags.li("Daily activity records from wearable fitness trackers"),
                ui.tags.li("Includes steps, distance, activity minutes, sedentary minutes, and calories"),
                ui.tags.li("Covers multiple anonymised users"),
                ui.tags.li("Cleaned by combining CSV files, removing duplicates, and creating new features"))),

        col_widths = (6, 6)),

    ui.card(
        ui.h3("How to Use the Dashboard"),
        ui.layout_columns(
            ui.div(
                ui.h4("1. Start with Overview"),
                ui.p("View headline statistics and overall activity patterns."),
                class_ = "step-box"),
            ui.div(
                ui.h4("2. Explore Trends"),
                ui.p("Filter by user, date range, and activity metric."),
                class_ = "step-box"),
            ui.div(
                ui.h4("3. Analyse Calories"),
                ui.p("Investigate which activity variables relate most strongly to calories."),
                class_ = "step-box"),
            ui.div(
                ui.h4("4. Compare Users"),
                ui.p("Use clustering to identify broad user activity profiles."),
                class_ = "step-box"),
            col_widths = (3, 3, 3, 3))),

    ui.div(
        ui.h4("Important Data Note"),
        ui.p(
            "Some records contain zero steps or zero distance. These values were kept because "
            "they may represent inactive days, rest days, or missing tracking periods. Derived "
            "metrics such as calories per step were only calculated where division was valid."),
        ui.p(
            "The data is anonymised and does not include demographic information. "
            "Therefore, the dashboard focuses on recorded activity patterns rather "
            "than making fitness claims about individuals."),
        class_ = "page-note")),

    # Page 2 - overview
    ui.nav_panel("Overview",
        ui.h1("Overview of the Dataset"),
        ui.div(
            ui.p(
                "Overall, users averaged ~7200 steps and ~2200 calories a day. "
                "Sedentary minutes make up the largest part of the recorded day."),
            class_ = "page-note"),


        ui.layout_columns(
            ui.card(
                ui.h4("Number of users"),
                ui.div(ui.output_text("totalUsers"), class_ = "value-text")),
            ui.card(
                ui.h4("Number of daily records"),
                ui.div(ui.output_text("totalRecords"), class_ = "value-text")),
            ui.card(
                ui.h4("Average daily steps"),
                ui.div(ui.output_text("averageSteps"), class_ = "value-text")),
            ui.card(
                ui.h4("Average daily calories"),
                ui.div(ui.output_text("averageCalories"), class_ = "value-text"))),

        ui.layout_columns(
            ui.card(
                ui.h3("Average Daily Steps Over Time"),
                output_widget("dailyStepsPlot")),
            ui.card(
                ui.h3("Average Daily Minutes by Activity Type"),
                output_widget("activityMinutesPlot")),
            col_widths = (6, 6))),

    # Page 3 - activity trends
    ui.nav_panel("Activity Trends",
        ui.h1("Activity Trends"),
        ui.div(
            ui.p(
                "Saturday had the highest average steps (weekend, more free time for exercise), " 
                "whilst Sunday had the lowest (generally considered a 'rest day')."),
            class_ = "page-note"),

        ui.layout_sidebar(
            ui.sidebar(
                ui.input_selectize(
                    "user_select",
                    "Select user:",
                    choices = userChoices,
                    selected = "All users"),

                ui.input_date_range(
                    "date_select",
                    "Select date range:",
                    start = df["activityDate"].min().date(),
                    end = df["activityDate"].max().date()),

                ui.input_selectize(
                    "metric_select",
                    "Select metric:",
                    choices = metricChoices,
                    selected = "totalSteps")),

            ui.card(
                ui.h3("Selected Metric Over Time"),
                output_widget("metricTimePlot")),

            ui.card(
                ui.h3("Average Steps by Weekday"),
                output_widget("weekdayStepsPlot")))),

    # Page 4 - calories & relationships
    ui.nav_panel("Calories & Relationships",
        ui.h1("Calories & Relationships"),
        ui.div(
            ui.p(
                "Calories are most strongly related to total distance, total steps, and very active minutes. "
                "Sedentary minutes show very little relationship with calories."),
            class_ = "page-note"),

        ui.layout_sidebar(
            ui.sidebar(
                ui.input_selectize(
                    "x_select",
                    "Select x-axis variable:",
                    choices = relationshipChoices,
                    selected = "totalDistance"),

                ui.input_checkbox(
                    "trendline_select",
                    "Show trendline",
                    value = True)),

            ui.card(
                ui.h3("Relationship with Calories"),
                output_widget("calorieScatterPlot")),

            ui.card(
                ui.h3("Correlation Heatmap"),
                ui.output_plot("correlationPlot")))),

    # Page 4 - user comparison/clustering
    ui.nav_panel("User Comparison/Clustering",
        ui.h1("User Comparison and Clustering"),
        ui.div(
            ui.p(
                "The clusters suggest three general user types: lower activity users, moderate "
                "activity users, and high activity or high calorie users."),
            class_ = "page-note"),

        ui.layout_sidebar(
            ui.sidebar(
                ui.input_slider(
                    "cluster_number",
                    "Number of clusters:",
                    min = 2,
                    max = 5,
                    value = 3),

                ui.input_checkbox_group(
                    "cluster_features",
                    "Select features for clustering:",
                    choices = clusterChoices,
                    selected = [
                        "totalSteps",
                        "totalDistance",
                        "veryActiveMinutes",
                        "lightlyActiveMinutes",
                        "sedentaryMinutes",
                        "calories"])),

            ui.card(
                ui.h3("User Clusters"),
                output_widget("clusterPlot")),

            ui.card(
                ui.h3("Cluster Averages"),
                output_widget("clusterAveragePlot")),

            ui.card(
                ui.h3("User Summary Table"),
                ui.output_data_frame("userSummaryTable")))),

    title = "Fitness Activity Dashboard",
    header = ui.include_css(baseDir + "/styles.css"))

# Server
def server(input, output, session):

    # Page 2 - overview
    @output
    @render.text
    def totalUsers():
        return str(df["ID"].nunique())

    @output
    @render.text
    def totalRecords():
        return str(len(df))

    @output
    @render.text
    def averageSteps():
        return int(round(df["totalSteps"].mean(), 0))

    @output
    @render.text
    def averageCalories():
        return int(round(df["calories"].mean(), 0))

    @output
    @render_widget
    def dailyStepsPlot():
        dailySteps = df.groupby("activityDate")["totalSteps"].mean().reset_index()

        dailySteps["activityDate"] = pd.to_datetime(dailySteps["activityDate"])
        dailySteps = dailySteps.sort_values("activityDate")
        dailySteps["activityDateText"] = dailySteps["activityDate"].dt.strftime("%d %b %Y")

        fig = px.line(dailySteps, x = "activityDateText", y = "totalSteps", title = "Average Daily Steps Over Time", labels = {
                     "activityDateText":"Date", "totalSteps":"Average Steps"})
        fig.update_xaxes(tickmode = "array", tickvals = dailySteps["activityDateText"][::7], tickangle = -45)

        return fig

    @output
    @render_widget
    def activityMinutesPlot():
        activityMinutes = df[["veryActiveMinutes", "fairlyActiveMinutes", "lightlyActiveMinutes", "sedentaryMinutes"]].mean().reset_index()

        activityMinutes.columns = ["activityType", "averageMinutes"]

        fig = px.bar(activityMinutes, x = "activityType", y = "averageMinutes", title = "Average Daily Minutes by Activity Type",
                    labels = {"activityType":"Activity Type", "averageMinutes":"Average Minutes"})

        return fig

    # Page 3 - activity trends
    @output
    @render_widget
    def metricTimePlot():

        selectedUser = input.user_select()
        selectedMetric = input.metric_select()
        startDate, endDate = input.date_select()

        filteredDF = df[(df["activityDate"] >= pd.to_datetime(startDate)) & (df["activityDate"] <= pd.to_datetime(endDate))]

        if selectedUser != "All users":
            filteredDF = filteredDF[filteredDF["ID"] == selectedUser]

        if selectedUser == "All users":
            plotDF = filteredDF.groupby("activityDate")[selectedMetric].mean().reset_index()
            yLabel = "Average " + metricChoices[selectedMetric]
        else:
            plotDF = filteredDF[["activityDate", selectedMetric]]
            yLabel = metricChoices[selectedMetric]

        plotDF["activityDate"] = pd.to_datetime(plotDF["activityDate"])
        plotDF = plotDF.sort_values("activityDate")
        plotDF["activityDateText"] = plotDF["activityDate"].dt.strftime("%d %b %Y")

        fig = px.line(plotDF, x = "activityDateText", y = selectedMetric,
            title = metricChoices[selectedMetric] + " Over Time", labels = {"activityDateText":"Date", selectedMetric:yLabel})

        fig.update_xaxes(tickmode = "array", tickvals = plotDF["activityDateText"][::7], tickangle = -45)

        return fig

    @output
    @render_widget
    def weekdayStepsPlot():

        weekdaySteps = df.groupby("weekday")["totalSteps"].mean().reset_index()

        weekdayOrder = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        weekdaySteps["weekday"] = pd.Categorical(weekdaySteps["weekday"], categories = weekdayOrder, ordered = True)

        weekdaySteps = weekdaySteps.sort_values("weekday")

        fig = px.bar(weekdaySteps, x = "weekday", y = "totalSteps", title = "Average Steps by Weekday", labels = {
                    "weekday":"Weekday", "totalSteps":"Average Steps"})

        return fig
    
    # Page 4 - calories & relationships
    @output
    @render_widget
    def calorieScatterPlot():

        xVariable = input.x_select()

        if input.trendline_select():
            fig = px.scatter(df, x = xVariable, y = "calories", color = "stepCategory", trendline = "ols",
                            title = "Calories Burned vs " + relationshipChoices[xVariable], labels = {xVariable:relationshipChoices[xVariable],
                            "calories":"Calories", "stepCategory":"Step Category"})
        else:
            fig = px.scatter(df, x = xVariable, y = "calories", color = "stepCategory",
                            title = "Calories Burned vs " + relationshipChoices[xVariable], labels = {xVariable:relationshipChoices[xVariable],
                            "calories":"Calories", "stepCategory":"Step Category"})

        return fig

    @output
    @render.plot
    def correlationPlot():

        correlationColumns = ["totalSteps", "totalDistance", "veryActiveMinutes", "fairlyActiveMinutes", "lightlyActiveMinutes",
                             "sedentaryMinutes", "activeMinutes", "calories"]

        correlation = df[correlationColumns].corr()

        plt.figure(figsize = (10, 7))
        sns.heatmap(correlation, annot = True, cmap = "coolwarm", fmt = ".2f")
        plt.title("Correlation Heatmap of Activity Variables")

    # Page 5 - user comparison/clustering
    def makeClusteredData():

        selectedFeatures = list(input.cluster_features())

        if len(selectedFeatures) < 2:
            selectedFeatures = ["totalSteps", "calories"]

        X = userSummary[selectedFeatures]

        scaler = StandardScaler()
        XScaled = scaler.fit_transform(X)

        kMeans = KMeans(n_clusters=input.cluster_number(), random_state = 42, n_init = 10)

        clusteredData = userSummary.copy()
        clusteredData["cluster"] = kMeans.fit_predict(XScaled)
        clusteredData["cluster"] = clusteredData["cluster"].astype(str)

        return clusteredData

    @output
    @render_widget
    def clusterPlot():

        clusteredData = makeClusteredData()

        fig = px.scatter(clusteredData, x = "totalSteps", y = "calories", color = "cluster", hover_data = ["ID"],
                        title = "User Clusters Based on Activity Behaviour", labels = {"totalSteps":"Average Daily Steps",
                        "calories":"Average Daily Calories", "cluster":"Cluster"})

        return fig

    @output
    @render_widget
    def clusterAveragePlot():

        clusteredData = makeClusteredData()

        clusterAverage = clusteredData.groupby("cluster")[["totalSteps", "totalDistance", "veryActiveMinutes", "lightlyActiveMinutes",
                                                         "sedentaryMinutes", "calories"]].mean().reset_index()

        clusterAverageLong = clusterAverage.melt(id_vars = "cluster", var_name = "variable", value_name = "averageValue")

        fig = px.bar(clusterAverageLong, x = "cluster", y = "averageValue", color = "variable", barmode = "group",
                    title = "Average Values by Cluster", labels = {"cluster":"Cluster", "averageValue":"Average Value",
                    "variable":"Variable"})

        return fig

    @output
    @render.data_frame
    def userSummaryTable():

        clusteredData = makeClusteredData()

        tableData = clusteredData.copy()

        # Round float columns to 2 decimal places
        floatColumns = tableData.select_dtypes(include = "float").columns

        for col in floatColumns:
            tableData[col] = tableData[col].round(2)

        # Convert integer columns to int
        intColumns = tableData.select_dtypes(include = "integer").columns

        for col in intColumns:
            tableData[col] = tableData[col].astype(int)

        return render.DataGrid(tableData, filters = True)

app = App(appUI, server)