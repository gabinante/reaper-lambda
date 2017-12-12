# Reaper Lambda

This lambda:
•Finds all instances in the selected region(s)

•Ensures all instances are tagged with "expiration_date" of "never" or
with an integer (epoch time).

•Terminates any instances without an expiration_date

•Terminates any instances past their expiration date

## Yes, this will blow up your AWS account if instances are not tagged!

## Notes
•This may not work in exceptionally large AWS accounts. For this reason
I've split it out by region - you may specify a smaller array of regions
at the top. If your account is exceptionally large, it would be a very
minor effort to add an additional for loop that iterates over each VPC
in a region. Feel free to add a PR!

•We use epoch time because integers are easy to compare and I'm lazy.
Deal with it or fix it in your own environment :)

•If you tag your instance with an expiration_date that causes a
ValueError, I don't think I've handled that properly. Please don't be
manually tagging your stuff. We have terraform and cloudformation for
this, people!
