# Huawei SMS forwarding
A python CLI program that allows you to forward SMS received by your Huawei router to a phone number.

**Why ?** <br />
I always wanted to use my router phone number but going on the router local website to check my SMS is not really convenient, so I needed to find a way to forward SMS that also allows me to filter some of them.

**Note:** <br />
This program uses the [Huawei LTE API](https://github.com/Salamek/huawei-lte-api) created by [Salamek](Salamek).


## Features:
- **Forwarded SMS format**: Forwarded SMS contains the date and the sender's phone number/contact.
- **Contacts**: To replace raw phone numbers by contact names inside the forwarded SMS.
- **Whitelist**: Only SMS received by phone numbers in this list are forwarded.
- **History**: A JSON file that contains all the forwarded SMS with their date and their content.


## The .env file:
All the parameters used by this program are stored inside a single .env file (in the same directory as `app.py`).

This file is created when the program is launched for the first time or if the program don't find the .env file,
the program will then terminate and ask you to fill the needed info inside of it.

**Note:** <br />
As you see, the account username and password is needed to connect to the router, it is not a big deal because these can only be used by someone connected to your local network, but don't hesitate to check my code to be sure that I never send them anywhere.

```py
# Your router IP address (generally 192.168.8.1)
ROUTER_IP_ADDRESS=192.168.8.1

# Account details (the same one used to identify yourself on the local Huawei router website)
ACCOUNT_USERNAME=""
ACCOUNT_PASSWORD=""

# International phone numbers of the router and the user, example: "+33 5 42 56 48 21"
# Spaces are removed when the file is loaded so you can add spaces if you want
# User phone number is the number where all the forwarded SMS are going
ROUTER_PHONE_NUMBER=""
USER_PHONE_NUMBER=""

# Senders whitelist
# Example: ["+33937023216"] means that only SMS sent by this number are forwarded
# Leaving the list empty deactivates this option
# Spaces and uppercase characters can be used
SENDERS_WHITELIST=[]

# Allows you to replace phone numbers by contact names inside the forwarded SMS
# Formatted as a list where a phone number is followed by its contact name
# Example: ["+33123456789", "Binance"] -> This number will be replaced by "Binance"
CONTACTS=[]

# Delay used to check SMS in a loop (in seconds)
LOOP_DELAY=15
```


## Compatibility:
**Note**: Tested only on a B525s-65a but it should work with the routers listed inside the [Huawei API](https://github.com/Salamek/huawei-lte-api#tested-on) doc.

#### 3G/LTE Routers:
* Huawei B310s-22
* Huawei B315s-22
* Huawei B525s-23a
* Huawei B525s-65a
* Huawei B715s-23c
* Huawei B528s
* Huawei B535-232
* Huawei B628-265
* Huawei B818-263
* Huawei E5186s-22a
* Huawei E5576-320
* Huawei E5577Cs-321
 
#### 3G/LTE USB sticks:
(Device must support NETWork mode aka. "HiLink" version, it wont work with serial mode)
* Huawei E3131
* Huawei E3372
* Huawei E3531


#### 5G Routers:
* Huawei 5G CPE Pro 2 (H122-373)

(probably will work for other Huawei LTE devices too)

#### Will NOT work on:
* Huawei B2368-22 (Incompatible firmware, testing device needed!)
* Huawei B593s-22 (Incompatible firmware, testing device needed!)
