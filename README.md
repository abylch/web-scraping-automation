# web-scraping-automation
python selenium web scraping automation

Web scraping is the automated gathering of content and data from a website or any other resource available on the internet. Unlike screen scraping, web scraping extracts the HTML code under the webpage. Users can then process the HTML code of the webpage to extract data and carry out data cleaning, manipulation, and analysis. Exhaustive amounts of this data can even be stored in a database for large-scale data analysis projects. The prominence and need for data analysis, along with the amount of raw data which can be generated using web scrapers, has led to the development of tailor-made python packages which make web scraping easy as pie.

Web Scraping with Selenium allows you to gather all the required data using Selenium Webdriver Browser Automation. Selenium crawls the target URL webpage and gathers data at scale. This article demonstrates how to do web scraping using Selenium.

# Researcher Information Scraper

# Rutgers University Departments Researcher Information Scraper

## Overview

This Python script is designed for scraping researcher information from various departments at Rutgers University. The script utilizes the Selenium web driver for automated interaction with the websites, fetching details like name, department, institution, title, expertise, publications, and gender probability.

## Setup

1. **Libraries:** The script requires several Python libraries, including `selenium`, `webdriver_manager`, `urllib`, `csv`, `json`, `openpyxl`, `pandas`, `time`, and `re`. Make sure to install them using `pip install [library_name]`.

2. **Web Driver:** The script uses the Chrome web driver. Ensure you have Chrome installed and download the appropriate web driver using `ChromeDriverManager().install()`.

3. **Run the Script:** Execute the script, and it will navigate through the specified department pages, extract researcher details, and save the results to an Excel file.

## Features

- The script provides functionalities such as counting publications, finding names in publications, determining department and rank based on specific keywords, cleaning and counting words in expertise, and fetching gender information from an external API.

- Each department has a dedicated function (`philosophy_res`, `biology_res`, `cs_res`, `psycho_res`, `law_res`) to handle the unique structure of its researcher pages.

- The final output is a consolidated Excel file named "result.xlsx" containing researcher information from all departments.

## Challenges

- The script addresses challenges related to diverse page structures, varying publication formats, and different information layouts on each department's website.

- It handles issues such as loading more people, extracting information from linked pages, and cleaning up expertise and publication text.

## Usage

1. Adjust the URLs for each department as needed.
2. Customize the functions (`department_func`, `rank_func`, `word_counter`, `api_gender`, `links`) for new department websites.
3. Run the script to gather and consolidate researcher information.

Feel free to tailor the script to your specific needs or extend it for additional departments.


## Part 1 – General Functions for All Departments:
- `def pub_count`: A function that counts publications based on the years appearing on the page, specifically counting how many times years between 1960 and 2022 appear. Later, it compares this to two other counters to get the most accurate number of researcher publications since each page is structured differently.
  
- `def name_in_pubs`: Counts the names of researchers in the publications section.

- `def department_func`: A function that checks the department name. If one of the 5 predefined departments is found, it returns one of the requested options (e.g., Law). In Biology, two different names appeared, so both options are included in the function.

- `def rank_func`: A function that checks the rank of a lecturer/researcher, examining words describing the professor's rank and returning the specified value according to the job. For example, if the word "Associate" appears, it returns "Associate Professor." If the rank is not one of the defined options, it returns "other" (which will be filtered later in writing to the file).

- `def word_counter`: A function that cleans the text from symbols and commas and returns clean text along with word count. In the case of "non available," it returns the specified value.

- `def api_gender`: A function that splits and inserts the researcher's name into a list, sends it to an API, and returns the gender and probability.

- `def links`: A function for extracting links. It receives the department's URL and returns the links of the lecturers on the page.

## Part 2 – Departments
Each stage is wrapped in try and except blocks.

### Philosophy:
- Insert the department's link to fetch links to researchers.
- Define general variables such as specialization, list of publications, etc., with each defined as str/list, for example. Counter reset.
- To obtain the researcher's name, rank, and specialization, access the container and extract based on the li tag from the page. The loop extracts the texts and adds them to the list variable. Identification of the name, rank, and specialization is based on the position in the list.
- Department Name: Found inside the class named "name-primary" and within the a tag. Extract the text and pass it to the function returning the department's name.
- Institution: Access the university's link inside the a tag and extract the first word to get the institution's name.
- Research Field Description: Collect the researcher's bio by searching for the xpath 'article body' and within the p tag. The loop extracts all the text and adds it to the counter variable in the function, returning clean text and word count.
- Submit the researcher's name to the API with the main function to obtain gender and probability.
- Publications: Access the element that is a link to publications on the researcher's page (if available). In the new publications page, access the articleBody and extract elements with the li tag. Then, loop through the elements, adding the text of each publication to the "publication" variable and counting how many li elements there are (as long as there are more than 2 words to filter out titles). If our counter is greater than 0, it adds to the variable; otherwise, it returns a "non available" value. In addition, submit the "publications" variable to the main function that counts the articles by years, applying a condition to take the data minimum when comparing li to the count of years (since there are cases where years appear multiple times in the same publication).

