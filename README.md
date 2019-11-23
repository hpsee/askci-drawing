# AskCI Pizza Drawing!

![pizza.png](pizza.png)

This script will help to select a drawing winner by using the Discourse API
to randomly select a post between two dates. You'll first need to export
an API key, discourse site, and username.

```bash
export DISCOURSE_API_KEY=xxxxxxxxxxxxxx
export DISCOURSE_API_USER=dinosaur
export DISCOURSE_BASE="https://ask.cyberinfrastructure.org"
```

You actually don't need to export the third if you are using AskCI (the default shown
is already set in the script if the environment variable is not defined).
Then you can run the drawing!

```bash
./drawing.py 2019-11-18 2019-11-22
```

The command above will select a winner between the 18th and 22nd of November,
print the winner to the screen, and also save the complete data to `contenders-<date>.json`
in case you need to re-roll.

## Contest History

 - [SC 2019](https://ask.cyberinfrastructure.org/t/calling-all-people-who-like-pizza-and-supercomputing/1134) was run between 2019-11-18 and 2019-11-22 on the 23rd of the month, corresponding with the result file [contenders](contests/contenders-2019-11-23.json).


See [winners](winners.md)


## How does it work?

 - We first get a list of all topics across all categories
 - We then look up the posts for each topic
 - If the post date is within the range, we add to a list of contenders
 - We randomly select a winner
 - The winner is printed to the screen, and data saved as `contenders-<date>.json`


Note that the sleep time (1.5 seconds) assumes an admin API key. If you have a user
token, you can't make requests as frequently, and will need to increase that.

## How could we improve it?

### Exclude Users

We could easily add a list of users to disclude, but instead we can just use
the list of contenders to select again (this is a weird and twisted way for those
that aren't allowed to contribute, the site admins, to see "Hey I could have won!" and 
then re-roll. How do we do that?

```bash
./reroll.py contests/contenders-<date>.json
```

### Query By Date

We are currently exporting all posts to check the date for. Very likely we can
use a query parameter for the discourse API to filter instead. I didn't do this
because I was nervous about how the timestamp would be parsed and wanted to do it myself.
