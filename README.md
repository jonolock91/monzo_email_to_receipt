# Monzo email to receipt

This was created as a personal project to see how easy/hard it would be to parse transactional emails and have them appear in my Monzo banking app as a Receipt.

 tl;dr
 --
 Currently supports .txt emails and works for parsing the following:
 - Asos
 - Myprotein
 - Gymshark
 - Bulk powders
 - eBay
 
 It should be fairly simple (hopefully) to add support for further emails.

![Monzo receipt created using this project](https://github.com/jonolock91/monzo_email_to_receipt/blob/master/example.png?raw=true)

Intro
--
This project is built in python and to be ran with python 3.

This has been built to parse .txt emails as I found this much easier to work with over HTML emails. I've been manually saving my emails as .txt and pasting them into the `emails` directory, this could be automated in the future.

Currently only a few merchant emails are supported but there's room to expand and add more easily enough. I initially tried to make the email parsing as generic as possible but found that by making it specific per brand (e.g. Asos) it was much quicker to write a regex expression to find the important data, i.e Total & line items.

This project handles all the Monzo authentication needed so just fill in with your Monzo creds which you can get over at their API. [Monzo developer](https://developers.monzo.com).
> The access token and potentially a few other methods I've used have been for speedy development and are not the most secure, but this is not a commercial project.

Get started
--
This is how I've been working on the project so it may be helpful
- Python 3
- Install using a [virtual env wrapper](https://virtualenvwrapper.readthedocs.io/en/latest/)
- External packages are in the requirements.txt file
- Create a developer account over at [Monzo](https://developers.monzo.com) and get your creds
- Convert your order email to .txt (Mac OSX mail: Selected email > File > Save as > Plain text)
- Drop a few .txt emails into the emails directory to begin
- Run the parse_email.py file in a terminal and follow the instructions for Auth'ing with Monzo!

Tweet me if you're using this project
--
https://twitter.com/jonolock

Enjoy!
