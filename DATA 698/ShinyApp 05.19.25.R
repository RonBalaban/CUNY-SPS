library(shiny)
library(dplyr)
library(tidyr)
library(shinyWidgets)
library(openxlsx)
library(later)
library(DT)
library(plotly)
library(ggplot2)
library(patchwork)

# Load data
all_ndc_nadac_awp_package_2013_2022 <- readRDS("all_ndc_nadac_awp_package_2013_2022.rds")

ui <- fluidPage(
  titlePanel("Drug Price and Utilization Trends"),
  sidebarLayout(
    sidebarPanel(
      width = 3,
      selectizeInput("drug", "Select Drug:",
                     choices = sort(unique(all_ndc_nadac_awp_package_2013_2022$Drug_Name)),
                     options = list(placeholder = "Type to search...", create = TRUE)),
      
      sliderInput("year_range", "Select Year Range:",
                  min = min(all_ndc_nadac_awp_package_2013_2022$year),
                  max = max(all_ndc_nadac_awp_package_2013_2022$year),
                  value = c(2013, 2022), sep = ""),
      
      selectInput("plot_type", "Plot Type:", choices = c("Overall", "Faceted")),
      
      checkboxGroupInput("ndc_category", "NDC Category:",
                         choices = sort(unique(all_ndc_nadac_awp_package_2013_2022$ndc_category))),
      
      selectInput("ndc_standard", "Select Standard NDC(s):", choices = NULL, multiple = TRUE),
      selectInput("ndc_11", "Select CMS NDC(s):", choices = NULL, multiple = TRUE),
      pickerInput("metrics", "Select Metrics:",
                  choices = c("average_nadac", "average_awp", "average_wac", "rebate_min", "rebate_avg", "rebate_max"),
                  selected = c("average_nadac", "average_awp", "average_wac", "rebate_min", "rebate_avg", "rebate_max"),
                  multiple = TRUE,
                  options = list(`actions-box` = TRUE)),
      
      downloadButton("download_data", "Download Data"),
      downloadButton("download_plot", "Download Plot"),
      hr(),
      uiOutput("brand_generic_panel"),
      uiOutput("clicked_name_info")
    ),
    mainPanel(
      uiOutput("plot_ui"),
      hr(),
      div(
        style = "height: 300px; overflow-y: auto; margin-top: 200px;",
        DTOutput("filtered_table")
      )
    )
  )
)

