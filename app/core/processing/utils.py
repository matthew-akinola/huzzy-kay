def remove_outlier(service_response):
    '''
    This Function Removes the Odd VIP Scores in the Source Classes Response

    How it works:
    - Remove Source Classes that returns an empty result,
    - Check if Response from the source classes are for more than one individual (
            e.g Will Smith search returns and Action and an American Footballer)
    - Get the max vip score in the response
    - Use max vip score to remove the outliers
    - return responses with almost similar vip_score
    '''
    # Remove Empty responses from nested responses
    service_response = [response for response in service_response if response != []]
    # Getting each element from nested Lists and storing them in a new list
    response_list_score = [element['vip_score'] for nestedlist in service_response for element in nestedlist]
    if response_list_score != []:
        all_ones = all([True if len(a) == 1 else False for a in service_response])
        if all_ones:
            top_vip_scores_list = [max(response_list_score)]
            # Remove Outlier
            for a in response_list_score:
                if (a > 80) or (max(response_list_score) - a) < 10:
                    top_vip_scores_list.append(a)
            # Return Response of the filter VIP Score
            filtered_service_response = []
            for response in service_response:
                source_class = []
                for result in response:
                    if result['vip_score'] in top_vip_scores_list:
                        source_class.append(result)
                filtered_service_response.append(source_class)
            return filtered_service_response
    return service_response