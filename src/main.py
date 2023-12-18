import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
import re
from questions_db import Question_DB
from pprint import pprint
import json

TOTAL_PAGES = 60
excluded_urls = [
    "https://leetcode.com/problemset/all-code-essentials",
    "https://leetcode.com/problemset/algorithms",
    "https://leetcode.com/problemset/database",
    "https://leetcode.com/problemset/shell",
    "https://leetcode.com/problemset/concurrency",
    "https://leetcode.com/problemset/javascript",
    "https://leetcode.com/problemset/pandas",
    "https://leetcode.com/problemset",
]

excluded_substring_1 = "/?envType=daily-question"
excluded_substring_2 = "/solution"
excluded_questions = ["W1", "W2", "W3", "W4", "W5"]


def configure_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--enable-chrome-browser-cloud-management")
    # options.add_argument("--headless")

    return webdriver.Chrome(options=options)


def exclude_urls_and_substrings(a_tags):
    result_data = []
    for tag in a_tags:
        href_attr = tag.get_attribute("href")
        if href_attr and "/problems" in href_attr:
            if any(url in href_attr for url in excluded_urls):
                continue
            elif excluded_substring_1 in href_attr or excluded_substring_2 in href_attr:
                continue
            if any(quest in tag.text for quest in excluded_questions):
                continue
            title_text = re.sub(r"^\d+\.\s+", "", tag.text.strip())
            result_data.append({"title": title_text, "link": href_attr})
    return result_data


def scrape_question_details(driver: webdriver, result_data: list[dict[str, str]]):
    question_details = []
    # for question in result_data:
    i = 1
    for question in result_data:
        print(f"OPENING QUESTION: {i}")
        example_list = []
        constraints_list = []
        my_question_dict = {
            "title": "",
            "difficulty": "",
            "example": [],
            "description": "",
            "constraints": [],
        }

        href = question["link"]
        driver.get(href)
        time.sleep(4)

        a_tag_details = driver.find_elements(by=By.TAG_NAME, value="a")
        if not a_tag_details:
            continue
        for tag in a_tag_details:
            href_attribute = tag.get_attribute("href")
            if href_attribute and "/problems" in href_attribute:
                if any(url in href_attribute for url in href_attribute):
                    continue
                elif (
                    excluded_substring_1 in href_attribute
                    or excluded_substring_2 in href_attribute
                ):
                    continue
                if any(quest in tag.text for quest in excluded_questions):
                    continue
                title_text = re.sub(r"^\d+\.\s+", "", tag.text.strip())
                my_question_dict["title"] = title_text

        difficulty_details = driver.find_elements(by=By.CLASS_NAME, value="capitalize")
        for el in difficulty_details:
            my_question_dict["difficulty"] = el.text.strip("'")

        details_div = driver.find_element(by=By.CLASS_NAME, value="xFUwe")
        details_of_quest = details_div.find_elements(by=By.TAG_NAME, value="p")
        example = details_div.find_elements(by=By.TAG_NAME, value="pre")
        constraints = details_div.find_elements(by=By.TAG_NAME, value="ul")

        details_of_quest_text = "\n".join(
            line.text
            for line in details_of_quest
            if not any(
                prefix in line.text
                for prefix in ["Example 1:", "Example 2:", "Example 3:", "Constraints:"]
            )
        )
        my_question_dict["description"] = details_of_quest_text

        for some in example:
            example_list.append(some.text)
        my_question_dict["example"] = example_list

        for some in constraints:
            constraints_list.append(some.text)
        my_question_dict["constraints"] = constraints_list

        question_details.append(my_question_dict)
        i += 1
    return question_details


def push_link_to_database(links: list, db: Question_DB):
    print("Pushing links to db")
    for link in links:
        db.insert_links(title=link["title"], link=link["link"])
    print("Pushed links to db success")


def push_questions_to_database(questions: list[dict], db: Question_DB):
    print("Pushing questions to db")

    for question in questions:
        examples = json.dumps(question["example"])
        constraints = json.dumps(question["constraints"])
        db.insert_question(
            title=question["title"],
            description=question["description"],
            difficulty=question["difficulty"],
            constrains=constraints,
            example=examples,
        )
    print("Pushed questions to db success")


def main():
    db = Question_DB("questions.sqlite")
    db.create_links_table()
    db.create_questions_table()

    driver = configure_driver()

    print("OPENING CHROME BROWSER")
    for page_no in range(1, TOTAL_PAGES + 1):
        print(f"Page no: {page_no}")
        driver.get(f"https://leetcode.com/problemset/all-code-essentials/?page={10}")
        time.sleep(3)
        print("OPENED CHROME BROWSER")

        a_tags = driver.find_elements(by=By.TAG_NAME, value="a")
        result_data = exclude_urls_and_substrings(a_tags)
        push_link_to_database(result_data, db)

        print(len(result_data))

        question_details = scrape_question_details(driver, result_data)
        push_questions_to_database(question_details, db)
    print("DONE")


if __name__ == "__main__":
    main()