### Biology:
- Insert the department's link to fetch links to researchers.
- Define general variables as in Philosophy.
- To obtain the researcher's name, rank, and department:
  - Researcher's Name: From the page header.
  - Rank and Department: From views-row and then field-content. Pass these to functions for rank and department and return the results.
- Submit the researcher's name to the API with the main function to obtain gender and probability.
- Specialization – Research Field:
  - Access field-body, if what was pulled is less than or equal to 2, return a "non available" value – indicating no research field description. Otherwise, access the element at position 1 in the list and has a p tag, extract the researcher's specialization. If the length of what was pulled is less than 20, pull from the div instead of the p since we've seen that the bio is always more than 20 in each researcher's page. If not found in either, check if there is an li that includes the researcher's bio and then apply the same conditions as long as less than or equal to 2, it does not enter a value, and if less than 20, it checks the div.
- Publications: Insert the div of field publications, save the texts of li in a variable, and submit to the counter function by years. If not present, search by the p tag and use the same counter. Also, count how many li and how many p are in the div. To get the most accurate result in the number of publications, we have applied a number of conditions for comparing counters before checking if the publications appear in li or p and then comparison between the counter of the researcher's name and the years.

### Computer Science:
- Insert the department's link to fetch links to researchers.
- Define general variables as in Philosophy.
- Specialization/Research Field:
  - Inside field-container, extract the li, and within it, look for the words "specialty" or "research groups" describing the research field on the page. Extract the text; if no text appears, return a "non available" value.
  - The research field is also collected from the researcher's bio, inside mainbody > articlebody, and added to what was previously pulled.
  - Submit to the text cleaning and word count function.
- Inside field-container, where li is extracted for specialization, search for the word researcher's name in position 1 and rank in position 2. Pass to the function to get the rank. When there is no image for the researcher, the name and rank are found in another location in the list, so we added a condition to find them in the second position.
- Department and Institution: Enter the footer and extract the p, then pass the text to the function of the department and insert it into the variable of the institution.
- Submit the researcher's name to the API with the main function to obtain gender and probability.
- No publications on researchers' pages, so did not fetch any.

### Psychology:
- Insert the department's link to fetch links to researchers.
- Define general variables as in Philosophy.
- Inside field-container where li is extracted, search for the researcher's name in position 1 and rank in position 2. Pass to the function to get the rank. Run a loop on li, and if the word "Areas" with colons appears, it extracts the research field from the li. Check if it appears in the bio in the articlebody and update the specialization (add to the areas if found).
- Access the footer and update the department and institution.
- Submit the researcher's name to the API with the main function to obtain gender and probability.
- Text cleaning and word count function.
- If there is a researcher's site with publications, access the driver and open a new site, and from the new site within the div containing publications, extract the p tag. There is a loop running on the text, and if it contains more than 15 words, it means it is an article, so it counts it. If there are articles, update the variable. Then, compare to the count function by years and by the researcher's name. Compare all counters to take the most accurate value.

### Law:
- Insert the department's link to fetch links to researchers.
- Define general variables as in Philosophy.
- Researcher's Name: Extract from the page title.
- Department: Extract from class=title, pass it to the function of the department, and get the department's name. Also, extract the rank from the same location.
- Institution: Extract from location 0 in itemprop=name.
- Remove hyphens from the name to pass to the API later, replace with spaces.
- Specialization/Research Field:
  - Click on a link containing the text "expertise" on the same page and check if class=expertise-areas exists. If yes, extract the text.
  - In researcher pages, there is usually a short paragraph under personal details describing the research field, marked with class="synopsis". Collect this text and append it to the previously gathered expertise.
  - If nothing was added to the expertise variable, give it a value of "non available".
  - Click on a link containing the text "Biography" on the same page, and if it exists, extract the text and add it to the expertise variable.
- Submit the researcher's name to the API with the main function to obtain gender and probability.
- Text cleaning and word count function for expertise.
- Publications:
  - Check if there is a link to publications on the researcher's page. If not, return "non available".
  - If there are multiple ways of counting (due to different page structures and formats under p, li, or em):
    - If under p or li:
      - If more than one paragraph, count each sentence ending with a period/comma/semicolon within the paragraph.
      - If only one paragraph, count each sentence ending with a period/comma/semicolon within the paragraph.
      - If no parentheses in the paragraph, count the number of words. If more than 7 words, consider it an article. This is suitable for multiple paragraphs where each paragraph is an article.
      - Compare the counters and take the highest number.
    - Sometimes, within a div, part of each article is under the em tag. In this case, count it and compare it with the result from p/li.

Write to the file:
Remove researchers with a rank of "other" (not one of the defined ranks in the guidelines). Write the full data frame of all departments to Excel.

Key Challenges:
The main challenge in the work was identifying the different pages and structures, mainly in the researchers' publications, and trying to collect the most accurate data on each structure. For example, in publications, there are pages structured with one large paragraph containing multiple publications, pages with lists where each li is an article, pages where each paragraph is an article, etc. Therefore, in the code description above, you can see that we tried to cover many possibilities and used counter comparisons to achieve the most accurate result.
