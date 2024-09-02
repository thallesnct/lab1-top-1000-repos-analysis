import pandas as pd
import matplotlib.pyplot as plt

def seconds_to_time_string(seconds):
    # Aproximação do numero de dias em um mes
    days_in_month = 30.44
    
    # Converter segundos para meses
    months, remainder = divmod(seconds, days_in_month * 24 * 3600)
    
    # Converter segundos restantes para dias
    days, remainder = divmod(remainder, 24 * 3600)
    
    # Converter segundos restantes para horas
    hours, remainder = divmod(remainder, 3600)
    
    # Converter segundos restantes para minutos
    minutes, seconds = divmod(remainder, 60)
    
    result = f"{int(months)} meses, {int(days)} dias, {int(hours)} horas, {int(minutes)} minutos e {int(seconds)} segundos"
    
    return result

def calculate_medians(pd_instance):
    pd_copy = pd_instance.copy()
    pd_copy["repo_age"] = pd_copy["time_since_created_at_in_seconds"].median() # RQ1
    pd_copy["pull_requests_accepted_median"] = pd_copy["pull_requests_accepted"].median() # RQ2
    pd_copy["releases_count_median"] = pd_copy["releases_count"].median() # RQ3
    pd_copy["time_since_last_update"] = pd_copy["time_since_last_update_in_seconds"].median() # RQ4
    pd_copy["closed_issues_ratio_median"] = pd_copy["closed_issues_ratio"].median() # RQ6

    return pd_copy

def calculate_filtered_release_count_median(pd_instance):
    pd_copy = pd_instance[pd_instance['releases_count'] > 1]
    releases_count_median = pd_copy["releases_count"].median() # RQ3 filtrada

    return releases_count_median

def addlabels(x,y):
    for i in range(len(x)):
        plt.text(i,y[i],y[i])

def calculate_and_print_percentage_of_most_popular_languages(pd_instance, language_indexes_list, language_list):
    filtered_df = pd_instance[pd_instance['primary_language_mapping'].isin(language_indexes_list)]

    percentage_series = filtered_df['primary_language_mapping'].value_counts()
    percentage_series = (percentage_series / 1000) * 100

    plt.figure(figsize=(10, 6))
    ax = percentage_series.plot(kind='bar')

    # Adicionar labels
    for p in ax.patches:
        ax.annotate(f'{p.get_height():.2f}%', (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='center', xytext=(0, 5), textcoords='offset points')

    plt.title('Porcentagem de repositórios em cada uma das 10 linguagens mais populares')
    plt.xlabel('Item')
    plt.ylabel('Porcentagem')
    plt.xticks(ticks=range(len(language_indexes_list)), labels=[language_list[item] for item in language_indexes_list], rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('most_popular_languages_pct_chart.png', format='png')



if __name__ == '__main__':
    data = pd.read_csv('github_repositories_data.csv')
    language_list = []

    with open('language_list.txt', mode='r', newline='') as file:
        language_list = file.readlines()

    most_popular_languages_indexes = []

    with open('most_popular_languages_indexes.txt', mode='r', newline='') as file:
        most_popular_languages_indexes = [int(item) for item in file.readlines()]
        
    data_with_medians = calculate_medians(data)
    # Set up the plotting area
    # plt.figure(figsize=(12, 8))

    # Plot each column
    # print(data_with_medians.at[1, "pull_requests_accepted_median"])
    print("Mediana da idade dos repositorios analisados: " + seconds_to_time_string(data_with_medians.at[1, "repo_age"])) # RQ1
    print("Mediana do numero de pull requests aceitos dos repositorios analisados: " + str(data_with_medians.at[1, "pull_requests_accepted_median"])) #RQ2
    print("Mediana do numero de releases dos repositorios analisados: " + str(data_with_medians.at[1, "releases_count_median"])) #RQ3
    print("Mediana do numero de releases dos repositorios analisados (filtrados por release count > 1): " + str(calculate_filtered_release_count_median(data))) #RQ3
    print("Mediana do tempo desde o ultimo update dos repositorios analisados: " + seconds_to_time_string(data_with_medians.at[1, "time_since_last_update"])) #RQ4
    print("Mediana do percentual de issues fechadas dos repositorios analisados: " + str(data_with_medians.at[1, "closed_issues_ratio_median"])) #RQ6

    calculate_and_print_percentage_of_most_popular_languages(data, most_popular_languages_indexes, language_list)
    # for column in ["pull_requests_accepted", "releases_count", "time_since_last_update", "closed_issues_ratio"]:
        # print(data_with_medians.at[1, column])
        # plt.plot(data_with_medians.index, data_with_medians[column], label=column, marker='o')

    # Add titles and labels
    # plt.title('Comparison of Different Metrics')
    # plt.xlabel('Index')
    # plt.ylabel('Values')

    # Add a legend
    # plt.legend()

    # Show the grid for better readability
    # plt.grid(True)

    # Display the plot
    # plt.show()
