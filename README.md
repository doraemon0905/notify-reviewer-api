# Notify Code Review
This is the source for the API to create a slash command for reviewing code on Employment Hero's Slack.

For more information, you can refer to the documentation:
[Bot Send message request review bot - Employment Hero Code Review](https://employmenthero.atlassian.net/wiki/spaces/Eternal/pages/3232694793/Bot+Send+message+request+review+bot+Employment+Hero+Code+Review)

# How to use command?

To send a message for code review, you must first install the **Employment Hero Code Review** app in your Slack channel.

You can install it using the following link:

```
https://employmenthero.slack.com/marketplace/A07R7MQ31KR-employment-hero-code-review?settings=1&tab=settings
```

Once installed, you can use the bot from any channel in the Employment Hero Slack workspace.

### Example Commands

Here are some example commands you can use with the **Employment Hero Code Review** app to request a code review:

```
/review ask @squad-eternals to review PR https://github.com/Thinkei/employment-hero/pull/46731
/review https://github.com/Thinkei/employment-hero/pull/46731 @squad-eternals #eh-eng-code-review
/review https://github.com/Thinkei/employment-hero/pull/46731 @squad-eternals
/review https://github.com/Thinkei/employment-hero/pull/46731 #eh-eng-code-review
/review https://github.com/Thinkei/employment-hero/pull/46731
```

### Explanation

- The first example will ask the **squad-eternals** to review the pull request (PR).
- The second example sends the PR to **squad-eternals** and posts the request in the `#eh-eng-code-review` channel.
- The third example sends the PR to **squad-eternals** only.
- The fourth example posts the request in the `#eh-eng-code-review` channel without tagging any specific user.
- The fifth example sends the review request using the default reviewers assigned on the pull request.


```
/review https://github.com/Thinkei/employment-hero/pull/46731
```

This command will automatically notify the reviewers requested on the pull request by default.
