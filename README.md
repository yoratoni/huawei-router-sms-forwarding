# Huawei SMS forwarding
A python CLI program that allows you to forward SMS received by your Huawei router to a phone number.

**Why ?** <br />
I always wanted to use my router phone number but going on the router local website to check my SMS is not really convenient, so I needed to find a way to forward SMS that also allows me to filter some of them.

This program is based on the [Huawei LTE API](https://github.com/Salamek/huawei-lte-api) created by [Salamek](Salamek).


## Features:
- **Forwarded SMS format**: Forwarded SMS contains the date and the sender's phone number/contact.
- **Contacts**: To replace raw phone numbers by contact names inside the forwarded SMS.
- **Whitelist**: Only SMS received by phone numbers in this list are forwarded.
- **History**: A JSON file that contains all the forwarded SMS with their date and their content.

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
