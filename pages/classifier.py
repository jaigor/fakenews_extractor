from pages.classifiers.bert import BERT
from twitter.models import Tweet


class Classifier:

    def __init__(self, method, tweets):
        self._method = method
        self._tweets = []
        self._predicted_tweets = {}

        for tweet in tweets:
            self._tweets.append((tweet, Tweet.objects.find_by_id(tweet).get().text))

    def loading_classifier(self):
        print("training model")
        if self._method == "BERT":
            # load bert model
            # text_test = ['Covid19 is a danger for humanity.']
            bert = BERT(self._tweets)
            self._predicted_tweets = bert.reload_model()
        else:
            print("No classifier method chosed")

        # save tweet predictioncort
        return self._save_tweets_data()

    def _save_tweets_data(self):
        # order list first
        ordered = sorted(self._predicted_tweets.items(), key=lambda x: x[1], reverse=True)

        tweets = []
        for tweet in ordered:
            tweets.append(Tweet.objects.update_spreader(tweet[0], tweet[1]))

        # show tweets in ranking service
        return tweets