server <- function(input, output, session) {
  
  observeEvent(input$drug, {
    valid_drugs <- unique(all_ndc_nadac_awp_package_2013_2022$Drug_Name)
    if (input$drug %in% valid_drugs) {
      filtered <- all_ndc_nadac_awp_package_2013_2022 %>%
        filter(Drug_Name == input$drug)
      updateSelectInput(session, "ndc_standard", choices = sort(unique(filtered$ndc_standard)), selected = NULL)
      updateSelectInput(session, "ndc_11", choices = sort(unique(filtered$ndc_11)), selected = NULL)
    } else {
      updateSelectInput(session, "ndc_standard", choices = NULL)
      updateSelectInput(session, "ndc_11", choices = NULL)
    }
  })
  
  observeEvent(input$ndc_standard, {
    req(input$drug %in% all_ndc_nadac_awp_package_2013_2022$Drug_Name)
    filtered <- all_ndc_nadac_awp_package_2013_2022 %>%
      filter(Drug_Name == input$drug, ndc_standard %in% input$ndc_standard)
    updateSelectInput(session, "ndc_11", choices = sort(unique(filtered$ndc_11)), selected = NULL)
  })
  
  filtered_data <- reactive({
    if (!(input$drug %in% all_ndc_nadac_awp_package_2013_2022$Drug_Name)) return(NULL)
    
    df <- all_ndc_nadac_awp_package_2013_2022 %>%
      filter(Drug_Name == input$drug,
             year >= input$year_range[1],
             year <= input$year_range[2])
    
    if (!is.null(input$ndc_category) && length(input$ndc_category) > 0) {
      df <- df %>% filter(ndc_category %in% input$ndc_category)
    }
    if (!is.null(input$ndc_standard) && length(input$ndc_standard) > 0) {
      df <- df %>% filter(ndc_standard %in% input$ndc_standard)
    }
    if (!is.null(input$ndc_11) && length(input$ndc_11) > 0) {
      df <- df %>% filter(ndc_11 %in% input$ndc_11)
    }
    
    df
  })
  
  output$plot_ui <- renderUI({
    show_util_plot <- input$plot_type == "Overall" &&
      is.null(input$ndc_standard) && is.null(input$ndc_11)
    
    if (show_util_plot) {
      fluidRow(
        column(width = 6, plotlyOutput("nadac_plot")),
        column(width = 6, plotlyOutput("rx_plot"))
      )
    } else {
      fluidRow(column(width = 12, plotlyOutput("nadac_plot")))
    }
  })
  
  output$nadac_plot <- renderPlotly({
    df <- filtered_data()
    
    if (nrow(df) == 0) {
      return(plotly_empty() %>%
               layout(title = list(text = "No data available for selected filters.")))
    }
    
    selected_metrics <- input$metrics
    if (length(selected_metrics) == 0) {
      return(plotly_empty() %>%
               layout(title = list(text = "Please select at least one metric.")))
    }
    
    if (input$plot_type == "Overall") {
      summary_data <- df %>%
        group_by(year) %>%
        summarise(across(all_of(selected_metrics), ~ mean(.x, na.rm = TRUE)), .groups = "drop") %>%
        pivot_longer(-year, names_to = "Metric", values_to = "Value")
      
      p <- ggplot(summary_data, aes(x = year, y = Value, color = Metric)) +
        geom_line(size = 1) +
        geom_point(size = 2) +
        labs(title = paste("Overall Price Trends for", input$drug),
             x = NULL, y = "Price ($)", color = "Metric") +
        scale_y_continuous(labels = scales::label_dollar()) +
        theme_minimal()
      
      ggplotly(p, source = "main_plot")
      
    } else {
      ndc_count <- length(unique(df$ndc_standard))
      if (ndc_count > 25) {
        limited_ndcs <- unique(df$ndc_standard)[1:25]
        df <- df %>% filter(ndc_standard %in% limited_ndcs)
      }
      
      long_data <- df %>%
        pivot_longer(cols = all_of(selected_metrics), names_to = "Metric", values_to = "Value")
      
      unique_standard <- unique(df$ndc_standard)
      unique_cms <- unique(df$ndc_cms)
      
      if (length(unique_standard) == 1 && length(unique_cms) > 1) {
        plots <- long_data %>%
          split(.$ndc_cms) %>%
          lapply(function(subdf) {
            ggplot(subdf, aes(x = year, y = Value, color = Metric)) +
              geom_line(size = 1) +
              geom_point(size = 2) +
              facet_wrap(~ ndc_standard, scales = "free_y") +
              labs(title = paste("CMS NDC:", unique(subdf$ndc_cms)),
                   x = NULL, y = "Price ($)", color = "Metric") +
              scale_y_continuous(labels = scales::label_dollar()) +
              theme_minimal() +
              theme(strip.text = element_text(face = "bold"))
          })
        
        final_plot <- wrap_plots(plots, ncol = 1)
        return(final_plot)
      }
      
      p <- ggplot(long_data, aes(x = year, y = Value, color = Metric)) +
        geom_line(size = 1) +
        geom_point(size = 2) +
        facet_wrap(~ ndc_standard, scales = "free_y") +
        labs(title = paste("Faceted Price Trends for", input$drug),
             x = NULL, y = "Price ($)", color = "Metric") +
        scale_y_continuous(labels = scales::label_dollar()) +
        theme_minimal() +
        theme(strip.text = element_text(face = "bold"))
      
      ggplotly(p, source = "main_plot")
    }
  })
  
  observe({
    df <- filtered_data()
    if (input$plot_type == "Faceted" && length(unique(df$ndc_standard)) > 25) {
      showModal(modalDialog(
        title = "Notice",
        "High number of NDC's detected, please narrow your selection in the side panel.",
        easyClose = TRUE,
        footer = NULL
      ))
    }
  })
  
  output$rx_plot <- renderPlotly({
    if (input$plot_type != "Overall" ||
        !is.null(input$ndc_standard) || length(input$ndc_standard) > 0 ||
        !is.null(input$ndc_11) || length(input$ndc_11) > 0) return(NULL)
    
    df <- filtered_data()
    if (is.null(df) || nrow(df) == 0) return(NULL)
    
    df <- df %>%
      mutate(`Total Prescriptions` = as.numeric(gsub(",", "", `Total Prescriptions`)),
             `Total Patients` = as.numeric(gsub(",", "", `Total Patients`)))
    
    summary_data <- df %>%
      group_by(year) %>%
      summarise(`Total Prescriptions` = sum(`Total Prescriptions`, na.rm = TRUE),
                `Total Patients` = sum(`Total Patients`, na.rm = TRUE),
                .groups = "drop") %>%
      pivot_longer(cols = -year, names_to = "Metric", values_to = "Value")
    
    plot_ly(summary_data, x = ~year, y = ~Value, color = ~Metric, type = 'scatter', mode = 'lines+markers') %>%
      layout(title = paste("Utilization Trends for", input$drug),
             xaxis = list(title = ""),
             yaxis = list(title = ""))
  })
  
  output$filtered_table <- renderDT({
    df <- filtered_data()
    if (is.null(df) || nrow(df) == 0) return(NULL)
    
    df <- df %>% select(-Brand_Names, -Generic_Names, -SAMPLE_PACKAGE)
    cols_to_round <- c("avg_old_nadac", "avg_new_nadac", "average_nadac", 
                       "average_awp", "average_wac", "rebate_min", 
                       "rebate_avg", "rebate_max")
    df_rounded <- df
    for (col in cols_to_round) {
      if (col %in% names(df_rounded)) {
        df_rounded[[col]] <- round(df_rounded[[col]], 2)
      }
    }
    datatable(df_rounded, options = list(pageLength = 5, lengthMenu = c(5, 10, 25, 50, 100)), rownames = FALSE)
  })
  
  output$brand_generic_panel <- renderUI({
    req(input$drug %in% all_ndc_nadac_awp_package_2013_2022$Drug_Name)
    filtered <- all_ndc_nadac_awp_package_2013_2022 %>%
      filter(Drug_Name == input$drug)
    brand_names <- unique(unlist(strsplit(paste(filtered$Brand_Names, collapse = "; "), "; ")))
    generic_names <- unique(unlist(strsplit(paste(filtered$Generic_Names, collapse = "; "), "; ")))
    tagList(
      strong("Brand Names:"), paste(brand_names, collapse = ", "), br(),
      strong("Generic Names:"), paste(generic_names, collapse = ", ")
    )
  })
  
  output$clicked_name_info <- renderUI({
    click_data <- event_data("plotly_click", source = "main_plot")
    if (is.null(click_data)) return(NULL)
    
    x_val <- click_data$x
    df <- filtered_data()
    if (!is.null(df) && nrow(df) > 0 && !is.null(x_val)) {
      drug_names <- unique(df$Drug_Name)
      tagList(
        tags$hr(),
        strong("Drug Name(s) associated with clicked point:"),
        tags$p(paste(drug_names, collapse = ", "))
      )
    } else {
      NULL
    }
  })
}

shinyApp(ui = ui, server = server)
