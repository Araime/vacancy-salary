import os
import requests
from terminaltables import DoubleTable
from dotenv import load_dotenv


def predict_salary(salary_from, salary_to):
    if salary_from and salary_to:
        return (salary_from + salary_to) / 2
    elif salary_from:
        return salary_from * 1.2
    elif salary_to:
        return salary_to * 0.8


def get_hh_vacancies(hh_url, language, town_code):
    vacancies = []
    payload = {
        'text': language,
        'area': town_code,
        'period': '30',
        'currency': 'RUR',
        'only_with_salary': 'true'
    }
    page = 0
    pages_number = 1
    while page < pages_number:
        payload['page'] = page
        response = requests.get(hh_url, params=payload)
        response.raise_for_status()
        page_data = response.json()
        vacancies.extend(page_data['items'])
        pages_number = page_data['pages']
        page += 1
    return vacancies


def predict_rub_salary_for_hh(vacancy):
    if not vacancy['salary']['currency'] == 'RUR':
        return None
    salary_from = vacancy['salary']['from']
    salary_to = vacancy['salary']['to']
    return predict_salary(salary_from, salary_to)


def get_language_statistics_for_hh(hh_url, programming_languages):
    vacancy_statistics = {}
    for language in programming_languages:
        vacancies = get_hh_vacancies(hh_url, language, moscow_code_for_hh)
        vacancies_found = len(vacancies)
        predicted_salaries = []
        for vacancy in vacancies:
            predicted_salary = predict_rub_salary_for_hh(vacancy)
            if predicted_salary:
                predicted_salaries.append(predicted_salary)
        vacancies_processed = len(predicted_salaries)
        try:
            average_salary = int(sum(predicted_salaries) / vacancies_processed)
        except ZeroDivisionError:
            average_salary = 0
        vacancy_statistics[language] = {
            'vacancies_found': vacancies_found,
            'vacancies_processed': vacancies_processed,
            'average_salary': average_salary
        }
    return vacancy_statistics


def get_sj_vacancies(sj_url, language, sj_secret_key, town_code, job_catalog_number):
    vacancies = []
    payload = {
        'keywords[keys][]': language,
        'town': town_code,
        'catalogues[]': job_catalog_number,
        'no_agreement': 1
    }
    headers = {
        'X-Api-App-Id': sj_secret_key
    }
    page = 0
    more = True
    while more:
        payload['page'] = page
        response = requests.get(sj_url, headers=headers, params=payload)
        response.raise_for_status()
        page_data = response.json()
        vacancies.extend(page_data['objects'])
        more = page_data['more']
        page += 1
    return vacancies


def predict_rub_salary_for_sj(vacancy):
    if not vacancy['currency'] == 'rub':
        return None
    salary_from = vacancy['payment_from']
    salary_to = vacancy['payment_to']
    return predict_salary(salary_from, salary_to)


def get_language_statistics_for_sj(sj_url, programming_languages, sj_secret_key):
    vacancy_statistics = {}
    for language in programming_languages:
        vacancies = get_sj_vacancies(sj_url, language, sj_secret_key, moscow_code_for_sj,
                                     development_and_programming_from_catalog)
        vacancies_found = len(vacancies)
        predicted_salaries = []
        for vacancy in vacancies:
            predicted_salary = predict_rub_salary_for_sj(vacancy)
            if predicted_salary:
                predicted_salaries.append(predicted_salary)
        vacancies_processed = len(predicted_salaries)
        try:
            average_salary = int(sum(predicted_salaries) / vacancies_processed)
        except ZeroDivisionError:
            average_salary = 0
        vacancy_statistics[language] = {
            'vacancies_found': vacancies_found,
            'vacancies_processed': vacancies_processed,
            'average_salary': average_salary
        }
    return vacancy_statistics


def get_table_instance(statistics, title):
    table = []
    table.append([
        'Язык программирования',
        'Вакансий найдено',
        'Вакансий обработано',
        'Средняя зарплата'
    ])
    for language, vacancy_statistic in statistics.items():
        row = []
        row.append(language)
        row.extend(list(vacancy_statistic.values()))
        table.append(row)
    table_instance = DoubleTable(table, title)
    return table_instance.table


if __name__ == '__main__':
    load_dotenv()

    hh_url = 'https://api.hh.ru/vacancies'
    moscow_code_for_hh = 1

    sj_secret_key = os.getenv('SUPERJOB_SECRET_KEY')
    sj_url = 'https://api.superjob.ru/2.33/vacancies/'
    moscow_code_for_sj = 4
    development_and_programming_from_catalog = 48

    programming_languages = [
        'JavaScript',
        'Java',
        'Python',
        'Ruby',
        'PHP',
        'C++',
        'C#',
        'Go'
    ]

    vacancy_statistics_for_hh = get_language_statistics_for_hh(hh_url, programming_languages)
    vacancy_statistics_for_sj = get_language_statistics_for_sj(sj_url, programming_languages, sj_secret_key)

    hh_table = get_table_instance(vacancy_statistics_for_hh, 'HeadHunter Москва')
    superjob_table = get_table_instance(vacancy_statistics_for_sj, 'Superjob Москва')
    print(hh_table)
    print(superjob_table)
