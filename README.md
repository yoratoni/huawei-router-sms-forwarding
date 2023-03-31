# Huawei SMS forwarding
A python CLI program that I made a long time ago and recently updated, that allows you to work
with SMS received on a 4G Huawei router.

**Why ?** <br />
As a 4G router takes a SIM card, it have a phone number and then, can be used to send SMS.
The problem with that is that you need to access your Huawei router interface on the internet.

**Credit:** <br />
This program uses the [Huawei LTE API](https://github.com/Salamek/huawei-lte-api) created by [Salamek](Salamek).


## Features:
These features are configurable from the `config.yaml` file at the root of the project (`/src`).

- **Contacts**: Allows you to link a name to a phone number, easier to identify each forwarded number.
- **Forwarders**: The SMS received by the router are forwarded to these numbers, a whitelist can be added
  to redirect only some numbers.
- **Repliers**: An auto-reply system, if a message is received from a specific number, and this message contains a string,
  like, if it starts with an "Hi!" (or "Hi!" at any place inside of the message), it replies something.
  I added this feature for someone who needed it to send an automatic message to his internet provider.


## History:
Here's an example of a forwarded SMS inside the history, the history can be found inside `/logs/history.json`.

![](https://raw.githubusercontent.com/yoratoni/huawei-router-sms-forwarding/1e445925ef691eb0ec1bd2283fb7a959093d13cf/doc/History.png "History example")

**Details**: <br />
- "40086" corresponds to the SMS ID (used by the router to identify every SMS).
- "Phone" is the phone number (not impacted by the contact names).
- "Content" is simply the content of the SMS
- "Date" is the date when the SMS has been received, not forwarded.
- "Contact" is the contact name that you optionally added to the "contacts" field inside the YAML file.


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
* SoyeaLink B535-333

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
