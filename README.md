# Notify Code Review
This is the source for API to create slash command review code on Employment Hero's Slack.

# How to use command?

To send the message, you must first install the app Employment Hero Code Review to your Slack channel.

```
https://employmenthero.slack.com/marketplace/A07R7MQ31KR-employment-hero-code-review?settings=1&tab=settings
```

You can use the bot from every channel on workspace of Employment Hero.

Here is some example command you can use for send message to review with Employment Hero Code Review app

```
/review ask @squad-eternals to review PR https://github.com/Thinkei/employment-hero/pull/46731
/review https://github.com/Thinkei/employment-hero/pull/46731 @squad-eternals #eh-eng-code-review
/review https://github.com/Thinkei/employment-hero/pull/46731 @squad-eternals
/review https://github.com/Thinkei/employment-hero/pull/46731 #eh-eng-code-review
/review https://github.com/Thinkei/employment-hero/pull/46731
```

It will mention the squad eternals or another Slack user you've indicated on command to review your PR

```
/review https://github.com/Thinkei/employment-hero/pull/46731
```

It will mentioned the reviewers requested on Pull Request by default
