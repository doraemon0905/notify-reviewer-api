class ReviewMessageDecorator:
    def __init__(self, review_message):
        self.review_message = review_message

    def message(self):
        user_id = self.review_message["user_id"]
        title = self.review_message["title"]
        pr_url = self.review_message["pr_url"]
        formatted_reviewers = self.review_message["formatted_reviewers"]

        message_review = f"{'cc ' + formatted_reviewers if formatted_reviewers else ''}"

        if formatted_reviewers:
            message_review += "\n"

        return (
            f"Hello team, please assist {'<@' + user_id + '> ' if user_id else ''}in reviewing this PR {pr_url} \n"
            f"Summary: {title} \n"
            f"{message_review}"
            "Thank you! :pepe_love:"
        )
